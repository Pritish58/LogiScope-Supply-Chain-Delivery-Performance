"""
Delivery Performance and Delay Risk
Machine Learning Training Pipeline

Project: Delivery Performance, Delay Risk, and Logistics
         Efficiency Analysis in Global Supply Chain Operations

Important:
This is a baseline classification experiment.
Predictive validity depends on verifying that all input features
are available at the intended prediction time.
"""

import json
import warnings
from datetime import datetime

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import ROOT_DIR


# ============================================================
# 1. PROJECT PATHS
# ============================================================

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "logistics_features.csv"
)

MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "reports" / "tables"

MODEL_PATH = MODEL_DIR / "delivery_risk_model.joblib"
METRICS_PATH = REPORT_DIR / "baseline_metrics.json"
CONFUSION_PATH = REPORT_DIR / "confusion_matrix.csv"
FEATURES_PATH = REPORT_DIR / "model_features.json"
REPORT_PATH = REPORT_DIR / "classification_report.txt"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CONFIGURATION
# ============================================================

TARGET = "late_delivery_risk"

TEST_SIZE = 0.20
RANDOM_STATE = 42

N_ESTIMATORS = 150

# Fields that directly describe the outcome or contain
# information that may not be available before delivery.
OUTCOME_COLUMNS = {
    "late_delivery_risk",
    "delivery_status",
    "order_status",
    "days_for_shipping_real",
    "shipping_delay_days",
    "duration_performance",
    "is_cancelled",
}

# Identifiers are excluded to reduce memorization.
IDENTIFIER_COLUMNS = {
    "customer_id",
    "order_customer_id",
    "order_id",
    "order_item_id",
    "order_item_cardprod_id",
    "product_card_id",
}

# These fields are suspicious for an early-warning model because
# they may contain post-outcome or accounting information.
# They are excluded conservatively until their timing is verified.
SUSPICIOUS_COLUMNS = {
    "order_profit_per_order",
    "order_item_profit_ratio",
    "benefit_per_order",
    "sales",
    "order_item_total",
    "product_price",
    "order_item_product_price",
}

# Free-text names are excluded by default.
TEXT_COLUMNS = {
    "customer_fname",
    "customer_lname",
    "product_name",
}


# ============================================================
# 3. LOAD AND VALIDATE DATA
# ============================================================

