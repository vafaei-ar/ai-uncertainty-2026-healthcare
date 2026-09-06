"""Reproduce the reference numbers in ANSWER_KEY.md.

Run after regenerating the datasets to confirm every hidden failure mode is
still detectable and still distinct:

    python project/check_signatures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from medsim import (  # noqa: E402
    FEATURES,
    performance_table,
    selective_risk_curve,
    shift_report,
    subgroup_report,
    train_val_split,
)

DATA = ROOT / "project" / "data"
CONTINUOUS = ["age", "heart_rate", "systolic_bp", "respiratory_rate", "creatinine", "lactate", "wbc"]


def baseline(train: pd.DataFrame, features=FEATURES):
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=3000),
    ).fit(train[features], train["outcome"])


def ensemble_spread(train, deploy, n_models: int = 30, seed: int = 0):
    imp = SimpleImputer(strategy="median").fit(train[FEATURES])
    scaler = StandardScaler().fit(imp.transform(train[FEATURES]))
    x_train = scaler.transform(imp.transform(train[FEATURES]))
    x_deploy = scaler.transform(imp.transform(deploy[FEATURES]))
    y = train["outcome"].to_numpy()

    rng = np.random.default_rng(seed)
    preds = []
    for _ in range(n_models):
        idx = rng.integers(0, len(y), len(y))
        preds.append(LogisticRegression(max_iter=3000).fit(x_train[idx], y[idx]).predict_proba(x_deploy)[:, 1])
    return np.vstack(preds).std(axis=0)


def main() -> None:
    pd.set_option("display.width", 200)
    for team in range(1, 7):
        train_all = pd.read_csv(DATA / f"team_{team}_train.csv")
        deploy = pd.read_csv(DATA / f"team_{team}_deployment.csv")
        train, val = train_val_split(train_all, 0.3, seed=7)

        model = baseline(train)
        p_val = model.predict_proba(val[FEATURES])[:, 1]
        p_dep = model.predict_proba(deploy[FEATURES])[:, 1]

        print(f"\n{'=' * 70}\nTEAM {team}\n{'=' * 70}")
        print(performance_table([("validation", val["outcome"], p_val),
                                 ("shadow mode", deploy["outcome"], p_dep)]).round(3).to_string(index=False))
        print("\nby subgroup (shadow mode):")
        print(subgroup_report(deploy, p_dep, "group").round(3).to_string(index=False))
        print("\ntop feature shifts:")
        print(shift_report(train, deploy, CONTINUOUS).round(3).head(4).to_string(index=False))

        spread = ensemble_spread(train, deploy)
        curve = selective_risk_curve(deploy["outcome"], p_dep, spread)
        at = lambda c: curve.iloc[int(np.argmin(np.abs(curve["coverage"] - c)))]["error_rate"]
        print(
            f"\nensemble SD: mean {spread.mean():.4f}  p95 {np.quantile(spread, 0.95):.4f}"
            f"   |   error at coverage 100%/70%/40%: {at(1.0):.3f} / {at(0.7):.3f} / {at(0.4):.3f}"
        )

        missing = {c: round(train[c].isna().mean(), 3) for c in FEATURES if train[c].isna().any()}
        print(f"train missingness: {missing}")

        if team == 1:
            complete = train.dropna(subset=FEATURES)
            print(
                f"complete-case: n {len(complete)} of {len(train)}, "
                f"event rate {complete['outcome'].mean():.3f} vs {train['outcome'].mean():.3f} overall"
            )
            def add_indicators(df):
                out = df.copy()
                out["creatinine_missing"] = out["creatinine"].isna().astype(int)
                out["lactate_missing"] = out["lactate"].isna().astype(int)
                return out
            extended = FEATURES + ["creatinine_missing", "lactate_missing"]
            model2 = baseline(add_indicators(train), extended)
            p2 = model2.predict_proba(add_indicators(deploy)[extended])[:, 1]
            print(performance_table([("with missingness indicators", deploy["outcome"], p2)]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
