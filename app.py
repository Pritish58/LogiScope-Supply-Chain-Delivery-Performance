import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path
from textwrap import dedent


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LogiScope | Supply Chain Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT / "data" / "processed" /
    "logistics_features.csv"
)


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* GLOBAL */

.stApp {
    background: #080f1f;
    color: #f1f5f9;
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 100%;
}

/* HIDE STREAMLIT BRANDING */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #081426;
    border-right: 1px solid #1d304e;
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

/* BRAND */

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 35px;
}

.brand-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg,#38bdf8,#8b5cf6);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    color: white;
    flex-shrink: 0;
}

.brand-title {
    font-size: 23px;
    font-weight: 800;
    color: white;
}

.brand-subtitle {
    font-size: 9px;
    letter-spacing: 1.5px;
    color: #7892b5;
}

/* NAVIGATION */

.nav-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #647fa4;
    margin: 20px 0 12px 10px;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 7px;
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border-radius: 11px;
    padding: 11px 9px;
    color: #b8c9df;
    font-weight: 600;
    transition: 0.2s;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: #172b49;
    color: white;
}

/* HEADINGS */

h1 {
    font-size: 36px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
}

h2, h3 {
    color: #f1f5f9 !important;
}

/* HEADER */

.breadcrumb {
    color: #8ba8cc;
    font-size: 13px;
    margin-bottom: 10px;
}

.subtitle {
    color: #91a8c7;
    font-size: 14px;
    margin-top: -10px;
}

/* KPI CARDS */

.kpi-card {
    background: linear-gradient(145deg,#14243e,#0d1a2e);
    border: 1px solid #263b5a;
    border-radius: 16px;
    padding: 19px 16px;
    min-height: 145px;
    position: relative;
    overflow: hidden;
}

.kpi-card:before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--accent);
}

.kpi-label {
    font-size: 12px;
    color: #a8bdd8;
    margin-bottom: 15px;
}

.kpi-value {
    font-size: 27px;
    font-weight: 800;
    color: white;
    margin-bottom: 8px;
}

.kpi-caption {
    font-size: 10px;
    color: #829bbd;
}

/* CHART CARDS */

.chart-card {
    background: #101e34;
    border: 1px solid #263b5a;
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 8px;
}

.chart-title {
    font-size: 17px;
    font-weight: 700;
    color: white;
    margin-bottom: 6px;
}

.chart-description {
    font-size: 11px;
    color: #829bbd;
}

/* BUTTONS */

.stButton > button {
    background: #5145cd;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #685cf0;
    color: white;
}

/* SELECTBOX */

[data-baseweb="select"] > div {
    background: #192c49;
    border: 1px solid #304767;
    border-radius: 9px;
}

/* INPUT */

[data-testid="stTextInput"] input {
    background: #192c49;
    border: 1px solid #304767;
    color: white;
    border-radius: 9px;
}

/* DATAFRAME */

[data-testid="stDataFrame"] {
    border: 1px solid #263b5a;
    border-radius: 12px;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #627b9d;
    font-size: 11px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. DATASET COLUMN MAPPING
# ============================================================

COLUMN_NAMES = {
    "shipping": "shipping_mode",
    "region": "order_region",
    "market": "market",
    "segment": "customer_segment",
    "country": "order_country",
    "gap": "delivery_duration_gap",
    "risk": "late_delivery_risk",
    "severity": "delay_severity",
    "product": "product_name"
}


def get_column(df, field):

    column = COLUMN_NAMES.get(field)

    if column in df.columns:
        return column

    return None


# ============================================================
# 4. DATASET LOADING
# ============================================================

@st.cache_data
def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False
    )

    gap_column = get_column(df, "gap")

    if gap_column:

        df["delivery_duration_gap"] = pd.to_numeric(
            df[gap_column],
            errors="coerce"
        )

    else:

        actual = "days_for_shipping_real"
        scheduled = "days_for_shipment_scheduled"

        if actual in df.columns and scheduled in df.columns:

            df["delivery_duration_gap"] = (
                pd.to_numeric(df[actual], errors="coerce")
                -
                pd.to_numeric(df[scheduled], errors="coerce")
            )

        else:

            raise ValueError(
                "Delivery duration gap could not be calculated."
            )

    df["delivery_outcome"] = "On-time"

    df.loc[
        df["delivery_duration_gap"] > 0,
        "delivery_outcome"
    ] = "Delayed"

    df.loc[
        df["delivery_duration_gap"] < 0,
        "delivery_outcome"
    ] = "Early"

    return df


