"""Colab starter for the ungraded, open hospital-transfer challenge."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.nbtools import Notebook, PLOT_STYLE


def build():
    nb = Notebook("Open hospital transfer challenge")
    nb.md("""
# Open challenge: when should a clinical risk model be trusted at a new hospital?

You are helping Hospital B decide what to do with a 48-hour deterioration-risk
model developed at Hospital A. It is running in shadow mode; nobody uses its
predictions for patient care. There is **no fixed correct solution**.

You have 4,000 labeled development records, 1,600 target-hospital records
without outcomes, and outcome labels for a **random audit of 75 target patients**.
The audit is small on purpose. You can choose a model, a validation method,
a deferral policy, and the extra information you would collect.

Your task is to give an evidence-based recommendation:
keep shadow mode, consider a limited supervised pilot, adapt the model,
or do not deploy. Explain what you *cannot* establish from the available labels.

All records are synthetic EHR-like examples, not real MIMIC-IV patients,
and the example is **not for clinical use**.

Read project/OPEN_RESEARCH_CHALLENGE.md for the scenario and discussion prompts.
""")
    nb.code("""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from medsim import FEATURES, train_val_split, performance_table, shift_report

""" + PLOT_STYLE + """
candidate_roots = [
    Path("project/open_data"),
    Path("ai-uncertainty-2026-healthcare/project/open_data"),
]
DATA = next((p for p in candidate_roots if p.exists()), None)
if DATA is None:
    raise FileNotFoundError(
        "Open challenge data not found. Run: python project/generate_open_challenge.py"
    )

development = pd.read_csv(DATA / "development.csv")
target = pd.read_csv(DATA / "new_hospital_unlabeled.csv")
audit_labels = pd.read_csv(DATA / "audit_labels.csv")
assert "outcome" not in target.columns
assert len(audit_labels) == 75
assert audit_labels["record_id"].is_unique
audit = target.merge(audit_labels, on="record_id", validate="one_to_one")

print("Development:", development.shape)
print("Target (unlabeled):", target.shape)
print("Target audit (labeled):", audit.shape)
print("Target outcomes available for only", len(audit), "of", len(target), "records.")
""")
    nb.md("""
## 1. Inspect before fitting

What can you detect using the unlabelled new-hospital features? What **cannot**
be established without outcomes? A difference in recorded laboratory values
could come from patients, measurement practice, or both.
""")
    nb.code("""
continuous = [
    "age", "heart_rate", "systolic_bp", "respiratory_rate",
    "creatinine", "lactate", "wbc"
]
display(shift_report(development, target, continuous).round(3))
display(pd.DataFrame({
    "development_missing": development[FEATURES].isna().mean(),
    "target_missing": target[FEATURES].isna().mean()
}).round(3))
""")
    nb.md("""
## 2. Establish a baseline and quantify what the audit tells you

The 75 outcomes are an audit, not a representative precision-calibration
guarantee. The table below is a **noisy estimate**. If you tune a recalibration
method using these labels, do not also claim an unbiased evaluation on
the same audit set.
""")
    nb.code("""
train, validation = train_val_split(development, val_fraction=0.25, seed=5)
model = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(max_iter=3000)
).fit(train[FEATURES], train["outcome"])

def predict(df):
    return model.predict_proba(df[FEATURES])[:, 1]

p_validation = predict(validation)
p_target = predict(target)
p_audit = predict(audit)

display(performance_table([
    ("Hospital A validation", validation["outcome"], p_validation),
    ("Hospital B random audit (n=75)", audit["outcome"], p_audit),
]).round(4))
print("Mean predicted target risk:", round(float(p_target.mean()), 3))
print("Observed event rate in target audit:", round(float(audit["outcome"].mean()), 3))
""")
    nb.md("""
## 3. Develop an approach

Possible ideas: simple recalibration, a hierarchical/site effect,
bootstrap disagreement, subgroup analysis, a referral/abstention policy,
or asking which outcomes should be collected next. It is also acceptable
to say the evidence is insufficient to permit deployment.

Write down your assumptions. Consider how you would discover a
change in the conditional risk, even when the input-drift report looks normal.
""")
    nb.code("""
# Your team's approach starts here.
# You may use the baseline, adapt it, or propose a different monitoring plan.
""")
    nb.md("""
## 4. Your three-slide team report (5 minutes)

1. **Evidence.** What looks reassuring and what worries you? Show one meaningful
   table or plot, and say how uncertain the estimate is.
2. **Action.** Would you remain in shadow mode, adapt, defer some predictions
   for review, or proceed only under explicit conditions? What is the review load?
3. **What next?** What assumptions remain untested? Which extra target-hospital
   outcomes or measurements would change your decision?

**Do not use** instructor_outcomes_for_debrief.csv before the group discussion.
It exists for a transparent, ungraded debrief, not for tuning your solution.
""")
    return nb


if __name__ == "__main__":
    for path in build().write(ROOT / "notebooks", "91_open_research_challenge_starter", variants=None):
        print("wrote", path.relative_to(ROOT))
