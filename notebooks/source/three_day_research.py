"""Three-day synthetic hospital-transfer research notebook: one runnable source."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.nbtools import Notebook, PLOT_STYLE


def build():
    nb = Notebook("Three-day research: trustworthy hospital transfer")
    nb.md("""
# When Can We Trust Clinical AI at a New Hospital?

**Research question:** With 25, 75, or 150 labeled target-hospital
admissions, can a simple calibration correction outperform an unchanged
risk model under different kinds of hospital transfer?

This notebook is a three-day research starter. All patient data are synthetic.
No model or result here is intended for medical decision making.

**Day 1:** inspect the data and reproduce a baseline.
**Day 2:** compare two calibration methods with an independent evaluation set.
**Day 3:** test more random seeds, identify failures, and prepare three slides.

Read the project protocol first: project/RESEARCH_PROTOCOL.md.
""")
    nb.md("""
## Day 1. Understand what is known and what is hidden

Hospital A provides labeled development records. Hospital B provides
unlabeled records and only a small random outcome audit.

An unlabeled feature comparison can detect some recording differences,
but cannot verify risk calibration or the outcome relationship.
""")
    nb.code("""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from medsim import FEATURES, train_val_split, performance_table, shift_report
from project.research_experiments import run_grid, summarize_results, plot_comparison
from project.mimic_like_adapter import split_tables, reconstruct_features, assert_roundtrip

""" + PLOT_STYLE + """
candidate_roots = [
    Path("project/open_data"),
    Path("ai-uncertainty-2026-healthcare/project/open_data"),
]
DATA = next((p for p in candidate_roots if p.exists()), None)
if DATA is None:
    raise FileNotFoundError("Run: python project/generate_open_challenge.py")

development = pd.read_csv(DATA / "development.csv")
target = pd.read_csv(DATA / "new_hospital_unlabeled.csv")
audit_labels = pd.read_csv(DATA / "audit_labels.csv")
audit = target.merge(audit_labels, on="record_id", validate="one_to_one")

print("Hospital A labeled records:", len(development))
print("Hospital B unlabeled records:", len(target))
print("Hospital B available audit outcomes:", len(audit_labels))
assert "outcome" not in target.columns
""")
    nb.md("""
## Day 1. What changed in recorded inputs?

Look at age, vital signs, and laboratory values. A table of standardised
mean differences and missingness can suggest a shift, but cannot prove
whether a risk model is still calibrated.
""")
    nb.code("""
features = ["age", "heart_rate", "systolic_bp", "respiratory_rate",
            "creatinine", "lactate", "wbc"]
display(shift_report(development, target, features).round(3))
display(pd.DataFrame({
    "source_missing": development[FEATURES].isna().mean(),
    "target_missing": target[FEATURES].isna().mean(),
}).round(3))
""")
    nb.md("""
## Day 1. Fit the unchanged source model

Use a held-out portion of Hospital A for validation. The 75 target labels
are too few to establish subgroup reliability precisely. Do not tune a
correction on those same 75 records and report its evaluation as unbiased.
""")
    nb.code("""
train, validation = train_val_split(development, val_fraction=0.25, seed=5)
source_model = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(max_iter=3000, random_state=0),
).fit(train[FEATURES], train["outcome"])

p_val = source_model.predict_proba(validation[FEATURES])[:, 1]
p_audit = source_model.predict_proba(audit[FEATURES])[:, 1]
display(performance_table([
    ("Hospital A held-out", validation["outcome"], p_val),
    ("Hospital B audit, n=75 (uncertain)", audit["outcome"], p_audit),
]).round(4))
""")
    nb.md("""
## Day 1 discussion

What could make Hospital B probabilities too low even when source
validation AUROC is acceptable? Which questions require outcome labels?
Write down one hypothesis your team wants to test.
""")
    nb.code("""
hypothesis = "Our team predicts that..."
print(hypothesis)
""")
    nb.md("""
## An optional bridge: how MIMIC-inspired tables fit together