try:

    df = load_data()

except Exception as error:

    st.error(f"Dataset loading failed: {error}")
    st.stop()


# ============================================================
# 5. SESSION STATE
# ============================================================

if "navigation" not in st.session_state:
    st.session_state.navigation = "Overview"

if "reset_filters" not in st.session_state:
    st.session_state.reset_filters = False


def reset_filter_values():

    st.session_state.shipping_filter = "All"
    st.session_state.region_filter = "All"
    st.session_state.market_filter = "All"
    st.session_state.segment_filter = "All"
    st.session_state.country_filter = "All"
    st.session_state.outcome_filter = "All"


# ============================================================
# 6. HELPER FUNCTIONS
# ============================================================

def get_options(field):

    column = get_column(df, field)

    if not column:
        return ["All"]

    values = (
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return ["All"] + sorted(values, key=str.casefold)


def kpi_card(title, value, caption, accent):

    html = f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-caption">{caption}</div>
    </div>
    """

    st.markdown(
        dedent(html).strip(),
        unsafe_allow_html=True
    )


def chart_header(title, description):

    html = f"""
    <div class="chart-card">
        <div class="chart-title">{title}</div>
        <div class="chart-description">{description}</div>
    </div>
    """

    st.markdown(
        dedent(html).strip(),
        unsafe_allow_html=True
    )


def style_chart(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#b8c9df",
            size=12
        ),
        margin=dict(
            l=20,
            r=20,
            t=35,
            b=20
        )
    )

    fig.update_xaxes(
        gridcolor="#233650"
    )

    fig.update_yaxes(
        gridcolor="#233650"
    )

    return fig


def calculate_group_performance(data, field):

    column = get_column(data, field)

    if not column:
        return pd.DataFrame()

    result = (
        data.groupby(column)
        .agg(
            shipments=(
                "delivery_duration_gap",
                "count"
            ),
            delayed=(
                "delivery_duration_gap",
                lambda x: (x > 0).sum()
            ),
            on_time=(
                "delivery_duration_gap",
                lambda x: (x == 0).sum()
            ),
            early=(
                "delivery_duration_gap",
                lambda x: (x < 0).sum()
            ),
            average_gap=(
                "delivery_duration_gap",
                "mean"
            )
        )
        .reset_index()
    )

    result["delay_rate"] = (
        result["delayed"]
        / result["shipments"].replace(0, pd.NA)
        * 100
    ).fillna(0)

    result["delay_rate"] = result["delay_rate"].round(2)

    result["average_gap"] = result["average_gap"].round(2)

    return result.sort_values(
        "shipments",
        ascending=False
    )


# ============================================================
# 7. SIDEBAR
# ============================================================

with st.sidebar:

    brand_html = """
    <div class="brand">
        <div class="brand-icon">◇</div>
        <div>
            <div class="brand-title">LogiScope</div>
            <div class="brand-subtitle">
                SUPPLY CHAIN INTELLIGENCE
            </div>
        </div>
    </div>
    """

    st.markdown(
        dedent(brand_html).strip(),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="nav-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    navigation = {
        "⌂  Overview": "Overview",
        "▥  Delivery Performance": "Delivery Performance",
        "◇  Delay Risk": "Delay Risk",
        "⇄  Shipping Modes": "Shipping Modes",
        "✣  Regional Intelligence": "Regional Intelligence",
        "♙  Customer Segments": "Customer Segments",
        "▤  Record Explorer": "Record Explorer"
    }

    selected = st.radio(
        "Navigation",
        list(navigation.keys()),
        index=list(navigation.values()).index(
            st.session_state.navigation
        ),
        label_visibility="collapsed"
    )

    page = navigation[selected]

    st.session_state.navigation = page

    st.markdown("---")

    status_html = """
    <div style="
        background:#12243e;
        padding:15px;
        border-radius:12px;
        border:1px solid #29415f;
    ">
        <div style="color:#829bbd;font-size:11px;">
            SYSTEM STATUS
        </div>
        <div style="
            color:#34d399;
            font-size:14px;
            font-weight:700;
            margin-top:8px;
        ">
            ● Analytics Engine Active
        </div>
        <div style="
            color:#829bbd;
            font-size:10px;
            margin-top:8px;
        ">
            LogiScope Intelligence Platform
        </div>
    </div>
    """

    st.markdown(
        dedent(status_html).strip(),
        unsafe_allow_html=True
    )


# ============================================================
# 8. HEADER
# ============================================================

st.markdown(
    f'<div class="breadcrumb">⌁ / {page}</div>',
    unsafe_allow_html=True
)

st.title(page)

descriptions = {
    "Overview":
        "A live view of delivery performance across the global supply chain.",

    "Delivery Performance":
        "Analyze delivery outcomes and shipment performance.",

    "Delay Risk":
        "Identify delivery risks and understand delay severity.",

    "Shipping Modes":
        "Compare logistics efficiency across shipping methods.",

    "Regional Intelligence":
        "Explore delivery performance across global regions.",

    "Customer Segments":
        "Understand delivery performance across customer segments.",

    "Record Explorer":
        "Search, inspect and export shipment records."
}

st.markdown(
    f'<div class="subtitle">{descriptions[page]}</div>',
    unsafe_allow_html=True
)


# ============================================================
# 9. FILTER PANEL
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3, f4, f5, f6, f7 = st.columns(
    [1, 1, 1, 1, 1, 1, 0.55]
)

with f1:

    shipping = st.selectbox(
        "Shipping Mode",
        get_options("shipping"),
        key="shipping_filter"
    )

with f2:

    region = st.selectbox(
        "Order Region",
        get_options("region"),
        key="region_filter"
    )

with f3:

    market = st.selectbox(
        "Market",
        get_options("market"),
        key="market_filter"
    )

with f4:

    segment = st.selectbox(
        "Customer Segment",
        get_options("segment"),
        key="segment_filter"
    )

with f5:

    country = st.selectbox(
        "Order Country",
        get_options("country"),
        key="country_filter"
    )

with f6:

    outcome = st.selectbox(
        "Delivery Outcome",
        ["All", "Early", "On-time", "Delayed"],
        key="outcome_filter"
    )

with f7:

    st.markdown("<br>", unsafe_allow_html=True)

    st.button(
        "↻ Reset",
        use_container_width=True,
        on_click=reset_filter_values
    )


# ============================================================
# 10. APPLY FILTERS
# ============================================================

filtered = df.copy()

filter_values = [
    ("shipping", shipping),
    ("region", region),
    ("market", market),
    ("segment", segment),
    ("country", country)
]

for field, value in filter_values:

    column = get_column(filtered, field)

    if value != "All" and column:

        filtered = filtered[
            filtered[column].fillna("Unknown").astype(str)
            == value
        ]

if outcome != "All":

    filtered = filtered[
        filtered["delivery_outcome"] == outcome
    ]


valid = filtered.dropna(
    subset=["delivery_duration_gap"]
)


# ============================================================
# 11. KPI CALCULATIONS
# ============================================================

total = len(valid)

delayed = int(
    (valid["delivery_duration_gap"] > 0).sum()
)

on_time = int(
    (valid["delivery_duration_gap"] == 0).sum()
)

early = int(
    (valid["delivery_duration_gap"] < 0).sum()
)

delay_rate = (
    delayed / total * 100 if total else 0
)

on_time_rate = (
    on_time / total * 100 if total else 0
)

average_gap = (
    valid["delivery_duration_gap"].mean()
    if total else 0
)

risk_column = get_column(filtered, "risk")

if risk_column:

    risk_values = pd.to_numeric(
        filtered[risk_column],
        errors="coerce"
    ).dropna()

    risk_rate = (
        (risk_values == 1).mean() * 100
        if len(risk_values) else 0
    )

else:

    risk_rate = 0


# ============================================================
# 12. OVERVIEW KPI CARDS
# ============================================================

if page == "Overview":

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        kpi_card(
            "Total Shipments",
            f"{total:,}",
            "Current filter selection",
            "#8b5cf6"
        )

    with c2:

        kpi_card(
            "On-time Rate",
            f"{on_time_rate:.1f}%",
            f"{on_time:,} on-time shipments",
            "#10b981"
        )

    with c3:

        kpi_card(
            "Delayed Rate",
            f"{delay_rate:.1f}%",
            f"{delayed:,} delayed shipments",
            "#fb6475"
        )

    with c4:

        kpi_card(
            "Average Delivery Gap",
            f"{average_gap:.2f} days",
            "Actual minus scheduled",
            "#38bdf8"
        )

    with c5:

        kpi_card(
            "Late Delivery Risk",
            f"{risk_rate:.1f}%",
            "Existing dataset label",
            "#fbbf24"
        )

    st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# 13. OVERVIEW DASHBOARD
# ============================================================

if page == "Overview":

    left, right = st.columns(2)

    with left:

        chart_header(
            "Delivery Outcome Mix",
            "Share of early, on-time and delayed shipments."
        )

        outcome_data = pd.DataFrame({
            "Outcome": [
                "Early",
                "On-time",
                "Delayed"
            ],
            "Shipments": [
                early,
                on_time,
                delayed
            ]
        })

        fig = px.pie(
            outcome_data,
            names="Outcome",
            values="Shipments",
            hole=0.62,
            color="Outcome",
            color_discrete_map={
                "Early": "#10c99a",
                "On-time": "#38a7f5",
                "Delayed": "#fb6475"
            }
        )

        fig.update_layout(
            annotations=[
                dict(
                    text=f"<b>{total:,}</b><br>Shipments",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font_size=18
                )
            ]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with right:

        chart_header(
            "Delay Rate by Shipping Mode",
            "Compare shipment delays across shipping methods."
        )

        shipping_analysis = calculate_group_performance(
            valid,
            "shipping"
        )

        if not shipping_analysis.empty:

            fig = px.bar(
                shipping_analysis,
                x="delay_rate",
                y="shipping_mode",
                orientation="h",
                text="delay_rate",
                labels={
                    "delay_rate": "Delay Rate (%)",
                    "shipping_mode": "Shipping Mode"
                }
            )

            fig.update_traces(
                marker_color="#38bdf8",
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        else:

            st.info("Shipping data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:

        chart_header(
            "Market Delay Rate",
            "Compare delivery delays across markets."
        )

        market_analysis = calculate_group_performance(
            valid,
            "market"
        )

        if not market_analysis.empty:

            fig = px.bar(
                market_analysis,
                x="market",
                y="delay_rate",
                color="delay_rate",
                color_continuous_scale="Teal"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    with right:

        chart_header(
            "Regional Performance",
            "Average delivery gap across global regions."
        )

        regional = calculate_group_performance(
            valid,
            "region"
        )

        if not regional.empty:

            fig = px.bar(
                regional,
                x="order_region",
                y="average_gap",
                color="average_gap",
                color_continuous_scale="RdYlGn_r"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )


# ============================================================
# 14. DELIVERY PERFORMANCE
# ============================================================

elif page == "Delivery Performance":

    st.subheader("Delivery Performance Analysis")

    left, right = st.columns(2)

    with left:

        fig = px.histogram(
            valid,
            x="delivery_duration_gap",
            nbins=25,
            title="Delivery Gap Distribution",
            color_discrete_sequence=["#38bdf8"]
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with right:

        fig = px.box(
            valid,
            x="shipping_mode",
            y="delivery_duration_gap",
            color="shipping_mode",
            title="Delivery Gap by Shipping Mode"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.subheader("Delivery Performance Summary")

    performance = (
        valid.groupby("delivery_outcome")
        .size()
        .reset_index(name="Shipments")
    )

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 15. DELAY RISK
# ============================================================

elif page == "Delay Risk":

    st.subheader("Delay Risk Intelligence")

    left, right = st.columns(2)

    severity_column = get_column(filtered, "severity")

    with left:

        if severity_column:

            severity = (
                filtered[severity_column]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            severity.columns = [
                "Severity",
                "Shipments"
            ]

            fig = px.pie(
                severity,
                names="Severity",
                values="Shipments",
                hole=0.5,
                title="Delay Severity Distribution"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        else:

            st.info("Delay severity column unavailable.")

    with right:

        if risk_column:

            risk = (
                pd.to_numeric(
                    filtered[risk_column],
                    errors="coerce"
                )
                .value_counts()
                .sort_index()
                .reset_index()
            )

            risk.columns = [
                "Risk Label",
                "Shipments"
            ]

            fig = px.bar(
                risk,
                x="Risk Label",
                y="Shipments",
                title="Existing Late Delivery Risk Labels"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        else:

            st.info("Risk labels unavailable.")

    st.info(
        "Risk labels shown here come from your existing dataset. "
        "They are not new machine-learning predictions."
    )


# ============================================================
# 16. SHIPPING MODES
# ============================================================

elif page == "Shipping Modes":

    st.subheader("Shipping Mode Intelligence")

    shipping_analysis = calculate_group_performance(
        valid,
        "shipping"
    )

    if not shipping_analysis.empty:

        left, right = st.columns(2)

        with left:

            fig = px.bar(
                shipping_analysis,
                x="shipping_mode",
                y="delay_rate",
                color="delay_rate",
                title="Delay Rate by Shipping Mode"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with right:

            fig = px.bar(
                shipping_analysis,
                x="shipping_mode",
                y="average_gap",
                color="average_gap",
                title="Average Delivery Gap"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        st.dataframe(
            shipping_analysis,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Shipping analytics unavailable.")


# ============================================================
# 17. REGIONAL INTELLIGENCE
# ============================================================

elif page == "Regional Intelligence":

    st.subheader("Regional Intelligence")

    regional = calculate_group_performance(
        valid,
        "region"
    )

    if not regional.empty:

        fig = px.bar(
            regional.sort_values(
                "delay_rate",
                ascending=False
            ),
            x="order_region",
            y="delay_rate",
            color="delay_rate",
            title="Regional Delay Rate"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

        st.dataframe(
            regional,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Regional analytics unavailable.")


# ============================================================
# 18. CUSTOMER SEGMENTS
# ============================================================

elif page == "Customer Segments":

    st.subheader("Customer Segment Analysis")

    segment_analysis = calculate_group_performance(
        valid,
        "segment"
    )

    if not segment_analysis.empty:

        fig = px.bar(
            segment_analysis,
            x="customer_segment",
            y="delay_rate",
            color="customer_segment",
            title="Customer Segment Delay Rate"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

        st.dataframe(
            segment_analysis,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Customer segment analytics unavailable.")


# ============================================================
# 19. RECORD EXPLORER
# ============================================================

elif page == "Record Explorer":

    st.subheader("Shipment Record Explorer")

    search = st.text_input(
        "Search product, region or country"
    )

    records = filtered.copy()

    if search:

        searchable_columns = [
            get_column(records, "product"),
            get_column(records, "region"),
            get_column(records, "country")
        ]

        searchable_columns = [
            c for c in searchable_columns if c
        ]

        if searchable_columns:

            mask = pd.Series(
                False,
                index=records.index
            )

            for column in searchable_columns:

                mask |= (
                    records[column]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        search,
                        case=False,
                        regex=False
                    )
                )

            records = records[mask]

    private_columns = [
        "customer_fname",
        "customer_lname",
        "customer_street",
        "customer_zipcode"
    ]

    records = records.drop(
        columns=private_columns,
        errors="ignore"
    )

    st.write(
        f"Total matching records: {len(records):,}"
    )

    st.dataframe(
        records.head(1000),
        use_container_width=True,
        hide_index=True
    )

    csv = records.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇ Download CSV Report",
        data=csv,
        file_name="logiscope_report.csv",
        mime="text/csv"
    )


# ============================================================
# 20. FOOTER
# ============================================================

st.markdown("---")

footer_html = """
<div class="footer">
    LOGISCOPE · SUPPLY CHAIN INTELLIGENCE
    <br><br>
    Delivery Performance | Analytics | Intelligence
</div>
"""

st.markdown(
    dedent(footer_html).strip(),
    unsafe_allow_html=True
)