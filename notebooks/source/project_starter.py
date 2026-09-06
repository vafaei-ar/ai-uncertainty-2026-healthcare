"""Team project starter notebook."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.nbtools import PLOT_STYLE, Notebook  # noqa: E402


def build() -> Notebook:
    nb = Notebook("Team project starter")

    nb.md(
        """
# Team project - starter notebook

*AI & Uncertainty School and Workshop 2026, healthcare module*

**Set `TEAM` in the next cell to your team number.**

Your hospital has a risk model for 48-hour deterioration. You have the
development records it was built on, and six months of records from the ward
where it is about to be switched on.

Something is wrong with it. The columns are the same for every team; the reason
each model should not be trusted is not.

Your job is to find it, say who it affects, decide when the model should refuse
to answer, and recommend for or against deployment. Full instructions are in
`project/PROJECT_BRIEF.md`; you will be marked against `project/RUBRIC.md`.

This notebook takes you as far as the first comparison that should make you
suspicious. After that it is your investigation.
"""
    )

    nb.code(
        """
TEAM = 1     # <-- change this
"""
    )

    nb.code(
        """
import numpy as np
import pandas as pd
from scipy.special import expit, logit

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, brier_score_loss

from medsim import (
    FEATURES, train_val_split,
    calibration_table, expected_calibration_error, performance_table,
    selective_risk_curve, shift_report, subgroup_report,
)
"""
        + PLOT_STYLE
        + """
rng = np.random.default_rng(0)
pd.set_option("display.width", 170)

import os
DATA = "project/data" if os.path.isdir("project/data") else "ai-uncertainty-2026-healthcare/project/data"

development = pd.read_csv(f"{DATA}/team_{TEAM}_train.csv")
deployment = pd.read_csv(f"{DATA}/team_{TEAM}_deployment.csv")

print(f"development records : {len(development)}")
print(f"deployment records  : {len(deployment)}")
print(f"columns             : {list(development.columns)}")
"""
    )

    nb.md(
        """
## Step 1 - look before you fit

Resist the urge to train something. Twenty minutes spent here will save you an
hour later.
"""
    )

    nb.code(
        """
print("event rate")
print(f"  development : {development['outcome'].mean():.3f}")
print(f"  deployment  : {deployment['outcome'].mean():.3f}")

print("\\nmissing fraction by column")
missing = pd.DataFrame({
    "development": development[FEATURES].isna().mean(),
    "deployment": deployment[FEATURES].isna().mean(),
})
display(missing.round(3))

display(development[FEATURES].describe().T.round(2))
"""
    )

    nb.md(
        """
## Step 2 - a baseline model, honestly evaluated

Hold out part of the development data. This is your internal validation set: it
is what you would have reported in a paper before ever seeing the new ward.
"""
    )

    nb.code(
        """
train, validation = train_val_split(development, val_fraction=0.3, seed=7)

model = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
).fit(train[FEATURES], train["outcome"])

def predict(df):
    return model.predict_proba(df[FEATURES])[:, 1]

display(performance_table([
    ("Internal validation", validation["outcome"], predict(validation)),
    ("Deployment ward", deployment["outcome"], predict(deployment)),
]).round(4))
"""
    )

    nb.md(
        """
**Stop and read that table before continuing.**

Compare every column, not just AUROC. Ask specifically:

- Did the **event rate** change, and did **mean predicted risk** follow it?
- Did **AUROC** hold up? Did it *improve*? An improvement is not automatically
  good news, and it is occasionally the loudest possible alarm.
- Did **ECE** or **Brier** move much more than AUROC did?

Write down, now, what you expect to find. Then go and check.
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for name, data in [("Internal validation", validation), ("Deployment ward", deployment)]:
    tab = calibration_table(data["outcome"], predict(data), n_bins=8)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", lw=2, label=name)

