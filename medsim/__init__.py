"""Teaching utilities for the healthcare AI module of the AI & Uncertainty School 2026."""

from medsim.simulator import (
    FEATURES,
    SITE_EFFECT,
    TRUTH_COLUMNS,
    SimConfig,
    simulate_ehr,
    train_val_split,
)
from medsim.metrics import (
    bootstrap_ensemble,
    calibration_table,
    expected_calibration_error,
    performance_row,
    performance_table,
    selective_risk_curve,
    shift_report,
    subgroup_report,
)

__all__ = [
    "FEATURES",
    "SITE_EFFECT",
    "TRUTH_COLUMNS",
    "SimConfig",
    "simulate_ehr",
    "train_val_split",
    "bootstrap_ensemble",
    "calibration_table",
    "expected_calibration_error",
    "performance_row",
    "performance_table",
    "selective_risk_curve",
    "shift_report",
    "subgroup_report",
]

__version__ = "0.2.0"
