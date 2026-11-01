from pathlib import Path
import io

import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


# ---------------------------------------------------------
# PROJECT CONFIGURATION
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "logistics_features.csv"
)


# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="LogiScope - Supply Chain Analytics",
    description=(
        "Delivery performance, delay risk and "
        "logistics efficiency analytics."
    ),
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------------------------------------
# DATASET COLUMN MAPPING
# Supports both original dataset names and cleaned names.
# ---------------------------------------------------------

COLUMN_NAMES = {
    "actual_days": [
        "Days for shipping (real)",
        "days_for_shipping_real"
    ],

    "scheduled_days": [
        "Days for shipment (scheduled)",
        "days_for_shipment_scheduled"
    ],

    "risk": [
        "Late_delivery_risk",
        "late_delivery_risk"
    ],

    "delivery_status": [
        "Delivery Status",
        "delivery_status"
    ],

    "shipping_mode": [
        "Shipping Mode",
        "shipping_mode"
    ],

    "region": [
        "Order Region",
        "order_region"
    ],

    "country": [
        "Order Country",
        "order_country"
    ],

    "market": [
        "Market",
        "market"
    ],

    "customer_segment": [
        "Customer Segment",
        "customer_segment"
    ],

    "latitude": [
        "Latitude",
        "latitude"
    ],

    "longitude": [
        "Longitude",
        "longitude"
    ]
}


DISPLAY_NAMES = {
    "shipping_mode": "Shipping Mode",
    "region": "Order Region",
    "country": "Order Country",
    "market": "Market",
    "customer_segment": "Customer Segment"
}


# ---------------------------------------------------------
# DATASET FUNCTIONS
# ---------------------------------------------------------

def load_dataset():

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATASET_PATH}"
        )

    df = pd.read_csv(
        DATASET_PATH,
        low_memory=False
    )

    return prepare_dataset(df)


def find_column(df, field_name):

    possible_names = COLUMN_NAMES.get(field_name, [])

    for column in possible_names:

        if column in df.columns:
            return column

    return None


def prepare_dataset(df):

    actual_column = find_column(df, "actual_days")
    scheduled_column = find_column(df, "scheduled_days")

    if actual_column and scheduled_column:

        actual_days = pd.to_numeric(
            df[actual_column],
            errors="coerce"
        )

        scheduled_days = pd.to_numeric(
            df[scheduled_column],
            errors="coerce"
        )

        # Positive gap = delayed
        # Zero gap = on-time
        # Negative gap = early

        df["delay_gap"] = actual_days - scheduled_days

        df["delivery_outcome"] = "On-time"

        df.loc[
            df["delay_gap"] > 0,
            "delivery_outcome"
        ] = "Delayed"

        df.loc[
            df["delay_gap"] < 0,
            "delivery_outcome"
        ] = "Early"

    return df


def clean_dataframe_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


# ---------------------------------------------------------
# FILTERING FUNCTIONS
# ---------------------------------------------------------

def apply_filters(
    df,
    shipping_mode="",
    region="",
    market="",
    segment="",
    country="",
    outcome="",
    search=""
):

    selected_filters = [
        (shipping_mode, "shipping_mode"),
        (region, "region"),
        (market, "market"),
        (segment, "customer_segment"),
        (country, "country")
    ]

    for selected_value, field_name in selected_filters:

        if not selected_value:
            continue

        column = find_column(df, field_name)

        if column:

            df = df[
                df[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.casefold()
                == selected_value.strip().casefold()
            ]

    # Filter by calculated delivery outcome

    if outcome and "delivery_outcome" in df.columns:

        df = df[
            df["delivery_outcome"].str.casefold()
            == outcome.casefold()
        ]

    # Search across relevant shipment fields

    if search:

        searchable_columns = [
            "Product Name",
            "product_name",
            "Order City",
            "order_city",
            "Order Country",
            "order_country",
            "Order Region",
            "order_region",
            "Market",
            "market",
            "Shipping Mode",
            "shipping_mode",
            "Customer Segment",
            "customer_segment"
        ]

        available_columns = [
            column
            for column in searchable_columns
            if column in df.columns
        ]

        if available_columns:

            search_mask = pd.Series(
                False,
                index=df.index
            )

            for column in available_columns:

                search_mask |= (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        search,
                        case=False,
                        regex=False
                    )
                )

            df = df[search_mask]

    return df


# ---------------------------------------------------------
# ANALYTICS FUNCTIONS
# ---------------------------------------------------------

