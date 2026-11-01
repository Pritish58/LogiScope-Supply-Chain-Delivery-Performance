import pandas as pd

from src.config import ROOT_DIR

INPUT_PATH = ROOT_DIR / "data" / "processed" / "logistics_cleaned.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "processed" / "logistics_features.csv"


def build_features():
    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_PATH, low_memory=False)

    print("Original dataset shape:", df.shape)

    # 1. Calculate the difference between actual and scheduled
    # shipping durations.
    actual_col = "days_for_shipping_real"
    scheduled_col = "days_for_shipment_scheduled"

    if actual_col in df.columns and scheduled_col in df.columns:
        df["shipping_delay_days"] = (
            pd.to_numeric(df[actual_col], errors="coerce")
            - pd.to_numeric(df[scheduled_col], errors="coerce")
        )

        print("\nShipping delay calculated.")
    else:
        print("\nShipping duration columns not found.")
        print("Available columns:", df.columns.tolist())

    # 2. Classify duration-based performance.
    # Positive = later than scheduled; zero = equal; negative = earlier.
    if "shipping_delay_days" in df.columns:
        df["duration_performance"] = "unknown"

        valid = df["shipping_delay_days"].notna()

        df.loc[
            valid & (df["shipping_delay_days"] > 0),
            "duration_performance"
        ] = "later_than_scheduled"

        df.loc[
            valid & (df["shipping_delay_days"] == 0),
            "duration_performance"
        ] = "equal_to_scheduled"

        df.loc[
            valid & (df["shipping_delay_days"] < 0),
            "duration_performance"
        ] = "earlier_than_scheduled"

    # 3. Normalize the existing delivery status for analysis.
    if "delivery_status" in df.columns:
        df["delivery_status"] = (
            df["delivery_status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # 4. Identify cancelled records without removing them.
    if "delivery_status" in df.columns:
        df["is_cancelled"] = (
            df["delivery_status"]
            .str.contains("cancel", na=False)
        )

    # 5. Save the feature dataset.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFeature engineering completed.")
    print("New dataset shape:", df.shape)
    print("Saved to:", OUTPUT_PATH)

    if "duration_performance" in df.columns:
        print("\nDuration performance counts:")
        print(df["duration_performance"].value_counts(dropna=False))

    if "delivery_status" in df.columns:
        print("\nDelivery status counts:")
        print(df["delivery_status"].value_counts(dropna=False))

    print("\nOriginal data remains unchanged.")


if __name__ == "__main__":
    build_features()

