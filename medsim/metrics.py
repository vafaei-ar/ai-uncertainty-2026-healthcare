"""Evaluation helpers for the healthcare uncertainty module.

Everything here answers a question a clinician would actually ask: do the
numbers mean what they claim, for whom do they stop meaning it, and what
happens if the model is allowed to say "I don't know".
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score


def expected_calibration_error(y_true, y_prob, n_bins: int = 10, strategy: str = "quantile") -> float:
    """Average gap between predicted risk and observed event rate, weighted by bin size."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)

    if strategy == "quantile":
        edges = np.unique(np.quantile(y_prob, np.linspace(0, 1, n_bins + 1)))
    else:
        edges = np.linspace(0, 1, n_bins + 1)
    if len(edges) < 3:
        return float(abs(y_prob.mean() - y_true.mean()))

    idx = np.clip(np.digitize(y_prob, edges[1:-1], right=True), 0, len(edges) - 2)
    error = 0.0
    for b in range(len(edges) - 1):
        mask = idx == b
        if mask.sum() == 0:
            continue
        error += mask.mean() * abs(y_prob[mask].mean() - y_true[mask].mean())
    return float(error)


def calibration_table(y_true, y_prob, n_bins: int = 10) -> pd.DataFrame:
    """Risk decile table: the format a clinical reviewer will ask for."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    edges = np.unique(np.quantile(y_prob, np.linspace(0, 1, n_bins + 1)))
    idx = np.clip(np.digitize(y_prob, edges[1:-1], right=True), 0, len(edges) - 2)

    rows = []
    for b in range(len(edges) - 1):
        mask = idx == b
        if mask.sum() == 0:
            continue
        rows.append(
            {
                "bin": b + 1,
                "n": int(mask.sum()),
                "mean_predicted": y_prob[mask].mean(),
                "observed_rate": y_true[mask].mean(),
                "gap": y_prob[mask].mean() - y_true[mask].mean(),
            }
        )
    return pd.DataFrame(rows)


def performance_row(name: str, y_true, y_prob) -> dict:
    """One line of the summary table used throughout the module."""
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.clip(np.asarray(y_prob, dtype=float), 1e-6, 1 - 1e-6)
    return {
        "dataset": name,
        "n": len(y_true),
        "event_rate": y_true.mean(),
        "mean_predicted": y_prob.mean(),
        "AUROC": roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else np.nan,
        "Brier": brier_score_loss(y_true, y_prob),
        "LogLoss": log_loss(y_true, y_prob, labels=[0, 1]),
        "ECE": expected_calibration_error(y_true, y_prob),
    }


def performance_table(named_predictions) -> pd.DataFrame:
    """``named_predictions`` is an iterable of ``(name, y_true, y_prob)``."""
    return pd.DataFrame([performance_row(n, y, p) for n, y, p in named_predictions])


def selective_risk_curve(y_true, y_prob, uncertainty, thresholds=None, decision_threshold: float = 0.5) -> pd.DataFrame:
    """Error rate as a function of how much of the cohort the model is allowed to skip.

    Patients are ranked by ``uncertainty``; the most uncertain are handed to a
    clinician first. A model that knows what it does not know should get more
    accurate the more it is allowed to defer.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    uncertainty = np.asarray(uncertainty, dtype=float)
    order = np.argsort(uncertainty)

    if thresholds is None:
        thresholds = np.linspace(0.2, 1.0, 17)

    rows = []
    for coverage in thresholds:
        k = max(int(round(len(order) * coverage)), 1)
        keep = order[:k]
        pred = (y_prob[keep] >= decision_threshold).astype(int)
        rows.append(
            {
                "coverage": k / len(order),
                "n_retained": k,
                "error_rate": float((pred != y_true[keep]).mean()),
                "brier": brier_score_loss(y_true[keep], y_prob[keep]) if len(np.unique(y_true[keep])) > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def subgroup_report(df: pd.DataFrame, y_prob, by: str, outcome: str = "outcome", min_n: int = 100) -> pd.DataFrame:
    """Per-subgroup discrimination and calibration.

    Aggregate metrics routinely hide a subgroup the model is useless for; this
    is the table that surfaces it.
    """
    y_prob = np.asarray(y_prob, dtype=float)
    rows = []
    for value, index in df.groupby(by, observed=True).groups.items():
        mask = df.index.isin(index)
        if mask.sum() < min_n:
            continue
        y = df.loc[mask, outcome].to_numpy(dtype=int)
        p = y_prob[mask]
        rows.append(performance_row(f"{by}={value}", y, p))
    return pd.DataFrame(rows).rename(columns={"dataset": "subgroup"})


def bootstrap_ensemble(fit_predict, X, y, X_eval, n_models: int = 40, seed: int = 0):
    """Bag a model over bootstrap resamples and return the full prediction matrix.

    ``fit_predict(X_train, y_train, X_eval) -> probabilities``. Spread across
    the ensemble is the module's cheap stand-in for epistemic uncertainty.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    preds = []
    for _ in range(n_models):
        idx = rng.integers(0, n, n)
        preds.append(fit_predict(X[idx] if isinstance(X, np.ndarray) else X.iloc[idx],
                                 y[idx] if isinstance(y, np.ndarray) else y.iloc[idx],
                                 X_eval))
    return np.vstack(preds)


def shift_report(reference: pd.DataFrame, candidate: pd.DataFrame, columns) -> pd.DataFrame:
    """Standardised mean differences plus missingness rates between two cohorts.

    No labels required, so it is the check that can actually be run before a
    model is switched on at a new hospital.
    """
    rows = []
    for col in columns:
        a = reference[col].astype(float)
        b = candidate[col].astype(float)
        pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
        smd = (b.mean() - a.mean()) / pooled if pooled > 0 else 0.0
        rows.append(
            {
                "feature": col,
                "reference_mean": a.mean(),
                "candidate_mean": b.mean(),
                "std_mean_diff": smd,
                "reference_missing": a.isna().mean(),
                "candidate_missing": b.isna().mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("std_mean_diff", key=np.abs, ascending=False).reset_index(drop=True)
