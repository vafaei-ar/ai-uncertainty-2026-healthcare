"""Lecture 1 - Honest probabilities in clinical prediction."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.nbtools import PLOT_STYLE, Notebook  # noqa: E402


def build() -> Notebook:
    nb = Notebook("Lecture 1")

    nb.md(
        """
# Lecture 1 - Honest probabilities in clinical prediction

*AI & Uncertainty School and Workshop 2026, healthcare module*

A deployed clinical model does not output a ranking. It outputs a number that a
tired registrar at 3am will read as a probability, and act on. This session is
about whether that number deserves to be read that way.

**Where we are going**

1. A point estimate is not an answer
2. Discrimination and calibration are different things, and only one of them
   survives a change of hospital
3. Epistemic and aleatoric uncertainty, and why the distinction changes what you
   do next
4. A synthetic EHR you can break on purpose
5. What happens to a good model at a new site
6. The information hidden in a blank cell

Everything runs on a free Colab CPU. The data are synthetic, so nothing here
needs credentialing, and you can regenerate any cohort with a different seed to
check that a result is real and not a fluke of one draw.
"""
    )

    nb.note(
        "Open by asking the room: 'your model says 0.30 for this patient - what "
        "does that mean?' You will get ranking answers and frequency answers. "
        "That split is the whole lecture."
    )

    nb.code(
        """
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import beta

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, brier_score_loss

from medsim import (
    FEATURES, SimConfig, simulate_ehr, train_val_split,
    calibration_table, expected_calibration_error,
    performance_table, shift_report,
)
"""
        + PLOT_STYLE
        + """
SEED = 20261116
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 160)
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 1. A point estimate is not an answer

A new sepsis alert has fired 10 times on your ward. 8 of those alerts led to an
intervention the team judged appropriate. Is the alert useful?

The point estimate is 0.8. The honest answer is a distribution.
"""
    )

    nb.code(
        """
prior_a, prior_b = 2.0, 2.0          # weakly sceptical: centred at 0.5, easily moved
useful, not_useful = 8, 2

post_a, post_b = prior_a + useful, prior_b + not_useful
grid = np.linspace(0, 1, 500)

plt.plot(grid, beta.pdf(grid, prior_a, prior_b), label="Prior", lw=2)
plt.plot(grid, beta.pdf(grid, post_a, post_b), label="Posterior after 10 alerts", lw=2)
plt.axvline(useful / (useful + not_useful), ls=":", c="0.4", label="Point estimate (0.80)")
plt.xlabel("Probability an alert is clinically useful")
plt.ylabel("Density")
plt.title("Ten observations move the belief, they do not settle it")
plt.legend()
plt.show()

lo, hi = beta.ppf([0.025, 0.975], post_a, post_b)
print(f"posterior mean {post_a / (post_a + post_b):.3f}")
print(f"95% credible interval [{lo:.3f}, {hi:.3f}]")
print(f"P(alert useful more than half the time) = {1 - beta.cdf(0.5, post_a, post_b):.3f}")
"""
    )

    nb.md(
        """
The point estimate says 0.80. The interval says the true rate is somewhere
between 0.48 and 0.94. Those two statements support very different decisions,
and only one of them is honest about ten observations.

Watch what evidence actually buys you.
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for n in [10, 50, 200, 1000]:
    a, b = prior_a + 0.8 * n, prior_b + 0.2 * n
    ax.plot(grid, beta.pdf(grid, a, b), lw=2, label=f"n = {n}")
ax.set_xlim(0.5, 1.0)
ax.set_xlabel("Probability an alert is clinically useful")
ax.set_ylabel("Density")
ax.set_title("Same 80% success rate, four different states of knowledge")
ax.legend()
plt.show()

widths = {}
for n in [10, 50, 200, 1000]:
    a, b = prior_a + 0.8 * n, prior_b + 0.2 * n
    lo, hi = beta.ppf([0.025, 0.975], a, b)
    widths[n] = hi - lo
print(pd.Series(widths, name="95% interval width").round(3).to_string())
"""
    )

    nb.md(
        """
