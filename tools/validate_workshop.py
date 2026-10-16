"""Small, dependency-light reproducibility and data-integrity checks.

Run after generating notebooks and project/open_data.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from medsim import FEATURES, train_val_split

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "project" / "open_data"

dev = pd.read_csv(DATA / "development.csv")
target = pd.read_csv(DATA / "new_hospital_unlabeled.csv")
audit = pd.read_csv(DATA / "audit_labels.csv")
reveal = pd.read_csv(DATA / "instructor_outcomes_for_debrief.csv")
assert len(dev) == 4000, len(dev)
assert len(target) == 1600, len(target)
assert len(audit) == 75, len(audit)
assert len(reveal) == len(target)
assert "outcome" in dev and "outcome" not in target
assert dev["record_id"].is_unique and target["record_id"].is_unique
assert audit["record_id"].is_unique
assert set(audit["record_id"]).issubset(set(target["record_id"]))
assert set(reveal["record_id"]) == set(target["record_id"])
assert not audit["outcome"].isna().any()

source_train, source_val = train_val_split(dev, val_fraction=0.25, seed=5)
model = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(),
    LogisticRegression(max_iter=3000)
).fit(source_train[FEATURES], source_train["outcome"])
p_val = model.predict_proba(source_val[FEATURES])[:, 1]
p_target = model.predict_proba(target[FEATURES])[:, 1]
assert np.isfinite(p_val).all() and np.isfinite(p_target).all()
assert p_val.min() >= 0 and p_target.max() <= 1
score = roc_auc_score(source_val["outcome"], p_val)
assert 0.6 < score < 0.95, score

nbpaths = [
    "01_lecture1_uncertainty_foundations_student.ipynb",
    "01_lecture1_uncertainty_foundations_instructor.ipynb",
    "02_lecture2_trustworthy_deployment_student.ipynb",
    "02_lecture2_trustworthy_deployment_instructor.ipynb",
    "90_team_project_starter.ipynb",
    "91_open_research_challenge_starter.ipynb",
]
for name in nbpaths:
    nbpath = ROOT / "notebooks" / name
    assert nbpath.exists(), str(nbpath)
    raw = json.loads(nbpath.read_text(encoding="utf-8"))
    assert raw["nbformat"] == 4 and len(raw["cells"]) > 10

notebook = (ROOT / "notebooks" / "91_open_research_challenge_starter.ipynb").read_text()
assert "audit_labels.csv" in notebook and "new_hospital_unlabeled.csv" in notebook

print(f"Validation OK. Source AUROC {score:.3f}; "
      f"target n={len(target)} with audit n={len(audit)}; "
      f"core notebooks structurally valid.")
