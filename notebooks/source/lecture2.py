"""Lecture 2 - Deciding under uncertainty."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.nbtools import PLOT_STYLE, Notebook  # noqa: E402


def build() -> Notebook:
    nb = Notebook("Lecture 2")

    nb.md(
        """
# Lecture 2 - Deciding under uncertainty

*AI & Uncertainty School and Workshop 2026, healthcare module*

Lecture 1 ended with a model that ranks patients well at a new hospital and
states their risk wrongly. This session is about what you do next.

**Where we are going**

1. Repairing calibration at a new site, and how many labelled patients that costs
2. Ensembles: turning model disagreement into a usable uncertainty signal
3. Selective prediction - letting the model say "not this patient"
4. Choosing a threshold from clinical costs instead of from 0.5
5. Subgroup reliability, and why the aggregate number lies
6. Hierarchical models: borrowing strength across hospitals
7. Simulation-based inference, where the model is a simulator rather than a fit

Sections 6 and 7 have full companion notebooks (`03_hierarchical_pymc` and
`04_simulation_based_inference`) for anyone who wants to go further during the
project block.
"""
    )

    nb.code(
        """
import numpy as np
import pandas as pd
from scipy.special import expit, logit

from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, brier_score_loss

from medsim import (
    FEATURES, SimConfig, simulate_ehr, train_val_split,
    calibration_table, expected_calibration_error, performance_table,
    selective_risk_curve, shift_report, subgroup_report,
)
"""
        + PLOT_STYLE
        + """
SEED = 20261117
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 170)


def fit_baseline(train, features=FEATURES):
    return make_pipeline(
        SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
    ).fit(train[features], train["outcome"])


development = simulate_ehr(SimConfig(n=8000, site="A", seed=11))
train, validation = train_val_split(development, val_fraction=0.3, seed=5)
model = fit_baseline(train)

def predict(df):
    return model.predict_proba(df[FEATURES])[:, 1]

site_b = simulate_ehr(SimConfig(n=6000, site="B", prevalence_shift=0.5, seed=21))

display(performance_table([
    ("Internal validation (site A)", validation["outcome"], predict(validation)),
    ("New hospital (site B)", site_b["outcome"], predict(site_b)),
]).round(4))
"""
    )

    nb.md(
        """
Where we left off: ranking survives the move, the probabilities do not. The model
tells site B that 15% of their ward is at risk while 26% of it deteriorates.

---
## 1. Recalibration, and what it costs

Three standard repairs, in increasing order of flexibility.

| Method | What it fits | Parameters | When it is the right choice |
| --- | --- | --- | --- |
| Intercept correction | A shift on the logit scale | 1 | Prevalence changed, the risk ordering did not |
| Platt scaling | Slope and intercept on the logit scale | 2 | Ordering is right but the spread is wrong too |
| Isotonic regression | Any monotone map | many | Plenty of labels and a distortion of unknown shape |

Every one of them needs **labelled patients from the new site**. That is the real
cost of deployment, and it is usually left out of the project plan.
"""
    )

    nb.code(
        """
calib_set, test_set = train_val_split(site_b, val_fraction=0.6, seed=9)
print(f"recalibration set: {len(calib_set)} patients   held-out test: {len(test_set)}")


def intercept_correction(p_calib, y_calib):
    fitted = LogisticRegression(max_iter=1000).fit(np.zeros((len(y_calib), 1)), y_calib)
    offset = float(fitted.intercept_[0]) - float(np.mean(logit(np.clip(p_calib, 1e-6, 1 - 1e-6))))
    return lambda p: expit(logit(np.clip(p, 1e-6, 1 - 1e-6)) + offset)


def platt_scaling(p_calib, y_calib):
    z = logit(np.clip(p_calib, 1e-6, 1 - 1e-6)).reshape(-1, 1)
    fitted = LogisticRegression(max_iter=1000).fit(z, y_calib)
    a, b = float(fitted.coef_[0][0]), float(fitted.intercept_[0])
    return lambda p: expit(a * logit(np.clip(p, 1e-6, 1 - 1e-6)) + b)


def isotonic(p_calib, y_calib):
    fitted = IsotonicRegression(out_of_bounds="clip").fit(p_calib, y_calib)
    return lambda p: np.clip(fitted.predict(p), 1e-6, 1 - 1e-6)