The interval narrows roughly as $1/\\sqrt{n}$. This is the shape of *epistemic*
uncertainty: it is a statement about what you do not yet know, and data removes
it. Hold on to that, because in section 3 we meet the kind that does not go away.
"""
    )

    nb.note(
        "Worth saying out loud: the prior did real work here. With Beta(2,2) and "
        "10 observations the posterior mean is 0.71, not 0.80. Ask the room "
        "whether that shrinkage is a bug. It is the same mechanism that saves the "
        "small hospital in Lecture 2."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 2. Two models, identical AUROC, one of them dangerous

AUROC asks: given a patient who deteriorated and one who did not, how often does
the model score the first one higher? It is a question about *order*.

Calibration asks: among the patients you assigned a risk of 0.3, did about 30%
actually deteriorate? It is a question about *meaning*.

A monotone transformation of the predictions leaves the order untouched and
destroys the meaning. AUROC cannot see it.
"""
    )

    nb.code(
        """
n = 6000
latent = rng.normal(0, 1.1, n)
p_true = expit(latent - 1.95)         # about 17% event rate, close to the cohorts below
y = rng.binomial(1, p_true)

p_honest = np.clip(p_true + rng.normal(0, 0.02, n), 1e-4, 1 - 1e-4)
p_overconfident = expit(2.4 * logit(p_honest))       # sharpened
p_timid = expit(0.45 * logit(p_honest))              # flattened

table = performance_table([
    ("Honest", y, p_honest),
    ("Overconfident", y, p_overconfident),
    ("Timid", y, p_timid),
])
display(table.round(4))
"""
    )

    nb.md(
        """
Identical AUROC to four decimal places, because all three are monotone
transformations of the same score. Brier, log loss and ECE separate them
immediately. Now look at the picture a clinical reviewer would ask for.
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for name, pred in [("Honest", p_honest), ("Overconfident", p_overconfident), ("Timid", p_timid)]:
    tab = calibration_table(y, pred, n_bins=10)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", lw=2, label=name)
ax.plot([0, 1], [0, 1], ls="--", c="0.4", label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("Same ranking, three different claims about the world")
ax.legend()
plt.show()

display(calibration_table(y, p_overconfident, n_bins=10).round(3))
"""
    )

    nb.md(
        """
Read the overconfident model's top decile: it promises a risk far above what the
ward delivers. If a bed-allocation rule is attached to a fixed threshold, this
model floods the ICU. The timid model does the opposite and lets patients through.

**Why this matters more than it looks.** AUROC is invariant to prevalence and to
any monotone rescaling. Those are exactly the two things that change when you
move a model to a new hospital. The metric that is most often reported is the
metric most blind to the most common deployment failure.
"""
    )

    nb.exercise(
        """
### Exercise 2.1

`p_overconfident` can be repaired by a single number, because we know it was
produced by scaling on the logit scale. Find the temperature $T$ that minimises
the Brier score of `expit(logit(p_overconfident) / T)`, and report AUROC, Brier
and ECE before and after.

Then answer in one line: did AUROC change, and why?
""",
        """
temperatures = np.linspace(0.5, 4.0, 141)
scores = [brier_score_loss(y, expit(logit(p_overconfident) / t)) for t in temperatures]
best_t = temperatures[int(np.argmin(scores))]

p_fixed = expit(logit(p_overconfident) / best_t)

plt.plot(temperatures, scores, lw=2)
plt.axvline(best_t, ls=":", c="0.4")
plt.xlabel("Temperature T")
plt.ylabel("Brier score")
plt.title(f"Best temperature = {best_t:.2f} (true value was 2.40)")
plt.show()

display(performance_table([
    ("Before scaling", y, p_overconfident),
    ("After scaling", y, p_fixed),
    ("Honest reference", y, p_honest),
]).round(4))

print("AUROC is unchanged: dividing the logit by a positive constant is monotone,")
print("so no pair of patients swaps order. Only the meaning of the numbers moved.")
""",
        stub="""
temperatures = np.linspace(0.5, 4.0, 141)

# 1. For each T, rescale: expit(logit(p_overconfident) / T)
# 2. Score each with brier_score_loss(y, ...)
# 3. Pick the best T, then compare before/after with performance_table

""",
    )

    nb.note(
        "The recovered temperature lands near 2.4 because that is exactly how the "
        "miscalibration was generated. Say so - it makes the point that "
        "recalibration works when you have correctly guessed the shape of the "
        "damage, and that in Lecture 2 we will meet damage of a shape we do not "
        "get to choose."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 3. Epistemic and aleatoric uncertainty

Two different reasons a prediction can be uncertain.

- **Aleatoric.** The outcome is genuinely stochastic given everything you
  recorded. Two patients with identical charts, different outcomes. More data on
  the same variables will not help. Only new *kinds* of measurement will.
- **Epistemic.** You are unsure about the model itself, because you have seen few
  patients like this one. More data of the same kind fixes it.

The distinction is not academic. It determines whether the correct response is
"collect more records", "measure something new", or "do not use the model on
this patient".
"""
    )

    nb.code(
        """
def bootstrap_band(n_train, n_models=60, seed=0):
    boot_rng = np.random.default_rng(seed)
    train = simulate_ehr(SimConfig(n=n_train, seed=seed + 1))
    grid_df = simulate_ehr(SimConfig(n=1500, seed=999))

    imputer = SimpleImputer(strategy="median").fit(train[FEATURES])
    scaler = StandardScaler().fit(imputer.transform(train[FEATURES]))
    x_train = scaler.transform(imputer.transform(train[FEATURES]))
    x_grid = scaler.transform(imputer.transform(grid_df[FEATURES]))
    y_train = train["outcome"].to_numpy()

    preds = []
    for _ in range(n_models):
        idx = boot_rng.integers(0, len(y_train), len(y_train))
        model = LogisticRegression(max_iter=3000).fit(x_train[idx], y_train[idx])
        preds.append(model.predict_proba(x_grid)[:, 1])
    return np.vstack(preds), grid_df


sizes = [250, 1000, 8000]
fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9), sharey=True)
summary = []

