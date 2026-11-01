
from pathlib import Path
import pandas as pd

from src.config import RAW_DATA_PATH, ROOT_DIR


# Output location for the cleaned dataset
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_DATA_PATH = PROCESSED_DIR / "logistics_cleaned.csv"


def load_raw_data() -> pd.DataFrame:
    """Load the original dataset without modifying the source file."""

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Original dataset not found: {RAW_DATA_PATH}"
        )

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(RAW_DATA_PATH, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to decode the original CSV.")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply conservative, documented data-cleaning operations."""

    cleaned = df.copy()

    # Standardize column names for easier Python access.
    cleaned.columns = (
        cleaned.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    # Normalize surrounding whitespace in text columns.
    text_columns = cleaned.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    # Report duplicates, but do not remove rows automatically.
    duplicate_count = int(cleaned.duplicated().sum())

    # Report missing values before making any decisions about them.
    missing_before = int(cleaned.isna().sum().sum())

    print("\nDATA CLEANING SUMMARY")
    print("-" * 40)
    print(f"Rows: {len(cleaned):,}")
    print(f"Columns: {len(cleaned.columns):,}")
    print(f"Duplicate rows found: {duplicate_count:,}")
    print(f"Missing cells before cleaning: {missing_before:,}")

    # Missing customer names and ZIP codes are retained as missing.
    # They are not required for delivery-performance analysis.
    missing_columns = cleaned.isna().sum()
    missing_columns = missing_columns[missing_columns > 0]

    print("\nMissing values by column:")
    if missing_columns.empty:
        print("None")
    else:
        print(missing_columns.to_string())

    # Check whether key delivery-related columns exist.
    important_columns = [
        "delivery_status",
        "late_delivery_risk",
        "days_for_shipping_real",
        "days_for_shipment_scheduled",
        "shipping_mode",
    ]

    print("\nKey column availability:")
    for column in important_columns:
        print(f"{column}: {'Present' if column in cleaned.columns else 'Not found'}")

    return cleaned


def main() -> None:
    raw_df = load_raw_data()
    cleaned_df = clean_data(raw_df)

    cleaned_df.to_csv(CLEANED_DATA_PATH, index=False)

    print("\nCleaning completed.")
    print(f"Saved cleaned dataset to:\n{CLEANED_DATA_PATH}")
    print("\nNote: Missing values and duplicate rows were not automatically removed.")


if __name__ == "__main__":
    main()

