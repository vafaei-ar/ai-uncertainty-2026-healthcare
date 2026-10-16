"""Render the lecture slide figures.

Same computations as the notebooks, same seeds, restyled for projection:
larger type, thicker marks, and a validated four-colour categorical palette.

    python slides/make_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import beta as beta_dist
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from medsim import (  # noqa: E402
    FEATURES, SimConfig, calibration_table, selective_risk_curve,
    shift_report, simulate_ehr, train_val_split,
)

OUT = ROOT / "slides" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Validated categorical palette (six-check pass, light and dark surfaces).
C = ["#2E74B5", "#DD5A22", "#0E8F6E", "#9C4BA0"]
INK = "#13293D"
MUTED = "#7C8794"

plt.rcParams.update({
    "figure.figsize": (8.2, 4.6),
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "font.size": 14,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 15,
    "axes.labelsize": 14,
    "axes.labelcolor": INK,
    "axes.edgecolor": MUTED,
    "axes.titlecolor": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DCE1E6",
    "grid.linewidth": 0.9,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "legend.frameon": False,
    "lines.linewidth": 2.6,
    "lines.markersize": 8,
})


def save(fig, name):
    # Every figure slide carries its own heading, so a single-panel figure would
    # otherwise show the same sentence twice. Multi-panel titles stay: they label
    # the panels, not the slide.
    if len(fig.axes) == 1:
        fig.axes[0].set_title("")
    path = OUT / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    print("  ", path.name)
    return path


def fit(train_df, features=FEATURES):
    return make_pipeline(
        SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)
    ).fit(train_df[features], train_df["outcome"])


# ----------------------------------------------------------------------
print("lecture 1")
rng = np.random.default_rng(20261116)

# 1. Prior to posterior, and the effect of evidence
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.2))
grid = np.linspace(0, 1, 500)
axes[0].plot(grid, beta_dist.pdf(grid, 2, 2), color=MUTED, label="Prior")
axes[0].plot(grid, beta_dist.pdf(grid, 10, 4), color=C[0], label="Posterior, 10 alerts")
axes[0].axvline(0.8, ls=":", color=C[1], lw=2.2, label="Point estimate 0.80")
axes[0].set_xlabel("P(alert is clinically useful)")
axes[0].set_ylabel("Density")
axes[0].set_title("Ten observations do not settle it")
axes[0].legend(fontsize=11)

for colour, n in zip(C, [10, 50, 200, 1000]):
    a, b = 2 + 0.8 * n, 2 + 0.2 * n
    axes[1].plot(grid, beta_dist.pdf(grid, a, b), color=colour, label=f"n = {n}")
axes[1].set_xlim(0.5, 1.0)
axes[1].set_xlabel("P(alert is clinically useful)")
axes[1].set_title("Same 80%, four states of knowledge")
axes[1].legend(fontsize=11)
fig.tight_layout()
save(fig, "l1_posterior")

# 2. Same AUROC, different calibration
n = 6000
latent = rng.normal(0, 1.1, n)
p_true = expit(latent - 1.95)
y = rng.binomial(1, p_true)
p_honest = np.clip(p_true + rng.normal(0, 0.02, n), 1e-4, 1 - 1e-4)
variants = {
    "Honest": p_honest,
    "Overconfident": expit(2.4 * logit(p_honest)),
    "Timid": expit(0.45 * logit(p_honest)),
}
fig, ax = plt.subplots()
for colour, (name, pred) in zip(C, variants.items()):
    tab = calibration_table(y, pred, n_bins=10)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", color=colour,
            label=f"{name}  (AUROC {roc_auc_score(y, pred):.3f})")
ax.plot([0, 0.75], [0, 0.75], ls="--", color=MUTED, lw=2, label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("Identical AUROC, three different claims about the world")
ax.legend(fontsize=11)
save(fig, "l1_calibration")

# 3. Epistemic shrinks with data, aleatoric does not
records = []
for n_train in [250, 1000, 4000, 16000]:
    boot = np.random.default_rng(n_train)
    tr = simulate_ehr(SimConfig(n=n_train, seed=n_train + 1))
    ev = simulate_ehr(SimConfig(n=1500, seed=999))
    imp = SimpleImputer(strategy="median").fit(tr[FEATURES])
    sc = StandardScaler().fit(imp.transform(tr[FEATURES]))
    xtr, xev = sc.transform(imp.transform(tr[FEATURES])), sc.transform(imp.transform(ev[FEATURES]))
    ytr = tr["outcome"].to_numpy()
    preds = []
    for _ in range(50):
        idx = boot.integers(0, len(ytr), len(ytr))
        preds.append(LogisticRegression(max_iter=3000).fit(xtr[idx], ytr[idx]).predict_proba(xev)[:, 1])
    preds = np.vstack(preds)
    m = preds.mean(axis=0)
    records.append({"n": n_train, "epistemic": preds.std(axis=0).mean(),
                    "aleatoric": np.sqrt(m * (1 - m)).mean()})
frame = pd.DataFrame(records)

fig, ax = plt.subplots()
ax.plot(frame["n"], frame["epistemic"], marker="o", color=C[0], label="Bootstrap spread (epistemic proxy)")
ax.plot(frame["n"], frame["aleatoric"], marker="s", color=C[1], label="Aleatoric term (outcome noise)")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Training patients")
ax.set_ylabel("Mean uncertainty")
ax.set_title("More data removes one of these, not the other")
ax.legend(fontsize=12)
save(fig, "l1_epistemic")

# 4. The aleatoric ceiling
truth = simulate_ehr(SimConfig(n=20000, seed=77), keep_truth=True)
tr_t, te_t = train_val_split(truth, 0.4, seed=3)
model_t = fit(tr_t)
bars = {
    "Our fitted\nmodel": roc_auc_score(te_t["outcome"], model_t.predict_proba(te_t[FEATURES])[:, 1]),
    "Ceiling on the\nrecorded columns": roc_auc_score(
        te_t["outcome"], expit(te_t["latent"] - 0.70 * te_t["concern"])),
    "Oracle including the\nunrecorded impression": roc_auc_score(te_t["outcome"], te_t["true_p"]),
}
fig, ax = plt.subplots(figsize=(8.2, 4.2))
positions = np.arange(len(bars))
ax.bar(positions, list(bars.values()), color=[C[0], C[2], C[1]], width=0.55)
for pos, value in zip(positions, bars.values()):
    ax.text(pos, value + 0.008, f"{value:.3f}", ha="center", fontsize=15, color=INK, fontweight="bold")
ax.set_xticks(positions)
ax.set_xticklabels(bars.keys(), fontsize=11.5)
ax.set_ylim(0.5, 0.86)
ax.set_ylabel("AUROC")
ax.set_title("The gap to a perfect model was never in your columns")
ax.grid(axis="x", visible=False)
save(fig, "l1_ceiling")

# 5-6. Two hospitals, two very different failures
development = simulate_ehr(SimConfig(n=8000, site="A", seed=11))
train, validation = train_val_split(development, 0.3, seed=5)
model = fit(train)
predict = lambda df: model.predict_proba(df[FEATURES])[:, 1]
site_b = simulate_ehr(SimConfig(n=5000, site="B", prevalence_shift=0.5, seed=21))
site_c = simulate_ehr(SimConfig(n=5000, site="A", measurement_noise=2.8, seed=22))

fig, ax = plt.subplots()
for colour, (name, data) in zip(C, [("Site A (development)", validation),
                                    ("Site B (higher baseline risk)", site_b),
                                    ("Site C (noisier instruments)", site_c)]):
    tab = calibration_table(data["outcome"], predict(data), n_bins=8)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", color=colour, label=name)
ax.plot([0, 0.55], [0, 0.55], ls="--", color=MUTED, lw=2, label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("A model that transfers its ranking but not its numbers")
ax.legend(fontsize=11)
save(fig, "l1_shift_calibration")

continuous = ["age", "heart_rate", "systolic_bp", "respiratory_rate", "creatinine", "lactate", "wbc"]
sb = shift_report(train, site_b, continuous).set_index("feature")["std_mean_diff"]
sc_ = shift_report(train, site_c, continuous).set_index("feature")["std_mean_diff"]
order = sc_.abs().sort_values().index
fig, ax = plt.subplots(figsize=(8.6, 4.4))
positions = np.arange(len(order))
ax.barh(positions - 0.2, sb.reindex(order).abs(), height=0.38, color=C[0], label="Site B (conditional shift)")
ax.barh(positions + 0.2, sc_.reindex(order).abs(), height=0.38, color=C[1], label="Site C (instrument drift)")
ax.axvline(0.1, ls=":", color=MUTED, lw=2)
ax.set_yticks(positions)
ax.set_yticklabels(order, fontsize=12)
ax.set_xlabel("|standardised mean difference| vs development")
ax.set_title("Input monitoring detects only some changes")
ax.grid(axis="y", visible=False)
ax.legend(fontsize=11, loc="lower right")
save(fig, "l1_shift_detection")

# 7. Missingness carries information
mnar = simulate_ehr(SimConfig(n=8000, missingness_strength=1.4, seed=31))
mnar_train, _ = train_val_split(mnar, 0.35, seed=6)
observed = mnar[mnar["creatinine"].notna()]["outcome"].mean()
absent = mnar[mnar["creatinine"].isna()]["outcome"].mean()
complete = mnar_train.dropna(subset=FEATURES)

top = max(observed, absent, mnar_train["outcome"].mean(), complete["outcome"].mean()) * 1.30

fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.2), sharey=True)
axes[0].set_ylim(0, top)
axes[0].bar(["Creatinine\nrecorded", "Creatinine\nnot recorded"], [observed, absent],
            color=[C[0], C[1]], width=0.5)
for i, v in enumerate([observed, absent]):
    axes[0].text(i, v + 0.004, f"{v:.3f}", ha="center", fontsize=15, color=INK, fontweight="bold")
axes[0].set_ylabel("Observed deterioration rate")
axes[0].set_title("A blank cell is a\nclinical judgement")
axes[0].grid(axis="x", visible=False)

axes[1].bar(["Full cohort", "Complete cases\nonly"],
            [mnar_train["outcome"].mean(), complete["outcome"].mean()],
            color=[C[0], C[1]], width=0.5)
for i, v in enumerate([mnar_train["outcome"].mean(), complete["outcome"].mean()]):
    axes[1].text(i, v + 0.004, f"{v:.3f}", ha="center", fontsize=15, color=INK, fontweight="bold")
axes[1].set_title(f"Dropping incomplete rows keeps {len(complete) / len(mnar_train):.0%},\nand selects the sickest")
axes[1].grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "l1_missingness")

# ----------------------------------------------------------------------
print("lecture 2")
rng = np.random.default_rng(20261117)
site_b6 = simulate_ehr(SimConfig(n=6000, site="B", prevalence_shift=0.5, seed=21))
calib_set, test_set = train_val_split(site_b6, 0.6, seed=9)
p_calib, p_test = predict(calib_set), predict(test_set)
y_calib, y_test = calib_set["outcome"].to_numpy(), test_set["outcome"].to_numpy()


def intercept_correction(pc, yc):
    m = LogisticRegression(max_iter=1000).fit(np.zeros((len(yc), 1)), yc)
    off = float(m.intercept_[0]) - float(np.mean(logit(np.clip(pc, 1e-6, 1 - 1e-6))))
    return lambda p: expit(logit(np.clip(p, 1e-6, 1 - 1e-6)) + off)


def platt(pc, yc):
    z = logit(np.clip(pc, 1e-6, 1 - 1e-6)).reshape(-1, 1)
    m = LogisticRegression(max_iter=1000).fit(z, yc)
    a, b = float(m.coef_[0][0]), float(m.intercept_[0])
    return lambda p: expit(a * logit(np.clip(p, 1e-6, 1 - 1e-6)) + b)


def isotonic(pc, yc):
    m = IsotonicRegression(out_of_bounds="clip").fit(pc, yc)
    return lambda p: np.clip(m.predict(p), 1e-6, 1 - 1e-6)


repairs = {"Uncorrected": lambda p: p,
           "Intercept correction": intercept_correction(p_calib, y_calib),
           "Platt scaling": platt(p_calib, y_calib),
           "Isotonic": isotonic(p_calib, y_calib)}

fig, ax = plt.subplots()
for colour, (name, fn) in zip(C, repairs.items()):
    tab = calibration_table(y_test, fn(p_test), n_bins=8)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", color=colour,
            label=f"{name}  (Brier {brier_score_loss(y_test, fn(p_test)):.3f})")
ax.plot([0, 0.7], [0, 0.7], ls="--", color=MUTED, lw=2, label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title("One parameter fixes most of it")
ax.legend(fontsize=11)
save(fig, "l2_recalibration")

rows = []
for n_calib in [25, 50, 100, 200, 400, 800, 1600]:
    for repeat in range(40):
        boot = np.random.default_rng(1000 * repeat + n_calib)
        sub = calib_set.iloc[boot.choice(len(calib_set), n_calib, replace=False)]
        ps, ys = predict(sub), sub["outcome"].to_numpy()
        if len(np.unique(ys)) < 2:
            continue
        for name, factory in [("Intercept", intercept_correction), ("Platt", platt), ("Isotonic", isotonic)]:
            rows.append({"n": n_calib, "method": name,
                         "brier": brier_score_loss(y_test, factory(ps, ys)(p_test))})
curve = pd.DataFrame(rows).groupby(["method", "n"])["brier"].median().reset_index()
fig, ax = plt.subplots()
for colour, (name, part) in zip(C, curve.groupby("method")):
    ax.plot(part["n"], part["brier"], marker="o", color=colour, label=name)
ax.axhline(brier_score_loss(y_test, p_test), ls="--", color=MUTED, lw=2, label="No correction")
ax.set_xscale("log")
ax.set_xlabel("Labelled patients from the new site")
ax.set_ylabel("Brier on held-out deployment data")
ax.set_title("Match the flexibility of the fix to the labels you can get")
ax.legend(fontsize=11)
save(fig, "l2_calibration_cost")

# Ensemble disagreement and OOD
ood = simulate_ehr(SimConfig(n=6000, site="A", ood_fraction=0.30, seed=41), keep_truth=True)
imp = SimpleImputer(strategy="median").fit(train[FEATURES])
sc2 = StandardScaler().fit(imp.transform(train[FEATURES]))
xtr = sc2.transform(imp.transform(train[FEATURES]))
xva = sc2.transform(imp.transform(validation[FEATURES]))
xood = sc2.transform(imp.transform(ood[FEATURES]))
ytr = train["outcome"].to_numpy()
boot = np.random.default_rng(0)
pv, po = [], []
for _ in range(60):
    idx = boot.integers(0, len(ytr), len(ytr))
    m = LogisticRegression(max_iter=3000).fit(xtr[idx], ytr[idx])
    pv.append(m.predict_proba(xva)[:, 1])
    po.append(m.predict_proba(xood)[:, 1])
pv, po = np.vstack(pv), np.vstack(po)
sd_val, sd_ood, mean_ood = pv.std(axis=0), po.std(axis=0), po.mean(axis=0)
is_ood = ood["is_ood"].to_numpy() == 1

fig, ax = plt.subplots()
ax.scatter(mean_ood[~is_ood], sd_ood[~is_ood], s=9, alpha=0.30, color=C[0],
           label="Seen in development")
ax.scatter(mean_ood[is_ood], sd_ood[is_ood], s=9, alpha=0.45, color=C[1],
           label="Unlike anything in development")
threshold = np.quantile(sd_val, 0.95)
ax.axhline(threshold, ls="--", color=INK, lw=2)
ax.set_xlim(-0.03, 1.12)
ax.set_ylim(0, float(max(sd_ood.max(), sd_val.max())) * 1.32)
ax.set_xlabel("Mean predicted risk")
ax.set_ylabel("Ensemble disagreement")
ax.set_title("In this simulation, disagreement flags unfamiliar patients")
ax.legend(fontsize=12, markerscale=2.4, loc="upper left")
save(fig, "l2_ensemble_ood")

flagged = sd_ood > threshold
print(f"    flagged {flagged.mean():.1%}, precision {is_ood[flagged].mean():.1%}, "
      f"recall {flagged[is_ood].mean():.1%}")

# Risk-coverage
y_ood = ood["outcome"]
rankings = {"Ensemble disagreement (proxy)": sd_ood,
            "Distance from 0.5 (aleatoric)": -np.abs(mean_ood - 0.5),
            "Random deferral": rng.random(len(mean_ood))}
fig, ax = plt.subplots()
for colour, (name, unc) in zip(C, rankings.items()):
    cv = selective_risk_curve(y_ood, mean_ood, unc, decision_threshold=0.30)
    ax.plot(cv["coverage"], cv["error_rate"], marker="o", ms=5, color=colour, label=name)
ax.set_xlabel("Coverage (fraction the model still answers for)")
ax.set_ylabel("Error rate among retained patients")
ax.set_title("Does the model know what it does not know?")
ax.legend(fontsize=11)
save(fig, "l2_risk_coverage")

# Net benefit
def net_benefit(yt, yp, ts):
    yt = np.asarray(yt)
    return np.array([np.sum((yp >= t) & (yt == 1)) / len(yt)
                     - np.sum((yp >= t) & (yt == 0)) / len(yt) * (t / (1 - t)) for t in ts])

ts = np.linspace(0.02, 0.60, 60)
prevalence = y_test.mean()
fig, ax = plt.subplots()
ax.plot(ts, net_benefit(y_test, p_test, ts), color=C[1], label="Uncorrected model")
ax.plot(ts, net_benefit(y_test, repairs["Intercept correction"](p_test), ts), color=C[0],
        label="Recalibrated model")
ax.plot(ts, prevalence - (1 - prevalence) * (ts / (1 - ts)), ls="--", color=MUTED,
        label="Escalate everyone")
ax.axhline(0, ls=":", color=MUTED, lw=2)
ax.axvline(1 / 11, ls=":", color=C[3], lw=2.4)
ax.text(1 / 11 + 0.012, 0.268, "10:1 cost ratio\nputs you here", fontsize=11.5, color=C[3], va="top")
ax.set_ylim(-0.06, 0.33)
ax.set_xlabel("Decision threshold  =  1 / (1 + cost ratio)")
ax.set_ylabel("Net benefit")
ax.set_title("Is the model better than what we would do without it?")
ax.legend(fontsize=11.5, loc="upper right")
save(fig, "l2_net_benefit")

# Subgroup
mixed = simulate_ehr(SimConfig(n=8000, site="A", subgroup_prevalence=0.40, subgroup_shift=1.0,
                               subgroup_interaction=-1.8, seed=51))
sparse = simulate_ehr(SimConfig(n=8000, site="A", subgroup_prevalence=0.08, subgroup_shift=1.0,
                                subgroup_interaction=-1.8, seed=52))
sparse_model = fit(sparse)
p_mixed = sparse_model.predict_proba(mixed[FEATURES])[:, 1]
fig, ax = plt.subplots()
labels = {0: "Majority group", 1: "Minority group (8% of development data)"}
for colour, value in zip(C, [0, 1]):
    mask = (mixed["group"] == value).to_numpy()
    auroc = roc_auc_score(mixed["outcome"].to_numpy()[mask], p_mixed[mask])
    tab = calibration_table(mixed["outcome"].to_numpy()[mask], p_mixed[mask], n_bins=6)
    ax.plot(tab["mean_predicted"], tab["observed_rate"], marker="o", color=colour,
            label=f"{labels[value]}  (AUROC {auroc:.2f})")
overall = roc_auc_score(mixed["outcome"], p_mixed)
ax.plot([0, 0.42], [0, 0.42], ls="--", color=MUTED, lw=2, label="Perfect calibration")
ax.set_xlabel("Predicted risk")
ax.set_ylabel("Observed event rate")
ax.set_title(f"Whole-ward AUROC {overall:.2f} describes neither group")
ax.legend(fontsize=11)
save(fig, "l2_subgroup")

# Partial pooling
sites = pd.DataFrame({"site": ["Large\nteaching", "District\ngeneral", "Rural", "New\nunit"],
                      "events": [210, 42, 8, 1], "patients": [1000, 180, 30, 4]})
sites["raw"] = sites["events"] / sites["patients"]
grand = sites["events"].sum() / sites["patients"].sum()
a0, b0 = grand * 40, (1 - grand) * 40
post_a, post_b = sites["events"] + a0, sites["patients"] - sites["events"] + b0
sites["pooled"] = post_a / (post_a + post_b)
lo = beta_dist.ppf(0.025, post_a, post_b)
hi = beta_dist.ppf(0.975, post_a, post_b)

fig, ax = plt.subplots()
x = np.arange(len(sites))
ax.scatter(x - 0.1, sites["raw"], s=140, color=C[1], zorder=3, label="Raw site estimate")
ax.errorbar(x + 0.1, sites["pooled"],
            yerr=[sites["pooled"] - lo, hi - sites["pooled"]],
            fmt="s", ms=11, color=C[0], capsize=6, lw=2.4, zorder=3,
            label="Partially pooled (95% interval)")
ax.axhline(grand, ls="--", color=MUTED, lw=2, label="Network average")
ax.set_xticks(x)
ax.set_xticklabels(sites["site"], fontsize=12)
ax.set_ylim(0, float(hi.max()) * 1.15)
ax.set_ylabel("Estimated deterioration rate")
ax.set_title("How far each site is pulled is estimated, not chosen")
ax.grid(axis="x", visible=False)
ax.legend(fontsize=11)
save(fig, "l2_pooling")

print("done")