for ax, n_train in zip(axes, sizes):
    preds, grid_df = bootstrap_band(n_train)
    mean_p, sd_p = preds.mean(axis=0), preds.std(axis=0)
    aleatoric = mean_p * (1 - mean_p)

    order = np.argsort(mean_p)
    ax.fill_between(mean_p[order], (mean_p - 2 * sd_p)[order], (mean_p + 2 * sd_p)[order],
                    alpha=0.3, label="Epistemic band (2 SD)")
    ax.plot(mean_p[order], mean_p[order], lw=1.5, c="0.2", label="Mean prediction")
    ax.set_title(f"trained on n = {n_train}")
    ax.set_xlabel("Predicted risk")
    summary.append({"n_train": n_train,
                    "mean epistemic SD": sd_p.mean(),
                    "mean aleatoric variance": aleatoric.mean()})

axes[0].set_ylabel("Predicted risk")
axes[0].legend(loc="upper left", fontsize=9)
plt.tight_layout()
plt.show()

display(pd.DataFrame(summary).round(4))
"""
    )

    nb.md(
        """
Epistemic uncertainty falls by roughly a factor of five between 250 and 8000
training patients. Aleatoric uncertainty barely moves - it is a property of the
cohort, not of your sample size.

There is a second, sharper way to see the aleatoric floor. Our simulator contains
a variable called `concern`: an unrecorded clinical impression that moves the
outcome and appears in no column of the dataset. It is exactly the situation of
every real EHR model, where the thing the nurse noticed at the bedside never
makes it into a structured field.
"""
    )

    nb.code(
        """
truth = simulate_ehr(SimConfig(n=20000, seed=77), keep_truth=True)

train_t, test_t = train_val_split(truth, 0.4, seed=3)
fitted = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
).fit(train_t[FEATURES], train_t["outcome"])

p_model = fitted.predict_proba(test_t[FEATURES])[:, 1]

