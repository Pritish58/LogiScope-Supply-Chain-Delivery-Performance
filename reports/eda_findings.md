# Exploratory Data Analysis (EDA) Findings

## 1. Project Overview

This report summarizes the exploratory analysis of the APL Logistics dataset used in the LogiScope Delivery Performance and Logistics Analytics project.

The analysis examines delivery outcomes, shipping-duration differences, data quality, and the distribution of existing late-delivery risk labels.

## 2. Dataset Overview

The original dataset contains:

* **Total records:** 180,519
* **Total columns:** 40
* **Exact duplicate rows:** 0
* **Missing values:** 11

The initial audit identified missing values in customer last-name and customer ZIP-code fields. These fields should be handled according to the preprocessing rules and excluded from public-facing outputs when they are not needed for analysis.

## 3. Delivery Status Distribution

The dataset contains four delivery outcome categories:

| Delivery status   |     Records |
| ----------------- | ----------: |
| Late delivery     |      98,977 |
| Advance shipping  |      41,592 |
| Shipping on time  |      32,196 |
| Shipping canceled |       7,754 |
| **Total**         | **180,519** |

Late deliveries represent the largest category in the dataset.

Cancelled shipments should be separated from completed shipments when calculating delivery performance rates.

## 4. Delivery Performance

There are 172,765 non-cancelled records.

Based on the supplied delivery-status labels:

* **Late-delivery rate:** 57.29%
* **On-time shipment rate:** 18.64%
* **Advance-shipment rate:** 24.07%

These percentages describe the records in this dataset. They should not automatically be interpreted as representative of all APL Logistics operations.

## 5. Late-Delivery Risk Labels

The dataset's `late_delivery_risk` field contains:

| Risk label |     Records |
| ---------- | ----------: |
| 1          |      98,977 |
| 0          |      81,542 |
| **Total**  | **180,519** |

The risk labels match the supplied delivery outcomes in the initial audit. This relationship must be considered carefully during machine learning because outcome-related fields can cause target leakage.

The existing labels describe recorded risk classifications; they do not independently establish that a model can predict late deliveries before they happen.

## 6. Data Quality Observations

The initial dataset audit found:

* No exact duplicate rows.
* Eleven missing values.
* No date/time fields identified in the initial inspection.

Further checks should verify column types, category consistency, valid shipping durations, and the treatment of cancelled records.

Customer names, street addresses, and ZIP codes should not be exposed in dashboard outputs or public reports.

## 7. Machine Learning Considerations

The project includes a baseline Random Forest classification experiment.

The initial experiment reported:

* Accuracy: approximately 78.13%
* Precision: approximately 90.43%
* Recall: approximately 67.23%
* F1-score: approximately 77.12%

These values are preliminary results from the baseline experiment.

Before interpreting them as evidence of predictive capability, the model requires further validation of feature availability, target leakage, repeated-order grouping, and the suitability of the train/test split.

Actual shipping duration and final delivery status must not be used as predictors for a model intended to forecast delays before delivery outcomes are known.

## 8. Key Findings

1. Late delivery is the largest recorded delivery category.
2. Cancelled shipments account for 7,754 records and should be reported separately from completed shipments.
3. The initial dataset audit found 11 missing values and no exact duplicate rows.
4. The risk label is closely aligned with the recorded delivery outcome, requiring careful treatment during modeling.
5. The dataset supports descriptive analysis of delivery outcomes and shipping efficiency.
6. Reliable advance prediction requires further validation beyond a baseline classification score.

## 9. Recommendations

* Monitor delivery outcomes by shipping mode and region.
* Separate cancelled shipments from completed deliveries in performance reporting.
* Avoid using personally identifying customer fields in public-facing analytics.
* Validate feature timing and target leakage before deploying predictive models.
* Use appropriate validation methods for repeated orders.
* Document assumptions and limitations alongside every reported KPI.

## 10. Conclusion

The exploratory analysis establishes a baseline understanding of the dataset's delivery outcomes, data quality, and risk-label distribution.

These findings provide a foundation for the LogiScope dashboard and further logistics analytics. Additional model validation is required before the classification experiment can be considered a reliable early-warning system.
