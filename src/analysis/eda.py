
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import ROOT_DIR


# Input and output paths
INPUT_PATH = ROOT_DIR / "data" / "processed" / "logistics_features.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"
TABLES_DIR = ROOT_DIR / "reports" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading feature dataset...")

    df = pd.read_csv(INPUT_PATH, low_memory=False)

    print("Dataset shape:", df.shape)

    # --------------------------------------------------
    # 1. Delivery status distribution
    # --------------------------------------------------
    if "delivery_status" in df.columns:
        status_counts = df["delivery_status"].value_counts(dropna=False)

        print("\nDelivery Status Distribution:")
        print(status_counts.to_string())

        status_counts.to_csv(
            TABLES_DIR / "delivery_status_distribution.csv",
            header=["count"]
        )

        plt.figure(figsize=(10, 6))
        sns.barplot(
            x=status_counts.index.astype(str),
            y=status_counts.values
        )
        plt.title("Distribution of Delivery Status")
        plt.xlabel("Delivery Status")
        plt.ylabel("Number of Records")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(
            FIGURES_DIR / "delivery_status_distribution.png",
            dpi=150
        )
        plt.close()

    # --------------------------------------------------
    # 2. Shipping delay distribution
    # --------------------------------------------------
    if "shipping_delay_days" in df.columns:
        delay = pd.to_numeric(
            df["shipping_delay_days"],
            errors="coerce"
        ).dropna()

        print("\nShipping Delay Summary:")
        print(delay.describe().to_string())

        delay.describe().to_csv(
            TABLES_DIR / "shipping_delay_summary.csv",
            header=["value"]
        )

        plt.figure(figsize=(9, 5))
        sns.histplot(delay, bins=20)
        plt.title("Distribution of Shipping Delay Days")
        plt.xlabel("Actual Shipping Days - Scheduled Shipping Days")
        plt.ylabel("Number of Records")
        plt.tight_layout()
        plt.savefig(
            FIGURES_DIR / "shipping_delay_distribution.png",
            dpi=150
        )
        plt.close()

    # --------------------------------------------------
    # 3. Shipping mode comparison
    # --------------------------------------------------
    if (
        "shipping_mode" in df.columns
        and "shipping_delay_days" in df.columns
    ):
        mode_summary = (
            df.groupby("shipping_mode", dropna=False)
            .agg(
                record_count=("shipping_delay_days", "size"),
                average_delay_days=("shipping_delay_days", "mean"),
                median_delay_days=("shipping_delay_days", "median")
            )
            .reset_index()
        )

        print("\nShipping Mode Summary:")
        print(mode_summary.to_string(index=False))

        mode_summary.to_csv(
            TABLES_DIR / "shipping_mode_summary.csv",
            index=False
        )

        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=mode_summary,
            x="shipping_mode",
            y="average_delay_days"
        )
        plt.title("Average Shipping Duration Difference by Shipping Mode")
        plt.xlabel("Shipping Mode")
        plt.ylabel("Average Delay Days")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(
            FIGURES_DIR / "shipping_mode_delay.png",
            dpi=150
        )
        plt.close()

    # --------------------------------------------------
    # 4. Late delivery risk distribution
    # --------------------------------------------------
    if "late_delivery_risk" in df.columns:
        risk_counts = df["late_delivery_risk"].value_counts(
            dropna=False
        ).sort_index()

        print("\nLate Delivery Risk Distribution:")
        print(risk_counts.to_string())

        risk_counts.to_csv(
            TABLES_DIR / "late_delivery_risk_distribution.csv",
            header=["count"]
        )

        plt.figure(figsize=(7, 5))
        sns.barplot(
            x=risk_counts.index.astype(str),
            y=risk_counts.values
        )
        plt.title("Late Delivery Risk Distribution")
        plt.xlabel("Late Delivery Risk Label")
        plt.ylabel("Number of Records")
        plt.tight_layout()
        plt.savefig(
            FIGURES_DIR / "late_delivery_risk_distribution.png",
            dpi=150
        )
        plt.close()

    print("\nEDA completed successfully.")
    print("Charts saved to:", FIGURES_DIR)
    print("Tables saved to:", TABLES_DIR)


if __name__ == "__main__":
    main()

