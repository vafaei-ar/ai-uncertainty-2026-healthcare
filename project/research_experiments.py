"""Reproducible, synthetic hospital-transfer method comparison.

Research question: with few labeled admissions from a new hospital, when does
simple recalibration improve probability reliability relative to no adaptation?

All outcomes come from the transparent synthetic simulator. Target evaluation
outcomes are generated independently from the target calibration pool. Never
interpret these findings as clinical validation or a publishable novelty claim.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import expit, logit
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from medsim import FEATURES, SimConfig, simulate_ehr
from medsim.metrics import expected_calibration_error

# Each mechanism is varied alone so that differences have a clear interpretation.
# "Hospital B" is a scenario label, not a claim that sites share any real data.
SCENARIOS = {
    "negative_control": {},
    "baseline_risk": {"prevalence_shift": 0.85},
    "measurement_noise": {"measurement_noise": 2.5},
    "subgroup_interaction": {"subgroup_interaction": -1.4},
    "informative_missingness": {"missingness_strength": 1.5},
}
METHODS = ("unchanged", "intercept", "platt")
DEFAULT_BUDGETS = (25, 75, 150)


def _risk_model(source: pd.DataFrame):
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=3000, random_state=0),
    )
    return model.fit(source[FEATURES], source["outcome"])


def _bounded_logit(p):
    return logit(np.clip(np.asarray(p, dtype=float), 1e-5, 1 - 1e-5))


def _intercept_recalibration(p_audit, y_audit, p_test):
    """Fit only a log-odds intercept, with weak L2 regularization."""
    z = _bounded_logit(p_audit)
    y = np.asarray(y_audit, dtype=float)

    def objective(b):
        pred = np.clip(expit(z + b), 1e-7, 1 - 1e-7)
        return -np.mean(y * np.log(pred) + (1 - y) * np.log(1 - pred)) + 0.01 * b * b

    fit = minimize_scalar(objective, bounds=(-5.0, 5.0), method="bounded")
    if not fit.success:
        raise RuntimeError("Intercept-only recalibration did not converge.")
    return expit(_bounded_logit(p_test) + float(fit.x))


def _platt_recalibration(p_audit, y_audit, p_test):
    """Fit logistic slope and intercept. A one-class audit is not estimable."""
    labels = np.asarray(y_audit, dtype=int)
    if np.unique(labels).size < 2:
        return np.asarray(p_test, dtype=float), False
    fit = LogisticRegression(C=1.0, max_iter=2000, random_state=0)
    fit.fit(_bounded_logit(p_audit).reshape(-1, 1), labels)
    return fit.predict_proba(_bounded_logit(p_test).reshape(-1, 1))[:, 1], True


def _metrics(y, p, group):
    y = np.asarray(y, dtype=int)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    group = np.asarray(group)
    subgroup_abs_gaps = []
    for value in np.unique(group):
        mask = group == value
        if mask.sum() >= 30:
            subgroup_abs_gaps.append(abs(float(p[mask].mean() - y[mask].mean())))
    return {
        "brier": float(brier_score_loss(y, p)),
        "auroc": float(roc_auc_score(y, p)) if np.unique(y).size == 2 else np.nan,
        "ece": float(expected_calibration_error(y, p)),
        "calibration_in_large_gap": float(p.mean() - y.mean()),
        # A descriptive stratified calibration gap, NOT a fairness/safety guarantee.
        "worst_group_abs_mean_gap": max(subgroup_abs_gaps, default=np.nan),
    }


def run_grid(
    repeats: int = 8,
    label_budgets=DEFAULT_BUDGETS,
    source_size: int = 4000,
    target_pool_size: int = 1600,
    test_size: int = 2400,
    seed: int = 2026,
):
    """Run paired, independent-test comparisons across scenario and label budget.

    Each replicate trains once on a fresh source cohort, draws independent
    target calibration and test cohorts, and samples nested random audits.
    Test outcomes are never passed to any fitting or recalibration function.
    """
    label_budgets = tuple(sorted({int(n) for n in label_budgets}))
    if repeats < 1 or not label_budgets or min(label_budgets) < 10:
        raise ValueError("Use >=1 replicate and label budgets of at least 10.")
    if max(label_budgets) > target_pool_size:
        raise ValueError("The largest audit cannot exceed the target calibration pool.")
    if min(source_size, test_size) < 100:
        raise ValueError("Source and independent test sizes must be at least 100.")

    rows = []
    for replicate in range(repeats):
        source = simulate_ehr(
            SimConfig(n=source_size, site="A", seed=seed + 10000 * replicate + 1)
        )
        model = _risk_model(source)
        for scenario_id, (scenario, kwargs) in enumerate(SCENARIOS.items()):
            base = seed + 10000 * replicate + 200 * (scenario_id + 1)
            calibration_pool = simulate_ehr(
                SimConfig(n=target_pool_size, site="A", seed=base + 1, **kwargs)
            )
            independent_test = simulate_ehr(
                SimConfig(n=test_size, site="A", seed=base + 2, **kwargs)
            )
            rng = np.random.default_rng(base + 3)
            audit_order = rng.permutation(target_pool_size)
            p_pool = model.predict_proba(calibration_pool[FEATURES])[:, 1]
            p_test = model.predict_proba(independent_test[FEATURES])[:, 1]
            y_test = independent_test["outcome"].to_numpy()
            group_test = independent_test["group"].to_numpy()
            for budget in label_budgets:
                indices = audit_order[:budget]
                y_audit = calibration_pool["outcome"].to_numpy()[indices]
                predictions = {
                    "unchanged": (p_test, True),
                    "intercept": (_intercept_recalibration(p_pool[indices], y_audit, p_test), True),
                    "platt": _platt_recalibration(p_pool[indices], y_audit, p_test),
                }
                for method, (predicted, fitted) in predictions.items():
                    rows.append({
                        "replicate": replicate,
                        "scenario": scenario,
                        "labels": budget,
                        "method": method,
                        "method_estimable": bool(fitted),
                        "audit_events": int(y_audit.sum()),
                        "n_test": int(len(y_test)),
                        **_metrics(y_test, predicted, group_test),
                    })
    frame = pd.DataFrame(rows)
    expected = repeats * len(SCENARIOS) * len(label_budgets) * len(METHODS)
    assert len(frame) == expected
    return frame


def summarize_results(frame: pd.DataFrame) -> pd.DataFrame:
    """Paired Brier differences: negative favors adaptation.

    The 10th/90th percentiles describe variation across simulated replicates.
    They are not confidence intervals and should not be called such.
    """
    wide = frame.pivot(
        index=["scenario", "labels", "replicate"], columns="method", values="brier"
    )
    reports = []
    for method in ("intercept", "platt"):
        contrast = (wide[method] - wide["unchanged"]).reset_index(name="delta_brier")
        for (scenario, labels), g in contrast.groupby(["scenario", "labels"], sort=True):
            d = g["delta_brier"].to_numpy()
            reports.append({
                "scenario": scenario,
                "labels": int(labels),
                "method": method,
                "replicates": int(len(d)),
                "mean_delta_brier": float(d.mean()),
                "p10_delta_brier": float(np.quantile(d, 0.1)),
                "p90_delta_brier": float(np.quantile(d, 0.9)),
                "fraction_replicates_improved": float(np.mean(d < 0)),
            })
    return pd.DataFrame(reports)


def plot_comparison(summary: pd.DataFrame, path: Path):
    """A single, transparent visual comparing paired Brier changes."""
    fig, ax = plt.subplots(figsize=(9, 5.6))
    scenario_names = list(SCENARIOS)
    x = np.arange(len(scenario_names))
    styles = {"intercept": ("o", "-"), "platt": ("s", "--")}
    budgets = sorted(summary["labels"].unique())
    # Keep one figure focused: show the middle available budget if there are >1.
    budget = budgets[len(budgets) // 2]
    for method, (marker, linestyle) in styles.items():
        subset = summary[(summary["method"] == method) & (summary["labels"] == budget)]
        ordered = subset.set_index("scenario").reindex(scenario_names)
        ax.plot(x, ordered["mean_delta_brier"], linestyle=linestyle, marker=marker, linewidth=2,
                label=method.capitalize())
    ax.axhline(0, color="black", linewidth=1, linestyle=":")
    ax.set_xticks(x, ["No shift", "Risk shift", "Measurement", "Subgroup", "Missingness"], rotation=10)
    ax.set_ylabel("Mean Brier change vs. unchanged model (lower is better)")
    ax.set_xlabel("Synthetic target-hospital condition")
    ax.set_title(f"Recalibration with {budget} audited outcomes")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--source-size", type=int, default=4000)
    parser.add_argument("--test-size", type=int, default=2400)
    parser.add_argument("--output-dir", type=Path, default=Path("project/results"))
    args = parser.parse_args()
    results = run_grid(
        repeats=args.repeats, seed=args.seed, source_size=args.source_size,
        test_size=args.test_size,
    )
    summary = summarize_results(results)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "method_results.csv", index=False)
    summary.to_csv(args.output_dir / "paired_summary.csv", index=False)
    plot_comparison(summary, args.output_dir / "brier_comparison.png")
    print(summary.round(4).to_string(index=False))
    print(f"Saved reproducible results in {args.output_dir}")


if __name__ == "__main__":
    main()