p_calib = predict(calib_set)
p_test = predict(test_set)
y_calib = calib_set["outcome"].to_numpy()

repairs = {
    "Uncorrected": lambda p: p,
    "Intercept correction": intercept_correction(p_calib, y_calib),
    "Platt scaling": platt_scaling(p_calib, y_calib),
    "Isotonic": isotonic(p_calib, y_calib),
}

display(performance_table([
    (name, test_set["outcome"], fn(p_test)) for name, fn in repairs.items()
]).round(4))
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for name, fn in repairs.items():
    tab = calibration_table(test_set["outcome"], fn(p_test), n_bins=8)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", lw=2, label=name)
ax.plot([0, 0.7], [0, 0.7], ls="--", c="0.4", label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("One parameter fixes most of it")
ax.legend()
plt.show()
"""
    )

    nb.md(
        """
AUROC is untouched by all three - none of them reorders anyone. Brier, log loss
and ECE improve sharply, and a single intercept recovers most of the gain,
because a single intercept is exactly the damage that was done.

The operational question is how many labelled patients you need before the
correction is trustworthy.
"""
    )

    nb.code(
        """
sizes = [25, 50, 100, 200, 400, 800, 1600]
records = []

for n_calib in sizes:
    for repeat in range(40):
        boot = np.random.default_rng(1000 * repeat + n_calib)
        idx = boot.choice(len(calib_set), n_calib, replace=False)
        subset = calib_set.iloc[idx]
        p_sub, y_sub = predict(subset), subset["outcome"].to_numpy()
        if len(np.unique(y_sub)) < 2:
            continue
        for name, factory in [("Intercept", intercept_correction), ("Platt", platt_scaling), ("Isotonic", isotonic)]:
            fn = factory(p_sub, y_sub)
            records.append({"n_calib": n_calib, "method": name,
                            "brier": brier_score_loss(test_set["outcome"], fn(p_test))})

curve = pd.DataFrame(records).groupby(["method", "n_calib"])["brier"].median().reset_index()

fig, ax = plt.subplots()
for name, part in curve.groupby("method"):
    ax.plot(part["n_calib"], part["brier"], marker="o", lw=2, label=name)
ax.axhline(brier_score_loss(test_set["outcome"], p_test), ls="--", c="0.4", label="No correction")
ax.set_xscale("log")
ax.set_xlabel("Labelled patients used for recalibration")
ax.set_ylabel("Brier score on held-out deployment data")
ax.set_title("How much outcome data does a fix actually need?")
ax.legend()
plt.show()

display(curve.pivot(index="n_calib", columns="method", values="brier").round(4))
"""
    )

    nb.md(
        """
The one-parameter correction is already close to its ceiling at around 100
labelled patients. Isotonic regression needs an order of magnitude more before it
stops being worse than doing nothing, because it is spending its flexibility on
noise.

**The general rule.** Match the flexibility of the repair to the amount of
outcome data you can actually get from the new site. A one-parameter fix on 100
charts beats a non-parametric fix on the same 100 charts, every time.
"""
    )

    nb.note(
        "Ask what happens if the model is recalibrated on the first 100 patients "
        "of a seasonal wave. The correction inherits whatever period it was "
        "estimated in - recalibration is a maintenance commitment, not a one-off "
        "task."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 2. Ensembles as an epistemic uncertainty signal

Refit the same model on bootstrap resamples of the training data. Where the
resampled models agree, the data pinned the answer down. Where they disagree, the
prediction is an extrapolation.

This is the cheapest useful epistemic signal there is, and unlike a predicted
probability it does not require the outcome to evaluate.
"""
    )

    nb.code(
        """
def bootstrap_predictions(train_df, eval_frames, n_models=60, seed=0):
    imputer = SimpleImputer(strategy="median").fit(train_df[FEATURES])
    scaler = StandardScaler().fit(imputer.transform(train_df[FEATURES]))
    x_train = scaler.transform(imputer.transform(train_df[FEATURES]))
    y_train = train_df["outcome"].to_numpy()
    x_eval = [scaler.transform(imputer.transform(df[FEATURES])) for df in eval_frames]

    boot = np.random.default_rng(seed)
    stacks = [[] for _ in eval_frames]
    for _ in range(n_models):
        idx = boot.integers(0, len(y_train), len(y_train))
        fitted = LogisticRegression(max_iter=3000).fit(x_train[idx], y_train[idx])
        for slot, matrix in zip(stacks, x_eval):
            slot.append(fitted.predict_proba(matrix)[:, 1])
    return [np.vstack(slot) for slot in stacks]


ood_ward = simulate_ehr(SimConfig(n=6000, site="A", ood_fraction=0.30, seed=41), keep_truth=True)

preds_val, preds_ood = bootstrap_predictions(train, [validation, ood_ward])
sd_val, sd_ood = preds_val.std(axis=0), preds_ood.std(axis=0)

fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2))
axes[0].hist(sd_val, bins=45, alpha=0.75, label="Familiar ward (site A)", density=True)
axes[0].hist(sd_ood, bins=45, alpha=0.6, label="Ward with unfamiliar patients", density=True)
axes[0].set_xlabel("Ensemble disagreement (SD across models)")
axes[0].set_ylabel("Density")
axes[0].set_title("Disagreement rises where the data run out")
axes[0].legend()

axes[1].scatter(preds_ood.mean(axis=0)[ood_ward["is_ood"] == 0], sd_ood[ood_ward["is_ood"] == 0],
                s=7, alpha=0.35, label="Seen in development")
axes[1].scatter(preds_ood.mean(axis=0)[ood_ward["is_ood"] == 1], sd_ood[ood_ward["is_ood"] == 1],
                s=7, alpha=0.5, label="Unlike anything in development")
axes[1].set_xlabel("Mean predicted risk")
axes[1].set_ylabel("Ensemble disagreement")
axes[1].set_title("The signal separates the two populations")
axes[1].legend()
plt.tight_layout()
plt.show()

flagged = sd_ood > np.quantile(sd_val, 0.95)
print(f"Patients flagged by a site-A 95th-percentile threshold : {flagged.mean():.1%}")
print(f"Of those flagged, genuinely out-of-distribution        : {ood_ward['is_ood'][flagged].mean():.1%}")
print(f"Of the truly OOD patients, caught by the flag          : "
      f"{flagged[ood_ward['is_ood'] == 1].mean():.1%}")
"""
    )

    nb.md(
        """
A threshold set on the *development* data alone - the 95th percentile of
disagreement at site A - flags a substantial slice of the new ward, and it is
enriched for the patients that really are unlike anything in development.

Note carefully what this required: **no outcome labels from the new site.** This
is the one uncertainty check you can run on day one of deployment, which makes it
disproportionately valuable relative to how cheap it is.

The limitation is equally important. Bootstrap disagreement measures sensitivity
to the training sample, not distance from the training distribution. A patient
far outside the data can still receive confident, wrong, unanimous predictions if
the model form extrapolates smoothly. Treat this as a screen, not a guarantee.
"""
    )

    nb.note(
        "If someone asks about deep ensembles, MC dropout or conformal prediction: "
        "the machinery differs, the logical role is identical. Conformal is the "
        "one worth naming, because it gives distribution-free coverage guarantees "
        "under exchangeability - and exchangeability is exactly what site B broke."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 3. Selective prediction: the model is allowed to abstain

A deployed model does not have to answer every question. Rank patients by
uncertainty, hand the worst back to a clinician, and measure the error rate on
what remains. The resulting risk-coverage curve is the honest summary of a
model that is allowed to say "I don't know".

The choice of *which* uncertainty to rank by matters more than people expect.
"""
    )

    nb.code(
        """
mean_ood = preds_ood.mean(axis=0)
y_ood = ood_ward["outcome"]

rankings = {
    "Ensemble disagreement": sd_ood,
    "Distance from 0.5": -np.abs(mean_ood - 0.5),
    "Predictive entropy": -(mean_ood * np.log(mean_ood + 1e-9) + (1 - mean_ood) * np.log(1 - mean_ood + 1e-9)),
    "Random deferral": rng.random(len(mean_ood)),
}

fig, ax = plt.subplots()
for name, uncertainty in rankings.items():
    curve = selective_risk_curve(y_ood, mean_ood, uncertainty, decision_threshold=0.30)
    ax.plot(curve["coverage"], curve["error_rate"], marker="o", ms=3.5, lw=2, label=name)
ax.set_xlabel("Coverage (fraction of patients the model still answers for)")
ax.set_ylabel("Error rate among retained patients")
ax.set_title("Risk-coverage: does the model know what it does not know?")
ax.legend()
plt.show()

summary = []
for name, uncertainty in rankings.items():
    curve = selective_risk_curve(y_ood, mean_ood, uncertainty, decision_threshold=0.30)
    def pick(c):
        return curve.iloc[int(np.argmin(np.abs(curve["coverage"] - c)))]["error_rate"]
    summary.append({"ranking": name, "error @100%": pick(1.0), "error @70%": pick(0.7), "error @40%": pick(0.4)})
display(pd.DataFrame(summary).round(4))
"""
    )

    nb.md(
        """
Random deferral is the null: it shrinks the cohort without improving anything, and
its curve is flat. Any ranking worth using must beat it.

"Distance from 0.5" usually looks strongest here, and it is worth being precise
about why: it is measuring *aleatoric* uncertainty - genuinely borderline
patients - and deferring borderline cases mechanically reduces classification
error. Ensemble disagreement is measuring something different, and more useful:
patients the model was never equipped to judge. The first improves your error
rate; the second protects you from confidently harming someone.

**Do not collapse them into one number.** Report both, and use them for different
things: aleatoric for triage of borderline cases, epistemic as a hard gate on
patients outside the model's competence.
"""
    )

    nb.exercise(
        """
### Exercise 3.1

The clinical service can absorb reviewing 20% of admissions by hand.

Build a two-stage rule for the `ood_ward` cohort:

1. Refuse to answer for any patient whose ensemble disagreement exceeds the
   site-A 95th percentile (the epistemic gate from section 2).
2. Spend whatever review capacity remains on the most aleatorically uncertain of
   the rest.

Report: total coverage, error rate on retained patients, and how the error rate
compares with spending the whole 20% budget on either signal alone.
""",
        """
budget = 0.20
n_total = len(mean_ood)

gate = sd_ood > np.quantile(sd_val, 0.95)
print(f"epistemic gate defers {gate.mean():.1%} of the ward")

remaining_budget = max(budget - gate.mean(), 0.0)
n_extra = int(round(remaining_budget * n_total))

borderline = -np.abs(mean_ood - 0.5)
candidates = np.where(~gate)[0]
extra = candidates[np.argsort(borderline[candidates])[:n_extra]] if n_extra > 0 else np.array([], dtype=int)

deferred = gate.copy()
deferred[extra] = True
retained = ~deferred

def error_rate(mask):
    return float(((mean_ood[mask] >= 0.30).astype(int) != y_ood[mask]).mean())

rows = [{"rule": "Answer for everyone", "coverage": 1.0, "error": error_rate(np.ones(n_total, bool))},
        {"rule": "Two-stage (gate then borderline)", "coverage": float(retained.mean()), "error": error_rate(retained)}]

for name, uncertainty in [("Epistemic only", sd_ood), ("Aleatoric only", borderline)]:
    cut = np.argsort(uncertainty)[: int(round((1 - budget) * n_total))]
    mask = np.zeros(n_total, bool); mask[cut] = True
    rows.append({"rule": f"{name}, 20% budget", "coverage": float(mask.mean()), "error": error_rate(mask)})

display(pd.DataFrame(rows).round(4))

print(f"\\nOf the patients the two-stage rule deferred, "
      f"{ood_ward['is_ood'][deferred].mean():.1%} were genuinely out-of-distribution,")
print(f"against {ood_ward['is_ood'].mean():.1%} in the ward as a whole.")
""",
        stub="""
budget = 0.20

# 1. gate = ensemble disagreement above the site-A 95th percentile
# 2. spend the remaining budget on the most borderline of the rest
# 3. compare coverage and error against each signal used alone

""",
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 4. The threshold is a clinical decision, not a default

`predict >= 0.5` encodes the assumption that a missed deterioration and an
unnecessary escalation cost the same. No clinician believes that.

If missing an event is $R$ times as costly as a false alarm, the threshold that
maximises expected utility is $t^* = 1/(1 + R)$. Net benefit puts the two error
types on one scale at a chosen threshold:

$$\\text{NB}(t) = \\frac{TP}{n} - \\frac{FP}{n} \\cdot \\frac{t}{1-t}$$

and this is only interpretable if the probabilities are calibrated - which brings
section 1 back as a prerequisite rather than a nicety.
"""
    )

    nb.code(
        """
def net_benefit(y_true, y_prob, thresholds):
    y_true = np.asarray(y_true)
    n = len(y_true)
    rows = []
    for t in thresholds:
        flagged = y_prob >= t
        tp = int(np.sum(flagged & (y_true == 1)))
        fp = int(np.sum(flagged & (y_true == 0)))
        rows.append({"threshold": t,
                     "net_benefit": tp / n - (fp / n) * (t / (1 - t)),
                     "alert_rate": flagged.mean()})
    return pd.DataFrame(rows)


thresholds = np.linspace(0.02, 0.60, 60)
recalibrated = repairs["Intercept correction"]

y_test = test_set["outcome"].to_numpy()
prevalence = y_test.mean()

fig, ax = plt.subplots()
ax.plot(thresholds, net_benefit(y_test, p_test, thresholds)["net_benefit"],
        lw=2, label="Uncorrected model")
ax.plot(thresholds, net_benefit(y_test, recalibrated(p_test), thresholds)["net_benefit"],
        lw=2, label="Recalibrated model")
ax.plot(thresholds, [prevalence - (1 - prevalence) * (t / (1 - t)) for t in thresholds],
        ls="--", c="0.5", label="Escalate everyone")
ax.axhline(0, ls=":", c="0.3", label="Escalate no one")
ax.set_ylim(-0.05, 0.22)
ax.set_xlabel("Decision threshold (= 1 / (1 + cost ratio))")
ax.set_ylabel("Net benefit")
ax.set_title("Where is the model actually worth using?")
ax.legend()
plt.show()

for ratio in [2, 5, 10, 20]:
    t = 1 / (1 + ratio)
    row_raw = net_benefit(y_test, p_test, [t]).iloc[0]
    row_fix = net_benefit(y_test, recalibrated(p_test), [t]).iloc[0]
    print(f"missed event {ratio:>2}x costlier -> threshold {t:.3f} | "
          f"alert rate {row_raw['alert_rate']:.3f} -> {row_fix['alert_rate']:.3f} | "
          f"net benefit {row_raw['net_benefit']:.4f} -> {row_fix['net_benefit']:.4f}")
"""
    )

    nb.md(
        """
Two things to take from this.

First, the useful range of thresholds is nowhere near 0.5. At a 10:1 cost ratio -
a modest assumption for a deterioration alert - the operating point is 0.09.
Reporting accuracy at 0.5 describes a decision nobody would make.

Second, miscalibration and threshold choice interact. The uncorrected model is
systematically low, so at any fixed threshold it under-alerts - at a 3:1 cost
ratio it flags 6% of the ward where the recalibrated model flags 30%. A
calibration error that looks cosmetic on a reliability plot becomes a decision
error at the operating point.

Third, and least comfortable: look at where the model's curve sits relative to
"escalate everyone". At a 10:1 cost ratio the recalibrated model earns a net
benefit of about 0.19 against roughly 0.19 for escalating the entire ward. On a
ward with a 26% event rate and that cost ratio, the model is not adding much over
a blanket policy. Net benefit asks the question a clinical director actually
asks - is this better than what we would do without you? - and it is the reason
to compute it before promising a benefit.
"""
    )

    nb.note(
        "Where does R come from? Not from the data. It comes from the service - "
        "ICU bed availability, staffing, what the escalation actually involves. "
        "Getting a clinician to state R is often the most valuable hour of a "
        "deployment project, and the number is rarely what the modelling team "
        "assumed."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 5. The aggregate number lies

A model can be well calibrated overall and badly calibrated for every subgroup in
it, because subgroup errors cancel. Aggregate metrics are averages, and averages
hide exactly the thing a fairness or safety review is looking for.
"""
    )

    nb.code(
        """
mixed = simulate_ehr(SimConfig(
    n=8000, site="A", subgroup_prevalence=0.40, subgroup_shift=1.0,
    subgroup_interaction=-1.8, seed=51,
))
sparse_train = simulate_ehr(SimConfig(
    n=8000, site="A", subgroup_prevalence=0.08, subgroup_shift=1.0,
    subgroup_interaction=-1.8, seed=52,
))

sparse_model = fit_baseline(sparse_train)
p_mixed = sparse_model.predict_proba(mixed[FEATURES])[:, 1]

print(f"the minority subgroup was {sparse_train['group'].mean():.1%} of development data "
      f"and is {mixed['group'].mean():.1%} of this ward\\n")

display(performance_table([("Whole ward", mixed["outcome"], p_mixed)]).round(4))
display(subgroup_report(mixed, p_mixed, "group").round(4))

mixed_by_age = mixed.assign(age_band=pd.cut(mixed["age"], [0, 55, 70, 80, 200],
                                            labels=["<55", "55-70", "70-80", "80+"]))
display(subgroup_report(mixed_by_age, p_mixed, "age_band").round(4))
"""
    )

    nb.code(
        """
fig, ax = plt.subplots()
for value in [0, 1]:
    mask = (mixed["group"] == value).to_numpy()
    tab = calibration_table(mixed["outcome"].to_numpy()[mask], p_mixed[mask], n_bins=6)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", lw=2, label=f"group = {value}")
ax.plot([0, 0.5], [0, 0.5], ls="--", c="0.4", label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("One ward, two very different models")
ax.legend()
plt.show()
"""
    )

    nb.md(
        """
For one subgroup the model discriminates respectably. For the other it is close to
a coin flip and understates risk throughout. The whole-ward AUROC sits between
them and describes neither.

Note what is *not* the problem here. The subgroup's covariate distribution is
fine - a shift report finds nothing. What differs is the conditional relationship
between labs and outcome, and 640 training patients could never have identified
it. This is a sample-size problem masquerading as a fairness problem, and it is
the case for the next section.

**Always report stratified.** By every categorical column you were given, by age
band, and by whether key labs were recorded. If a stratum is too small to
evaluate, that is itself the finding.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 6. Hierarchical models: borrowing strength

Four hospitals report deterioration rates. One of them saw four patients and one
event.
"""
    )

    nb.code(
        """
sites = pd.DataFrame({
    "site": ["Large teaching", "District general", "Rural", "New unit"],
    "events": [210, 42, 8, 1],
    "patients": [1000, 180, 30, 4],
})
sites["raw_rate"] = sites["events"] / sites["patients"]

# Empirical-Bayes prior: method of moments on the observed site rates.
grand_mean = sites["events"].sum() / sites["patients"].sum()
concentration = 40.0
prior_a, prior_b = grand_mean * concentration, (1 - grand_mean) * concentration

sites["pooled"] = (sites["events"] + prior_a) / (sites["patients"] + prior_a + prior_b)
sites["shrinkage"] = 1 - (sites["pooled"] - grand_mean) / (sites["raw_rate"] - grand_mean)

from scipy.stats import beta as beta_dist
post_a = sites["events"] + prior_a
post_b = sites["patients"] - sites["events"] + prior_b
sites["ci_low"] = beta_dist.ppf(0.025, post_a, post_b)
sites["ci_high"] = beta_dist.ppf(0.975, post_a, post_b)
display(sites.round(3))

fig, ax = plt.subplots()
x = np.arange(len(sites))
ax.errorbar(x - 0.08, sites["raw_rate"], fmt="o", ms=9, label="Raw site estimate")
ax.errorbar(x + 0.08, sites["pooled"],
            yerr=[sites["pooled"] - sites["ci_low"], sites["ci_high"] - sites["pooled"]],
            fmt="s", ms=9, capsize=4, label="Partially pooled (95% interval)")
ax.axhline(grand_mean, ls="--", c="0.4", label="Pooled across all sites")
ax.set_xticks(x)
ax.set_xticklabels(sites["site"], rotation=15)
ax.set_ylabel("Estimated deterioration rate")
ax.set_title("Small hospitals are pulled toward the shared prior")
ax.legend()
plt.show()
"""
    )

    nb.md(
        """
The new unit's raw rate is 25%. Its partially pooled estimate is close to the
group average, with an interval wide enough to be honest about four patients.

The shrinkage column shows the mechanism: the large teaching hospital is barely
moved, the new unit almost entirely. **The amount of pooling is determined by the
data, not chosen.** That is what makes hierarchical modelling different from
either extreme - fitting each site separately (no pooling, and the new unit gets
a 25% rate) or fitting one model for all sites (complete pooling, and site
differences vanish).

This is the principled answer to section 5's subgroup problem: give the small
subgroup its own parameters, and let the data decide how far to shrink them.

`03_hierarchical_pymc.ipynb` builds the full model in PyMC, with site-level
intercepts and slopes, and shows what the posterior over the group-level
variance is telling you.
"""
    )

    nb.note(
        "The concentration parameter is set by hand here, which is exactly what a "
        "real hierarchical model estimates. Say that plainly rather than hiding "
        "it - it motivates the PyMC notebook."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 7. When the model is a simulator

Everything so far fits a function to recorded data. Sometimes you have something
better: a mechanistic model of how the data came about, with parameters that mean
something clinically. Transmission rates, progression rates, an intervention
effect.

You can simulate from it and you cannot write down its likelihood. Simulation-based
inference is how you get a posterior anyway. The simplest version accepts the
parameters that produced data resembling what you saw.
"""
    )

    nb.code(
        """
def ward_simulator(theta, n_patients=600, seed=None):
    sim_rng = np.random.default_rng(seed)
    age = np.clip(sim_rng.normal(65, 14, n_patients), 18, 95)
    p = expit(-4.3 + 0.04 * age + theta)
    events = sim_rng.binomial(1, p)
    return np.array([events.mean(), events[age > 70].mean()])


theta_true = 0.55
observed = ward_simulator(theta_true, n_patients=600, seed=123)
print(f"observed summaries: overall rate {observed[0]:.3f}, rate over 70 {observed[1]:.3f}")

n_sims = 12000
theta_prior = rng.uniform(-2.0, 2.0, n_sims)
simulated = np.array([ward_simulator(t, 600, seed=5000 + i) for i, t in enumerate(theta_prior)])

scale = simulated.std(axis=0)
distance = np.linalg.norm((simulated - observed) / scale, axis=1)
accepted = theta_prior[distance <= np.quantile(distance, 0.02)]

plt.hist(theta_prior, bins=50, density=True, alpha=0.3, label="Prior")
plt.hist(accepted, bins=30, density=True, alpha=0.7, label="ABC posterior")
plt.axvline(theta_true, ls="--", c="0.2", label="True value")
plt.xlabel("Latent ward-level risk parameter")
plt.ylabel("Density")
plt.title("A posterior without a likelihood")
plt.legend()
plt.show()

print(f"posterior mean {accepted.mean():.3f}   "
      f"95% interval [{np.quantile(accepted, 0.025):.3f}, {np.quantile(accepted, 0.975):.3f}]   "
      f"from {len(accepted)} accepted of {n_sims} simulations")
"""
    )

    nb.md(
        """
That took 12,000 simulations to keep 240, and the acceptance rate would collapse
if `theta` had five dimensions instead of one. That inefficiency is precisely what
neural SBI fixes: train a density estimator on the simulations so that every one
of them contributes, and the posterior for a new observation comes out without
rerunning the simulator at all.

`04_simulation_based_inference.ipynb` does that with the `sbi` package and
compares it directly against this rejection sampler.

**Why a clinical audience should care.** The parameters of a mechanistic model are
things a clinician can argue with - a progression rate, an effect size - and a
posterior over them is a statement about the world rather than about a fitted
function. When you need to reason about an intervention that is not in your
historical data, this is the tool that still works.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## What to take away

1. Recalibration is cheap, effective and needs labelled patients from the new
   site. Match the flexibility of the fix to the labels you can actually get.
2. Ensemble disagreement is a usable epistemic signal that needs no outcome data,
   which makes it the check you can run on day one.
3. Epistemic and aleatoric uncertainty do different jobs in an abstention rule.
   Do not average them into one score.
4. The operating threshold comes from the cost ratio, not from 0.5, and it is
   usually far lower than people expect.
5. Report every metric stratified. If a stratum is too small to evaluate, say so.
6. Partial pooling lets the data decide how much a small site or subgroup should
   borrow from everyone else.
7. When you have a simulator, you can have a posterior over parameters that mean
   something, with no likelihood.

---
## Your project

You now have every tool the project needs. Each team gets development data and
deployment data from one hospital, and each hospital hides a different reason the
model should not be trusted.

Read `project/PROJECT_BRIEF.md` and start from
`notebooks/90_team_project_starter.ipynb`.

The task is not to raise AUROC. It is to work out what is wrong, who it is wrong
for, and what the model should do about it.
"""
    )

    return nb


if __name__ == "__main__":
    paths = build().write(ROOT / "notebooks", "02_lecture2_trustworthy_deployment")
    for path in paths:
        print("wrote", path.relative_to(ROOT))
