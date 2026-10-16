"""Build reproducible, synthetic data for the open hospital-transfer challenge.

No patient data, no MIMIC-IV extracts and no claims of clinical realism.
Run from anywhere: python project/generate_open_challenge.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from medsim import SimConfig, simulate_ehr


def main():
    out = ROOT / "project" / "open_data"
    out.mkdir(parents=True, exist_ok=True)

    development = simulate_ehr(SimConfig(n=4000, site="A", seed=501))
    new_hospital = simulate_ehr(
        SimConfig(
            n=1600,
            site="B",
            seed=502,
            prevalence_shift=0.25,
            measurement_noise=1.25,
            missingness_strength=1.1,
            subgroup_interaction=-0.8,
        )
    )
    development.insert(0, "record_id", [f"A-{i:05d}" for i in range(len(development))])
    new_hospital.insert(0, "record_id", [f"B-{i:05d}" for i in range(len(new_hospital))])

    # A genuinely small, randomly chosen outcome-audit sample.
    # The other outcomes are not part of the student target file.
    rng = np.random.default_rng(503)
    audit_idx = np.sort(rng.choice(len(new_hospital), 75, replace=False))
    audit = new_hospital.iloc[audit_idx][["record_id", "outcome"]].copy()

    development.to_csv(out / "development.csv", index=False, float_format="%.7g")
    new_hospital.drop(columns=["outcome"]).to_csv(
        out / "new_hospital_unlabeled.csv", index=False, float_format="%.7g"
    )
    audit.to_csv(out / "audit_labels.csv", index=False)
    new_hospital[["record_id", "outcome"]].to_csv(
        out / "instructor_outcomes_for_debrief.csv", index=False
    )

    # Never include patient data. A public debrief file is acceptable for this
    # exploratory, ungraded exercise, but students should not use it until debrief.
    assert set(audit["record_id"]).issubset(set(new_hospital["record_id"]))
    assert new_hospital["record_id"].is_unique
    print(f"Created {len(development)} development records, "
          f"{len(new_hospital)} unlabeled target records, "
          f"{len(audit)} target-audit labels.")


if __name__ == "__main__":
    main()
