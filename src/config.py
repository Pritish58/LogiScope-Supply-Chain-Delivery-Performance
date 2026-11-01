from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Dataset paths
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "APL_Logistics.csv"

# Report directories
REPORTS_DIR = ROOT_DIR / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"

# Create output directories if they do not exist
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)