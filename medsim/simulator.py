"""Synthetic EHR simulator for the healthcare uncertainty module.

The generator is deliberately transparent: every failure mode that participants
are asked to diagnose is a single, named knob. Nothing here needs credentialed
data, and everything runs on a free Colab CPU in a few seconds.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.special import expit

FEATURES = [
    "age",
    "heart_rate",
    "systolic_bp",
    "respiratory_rate",
    "creatinine",
    "lactate",
    "wbc",
    "prior_stroke",
    "diabetes",
    "group",
]

TRUTH_COLUMNS = ["concern", "true_p", "latent", "clean_outcome", "is_ood"]

SITE_EFFECT = {"A": 0.00, "B": 0.45, "C": -0.35, "D": 0.15}


@dataclass
class SimConfig:
    """One hospital-worth of data-generating assumptions."""

    n: int = 5000
    site: str = "A"
    seed: int = 0
    prevalence_shift: float = 0.0
    measurement_noise: float = 1.0
    missingness_strength: float = 0.0
    label_noise: float = 0.0
    subgroup_shift: float = 0.0
    subgroup_interaction: float = 0.0
    subgroup_prevalence: float = 0.35
    ood_fraction: float = 0.0
    coefficient_drift: dict = field(default_factory=dict)


def _base_covariates(rng: np.random.Generator, n: int, ood_fraction: float):
    """Draw the covariate block, optionally mixing in an unfamiliar population."""
    n_ood = int(round(n * ood_fraction))
    n_main = n - n_ood

    age = np.clip(rng.normal(66, 14, n_main), 18, 95)
    heart_rate = rng.normal(82, 15, n_main)
    systolic_bp = rng.normal(128, 22, n_main)
    respiratory_rate = rng.normal(18, 4, n_main)
    creatinine = np.exp(rng.normal(np.log(1.0), 0.45, n_main))
    lactate = np.exp(rng.normal(np.log(1.6), 0.40, n_main))
    wbc = np.exp(rng.normal(np.log(9.0), 0.35, n_main))
    is_ood = np.zeros(n_main, dtype=int)

    if n_ood > 0:
        # A referral stream the training hospital never sees: younger, sicker
        # kidneys, and physiology that sits outside the fitted feature range.
        age = np.concatenate([age, np.clip(rng.normal(34, 9, n_ood), 18, 95)])
        heart_rate = np.concatenate([heart_rate, rng.normal(104, 18, n_ood)])
        systolic_bp = np.concatenate([systolic_bp, rng.normal(101, 18, n_ood)])
        respiratory_rate = np.concatenate([respiratory_rate, rng.normal(26, 5, n_ood)])
        creatinine = np.concatenate([creatinine, np.exp(rng.normal(np.log(3.4), 0.55, n_ood))])
        lactate = np.concatenate([lactate, np.exp(rng.normal(np.log(3.9), 0.50, n_ood))])
        wbc = np.concatenate([wbc, np.exp(rng.normal(np.log(15.0), 0.45, n_ood))])
        is_ood = np.concatenate([is_ood, np.ones(n_ood, dtype=int)])

    return dict(
        age=age,
        heart_rate=heart_rate,
        systolic_bp=systolic_bp,
        respiratory_rate=respiratory_rate,
        creatinine=creatinine,
        lactate=lactate,
        wbc=wbc,
        is_ood=is_ood,
    )


def simulate_ehr(config: SimConfig | None = None, keep_truth: bool = False, **kwargs) -> pd.DataFrame:
    """Generate one synthetic cohort.

    Parameters mirror :class:`SimConfig`; pass either a config or keyword
    arguments. Set ``keep_truth=True`` to retain the columns that reveal the
    generating process (used for instructor material and for grading).
    """
    if config is None:
        config = SimConfig(**kwargs)
    elif kwargs:
        config = SimConfig(**{**config.__dict__, **kwargs})

    rng = np.random.default_rng(config.seed)
    n = config.n

    cov = _base_covariates(rng, n, config.ood_fraction)
    prior_stroke = rng.binomial(1, 0.18, n)
    diabetes = rng.binomial(1, 0.28, n)
    group = rng.binomial(1, config.subgroup_prevalence, n)

    # An unrecorded clinical impression. It moves the outcome and it drives which
    # labs get ordered, but it never appears as a column. This is the reason a
    # blank cell can be informative and the reason the ceiling on AUROC is
    # well below 1.
    concern = rng.normal(0.0, 1.0, n)

    coef = {
        "age": 0.042,
        "heart_rate": 0.018,
        "systolic_bp": -0.012,
        "respiratory_rate": 0.075,
        "log_creatinine": 0.78,
        "log_lactate": 0.95,
        "prior_stroke": 0.70,
        "diabetes": 0.50,
    }
    coef.update(config.coefficient_drift)

    latent = (
        -5.75
        + coef["age"] * cov["age"]
        + coef["heart_rate"] * (cov["heart_rate"] - 80.0)
        + coef["systolic_bp"] * (cov["systolic_bp"] - 125.0)
        + coef["respiratory_rate"] * (cov["respiratory_rate"] - 18.0)
        + coef["log_creatinine"] * np.log(cov["creatinine"])
        + coef["log_lactate"] * np.log(cov["lactate"])
        + coef["prior_stroke"] * prior_stroke
        + coef["diabetes"] * diabetes
        + 0.70 * concern
        + config.subgroup_shift * group
        + config.subgroup_interaction
        * group
        * (np.log(cov["lactate"]) + 0.05 * (cov["age"] - 66.0))
        + SITE_EFFECT.get(config.site, 0.0)
        + config.prevalence_shift
    )

    true_p = expit(latent)
    clean_outcome = rng.binomial(1, true_p)

    outcome = clean_outcome.copy()
    if config.label_noise > 0:
        # Chart-review error is rarely symmetric: events are missed more often
        # than non-events are invented.
        flip_pos = rng.random(n) < config.label_noise
        flip_neg = rng.random(n) < config.label_noise * 0.10
        outcome = np.where((clean_outcome == 1) & flip_pos, 0, outcome)
        outcome = np.where((clean_outcome == 0) & flip_neg, 1, outcome)

    # Measurement noise is applied after the outcome is drawn: the physiology is
    # real, the recorded number is what degrades.
    extra = max(config.measurement_noise - 1.0, 0.0)
    observed = {
        "age": cov["age"],
        "heart_rate": cov["heart_rate"] + rng.normal(0, 6.0 * extra, n),
        "systolic_bp": cov["systolic_bp"] + rng.normal(0, 9.0 * extra, n),
        "respiratory_rate": cov["respiratory_rate"] + rng.normal(0, 2.0 * extra, n),
        "creatinine": cov["creatinine"] * np.exp(rng.normal(0, 0.28 * extra, n)),
        "lactate": cov["lactate"] * np.exp(rng.normal(0, 0.26 * extra, n)),
        "wbc": cov["wbc"] * np.exp(rng.normal(0, 0.22 * extra, n)),
    }

    df = pd.DataFrame(
        {
            "age": observed["age"],
            "heart_rate": observed["heart_rate"],
            "systolic_bp": observed["systolic_bp"],
            "respiratory_rate": observed["respiratory_rate"],
            "creatinine": observed["creatinine"],
            "lactate": observed["lactate"],
            "wbc": observed["wbc"],
            "prior_stroke": prior_stroke,
            "diabetes": diabetes,
            "group": group,
            "site": config.site,
            "outcome": outcome,
        }
    )

    if config.missingness_strength > 0:
        # Missing not at random: the sickest patients are the ones whose labs get
        # sent, so a blank cell is itself evidence about the outcome.
        s = config.missingness_strength
        p_missing_lab = expit(-0.9 - s * (1.5 * concern + 0.4 * (latent + 2.2)))
        p_missing_lactate = expit(-0.7 - s * (1.7 * concern + 0.3 * (latent + 2.2)))
        df.loc[rng.random(n) < p_missing_lab, "creatinine"] = np.nan
        df.loc[rng.random(n) < p_missing_lactate, "lactate"] = np.nan
    else:
        # A low, uninformative baseline of missingness so that "there are NaNs"
        # is never by itself the answer.
        df.loc[rng.random(n) < 0.03, "creatinine"] = np.nan
        df.loc[rng.random(n) < 0.05, "lactate"] = np.nan

    if keep_truth:
        df["concern"] = concern
        df["true_p"] = true_p
        df["latent"] = latent
        df["clean_outcome"] = clean_outcome
        df["is_ood"] = cov["is_ood"]

    return df.sample(frac=1.0, random_state=config.seed).reset_index(drop=True)


def train_val_split(df: pd.DataFrame, val_fraction: float = 0.3, seed: int = 0):
    """Split a cohort without touching scikit-learn, so the module stays light."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))
    cut = int(len(df) * (1 - val_fraction))
    return df.iloc[idx[:cut]].reset_index(drop=True), df.iloc[idx[cut:]].reset_index(drop=True)
