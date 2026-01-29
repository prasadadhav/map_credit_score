import os
import glob
import pandas as pd

CSV_DIR = r".\a4s-LCLD-data\results"

DATASET_CSV = os.path.join(CSV_DIR, "a4s_backend_dataset.csv")
MODEL_CSV   = os.path.join(CSV_DIR, "a4s_backend_model.csv")
FEATURE_CSV = os.path.join(CSV_DIR, "a4s_backend_feature.csv")
DSHAPE_CSV  = os.path.join(CSV_DIR, "a4s_backend_datashape.csv")

OUT_ELEMENT = os.path.join(CSV_DIR, "a4s_backend_element.csv")

# ---------- load base tables
dataset = pd.read_csv(DATASET_CSV)
model   = pd.read_csv(MODEL_CSV)
feature = pd.read_csv(FEATURE_CSV)
dshape  = pd.read_csv(DSHAPE_CSV)

# ---------- build lookup helpers
dataset_ids = set(dataset["id"].astype(int).tolist())
model_ids   = set(model["id"].astype(int).tolist())
feature_ids = set(feature["id"].astype(int).tolist())

# We want a single global id space across dataset/model/feature/...
# Keep dataset ids as-is, and reassign model + feature ids above max(dataset.id)
max_id = int(max(dataset["id"].max(), model["id"].max(), feature["id"].max()))

def make_new_ids(old_ids, start_after):
    """
    Create a 1-1 mapping old_id -> new_unique_id, sequentially allocated.
    """
    mapping = {}
    next_id = start_after + 1
    for oid in sorted(set(int(x) for x in old_ids)):
        mapping[oid] = next_id
        next_id += 1
    return mapping, next_id - 1

# If model ids collide with dataset ids, remap models.
model_collision = bool(dataset_ids.intersection(model_ids))
feature_collision = bool(dataset_ids.intersection(feature_ids) or model_ids.intersection(feature_ids))

model_id_map = {}
feature_id_map = {}

cursor = int(dataset["id"].max())

if model_collision:
    model_id_map, cursor = make_new_ids(model["id"], cursor)
    print(f"Remapping MODEL ids into range > {dataset['id'].max()}. New max id now {cursor}.")
else:
    print("No dataset-model id collision detected. Keeping model ids unchanged.")
    cursor = max(cursor, int(model["id"].max()))

# For features, avoid collisions with datasets and (possibly remapped) models
# Determine occupied ids after model remap
occupied = set(dataset["id"].astype(int))
if model_id_map:
    occupied |= set(model_id_map.values())
else:
    occupied |= set(model["id"].astype(int))

if feature_collision or (set(feature["id"].astype(int)) & occupied):
    feature_id_map, cursor = make_new_ids(feature["id"], cursor)
    print(f"Remapping FEATURE ids into range > current max. New max id now {cursor}.")
else:
    print("No feature id collision detected. Keeping feature ids unchanged.")
    cursor = max(cursor, int(feature["id"].max()))

# ---------- apply remaps to model/feature tables (primary keys)
model_fixed = model.copy()
if model_id_map:
    model_fixed["id"] = model_fixed["id"].astype(int).map(model_id_map)

feature_fixed = feature.copy()
if feature_id_map:
    feature_fixed["id"] = feature_fixed["id"].astype(int).map(feature_id_map)

# ---------- update other CSVs in folder that reference model_id / feature_id
all_csvs = glob.glob(os.path.join(CSV_DIR, "*.csv"))

def remap_fk_columns(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()

    # Common FK column names that might exist across your result CSVs
    fk_candidates = list(df2.columns)

    if model_id_map and "model_id" in fk_candidates:
        df2["model_id"] = df2["model_id"].astype("Int64").map(lambda x: model_id_map.get(int(x), x) if pd.notna(x) else x)

    if feature_id_map and "feature_id" in fk_candidates:
        df2["feature_id"] = df2["feature_id"].astype("Int64").map(lambda x: feature_id_map.get(int(x), x) if pd.notna(x) else x)

    # Some tables may refer to "element_id" when linking to element
    # If so, and the element is really a model/feature element, remap it too.
    if "element_id" in fk_candidates:
        # remap element_id if it matches any remapped IDs
        def remap_element(x):
            if pd.isna(x):
                return x
            xi = int(x)
            if model_id_map and xi in model_id_map:
                return model_id_map[xi]
            if feature_id_map and xi in feature_id_map:
                return feature_id_map[xi]
            return xi
        df2["element_id"] = df2["element_id"].astype("Int64").map(remap_element)

    return df2

for path in all_csvs:
    base = os.path.basename(path)

    # We'll overwrite model/feature separately (using the fixed dfs),
    # but we still want to update FK references in other CSVs.
    if base in {"a4s_backend_model.csv", "a4s_backend_feature.csv"}:
        continue

    df = pd.read_csv(path)
    df_fixed = remap_fk_columns(df)

    # Only write if something changed
    if not df_fixed.equals(df):
        df_fixed.to_csv(path, index=False)
        print("Updated FK references in:", base)

# ---------- write back fixed model/feature
model_fixed.to_csv(MODEL_CSV, index=False)
feature_fixed.to_csv(FEATURE_CSV, index=False)
print("Wrote fixed:", os.path.basename(MODEL_CSV))
print("Wrote fixed:", os.path.basename(FEATURE_CSV))

# ---------- now build element table (FK-safe project_id derivation)
# dataset -> element
elem_dataset = dataset[["id", "name", "description", "project_id"]].copy()
elem_dataset["type_spec"] = "dataset"

# model -> element (project via model.dataset_id -> dataset.project_id)
ds_project = dataset.set_index("id")["project_id"].to_dict()
elem_model = model_fixed[["id", "name", "description", "dataset_id"]].copy()
elem_model["project_id"] = elem_model["dataset_id"].map(ds_project)
elem_model["type_spec"] = "model"
elem_model = elem_model.drop(columns=["dataset_id"])

# feature -> element (project via feature.datashape_id -> datashape.dataset_id -> dataset.project_id)
shape_to_dataset = dshape.set_index("id")["dataset_id"].to_dict()
elem_feature = feature_fixed[["id", "name", "description", "datashape_id"]].copy()
elem_feature["dataset_id"] = elem_feature["datashape_id"].map(shape_to_dataset)
elem_feature["project_id"] = elem_feature["dataset_id"].map(ds_project)
elem_feature["type_spec"] = "feature"
elem_feature = elem_feature.drop(columns=["datashape_id", "dataset_id"])

element = pd.concat([elem_dataset, elem_model, elem_feature], ignore_index=True)

# ---------- final safety checks
dupes = element[element["id"].duplicated(keep=False)].sort_values("id")
if not dupes.empty:
    raise ValueError(f"Still have duplicate element.id values:\n{dupes.head(50)}")

missing = element[element["project_id"].isna() & (element["type_spec"] != "dataset")]
if not missing.empty:
    raise ValueError(f"Some model/feature rows could not resolve project_id:\n{missing.head(50)}")

element.to_csv(OUT_ELEMENT, index=False)
print("Wrote:", os.path.basename(OUT_ELEMENT), "rows:", len(element))
