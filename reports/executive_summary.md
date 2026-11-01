# Executive Summary

## LogiScope: Delivery Performance & Logistics Analytics

### 1. Project Overview

LogiScope is a supply chain analytics project designed to examine delivery performance, shipping efficiency, and late-delivery risk using the supplied APL Logistics dataset.

The solution combines data preprocessing, exploratory data analysis, a baseline machine learning experiment, a FastAPI backend, and a React-based interactive dashboard.

### 2. Business Problem

Delivery delays can affect customer satisfaction, operational planning, and supply chain efficiency. Logistics teams need clear performance indicators to understand delivery outcomes, identify patterns, and investigate potential areas for improvement.

LogiScope provides a centralized view of recorded delivery outcomes and shipping-duration patterns to support data-informed investigation.

### 3. Dataset Summary

The original dataset contains 180,519 records and 40 columns.

The initial data-quality audit identified:

* 11 missing values.
* 0 exact duplicate rows.
* Four recorded delivery outcome categories.

### 4. Key Findings

The dataset contains the following delivery outcomes:

| Delivery outcome  |     Records |
| ----------------- | ----------: |
| Late delivery     |      98,977 |
| Advance shipping  |      41,592 |
| Shipping on time  |      32,196 |
| Shipping canceled |       7,754 |
| **Total**         | **180,519** |

After excluding cancelled records, 172,765 records remain for the non-cancelled delivery-rate calculation.

The recorded delivery rates among non-cancelled records are:

* **Late deliveries:** 57.29%
* **On-time shipments:** 18.64%
* **Advance shipments:** 24.07%

These figures describe the supplied dataset and should not be assumed to represent every logistics operation.

### 5. Technical Solution

The project includes:

* **Data processing:** Python and Pandas.
* **Exploratory analysis:** Statistical summaries and visual analysis.
* **Machine learning:** A baseline Random Forest classification experiment.
* **Backend:** FastAPI endpoints for summary statistics, shipping-mode comparisons, and risk-label distribution.
* **Frontend:** A React dashboard with Overview, Delivery Analysis, Shipping Efficiency, and Risk Analysis sections.
* **Testing:** Five API tests passed in the current test run.

### 6. Baseline Machine Learning Results

The initial Random Forest experiment reported:

| Metric    | Result |
| --------- | -----: |
| Accuracy  | 78.13% |
| Precision | 90.43% |
| Recall    | 67.23% |
| F1-score  | 77.12% |

These are preliminary baseline results, not evidence of a validated operational forecasting system.

The risk label is closely aligned with the recorded delivery outcome. Further work must verify predictor availability at prediction time, prevent target leakage, and account for repeated orders during model validation.

### 7. Recommendations

1. Monitor delivery outcomes by shipping mode and region.
2. Report cancelled shipments separately from completed deliveries.
3. Investigate factors associated with late deliveries using appropriate analytical methods.
4. Protect customer information in dashboards and reports.
5. Validate machine learning features and evaluation methods before using predictions operationally.
6. Improve data quality monitoring and document KPI definitions consistently.

### 8. Limitations

The analysis depends on the fields available in the supplied dataset. The initial inspection did not identify date/time fields suitable for time-based trend analysis.

The recorded risk labels and baseline model results do not establish that late deliveries can be reliably predicted in advance. Further validation is required.

### 9. Conclusion

LogiScope provides an integrated foundation for analyzing recorded delivery outcomes and shipping efficiency through a web-based dashboard.

The project demonstrates an end-to-end data analytics workflow, from dataset inspection to API development and visualization. Its findings can support further investigation of logistics performance, while additional validation is needed before deploying a predictive early-warning model.

**Project:** LogiScope — Delivery Performance & Logistics Analytics
**Dataset:** APL Logistics CSV dataset
**Backend:** FastAPI
**Frontend:** React
**Machine Learning:** Random Forest baseline classification