def load_dataset() -> pd.DataFrame:
    """Load the engineered dataset and validate its target."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_PATH}\n"
            "Run the preprocessing and feature-engineering steps first."
        )

    print("=" * 65)
    print("DELIVERY RISK MODEL — TRAINING PIPELINE")
    print("=" * 65)

    print("\nLoading dataset...")

    df = None
    last_error = None

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            df = pd.read_csv(
                DATA_PATH,
                encoding=encoding,
                low_memory=False,
            )
            break
        except UnicodeDecodeError as exc:
            last_error = exc

    if df is None:
        raise ValueError(
            f"Could not decode dataset: {last_error}"
        )

    # Normalize column names for consistent access.
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    if df.columns.duplicated().any():
        duplicates = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(
            f"Duplicate column names after normalization: {duplicates}"
        )

    if TARGET not in df.columns:
        raise ValueError(
            f"Required target '{TARGET}' was not found.\n"
            f"Available columns: {df.columns.tolist()}"
        )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    return df


# ============================================================
# 4. TARGET VALIDATION
# ============================================================

def prepare_target(df: pd.DataFrame):
    """Validate the binary target and remove unknown target rows."""

    df = df.copy()

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    original_rows = len(df)

    df = df[df[TARGET].isin([0, 1])].copy()
    df[TARGET] = df[TARGET].astype(int)

    print("\nTARGET DISTRIBUTION")
    print("-" * 65)
    print(df[TARGET].value_counts().sort_index().to_string())

    removed = original_rows - len(df)

    if removed:
        print(f"\nRows excluded due to invalid target: {removed:,}")

    if df[TARGET].nunique() != 2:
        raise ValueError(
            "The target must contain both classes 0 and 1."
        )

    print("\nChecking target relationship with delivery status...")

    if "delivery_status" in df.columns:
        print(
            pd.crosstab(
                df["delivery_status"],
                df[TARGET],
                dropna=False,
            ).to_string()
        )

        print(
            "\nWARNING: If the target exactly matches delivery_status, "
            "the target represents an outcome label. It must not be "
            "interpreted as proof of advance prediction."
        )

    return df


# ============================================================
# 5. FEATURE SELECTION
# ============================================================

def select_features(df: pd.DataFrame):
    """
    Select candidate predictors while excluding direct outcomes,
    identifiers, and suspicious fields.
    """

    excluded = (
        OUTCOME_COLUMNS
        | IDENTIFIER_COLUMNS
        | SUSPICIOUS_COLUMNS
        | TEXT_COLUMNS
    )

    excluded_present = sorted(
        column for column in excluded
        if column in df.columns
    )

    X = df.drop(
        columns=[column for column in excluded if column in df.columns],
        errors="ignore",
    ).copy()

    y = df[TARGET].copy()

    # Remove target-related columns by exact name.
    # Do not automatically remove every field containing "order":
    # some order attributes may be valid if available at prediction time.
    constant_columns = [
        column
        for column in X.columns
        if X[column].nunique(dropna=False) <= 1
    ]

    if constant_columns:
        X = X.drop(columns=constant_columns)

    # Remove columns that contain no usable values.
    empty_columns = [
        column
        for column in X.columns
        if X[column].isna().all()
    ]

    if empty_columns:
        X = X.drop(columns=empty_columns)

    if X.empty:
        raise ValueError(
            "No usable predictors remain after feature selection."
        )

    print("\nFEATURE SELECTION")
    print("-" * 65)

    print("\nExcluded columns:")
    print(
        excluded_present
        if excluded_present
        else "No predefined excluded columns were present."
    )

    print("\nConstant columns removed:")
    print(constant_columns if constant_columns else "None")

    print("\nEmpty columns removed:")
    print(empty_columns if empty_columns else "None")

    print("\nFEATURES USED BY THE MODEL:")
    for column in X.columns:
        print(f"- {column}")

    print(f"\nTotal candidate features: {len(X.columns)}")

    print(
        "\nWARNING: Feature-name exclusion is only a first-pass "
        "leakage safeguard. Each remaining feature must be checked "
        "to determine whether it is available at prediction time."
    )

    return X, y, excluded_present


# ============================================================
# 6. PREPROCESSING PIPELINE
# ============================================================

def build_pipeline(X: pd.DataFrame) -> Pipeline:
    """Create preprocessing and Random Forest model pipeline."""

    categorical_columns = X.select_dtypes(
        include=["object", "category", "string", "bool"]
    ).columns.tolist()

    numeric_columns = X.select_dtypes(
        include=["number"]
    ).columns.tolist()

    unsupported_columns = [
        column
        for column in X.columns
        if column not in categorical_columns
        and column not in numeric_columns
    ]

    if unsupported_columns:
        X.drop(columns=unsupported_columns, inplace=True)

    transformers = []

    if numeric_columns:
        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median"),
                ),
            ]
        )

        transformers.append(
            (
                "numeric",
                numeric_pipeline,
                numeric_columns,
            )
        )

    if categorical_columns:
        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="most_frequent"),
                ),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                    ),
                ),
            ]
        )

        transformers.append(
            (
                "categorical",
                categorical_pipeline,
                categorical_columns,
            )
        )

    if not transformers:
        raise ValueError(
            "No supported numeric or categorical predictors remain."
        )

    preprocessing = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    classifier = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", classifier),
        ]
    )


# ============================================================
# 7. MODEL TRAINING AND EVALUATION
# ============================================================

def train_and_evaluate(
    X: pd.DataFrame,
    y: pd.Series,
):
    """Split data, train the baseline model, and evaluate it."""

    print("\nSPLITTING DATA")
    print("-" * 65)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")

    model = build_pipeline(X)

    print("\nTraining Random Forest classifier...")
    model.fit(X_train, y_train)

    print("Training completed.")

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1_score": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(y_test, probabilities)
        ),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_count": int(X.shape[1]),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "model_type": "RandomForestClassifier",
        "experiment_type": "baseline_random_split",
        "trained_at": datetime.now().isoformat(timespec="seconds"),
    }

    print("\nMODEL EVALUATION")
    print("=" * 65)

    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: {value}")

    print("\nCLASSIFICATION REPORT")
    print("-" * 65)

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["low_risk_0", "high_risk_1"],
        zero_division=0,
    )

    print(report)

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    )

    confusion_df = pd.DataFrame(
        matrix,
        index=["actual_0", "actual_1"],
        columns=["predicted_0", "predicted_1"],
    )

    print("\nCONFUSION MATRIX")
    print("-" * 65)
    print(confusion_df.to_string())

    return model, metrics, confusion_df, report


# ============================================================
# 8. SAVE ARTIFACTS
# ============================================================

def save_artifacts(
    model,
    metrics: dict,
    confusion_df: pd.DataFrame,
    report: str,
    X: pd.DataFrame,
    excluded_columns: list,
):
    """Save the trained model, metrics, features, and report."""

    print("\nSAVING MODEL AND REPORTS")
    print("-" * 65)

    joblib.dump(model, MODEL_PATH)

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=4),
        encoding="utf-8",
    )

    confusion_df.to_csv(CONFUSION_PATH)

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    feature_info = {
        "target": TARGET,
        "features": X.columns.tolist(),
        "excluded_columns": excluded_columns,
        "model_type": "RandomForestClassifier",
        "experiment_type": "baseline_random_split",
        "warning": (
            "This is a baseline experiment. Confirm feature availability "
            "at prediction time and investigate repeated orders, "
            "label leakage, and validation strategy before operational use."
        ),
    }

    FEATURES_PATH.write_text(
        json.dumps(feature_info, indent=4),
        encoding="utf-8",
    )

    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(f"Confusion matrix: {CONFUSION_PATH}")
    print(f"Classification report: {REPORT_PATH}")
    print(f"Feature list: {FEATURES_PATH}")


# ============================================================
# 9. MAIN
# ============================================================

def main():
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
    )

    df = load_dataset()

    df = prepare_target(df)

    X, y, excluded_columns = select_features(df)

    model, metrics, confusion_df, report = train_and_evaluate(
        X,
        y,
    )

    save_artifacts(
        model,
        metrics,
        confusion_df,
        report,
        X,
        excluded_columns,
    )

    print("\n" + "=" * 65)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 65)

    print(
        "\nIMPORTANT: This experiment uses a random train/test split. "
        "It is not yet evidence of reliable advance prediction. "
        "Verify feature timing, target semantics, and repeated-order "
        "grouping before operational use."
    )


if __name__ == "__main__":
    main()
