"""Build the team project datasets.

Every team is handed the same task and the same column headers. Each dataset
hides a different reason the model should not be trusted. Run this from the
repository root:

    python project/make_team_data.py

Regenerating with unchanged seeds reproduces byte-identical CSVs, so the
answer key stays valid.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from medsim.simulator import FEATURES, SimConfig, simulate_ehr  # noqa: E402

RELEASE_COLUMNS = FEATURES + ["site", "outcome"]

# Each entry is (train cohort, deployment cohort). The deployment set is framed
# to participants as six months of silent prospective validation - the model ran
# in shadow mode at the adopting hospital, scoring every admission without
# anyone acting on the scores.
TEAMS = {
    1: {
        "slug": "team_1",
        "public_title": "Sepsis deterioration risk, Hospital Alpha",
        "hidden_mode": "Informative missingness (MNAR)",
        "train": SimConfig(n=6000, site="A", missingness_strength=1.4, seed=1101),
        "deployment": SimConfig(n=4000, site="A", missingness_strength=1.4, seed=1102),
    },
    2: {
        "slug": "team_2",
        "public_title": "Sepsis deterioration risk, Hospital Beta",
        "hidden_mode": "Site and prevalence shift",
        "train": SimConfig(n=6000, site="A", seed=1201),
        "deployment": SimConfig(n=4000, site="B", prevalence_shift=0.5, seed=1202),
    },
    3: {
        "slug": "team_3",
        "public_title": "Sepsis deterioration risk, Hospital Gamma",
        "hidden_mode": "Measurement noise / instrument drift",
        "train": SimConfig(n=6000, site="A", seed=1301),
        "deployment": SimConfig(n=4000, site="A", measurement_noise=2.8, seed=1302),
    },
    4: {
        "slug": "team_4",
        "public_title": "Sepsis deterioration risk, Hospital Delta",
        "hidden_mode": "Label noise in the training records",
        "train": SimConfig(n=6000, site="A", label_noise=0.22, seed=1401),
        "deployment": SimConfig(n=4000, site="A", label_noise=0.0, seed=1402),
    },
    5: {
        "slug": "team_5",
        "public_title": "Sepsis deterioration risk, Hospital Epsilon",
        "hidden_mode": "Subgroup shift with a different risk relationship",
        "train": SimConfig(
            n=6000, site="A", subgroup_prevalence=0.08, subgroup_shift=1.0,
            subgroup_interaction=-1.8, seed=1501,
        ),
        "deployment": SimConfig(
            n=4000, site="A", subgroup_prevalence=0.42, subgroup_shift=1.0,
            subgroup_interaction=-1.8, seed=1502,
        ),
    },
    6: {
        "slug": "team_6",
        "public_title": "Sepsis deterioration risk, Hospital Zeta",
        "hidden_mode": "Out-of-distribution patients at deployment",
        "train": SimConfig(n=6000, site="A", seed=1601),
        "deployment": SimConfig(n=4000, site="A", ood_fraction=0.30, seed=1602),
    },
}


def build(output_dir: Path | None = None, with_truth: bool = False) -> None:
    output_dir = output_dir or (ROOT / "project" / "data")
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for team_id, spec in TEAMS.items():
        for split in ("train", "deployment"):
            df = simulate_ehr(spec[split], keep_truth=with_truth)
            columns = RELEASE_COLUMNS + ([c for c in df.columns if c not in RELEASE_COLUMNS] if with_truth else [])
            out = df[columns]
            path = output_dir / f"{spec['slug']}_{split}.csv"
            out.to_csv(path, index=False, float_format="%.4f")
            manifest.append(
                {
                    "team": team_id,
                    "split": split,
                    "file": path.name,
                    "n": len(out),
                    "event_rate": round(float(out["outcome"].mean()), 4),
                    "missing_cells": int(out[FEATURES].isna().sum().sum()),
                }
            )
        print(f"team {team_id}: {spec['public_title']}")

    pd.DataFrame(manifest).to_csv(output_dir / "manifest.csv", index=False)
    print(f"\nwrote {len(manifest)} files to {output_dir}")


if __name__ == "__main__":
    build(with_truth="--with-truth" in sys.argv)