print(f"AUROC of our fitted model            {roc_auc_score(test_t['outcome'], p_model):.3f}")
print(f"AUROC of the true probability        {roc_auc_score(test_t['outcome'], test_t['true_p']):.3f}")
print(f"AUROC of true p without 'concern'    "
      f"{roc_auc_score(test_t['outcome'], expit(test_t['latent'] - 0.70 * test_t['concern'])):.3f}")
"""
    )

    nb.md(
        """
An oracle with access to every recorded feature *and* the unrecorded clinical
impression reaches about 0.78. Strip the impression out, and the ceiling for any
model built on the columns we actually have falls to roughly 0.73. Our fitted
model sits at 0.72.

Read those three numbers again. Our model is within about 0.01 of the best any
model could do on this data, and essentially the entire remaining gap to 0.78 is
a variable that was never written down.

**The practical consequence.** When a reviewer asks why your AUROC is not 0.90,
the answer is a statement about the data-generating process, not an apology. And
the way to move the ceiling is to record something new - not to fit a deeper
network to the same seven columns.
"""
    )

    nb.note(
        "This is the slide people remember. If the room only takes one thing from "
        "Lecture 1, make it this: know your aleatoric floor before you promise "
        "anyone an improvement."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 4. A synthetic EHR you can break on purpose

`medsim.simulate_ehr` generates admissions with vitals, labs and comorbidities,
and a 48-hour deterioration outcome. Every failure mode we care about is a named
argument, so you can turn one on, see exactly what it does to the metrics, and
turn it off again.

```python
SimConfig(
    n, site, seed,
    prevalence_shift,        # baseline risk differs between hospitals
    measurement_noise,       # instruments and assays drift
    missingness_strength,    # labs are ordered for a reason
    label_noise,             # chart review is imperfect
    subgroup_shift,          # a subgroup carries different baseline risk
    subgroup_interaction,    # ...or a different risk relationship entirely
    ood_fraction,            # patients unlike anything in development
)
```
"""
    )

    nb.code(
        """
development = simulate_ehr(SimConfig(n=8000, site="A", seed=11))
train, validation = train_val_split(development, val_fraction=0.3, seed=5)

baseline_model = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
).fit(train[FEATURES], train["outcome"])

def predict(df):
    return baseline_model.predict_proba(df[FEATURES])[:, 1]

display(performance_table([
    ("Training split", train["outcome"], predict(train)),
    ("Internal validation", validation["outcome"], predict(validation)),
]).round(4))

display(development[FEATURES].describe().T.round(2))
"""
    )

    nb.md(
        """
A respectable internal validation. In a paper this is the row that gets reported,
usually without an interval. Let us put one on it, because an AUROC computed on
2400 patients with a 14% event rate is less precise than it looks.
"""
    )

    nb.code(
        """
def bootstrap_ci(y_true, y_prob, statistic=roc_auc_score, n_boot=400, seed=0):
    boot_rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    values = []
    for _ in range(n_boot):
        idx = boot_rng.integers(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        values.append(statistic(y_true[idx], y_prob[idx]))
    return np.quantile(values, [0.025, 0.5, 0.975])

lo, mid, hi = bootstrap_ci(validation["outcome"], predict(validation))
print(f"validation AUROC {mid:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  (width {hi - lo:.3f})")

lo_b, mid_b, hi_b = bootstrap_ci(validation["outcome"], predict(validation), brier_score_loss)
print(f"validation Brier {mid_b:.4f}  95% CI [{lo_b:.4f}, {hi_b:.4f}]")
"""
    )

    nb.md(
        """
The interval spans roughly 0.06. Two models whose AUROCs differ by 0.01, or by
0.02, are indistinguishable on this much data. A large share of reported
improvements in the clinical ML literature are narrower than this interval, and
are reported without one.
"""
    )

    nb.note(
        "Good place for a pause. Ask how many papers they have read that report a "
        "0.01 AUROC gain as an improvement, and how many reported an interval."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 5. The model meets a second hospital

The model above is now offered to two other hospitals in the group.

- **Site B** has a sicker intake: the same patients carry higher baseline risk.
- **Site C** runs older analysers: the same physiology, recorded more noisily.

Nothing about the model changes. Watch which metric notices.
"""
    )

    nb.code(
        """
site_b = simulate_ehr(SimConfig(n=5000, site="B", prevalence_shift=0.5, seed=21))
site_c = simulate_ehr(SimConfig(n=5000, site="A", measurement_noise=2.8, seed=22))

display(performance_table([
    ("Site A (internal validation)", validation["outcome"], predict(validation)),
    ("Site B (sicker intake)", site_b["outcome"], predict(site_b)),
    ("Site C (noisier instruments)", site_c["outcome"], predict(site_c)),
]).round(4))
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for name, data in [("Site A", validation), ("Site B", site_b), ("Site C", site_c)]:
    tab = calibration_table(data["outcome"], predict(data), n_bins=8)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", lw=2, label=name)
ax.plot([0, 0.6], [0, 0.6], ls="--", c="0.4", label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("A model that transfers its ranking but not its numbers")
ax.legend()
plt.show()
"""
    )

    nb.md(
        """
At site B, AUROC holds up and the model understates risk by roughly a factor of
two across the whole range. If the alert threshold stays at 0.5, the model
essentially stops firing on a ward where a quarter of patients deteriorate.

Now the question that matters operationally: **could you have detected this
before switching the model on**, without waiting six months for outcomes?
"""
    )

    nb.code(
        """
continuous = ["age", "heart_rate", "systolic_bp", "respiratory_rate", "creatinine", "lactate", "wbc"]

print("Site B versus site A - covariates only, no labels used:")
display(shift_report(train, site_b, continuous).round(3))

print("Site C versus site A:")
display(shift_report(train, site_c, continuous).round(3))
"""
    )

    nb.md(
        """
This is the central asymmetry of deployment monitoring.

- **Site C is visible without labels.** The standardised mean differences on
  lactate, creatinine and WBC are large. A covariate-shift alarm would have fired
  on day one.
- **Site B is invisible without labels.** Every standardised mean difference is
  under 0.03. The covariate distribution $P(X)$ is unchanged; what moved is
  $P(Y \\mid X)$. No amount of input monitoring will find it.

So input-drift dashboards, which is what most deployed monitoring actually is,
catch one of these two failures and are structurally blind to the other. The only
thing that finds site B is outcome data - which means prospective label
collection is not optional infrastructure, it is the monitoring system.
"""
    )

    nb.note(
        "If time is short, this is the section to protect. It is the one finding "
        "in the lecture that changes what people build on Monday."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 6. The information in a blank cell

Standard practice treats missing values as damage to be repaired: impute the
median, or drop the row. Both moves assume the value went missing for reasons
unrelated to the outcome.

In an EHR that assumption is almost always false. A lab is missing because nobody
ordered it, and nobody ordered it because nobody was worried.
"""
    )

    nb.code(
        """
mnar = simulate_ehr(SimConfig(n=8000, missingness_strength=1.4, seed=31))
mnar_train, mnar_test = train_val_split(mnar, 0.35, seed=6)

print("missing fraction:")
print(mnar[FEATURES].isna().mean().round(3)[lambda s: s > 0].to_string())

observed = mnar[mnar["creatinine"].notna()]["outcome"].mean()
absent = mnar[mnar["creatinine"].isna()]["outcome"].mean()
print(f"\\ndeterioration rate, creatinine recorded : {observed:.3f}")
print(f"deterioration rate, creatinine absent   : {absent:.3f}")

fig, ax = plt.subplots(figsize=(5.4, 3.8))
ax.bar(["Creatinine\\nrecorded", "Creatinine\\nabsent"], [observed, absent], color=["#4C72B0", "#C44E52"])
ax.set_ylabel("Observed deterioration rate")
ax.set_title("The blank cell is a clinical judgement")
plt.show()
"""
    )

    nb.md(
        """
Patients whose creatinine was never sent deteriorate at less than half the rate of
those whose was. The missingness pattern carries more signal than several of the
recorded features.

Two standard responses, both wrong:
"""
    )

    nb.code(
        """
complete_case = mnar_train.dropna(subset=FEATURES)
print(f"complete-case analysis keeps {len(complete_case)} of {len(mnar_train)} patients "
      f"({len(complete_case) / len(mnar_train):.0%})")
print(f"  event rate in the complete cases : {complete_case['outcome'].mean():.3f}")
print(f"  event rate in the full cohort    : {mnar_train['outcome'].mean():.3f}")
print("\\nDropping incomplete rows silently selected the sickest part of the ward.")
"""
    )

    nb.exercise(
        """
### Exercise 6.1

Fit two models on `mnar_train` and evaluate both on `mnar_test`:

1. **Median imputation only**, using `FEATURES`.
2. **Median imputation plus explicit missingness indicators** -
   add `creatinine_missing` and `lactate_missing` as binary columns.

Compare AUROC, Brier and ECE. Then say in one line what the second model learned
that the first one threw away.
""",
        """
def with_indicators(df):
    out = df.copy()
    out["creatinine_missing"] = out["creatinine"].isna().astype(int)
    out["lactate_missing"] = out["lactate"].isna().astype(int)
    return out

extended = FEATURES + ["creatinine_missing", "lactate_missing"]

plain = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
).fit(mnar_train[FEATURES], mnar_train["outcome"])

flagged = make_pipeline(
    SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
).fit(with_indicators(mnar_train)[extended], mnar_train["outcome"])

p_plain = plain.predict_proba(mnar_test[FEATURES])[:, 1]
p_flagged = flagged.predict_proba(with_indicators(mnar_test)[extended])[:, 1]

display(performance_table([
    ("Median imputation", mnar_test["outcome"], p_plain),
    ("Imputation + missingness flags", mnar_test["outcome"], p_flagged),
]).round(4))

coefficients = flagged.named_steps["logisticregression"].coef_[0]
print(pd.Series(coefficients, index=extended).sort_values(key=np.abs, ascending=False).round(3).to_string())

print("\\nThe flags recover the ordering decision itself: whether a clinician")
print("thought the lab was worth sending. Median imputation overwrites that")
print("judgement with the population median and loses it.")
""",
        stub="""
def with_indicators(df):
    out = df.copy()
    out["creatinine_missing"] = out["creatinine"].isna().astype(int)
    out["lactate_missing"] = out["lactate"].isna().astype(int)
    return out

extended = FEATURES + ["creatinine_missing", "lactate_missing"]

# Fit both models, predict on mnar_test, and compare with performance_table.
# Then look at the fitted coefficients on the two indicator columns.

""",
    )

    nb.md(
        """
A caution to carry into deployment: the indicator is informative *because* it
encodes local ordering practice. Move the model to a hospital that sends a routine
lab panel on every admission and the feature means something completely
different. Useful features and fragile features are frequently the same features.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## What to take away

1. Report a distribution, or at minimum an interval. A point estimate on ten
   observations is not a finding.
2. AUROC measures order. Brier, log loss and calibration curves measure meaning.
   Deployment breaks meaning first, and AUROC is blind to it by construction.
3. Separate the uncertainty you can remove with more of the same data from the
   uncertainty you cannot. They call for different responses, and only one of
   them is a modelling problem.
4. Know your aleatoric floor. Some of the gap to a perfect model was never in
   your columns.
5. Covariate-shift monitoring catches noisy instruments and misses shifted
   prevalence. Plan label collection accordingly.
6. Missingness is a recorded decision. Model it; do not impute it away, and never
   drop the rows.

**In Lecture 2:** repairing calibration at a new site, using ensemble
disagreement to decide when a model should refuse to answer, choosing an
operating threshold from clinical costs rather than from 0.5, and borrowing
strength across hospitals with hierarchical models.
"""
    )

    return nb


if __name__ == "__main__":
    paths = build().write(ROOT / "notebooks", "01_lecture1_uncertainty_foundations")
    for path in paths:
        print("wrote", path.relative_to(ROOT))
