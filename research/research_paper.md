# Delivery Performance, Delay Risk, and Logistics Efficiency Analysis

## Abstract

This project presents LogiScope, a data analytics application developed to examine delivery outcomes, shipping efficiency, and late-delivery risk using an APL Logistics dataset. The solution combines data preprocessing, exploratory data analysis, a baseline machine learning experiment, a FastAPI backend, and a React-based dashboard. The original dataset contains 180,519 records and 40 columns. Exploratory analysis identified late delivery as the largest recorded delivery category. A baseline Random Forest experiment was also conducted. Its preliminary metrics are reported alongside limitations concerning target leakage, feature availability, and validation. The project provides a foundation for logistics performance monitoring and further predictive-model research.

**Keywords:** Supply Chain Analytics, Delivery Performance, Logistics, Machine Learning, Random Forest, FastAPI, React, Data Visualization.

## 1. Introduction

Delivery performance is an important component of supply chain operations. Delays can affect customer satisfaction, planning, and operational efficiency. Data analytics can help organizations understand delivery outcomes, compare shipping methods, and identify areas requiring further investigation.

LogiScope was developed to analyze delivery records and present key findings through an interactive dashboard. The project also investigates whether machine learning can provide a useful starting point for studying late-delivery risk.

## 2. Objectives

The primary objectives are:

1. Examine the quality and structure of the supplied dataset.
2. Analyze delivery outcomes and shipping-duration differences.
3. Compare delivery performance across shipping modes and available operational categories.
4. Summarize the distribution of existing late-delivery risk labels.
5. Develop a baseline classification experiment.
6. Build a web-based dashboard supported by a FastAPI backend.
7. Document findings, limitations, and opportunities for improvement.

## 3. Dataset Description

The original APL Logistics CSV dataset contains 180,519 records and 40 columns.

Relevant fields include delivery status, late-delivery risk, actual shipping duration, scheduled shipping duration, shipping mode, and regional or market information.

The initial audit identified 11 missing values and no exact duplicate rows. The dataset is treated as a collection of records rather than assuming every row represents a unique shipment.

Customer-identifying fields should be excluded from public-facing reports and unnecessary analytical outputs.

## 4. Methodology

The project follows a staged analytics workflow.

### 4.1 Dataset Audit

The original dataset was inspected for dimensions, data types, missing values, duplicate rows, and important categorical distributions.

### 4.2 Data Cleaning

A processed dataset was created for subsequent analysis. Cleaning decisions should be documented to explain how missing values, inconsistent values, and data types were handled.

### 4.3 Feature Engineering

Additional features were created to support delivery-duration analysis. Engineered features must be evaluated according to their intended use and the time at which a prediction would be made.

### 4.4 Exploratory Data Analysis

Delivery-status counts, risk-label distributions, and shipping-duration differences were examined. Cancelled shipments were separated from non-cancelled records when calculating delivery-rate percentages.

### 4.5 Machine Learning Experiment

A baseline Random Forest classification experiment was conducted. Its results were recorded using accuracy, precision, recall, and F1-score.

The model is considered preliminary. Further validation is necessary to confirm that predictors are available before the target outcome and that repeated orders do not create misleading evaluation results.

### 4.6 Application Development

A FastAPI backend exposes endpoints for high-level summary statistics, shipping-mode comparisons, and risk-label distributions.

A React frontend presents the results through four main sections: Overview, Delivery Analysis, Shipping Efficiency, and Risk Analysis.

### 4.7 Testing

Five API tests passed in the recorded test run. These tests provide basic endpoint verification but do not independently validate every analytical calculation or the predictive model.

## 5. Exploratory Analysis Results

### 5.1 Delivery Outcome Distribution

The original dataset contains the following delivery outcomes:

| Delivery status   |     Records |
| ----------------- | ----------: |
| Late delivery     |      98,977 |
| Advance shipping  |      41,592 |
| Shipping on time  |      32,196 |
| Shipping canceled |       7,754 |
| **Total**         | **180,519** |

