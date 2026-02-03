import argparse
import uuid
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measurement", required=True, help="Path to a4s_backend_measurement.csv")
    ap.add_argument("--observation_template", required=True, help="Path to a4s_backend_observation.csv (template row)")
    ap.add_argument("--out_dir", required=True, help="Output directory for regenerated CSVs")
    ap.add_argument("--obs_id_start", type=int, default=None, help="Optional explicit starting observation.id")
    ap.add_argument(
        "--keep_existing_obs_id",
        action="store_true",
        help="If set, keeps existing observation rows and starts new IDs after max(template.id).",
    )
    args = ap.parse_args()

    meas_path = Path(args.measurement)
    obs_path = Path(args.observation_template)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    m = pd.read_csv(meas_path)
    o = pd.read_csv(obs_path)

    # Expected columns based on your current CSVs:
    # measurement: ['id','pid','name','description','unit','time','score','error','uncertainty','feature_id','metric_id','observation_id']
    # observation: ['id','pid','name','description','observer','tool','whenObserved','evaluation_id','dataset_2_id']
    required_m_cols = {"id", "time", "observation_id"}
    required_o_cols = {"id", "name", "description", "observer", "tool", "whenObserved", "evaluation_id", "dataset_2_id"}

    missing_m = required_m_cols - set(m.columns)
    missing_o = required_o_cols - set(o.columns)
    if missing_m:
        raise ValueError(f"Measurement CSV missing required columns: {sorted(missing_m)}")
    if missing_o:
        raise ValueError(f"Observation CSV missing required columns: {sorted(missing_o)}")

    if len(o) < 1:
        raise ValueError("Observation template CSV is empty; needs at least 1 row.")

    # Use first row as template
    template = o.iloc[0].copy()

    # Normalize time → string keys (keep exact string to avoid TZ parsing surprises)
    # If you prefer normalized datetime, parse & re-format instead.
    times = pd.Series(m["time"].astype(str).unique()).sort_values(kind="stable").tolist()

    # Decide starting observation IDs
    template_max_id = int(o["id"].max())
    if args.obs_id_start is not None:
        next_obs_id = int(args.obs_id_start)
    else:
        # Default: start after the max ID in the template file
        next_obs_id = template_max_id + 1

    # Build mapping: time_str -> new observation.id
    time_to_obs_id = {}
    new_obs_rows = []

    for t in times:
        obs_id = next_obs_id
        next_obs_id += 1
        time_to_obs_id[t] = obs_id

        row = template.copy()
        row["id"] = obs_id
        row["pid"] = str(uuid.uuid4()) if "pid" in o.columns else None
        row["whenObserved"] = t  # <-- critical: date lives here
        new_obs_rows.append(row)

    new_obs = pd.DataFrame(new_obs_rows)

    # Optionally keep existing observation rows from template file
    if args.keep_existing_obs_id:
        obs_out = pd.concat([o, new_obs], ignore_index=True)
    else:
        # Output only regenerated observations (recommended for a clean reload)
        obs_out = new_obs

    # Remap measurement.observation_id based on measurement.time
    m2 = m.copy()
    m2["time"] = m2["time"].astype(str)
    m2["observation_id"] = m2["time"].map(time_to_obs_id)

    if m2["observation_id"].isna().any():
        bad = m2[m2["observation_id"].isna()][["id", "time"]].head(20)
        raise ValueError(f"Some measurement rows could not be mapped to an observation_id:\n{bad}")

    # Write outputs
    obs_out_path = out_dir / "a4s_backend_observation_by_measure_time.csv"
    meas_out_path = out_dir / "a4s_backend_measurement_remapped_obs.csv"

    obs_out.to_csv(obs_out_path, index=False)
    m2.to_csv(meas_out_path, index=False)

    print("Wrote:")
    print(f"  {obs_out_path}")
    print(f"  {meas_out_path}")
    print("")
    print("Summary:")
    print(f"  unique measurement times: {len(times)}")
    print(f"  observations written:     {len(obs_out)}")
    print(f"  measures remapped:        {len(m2)}")


if __name__ == "__main__":
    main()
