# Loading instrucitons



## first set the python env alias
```bash
Set-Alias python313 "C:\Users\adhav\AppData\Local\Programs\Python\Python313\python.exe"

# to generate the SQL DB run the py script generated from the BESSER web platform
python313 ./sql_alchemy.py
```



## fix when observed dates for measures
The observation date is in measures csv, where as we actually need the date as when observed in the observations table to be able to establish correct relationship.
```bash
python313 .\regen_observations_from_measure_time.py `
  --measurement ".\a4s-LCLD-data\results\a4s_backend_measurement_old.csv" `
  --observation_template ".\a4s-LCLD-data\results\a4s_backend_observation.csv" `
  --out_dir ".\a4s-LCLD-data\results\_fixed_dates" `
  --keep_existing_obs_id
```



## data mappings (use powershell vairables below)
```bash
DB="./snt_credit_jan_2026.db"
CSV_DIR="./a4s-LCLD-data/results"
SPEC_DIR="./spec_templates_all_tables_credit_snt"

$DB=".\snt_credit_jan_2026.db"
$CSV_DIR=".\a4s-LCLD-data\results"
$SPEC_DIR=".\spec_templates_all_tables_credit_snt"

python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_project.csv" --spec "$SPEC_DIR/project.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_datashape_new.csv" --spec "$SPEC_DIR/datashape.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_configuration.csv" --spec "$SPEC_DIR/configuration.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_tool.csv" --spec "$SPEC_DIR/tool.yml"

# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_metriccategory.csv" --spec "$SPEC_DIR/metriccategory.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_metric.csv" --spec "$SPEC_DIR/metric.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_direct.csv" --spec "$SPEC_DIR/direct.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_derived.csv" --spec "$SPEC_DIR/derived.yml"

python313 .\element_table_maker.py
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_element.csv" --spec "$SPEC_DIR/element.yml"

python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_dataset.csv" --spec "$SPEC_DIR/dataset.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_model.csv" --spec "$SPEC_DIR/model.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_feature.csv" --spec "$SPEC_DIR/feature.yml"

python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_evaluation.csv" --spec "$SPEC_DIR/evaluation.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_confparam.csv" --spec "$SPEC_DIR/confparam.yml"

# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_observation.csv" --spec "$SPEC_DIR/observation.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_observation_by_measure_time.csv" --spec "$SPEC_DIR/observation.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_measurement.csv" --spec "$SPEC_DIR/measure.yml"
python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_measurement_remapped_obs.csv" --spec "$SPEC_DIR/measure.yml"

# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_metriccategory_metrics.csv" --spec "$SPEC_DIR/metriccategory_metric.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_derived_metric.csv" --spec "$SPEC_DIR/derived_metric.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_evaluation_element.csv" --spec "$SPEC_DIR/evaluation_element.yml"
# python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_evaluates_eval.csv" --spec "$SPEC_DIR/evaluates_eval.yml"


python313 ./csv_to_sql_loader.py --db "$DB" --csv "$CSV_DIR/a4s_backend_comments.csv" --spec "$SPEC_DIR/comments.yml"
```



```Powershell
$DB=".\snt_credit_jan_2026.db"
$CSV_DIR=".\a4s-LCLD-data\results"
$SPEC_DIR=".\spec_templates_all_tables_credit_snt"

python .\csv_to_sql_loader.py --db $DB --csv "$CSV_DIR\a4s_backend_datashape.csv" --spec "$SPEC_DIR\datashape.yml"
python .\csv_to_sql_loader.py --db $DB --csv "$CSV_DIR\a4s_backend_configuration.csv" --spec "$SPEC_DIR\configuration.yml"
python .\csv_to_sql_loader.py --db $DB --csv "$CSV_DIR\a4s_backend_tool.csv" --spec "$SPEC_DIR\tool.yml"
.
.
.
```








Recommended load order

A. Roots (nothing depends on these)

project

datashape

configuration

tool

metriccategory

metric

direct

derived

element

B. Depends-on-roots
10. dataset (depends on element, datashape)
11. model (depends on element, dataset)
12. feature (depends on element, datashape)
13. evaluation (depends on project, configuration)
14. confparam (depends on configuration)
15. observation (depends on tool, dataset, evaluation)
16. measure / measurement (depends on element, metric, observation)
- Your CSV is named a4s_backend_measurement.csv, but the SQLAlchemy table is measure. Your spec file controls the target table name. 

sql_alchemy

C. Junction tables (many-to-many) — load last
17. metriccategory_metric
18. derived_metric
19. evaluation_element
20. evaluates_eval

D. Optional

comments (standalone)
legalrequirement (depends on project)