Late delivery is the largest recorded category.

### 5.2 Delivery Rates

After excluding cancelled records, 172,765 non-cancelled records remain.

The corresponding rates are:

* Late-delivery rate: 57.29%.
* On-time shipment rate: 18.64%.
* Advance-shipment rate: 24.07%.

These are descriptive statistics for the supplied dataset. They should not be interpreted as estimates of overall company performance without evidence that the data is representative.

### 5.3 Risk-Label Distribution

The recorded `late_delivery_risk` field contains:

| Risk label |     Records |
| ---------- | ----------: |
| 1          |      98,977 |
| 0          |      81,542 |
| **Total**  | **180,519** |

The close alignment between risk labels and recorded delivery outcomes raises a potential target-leakage concern. Predictive modeling must distinguish between an existing classification label and a genuinely prospective forecast.

## 6. Baseline Machine Learning Results

The initial Random Forest experiment reported the following metrics:

| Metric    | Baseline result |
| --------- | --------------: |
| Accuracy  |          78.13% |
| Precision |          90.43% |
| Recall    |          67.23% |
| F1-score  |          77.12% |

These results describe the recorded baseline experiment. They should not be treated as validated evidence of advance prediction until the feature set, label definition, split strategy, and leakage risks have been reviewed.

A future evaluation should use appropriate holdout data, consider grouping repeated orders, and select features based on their availability at the intended prediction time.

## 7. System Architecture

The application uses three main components:

1. **Data and ML layer:** Python-based preprocessing, feature engineering, exploratory analysis, and baseline modeling.
2. **Backend layer:** FastAPI endpoints that expose selected analytical results.
3. **Frontend layer:** A React dashboard that displays delivery and shipping-performance summaries.

The frontend communicates with the backend over HTTP. The current workflow uses processed CSV files as its analytical data source.

## 8. Discussion

The descriptive results show that late delivery is the largest category in the supplied dataset. This makes delivery performance an important area for further investigation.

Comparisons across shipping modes, markets, and regions may help identify differences in recorded outcomes. However, these comparisons should be interpreted carefully because differences in customer mix, products, order characteristics, or operational context may influence the results.

The baseline classification metrics are encouraging as an initial experiment but do not establish that the model can reliably forecast future delays. The target's relationship to recorded delivery outcomes makes feature validation particularly important.

## 9. Limitations

The project has several limitations:

* The dataset may contain multiple records for the same order.
* The initial inspection did not identify date/time fields suitable for reliable time-based trend analysis.
* The existing risk label is closely aligned with recorded delivery outcomes.
* The baseline model requires further validation for target leakage and generalization.
* The supplied dataset may not represent all logistics operations.
* The current API test suite checks basic endpoint behavior rather than the correctness of every analytical result.

## 10. Future Work

Future development could include:

1. Group-aware or time-aware model evaluation where supported by the available data.
2. Validation of the intended prediction point and feature availability.
3. Additional analysis of shipping modes, markets, and regions.
4. More comprehensive automated tests for preprocessing and KPI calculations.
5. Model explainability and feature-importance analysis.
6. Data-quality monitoring and clearer metric definitions.
7. Deployment, security, and performance testing.

## 11. Conclusion

LogiScope demonstrates an end-to-end workflow for logistics data analysis, baseline machine learning, API development, and interactive visualization.

The project provides a foundation for examining delivery outcomes and shipping efficiency. Its descriptive findings can guide further analysis, while the machine learning component requires additional validation before it can support operational early-warning decisions.

## References

1. The APL Logistics CSV dataset supplied for this project.
2. Official Pandas documentation.
3. Official Scikit-learn documentation.
4. Official FastAPI documentation.
5. Official React documentation.

*Note: Add complete bibliographic details and access dates for external sources if this report is submitted as a formal academic research paper.*