def calculate_group_performance(df, field_name):

    column = find_column(df, field_name)

    if not column or "delay_gap" not in df.columns:
        return []

    display_column = DISPLAY_NAMES[field_name]

    working_df = df.copy()

    working_df[column] = (
        working_df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

    # Calculate delivery performance for each group

    grouped = (
        working_df
        .groupby(column)
        .agg(
            shipments=("delay_gap", "count"),

            delayed=(
                "delay_gap",
                lambda values: int((values > 0).sum())
            ),

            on_time=(
                "delay_gap",
                lambda values: int((values == 0).sum())
            ),

            early=(
                "delay_gap",
                lambda values: int((values < 0).sum())
            ),

            average_gap=(
                "delay_gap",
                "mean"
            )
        )
        .reset_index()
    )

    # A shipment is SLA-compliant when it arrives early or on time.
    # The denominator is shipments with a valid actual/scheduled gap.
    grouped["delay_rate"] = (
        grouped["delayed"]
        / grouped["shipments"]
        * 100
    ).round(2)

    grouped["sla_compliance_rate"] = (
        (grouped["early"] + grouped["on_time"])
        / grouped["shipments"]
        * 100
    ).round(2)

    grouped["average_gap"] = grouped["average_gap"].round(2)
    grouped["average_gap"] = grouped["average_gap"].mask(
        grouped["average_gap"].abs() < 0.005, 0
    )

    # Use consistent field names for the React frontend

    grouped = grouped.rename(
        columns={
            column: display_column
        }
    )

    grouped = grouped.sort_values(
        by="shipments",
        ascending=False
    )

    return grouped.to_dict(orient="records")


def calculate_histogram(df):

    if "delay_gap" not in df.columns:
        return []

    delays = df["delay_gap"].dropna()

    if delays.empty:
        return []

    number_of_bins = min(
        20,
        max(5, int(delays.nunique()))
    )

    categories = pd.cut(
        delays,
        bins=number_of_bins,
        include_lowest=True
    )

    distribution = (
        categories
        .value_counts()
        .sort_index()
    )

    return [
        {
            "range": str(interval),
            "count": int(count)
        }

        for interval, count in distribution.items()
    ]


# ---------------------------------------------------------
# HOME AND HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "project": "LogiScope",
        "description": "Delivery Performance and Logistics Analytics",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "dataset_exists": DATASET_PATH.exists(),
        "service": "LogiScope Analytics API"
    }


# ---------------------------------------------------------
# FILTER OPTIONS
# ---------------------------------------------------------