The simulator normally gives one flat row per admission. The adapter
demonstrates patients, admissions, bedside observations, labs, and coded
conditions using synthetic IDs and codes. It is not a MIMIC-IV extract
or a validated MIMIC schema emulator.
""")
    nb.code("""
toy = development.head(12).copy()
toy_tables = split_tables(toy)
assert_roundtrip(toy, toy_tables)
for name, table in toy_tables.items():
    print(name, len(table), "rows")
display(toy_tables["labevents"].head(5))
""")
    nb.md("""
## Day 2. The methodological comparison

We now simulate a fresh labeled Hospital A cohort, a target calibration
pool, and a completely independent target evaluation cohort.

For each target condition, we compare:
1. The unchanged Hospital A probabilities.
2. One-parameter intercept recalibration.
3. Two-parameter logistic (Platt) recalibration.

Audit labels may be used for recalibration. They must never be reused as
the reported evaluation set. The independent evaluation outcomes are
needed for this simulation study, not for a real deployment decision.
""")
    nb.code("""
# Short live run. Use more replicates for a serious analysis.
results = run_grid(
    repeats=3, label_budgets=(25, 75, 150),
    source_size=2000, target_pool_size=1600, test_size=1200, seed=2026,
)
summary = summarize_results(results)
print("Method-level results:", results.shape)
display(summary.round(4))
""")
    nb.md("""
## Day 2. Read the paired result correctly

The main quantity is Brier score after adaptation MINUS Brier score
without adaptation on exactly the same independent target test patients.
Negative means the adaptation improved this metric.

The percentile columns describe variation across simulated runs.
They are not confidence intervals. With only three runs, conclusions
should be very cautious.
""")
    nb.code("""
import matplotlib.pyplot as plt
plot_comparison(summary, Path("/tmp/workshop_brier_comparison.png"))
from IPython.display import Image, display
display(Image(filename="/tmp/workshop_brier_comparison.png"))
""")
    nb.md("""
## Day 2. Investigate a failure rather than hiding it

Find one scenario and label budget where recalibration performs worse
than the unchanged model, or where results vary across repetitions.
Report the audit event count and the number of replicates.
""")
    nb.code("""
worst = summary.sort_values("mean_delta_brier", ascending=False).head(5)
display(worst.round(4))
display(results.groupby(["scenario", "labels"])["audit_events"].agg(["min", "median", "max"]))
""")
    nb.md("""
## Day 3. Improve the precision and report limitations

Run the larger protocol outside the quick notebook, or change the
number of repeats here. Before adding methods, report paired variation
and whether methods failed to fit because an audit had one outcome class.

For the full simulation from the repository root:

    python -m project.research_experiments --repeats 8

A publication-quality study would require a literature review, broader
conditions, more repetitions, and ideally independent real-world validation.
""")
    nb.code("""
display(
    results.groupby(["scenario", "labels", "method"], as_index=False)
           .agg(mean_brier=("brier", "mean"),
                mean_auroc=("auroc", "mean"),
                max_gap=("worst_group_abs_mean_gap", "mean"),
                fit_rate=("method_estimable", "mean"))
           .round(4)
)
""")
    nb.md("""
## Day 3. Your five-minute, three-slide report

**Slide 1: Question and experiment.** What target changes and label budgets
did you compare? State the independent test design.

**Slide 2: One main figure.** Show paired Brier score differences and one
secondary reliability finding. Distinguish simulated variation from a
statistical confidence interval.

**Slide 3: Interpretation.** Which method worked, which failed, what
assumptions limit the result, and what should we test next?

A well-supported negative result is as informative as a positive one.
Do not claim the model is ready for patient care.
""")
    nb.note("""
Ask teams to compare at least one negative control and one true shift.
Check that no student has used the public debrief outcomes for fitting,
and that target evaluation data never enter any adjustment. Emphasise
that a single simulator study is preliminary, not a publication.
""")
    return nb


if __name__ == "__main__":
    for path in build().write(ROOT / "notebooks", "92_three_day_research_starter", variants=None):
        print("wrote", path.relative_to(ROOT))