upper = max(tab["mean_predicted"].max(), tab["observed_rate"].max()) * 1.1
ax.plot([0, upper], [0, upper], ls="--", c="0.4", label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title(f"Team {TEAM}: calibration, development versus deployment")
ax.legend()
plt.show()
"""
    )

    nb.md(
        """
## Step 3 - the three diagnostics that find most problems

Run all three even if you think you already know the answer. One of them will
come back empty, and *which* one is empty is itself evidence.
"""
    )

    nb.code(
        """
continuous = ["age", "heart_rate", "systolic_bp", "respiratory_rate", "creatinine", "lactate", "wbc"]

print("A. Has the input distribution shifted? (no outcome labels needed)")
display(shift_report(train, deployment, continuous).round(3))
"""
    )

    nb.code(
        """
print("B. Does the aggregate number hide a subgroup?")
display(subgroup_report(deployment, predict(deployment), "group").round(4))

banded = deployment.assign(
    age_band=pd.cut(deployment["age"], [0, 55, 70, 80, 200], labels=["<55", "55-70", "70-80", "80+"])
)
display(subgroup_report(banded, predict(deployment), "age_band", min_n=50).round(4))
"""
    )

    nb.code(
        """
print("C. Is a blank cell telling you something?")
for column in ["creatinine", "lactate"]:
    absent = development[column].isna()
    if absent.sum() == 0:
        print(f"  {column}: nothing missing")
        continue
    print(f"  {column}: missing for {absent.mean():.1%} of patients | "
          f"event rate {development.loc[absent, 'outcome'].mean():.3f} when absent "
          f"vs {development.loc[~absent, 'outcome'].mean():.3f} when recorded")
"""
    )

    nb.md(
        """
## Step 4 - uncertainty, and the option to abstain

A bootstrap ensemble gives you a cheap epistemic signal. Where the resampled
models disagree, the training data did not pin the answer down.
"""
    )

    nb.code(
        """
def bootstrap_spread(train_df, eval_df, n_models=40, seed=0):
    imputer = SimpleImputer(strategy="median").fit(train_df[FEATURES])
    scaler = StandardScaler().fit(imputer.transform(train_df[FEATURES]))
    x_train = scaler.transform(imputer.transform(train_df[FEATURES]))
    x_eval = scaler.transform(imputer.transform(eval_df[FEATURES]))
    y_train = train_df["outcome"].to_numpy()

    boot = np.random.default_rng(seed)
    preds = []
    for _ in range(n_models):
        idx = boot.integers(0, len(y_train), len(y_train))
        preds.append(LogisticRegression(max_iter=3000).fit(x_train[idx], y_train[idx]).predict_proba(x_eval)[:, 1])
    return np.vstack(preds)


ensemble = bootstrap_spread(train, deployment)
mean_p, sd_p = ensemble.mean(axis=0), ensemble.std(axis=0)

fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2))
axes[0].scatter(mean_p, sd_p, s=7, alpha=0.3)
axes[0].set_xlabel("Mean predicted risk")
axes[0].set_ylabel("Ensemble disagreement (SD)")
axes[0].set_title("Where does the model disagree with itself?")

curve = selective_risk_curve(deployment["outcome"], mean_p, sd_p, decision_threshold=0.3)
axes[1].plot(curve["coverage"], curve["error_rate"], marker="o", ms=4, lw=2)
axes[1].set_xlabel("Coverage")
axes[1].set_ylabel("Error rate among retained patients")
axes[1].set_title("Risk-coverage curve")
plt.tight_layout()
plt.show()

display(curve.round(4))
"""
    )

    nb.md(
        """
## Step 5 - your investigation starts here

You now have the symptom. Find the mechanism.

Things worth trying, depending on what you saw:

- Add explicit missingness indicators and refit. Does anything improve?
- Recalibrate on part of the deployment data (an intercept correction is one
  line) and see how much of the gap it closes. If it closes all of it, the
  problem was prevalence. If it does not, the problem is structural.
- Stratify by every categorical column you have, and by whether each lab was
  recorded.
- Compare AUROC on your internal validation split against AUROC on deployment.
  If deployment is *better*, ask what that implies about your validation labels.
- Put a bootstrap interval on any difference you plan to claim. Several of the
  gaps you will see are inside the noise.
- Characterise the patients with the highest ensemble disagreement. What do they
  have in common?

Then answer the seven questions in `project/PROJECT_BRIEF.md` and build three or
four slides.

**Remember the actual task.** Not a higher AUROC. A defensible answer to: should
this model be switched on, for whom, and with what safeguards?
"""
    )

    return nb


if __name__ == "__main__":
    paths = build().write(ROOT / "notebooks", "90_team_project_starter", variants=None)
    for path in paths:
        print("wrote", path.relative_to(ROOT))