@app.get("/filters")
def get_filter_options():

    try:

        df = load_dataset()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    filter_fields = {
        "shipping_modes": "shipping_mode",
        "regions": "region",
        "markets": "market",
        "segments": "customer_segment",
        "countries": "country"
    }

    result = {}

    for response_name, field_name in filter_fields.items():

        column = find_column(df, field_name)

        if column:

            result[response_name] = sorted(
                df[column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        else:

            result[response_name] = []

    # Check whether an actual date column exists

    date_columns = [
        column
        for column in df.columns
        if "date" in column.casefold()
    ]

    result["date_columns"] = date_columns

    result["date_filter_available"] = bool(
        date_columns
    )

    return result


# ---------------------------------------------------------
# MAIN DASHBOARD ANALYTICS
# ---------------------------------------------------------

@app.get("/dashboard")
def dashboard_analytics(
    shipping_mode: str = "",
    region: str = "",
    market: str = "",
    segment: str = "",
    country: str = "",
    outcome: str = ""
):

    try:

        df = load_dataset()

        df = apply_filters(
            df,
            shipping_mode=shipping_mode,
            region=region,
            market=market,
            segment=segment,
            country=country,
            outcome=outcome
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    if "delay_gap" not in df.columns:

        raise HTTPException(
            status_code=422,
            detail=(
                "Actual and scheduled shipping "
                "duration columns are required."
            )
        )

    delays = df["delay_gap"].dropna()

    total_shipments = len(delays)

    delayed_count = int(
        (delays > 0).sum()
    )

    on_time_count = int(
        (delays == 0).sum()
    )

    early_count = int(
        (delays < 0).sum()
    )

    average_delay = (
        round(float(delays.mean()), 2)
        if total_shipments else 0
    )

    median_delay = (
        round(float(delays.median()), 2)
        if total_shipments else 0
    )

    # Calculate late delivery risk using existing labels

    risk_column = find_column(df, "risk")

    risk_distribution = []
    late_risk_rate = None

    if risk_column:

        risk_values = pd.to_numeric(
            df[risk_column],
            errors="coerce"
        )

        risk_counts = (
            risk_values
            .value_counts(dropna=False)
            .sort_index()
        )

        risk_distribution = [

            {
                "label": (
                    "Unknown"
                    if pd.isna(value)
                    else str(int(value))
                ),

                "count": int(count)
            }

            for value, count in risk_counts.items()
        ]

        valid_risk = risk_values.dropna()

        if not valid_risk.empty:

            late_risk_rate = round(
                float((valid_risk == 1).mean() * 100),
                2
            )

    # Delivery status distribution

    status_distribution = []

    status_column = find_column(
        df,
        "delivery_status"
    )

    if status_column:

        status_counts = (
            df[status_column]
            .fillna("Unknown")
            .value_counts()
        )

        status_distribution = [

            {
                "label": str(status),
                "count": int(count)
            }

            for status, count in status_counts.items()
        ]

    # Prepare the complete dashboard response

    response = {

        "total_shipments": int(total_shipments),

        "on_time_count": on_time_count,

        "delayed_count": delayed_count,

        "early_count": early_count,

        "on_time_rate": round(
            on_time_count / total_shipments * 100,
            2
        ) if total_shipments else 0,

        "delayed_rate": round(
            delayed_count / total_shipments * 100,
            2
        ) if total_shipments else 0,

        "early_rate": round(
            early_count / total_shipments * 100,
            2
        ) if total_shipments else 0,

        "average_delay": average_delay,

        "median_delay": median_delay,

        "late_risk_rate": late_risk_rate,

        "risk_distribution": risk_distribution,

        "status_counts": status_distribution,

        "histogram": calculate_histogram(df),

        "shipping_modes": calculate_group_performance(
            df,
            "shipping_mode"
        ),

        "regions": calculate_group_performance(
            df,
            "region"
        ),

        "countries": calculate_group_performance(
            df,
            "country"
        ),

        "markets": calculate_group_performance(
            df,
            "market"
        ),

        "segments": calculate_group_performance(
            df,
            "customer_segment"
        ),

        "note": (
            "Delay gap = actual shipping days minus "
            "scheduled shipping days. Positive values "
            "indicate delayed shipments, zero indicates "
            "on-time shipments and negative values "
            "indicate early shipments. Late delivery risk "
            "comes from existing dataset labels."
        )
    }

    return response


# ---------------------------------------------------------
# SHIPMENT RECORD EXPLORER
# ---------------------------------------------------------

@app.get("/records")
def get_records(

    page: int = Query(1, ge=1),

    page_size: int = Query(20, ge=1, le=500),

    shipping_mode: str = "",

    region: str = "",

    market: str = "",

    segment: str = "",

    country: str = "",

    outcome: str = "",

    search: str = ""

):

    try:

        df = load_dataset()

        df = apply_filters(
            df,
            shipping_mode=shipping_mode,
            region=region,
            market=market,
            segment=segment,
            country=country,
            outcome=outcome,
            search=search
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    # Do not expose personal customer information

    private_columns = [
        "Customer Fname",
        "Customer Lname",
        "Customer Street",
        "Customer Zipcode",
        "customer_fname",
        "customer_lname",
        "customer_street",
        "customer_zipcode"
    ]

    df = df.drop(
        columns=private_columns,
        errors="ignore"
    )

    total_records = len(df)

    start = (page - 1) * page_size

    end = start + page_size

    selected_records = df.iloc[start:end].copy()

    # Convert missing values into JSON-compatible values

    selected_records = selected_records.astype(object)

    selected_records = selected_records.where(
        pd.notna(selected_records),
        None
    )

    records = selected_records.to_dict(
        orient="records"
    )

    return {

        "total": int(total_records),

        "page": page,

        "page_size": page_size,

        "records": records

    }


# ---------------------------------------------------------
# EXPORT FILTERED RECORDS
# ---------------------------------------------------------

@app.get("/records/export")
def export_records(

    shipping_mode: str = "",

    region: str = "",

    market: str = "",

    segment: str = "",

    country: str = "",

    outcome: str = "",

    search: str = ""

):

    try:

        df = load_dataset()

        df = apply_filters(
            df,
            shipping_mode=shipping_mode,
            region=region,
            market=market,
            segment=segment,
            country=country,
            outcome=outcome,
            search=search
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    private_columns = [
        "Customer Fname",
        "Customer Lname",
        "Customer Street",
        "Customer Zipcode",
        "customer_fname",
        "customer_lname",
        "customer_street",
        "customer_zipcode"
    ]

    df = df.drop(
        columns=private_columns,
        errors="ignore"
    )

    csv_file = io.StringIO()

    df.to_csv(
        csv_file,
        index=False
    )

    csv_file.seek(0)

    return StreamingResponse(

        iter([csv_file.getvalue()]),

        media_type="text/csv",

        headers={
            "Content-Disposition":
            "attachment; filename=logiscope_filtered_records.csv"
        }

    )


# ---------------------------------------------------------
# BACKWARD-COMPATIBLE ENDPOINTS
# Supports the original dashboard API requests.
# ---------------------------------------------------------

@app.get("/summary")
def summary():

    return dashboard_analytics()


@app.get("/shipping-modes")
def shipping_modes():

    result = dashboard_analytics()

    return {
        "results": result["shipping_modes"]
    }


@app.get("/risk-distribution")
def risk_distribution():

    result = dashboard_analytics()

    return {

        "label_source": (
            "Existing dataset labels; "
            "not machine-learning predictions."
        ),

        "counts": {
            item["label"]: item["count"]
            for item in result["risk_distribution"]
        }

    }