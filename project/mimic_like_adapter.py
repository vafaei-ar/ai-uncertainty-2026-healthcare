"""MIMIC-inspired *teaching* table adapter for synthetic admissions.

This is NOT a MIMIC-IV schema emulator and is NOT a real clinical ETL.
It demonstrates patients/admissions/events/labs/diagnosis joins with synthetic
IDs, pseudo-times and item codes, then checks a lossless flat-feature roundtrip.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from medsim import FEATURES, SimConfig, simulate_ehr

VITAL_CODES = {
    "heart_rate": "SYN_HEART_RATE",
    "systolic_bp": "SYN_SYSTOLIC_BP",
    "respiratory_rate": "SYN_RESP_RATE",
}
LAB_CODES = {
    "creatinine": "SYN_CREATININE",
    "lactate": "SYN_LACTATE",
    "wbc": "SYN_WBC",
}
DIAG_CODES = {
    "prior_stroke": "SYN_PRIOR_STROKE",
    "diabetes": "SYN_DIABETES",
}


def split_tables(cohort: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split a flat synthetic cohort without creating any new clinical facts."""
    if "record_id" not in cohort or not cohort["record_id"].is_unique:
        raise ValueError("Require a unique record_id for each synthetic admission.")
    required = set(FEATURES) | {"site"}
    if not required.issubset(cohort.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(cohort.columns))}")

    keys = cohort[["record_id"]].copy()
    keys["subject_id"] = "SYN_PERSON_" + cohort["record_id"].astype(str)
    keys["hadm_id"] = "SYN_ADM_" + cohort["record_id"].astype(str)
    # The timestamps make temporal joins demonstrable, but are not real care times.
    keys["admittime"] = pd.Timestamp("2020-01-01") + pd.to_timedelta(
        np.arange(len(keys)), unit="h"
    )
    patients = keys[["subject_id"]].copy()
    patients["anchor_age"] = cohort["age"].to_numpy()
    patients["synthetic_group"] = cohort["group"].to_numpy()
    admissions = keys[["hadm_id", "subject_id", "admittime"]].copy()
    admissions["record_id"] = cohort["record_id"].to_numpy()
    admissions["site"] = cohort["site"].to_numpy()

    def make_events(code_map, offset_minutes):
        parts = []
        for field, code in code_map.items():
            frame = keys[["hadm_id", "admittime"]].copy()
            frame["itemid"] = code
            frame["charttime"] = frame["admittime"] + pd.Timedelta(minutes=offset_minutes)
            frame["valuenum"] = cohort[field].to_numpy()
            frame = frame.loc[frame["valuenum"].notna(), ["hadm_id", "itemid", "charttime", "valuenum"]]
            parts.append(frame)
        return pd.concat(parts, ignore_index=True)

    diagnoses = []
    for name, code in DIAG_CODES.items():
        mask = cohort[name].fillna(0).astype(int).to_numpy() == 1
        frame = keys.loc[mask, ["hadm_id"]].copy()
        frame["icd_code"] = code
        diagnoses.append(frame)

    tables = {
        "patients": patients,
        "admissions": admissions,
        "chartevents": make_events(VITAL_CODES, 5),
        "labevents": make_events(LAB_CODES, 15),
        "diagnoses_icd": pd.concat(diagnoses, ignore_index=True),
    }
    if "outcome" in cohort:
        outcomes = keys[["hadm_id"]].copy()
        outcomes["outcome"] = cohort["outcome"].to_numpy()
        tables["outcomes"] = outcomes
    return tables


def reconstruct_features(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Recover the supplied analysis features; no temporal selection is implied."""
    admission = tables["admissions"].merge(
        tables["patients"], on="subject_id", how="left", validate="many_to_one"
    )
    flat = admission[["record_id", "hadm_id", "site"]].copy()
    flat["age"] = admission["anchor_age"].to_numpy()
    flat["group"] = admission["synthetic_group"].to_numpy()

    for name, codes in (("chartevents", VITAL_CODES), ("labevents", LAB_CODES)):
        events = tables[name]
        if events.duplicated(["hadm_id", "itemid"]).any():
            raise ValueError(f"Multiple {name} measurements: define an aggregation window first.")
        pivot = events.pivot(index="hadm_id", columns="itemid", values="valuenum")
        for feature, code in codes.items():
            flat[feature] = flat["hadm_id"].map(pivot[code]) if code in pivot else np.nan

    diagnoses = tables["diagnoses_icd"]
    for feature, code in DIAG_CODES.items():
        values = set(diagnoses.loc[diagnoses["icd_code"] == code, "hadm_id"])
        flat[feature] = flat["hadm_id"].isin(values).astype(int)

    if "outcomes" in tables:
        flat = flat.merge(tables["outcomes"], on="hadm_id", how="left", validate="one_to_one")
    cols = ["record_id", *FEATURES, "site"]
    if "outcome" in flat:
        cols.append("outcome")
    return flat[cols].sort_values("record_id").reset_index(drop=True)


def assert_roundtrip(original: pd.DataFrame, tables: dict[str, pd.DataFrame]):
    rebuilt = reconstruct_features(tables)
    source = original.sort_values("record_id").reset_index(drop=True)
    for feature in FEATURES:
        np.testing.assert_allclose(
            rebuilt[feature].to_numpy(dtype=float),
            source[feature].to_numpy(dtype=float),
            equal_nan=True, rtol=0, atol=1e-10,
            err_msg=f"Mismatch for feature {feature}",
        )
    assert rebuilt["record_id"].tolist() == source["record_id"].tolist()
    assert rebuilt["site"].tolist() == source["site"].tolist()
    if "outcome" in source:
        np.testing.assert_array_equal(rebuilt["outcome"], source["outcome"])
    return True


def demo(output_dir: Path, n: int = 80):
    if n < 1:
        raise ValueError("n must be positive.")
    original = simulate_ehr(
        SimConfig(n=n, site="A", seed=6767, missingness_strength=1.0)
    )
    original.insert(0, "record_id", [f"DEMO_{i:05d}" for i in range(len(original))])
    tables = split_tables(original)
    assert_roundtrip(original, tables)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
    print(f"Wrote {len(tables)} MIMIC-inspired synthetic tables for {n} admissions to {output_dir}")
    return tables


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--output-dir", type=Path, default=Path("project/mimic_like_demo"))
    args = parser.parse_args()
    if not args.demo:
        parser.error("Use --demo to generate and verify a small teaching example.")
    demo(args.output_dir, args.n)


if __name__ == "__main__":
    main()
