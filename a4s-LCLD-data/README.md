# Structure:
- ./input_data: Folder containing input datasets before running evaluations in csv format
- ./results: Folder containing results of evaluations exported from the db
- ./visualizations: Folder containing visualizations of evaluations


# Important features in the dataset:
- issue_d: date of the issue of the loan
- charged_off: target variable (1 if the loan was charged off, 0 otherwise)


# Some explanation of the metrics computed:
Drift related metrics (overtime):
- wasserstein_distance: Distance of numerical features
- jensenshannon: Distance of categorical features

Performance related metrics 
- over time: 
    - accuracy
    - precision
    - recall
    - f1
    - ROCAUC
    - MCC: Matthews correlation coefficient
- Overall:
    - Confusion Matrix (This is a bit hard coded and handcrafted for the moment)

Data anomaly detection metrics (with frontend computing severity levels: Pass, Low, Severe):
- Distribution Inside -> number of test data points inside the reference distribution (Pass)
- Distribution Outside -> number of test data points outside the reference distribution (Low if any, Pass otherwise)
- Number of Evaluated Constraint Violations (Lower) -> number of test data that violate min values defined in datashape (Severe if any, Pass otherwise)
- Number of Evaluated Constraint Violations (Upper) -> number of test data that violate max values defined in datashape (Severe if any, Pass otherwise)
- Number of Missing Categories in Test Data Feature -> Per feature, number of categories missing compared to reference data (Low if any, Pass otherwise)
- Number of Missing Category Instances in Test Data -> Total number of missing categories (Low if any, Pass otherwise) 
- Number of New Categories in Test Data Feature     -> Per feature, number of new categories compared to reference data (Severe if any, Pass otherwise)
- Number of New Category Instances in Test Data     -> Total number of new categories (Severe if any, Pass otherwise)
- Number of Reference Constraint Violations (Lower) -> number of referent data that violate min values defined in datashape (Severe if any, Pass otherwise)
- Number of Reference Constraint Violations (Upper) -> number of referent data that violate max values defined in datashape (Severe if any, Pass otherwise)