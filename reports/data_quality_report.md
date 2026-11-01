# APL Logistics Dataset Quality Audit

## 1. Dataset Overview

- **Source file:** `APL_Logistics.csv`
- **Rows:** 180,519
- **Columns:** 40
- **Duplicate rows:** 0
- **Missing cells:** 11
- **Memory usage:** 90.24 MB

## 2. Column Types

```text
Type                                 str
Days for shipping (real)           int64
Days for shipment (scheduled)      int64
Benefit per order                float64
Sales per customer               float64
Delivery Status                      str
Late_delivery_risk                 int64
Category Id                        int64
Category Name                        str
Customer City                        str
Customer Country                     str
Customer Fname                       str
Customer Id                        int64
Customer Lname                       str
Customer Segment                     str
Customer State                       str
Customer Street                      str
Customer Zipcode                 float64
Department Id                      int64
Department Name                      str
Latitude                         float64
Longitude                        float64
Market                               str
Order City                           str
Order Country                        str
Order Customer Id                  int64
Order Item Discount              float64
Order Item Discount Rate         float64
Order Item Product Price         float64
Order Item Profit Ratio          float64
Order Item Quantity                int64
Sales                            float64
Order Item Total                 float64
Order Profit Per Order           float64
Order Region                         str
Order State                          str
Order Status                         str
Product Name                         str
Product Price                    float64
Shipping Mode                        str
```

## 3. Missing Values

| column           |   missing_count |   missing_percentage |
|:-----------------|----------------:|---------------------:|
| Customer Lname   |               8 |                0.004 |
| Customer Zipcode |               3 |                0.002 |

## 4. Potential Date/Time Columns

No columns with obvious date/time names were detected.

## 5. Potential Target Columns

['Delivery Status', 'Late_delivery_risk']

## 6. Potential Identifier or Sensitive Columns

['Category Id', 'Category Name', 'Customer Fname', 'Customer Id', 'Customer Lname', 'Customer Street', 'Customer Zipcode', 'Department Id', 'Department Name', 'Order Customer Id', 'Product Name']

## 7. Numeric Summary

The full numeric summary is saved in `tables/numeric_summary.csv`.

## 8. Audit Notes

- The original CSV has not been modified.
- Missing values and duplicates have been reported, not removed.
- Column names are checked for potential date, target, and identifier fields.
- Identifier and personal-information columns should not be used as predictive features without a clear, justified purpose.
- Potential target columns must be validated before machine-learning training.

## 9. Generated Files

- `tables/column_profile.csv`
- `tables/missing_values.csv`
- `tables/numeric_summary.csv`
- `tables/categorical_profiles.csv`