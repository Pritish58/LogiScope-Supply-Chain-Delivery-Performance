from pathlib import Path
import pandas as pd

from src.config import (
    RAW_DATA_PATH,
    REPORTS_DIR,
    TABLES_DIR,
)


def load_dataset(path: Path) -> pd.DataFrame:
    """Load the original CSV without modifying its contents."""

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Place APL_Logistics.csv inside data/raw/."
        )

    # The dataset may contain characters that require cp1252 encoding.
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("Could not decode the CSV using supported encodings.")


def run_audit() -> None:
    """Inspect the original dataset and save audit reports."""

    df = load_dataset(RAW_DATA_PATH)

    print("\n" + "=" * 60)
    print("APL LOGISTICS — DATASET AUDIT")
    print("=" * 60)

    # 1. Dataset dimensions
    rows, columns = df.shape

    print(f"\nRows: {rows:,}")
    print(f"Columns: {columns:,}")
    print(f"Duplicate rows: {df.duplicated().sum():,}")
    print(f"Missing cells: {df.isna().sum().sum():,}")

    # 2. Column profile
    profile = pd.DataFrame({
        "column": df.columns,
        "data_type": [str(df[col].dtype) for col in df.columns],
        "missing_count": [int(df[col].isna().sum()) for col in df.columns],
        "missing_percentage": [
            round(df[col].isna().mean() * 100, 3)
            for col in df.columns
        ],
        "unique_values": [int(df[col].nunique(dropna=True)) for col in df.columns],
    })

    profile_path = TABLES_DIR / "column_profile.csv"
    profile.to_csv(profile_path, index=False)

    # 3. Missing-value report
    missing = profile.loc[
        profile["missing_count"] > 0
    ].sort_values("missing_count", ascending=False)

    missing_path = TABLES_DIR / "missing_values.csv"
    missing.to_csv(missing_path, index=False)

    # 4. Numeric column summaries
    numeric = df.select_dtypes(include="number")
    numeric_summary = numeric.describe().T if not numeric.empty else pd.DataFrame()

    numeric_path = TABLES_DIR / "numeric_summary.csv"
    numeric_summary.to_csv(numeric_path)

    # 5. Potential date/time columns
    date_time_columns = [
        col for col in df.columns
        if any(word in col.lower() for word in (
            "date", "time", "timestamp", "month", "year"
        ))
    ]

    # 6. Potential target columns
    target_candidates = [
        col for col in df.columns
        if any(word in col.lower() for word in (
            "late_delivery_risk", "delivery status", "shipping status"
        ))
    ]

    # 7. Likely identifier and sensitive columns
    identifier_candidates = [
        col for col in df.columns
        if any(word in col.lower() for word in (
            "id", "name", "email", "address", "street", "zipcode", "postal"
        ))
    ]

    # 8. Categorical profiles
    categorical = df.select_dtypes(include=["object", "category"])
    category_rows = []

    for col in categorical.columns:
        top_values = (
            df[col]
            .value_counts(dropna=False)
            .head(10)
        )

        for value, count in top_values.items():
            category_rows.append({
                "column": col,
                "value": str(value),
                "count": int(count),
                "percentage": round(count / len(df) * 100, 3),
            })

    categorical_profile = pd.DataFrame(
        category_rows,
        columns=["column", "value", "count", "percentage"]
    )

    categorical_path = TABLES_DIR / "categorical_profiles.csv"
    categorical_profile.to_csv(categorical_path, index=False)

    # 9. Build human-readable Markdown report
    report_lines = [
        "# APL Logistics Dataset Quality Audit",
        "",
        "## 1. Dataset Overview",
        "",
        f"- **Source file:** `{RAW_DATA_PATH.name}`",
        f"- **Rows:** {rows:,}",
        f"- **Columns:** {columns:,}",
        f"- **Duplicate rows:** {int(df.duplicated().sum()):,}",
        f"- **Missing cells:** {int(df.isna().sum().sum()):,}",
        f"- **Memory usage:** "
        f"{df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB",
        "",
        "## 2. Column Types",
        "",
        "```text",
        df.dtypes.to_string(),
        "```",
        "",
        "## 3. Missing Values",
        "",
    ]

    if missing.empty:
        report_lines.append("No missing values were found.")
    else:
        report_lines.append(
            missing[
                ["column", "missing_count", "missing_percentage"]
            ].to_markdown(index=False)
        )

    report_lines += [
        "",
        "## 4. Potential Date/Time Columns",
        "",
        str(date_time_columns) if date_time_columns else
        "No columns with obvious date/time names were detected.",
        "",
        "## 5. Potential Target Columns",
        "",
        str(target_candidates) if target_candidates else
        "No obvious target columns were detected.",
        "",
        "## 6. Potential Identifier or Sensitive Columns",
        "",
        str(identifier_candidates) if identifier_candidates else
        "No obvious identifier or sensitive columns were detected.",
        "",
        "## 7. Numeric Summary",
        "",
        "The full numeric summary is saved in `tables/numeric_summary.csv`.",
        "",
        "## 8. Audit Notes",
        "",
        "- The original CSV has not been modified.",
        "- Missing values and duplicates have been reported, not removed.",
        "- Column names are checked for potential date, target, and identifier fields.",
        "- Identifier and personal-information columns should not be used as predictive "
        "features without a clear, justified purpose.",
        "- Potential target columns must be validated before machine-learning training.",
        "",
        "## 9. Generated Files",
        "",
        "- `tables/column_profile.csv`",
        "- `tables/missing_values.csv`",
        "- `tables/numeric_summary.csv`",
        "- `tables/categorical_profiles.csv`",
    ]

    report_path = REPORTS_DIR / "data_quality_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nAudit completed successfully.")
    print(f"Report: {report_path}")
    print(f"Column profile: {profile_path}")
    print(f"Missing values: {missing_path}")
    print(f"Numeric summary: {numeric_path}")
    print(f"Categorical profiles: {categorical_path}")


if __name__ == "__main__":
    run_audit()