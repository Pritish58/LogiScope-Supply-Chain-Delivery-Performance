# LogiScope — Delivery Performance & Logistics Analytics

A data analytics and machine learning project designed to analyze delivery performance, shipping efficiency, and late-delivery risk using a logistics dataset.

## 1. Project Overview

LogiScope is a supply chain analytics dashboard that helps users understand delivery outcomes, compare shipping methods, and examine existing late-delivery risk labels.

The project combines data preprocessing, exploratory data analysis (EDA), machine learning experimentation, a FastAPI backend, and a React frontend to present logistics information through an interactive dashboard.

## 2. Objectives

* Analyze delivery outcomes across the dataset.
* Compare actual shipping duration with scheduled shipping duration.
* Identify patterns associated with late deliveries.
* Compare shipping performance across shipping modes.
* Examine the distribution of existing late-delivery risk labels.
* Present key performance indicators through a dashboard.
* Provide a foundation for further logistics analytics and predictive modeling.

## 3. Technology Stack

### Data Analysis and Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* Matplotlib
* Seaborn

### Backend

* FastAPI
* Uvicorn

### Frontend

* React
* JavaScript
* Vite
* CSS

### Testing

* Pytest
* FastAPI TestClient

## 4. Project Structure

```text
Delivery/
├── backend/
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── raw/
│   │   └── APL_Logistics.csv
│   ├── interim/
│   └── processed/
│       ├── logistics_cleaned.csv
│       └── logistics_features.csv
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── app.jsx
│   │   ├── main.jsx
│   │   └── style.css
│   ├── index.html
│   └── package.json
├── models/
├── notebooks/
├── reports/
├── src/
│   ├── analysis/
│   ├── data/
│   ├── features/
│   └── ml/
├── tests/
│   └── test_api.py
├── requirements.txt
└── README.md
```

*Note: This structure describes the main project components. Some files may differ depending on your current implementation.*

## 5. Dataset

The project uses the APL Logistics CSV dataset.

The original dataset contains **180,519 records and 40 columns**.

The processed feature dataset contains additional engineered columns for delivery analysis.

Important fields include:

* Delivery status
* Late-delivery risk
* Scheduled shipping duration
* Actual shipping duration
* Shipping mode
* Market and regional information
* Customer and product-related attributes

### Data Quality Findings

The initial dataset audit identified:

* Total records: 180,519
* Exact duplicate rows: 0
* Missing values: 11

The missing values and data quality issues should be handled according to the preprocessing rules documented in the project.

## 6. Dashboard Features

### Overview

Displays the overall dataset size and distribution of delivery outcomes.

### Delivery Analysis

Provides insights into delivery status and shipping-duration performance.

### Shipping Efficiency

Compares shipping-duration patterns across shipping modes.

### Risk Analysis

Summarizes the dataset's existing late-delivery risk labels.

## 7. Data Processing Workflow

The project follows this workflow:

1. Dataset audit
2. Data cleaning
3. Feature engineering
4. Exploratory data analysis
5. Baseline machine learning experiment
6. Backend API development
7. Dashboard integration
8. API testing
9. Project documentation

## 8. Installation and Setup

### Prerequisites

Install the following software:

* Python
* Node.js and npm
* Visual Studio Code

### Step 1: Install Python Dependencies

Open a terminal in the project root directory.

```bash
py -m pip install -r requirements.txt
```

### Step 2: Start the Backend

From the project root, run:

```bash
py -m uvicorn backend.main:app --reload
```

The backend should be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### Step 3: Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, usually:

`http://localhost:5173`

Keep both backend and frontend terminals running while using the dashboard.

## 9. API Endpoints

The current backend includes the following endpoints:

| Method | Endpoint             | Purpose                          |
| ------ | -------------------- | -------------------------------- |
| GET    | `/`                  | API home                         |
| GET    | `/health`            | Health check                     |
| GET    | `/summary`           | High-level dataset summary       |
| GET    | `/shipping-modes`    | Shipping-mode comparison         |
| GET    | `/risk-distribution` | Existing risk-label distribution |

Use `/docs` to inspect and test the available endpoints.

## 10. Machine Learning

The project includes a baseline Random Forest classification experiment for late-delivery risk.

The initial experiment reported:

* Accuracy: approximately 78.13%
* Precision: approximately 90.43%
* Recall: approximately 67.23%
* F1-score: approximately 77.12%

These metrics describe the baseline experiment, not a validated operational early-warning system.

Before using the model for early prediction, verify that:

* All predictor features are available when the prediction is made.
* Outcome-related features do not leak information about the target.
* Repeated orders are handled appropriately during validation.
* Performance is evaluated on a suitable holdout strategy.

In particular, actual shipping duration and final delivery status should not be used as predictors when the intended prediction occurs before the delivery outcome is known.

## 11. Testing

API tests are available in the `tests` directory.

Run them from the project root:

```bash
py -m pytest tests/test_api.py -v
```

The current API test run completed successfully with **5 passing tests**.

## 12. Limitations

* The dataset may contain multiple records associated with the same order.
* The recorded risk label reflects the supplied dataset and requires further validation before operational use.
* The absence of suitable timestamps limits time-based trend analysis.
* Baseline machine learning performance does not guarantee reliable future predictions.
* The analysis is limited to the fields available in the supplied dataset.

## 13. Future Improvements

* Introduce group-aware or time-aware model validation where supported by the data.
* Improve data quality monitoring.
* Add automated preprocessing tests.
* Develop more detailed shipping-mode and regional comparisons.
* Add model explainability and feature-importance analysis.
* Improve dashboard filtering and export capabilities.
* Prepare deployment and monitoring documentation.

## 14. Conclusion

LogiScope combines logistics data analysis, baseline machine learning, API development, and interactive visualization in a single project.

It provides a foundation for understanding delivery performance and shipping efficiency while identifying the validation requirements that must be addressed before deploying a predictive risk model.

---

**Project:** LogiScope — Delivery Performance & Logistics Analytics
**Dataset:** APL Logistics CSV dataset
**Backend:** FastAPI
**Frontend:** React and Vite
**Language:** Python and JavaScript
