# Pre-analysis protocol for the student simulation

## Aim and estimand

**Question:** Under which synthetic hospital-transfer mechanisms and target
outcome-label budgets does a simple calibration update improve an unchanged
source model?

The primary estimand is the mean **paired difference in Brier score**,
recalibrated minus unchanged, on a fully independent target test cohort.
A negative difference favors recalibration. The comparison is *within the
same simulated replicate and hospital scenario*.

This is an educational simulation protocol, not a registered clinical study.
Do not use post hoc claims of confirmation or publication novelty.

## Dataset generation

- A fresh 4,000-record Hospital A source cohort is simulated per replicate.
- A new 1,600-record target calibration pool is simulated separately.
- A third target test cohort is generated with a separate random seed and
  must never be used for fitting, hyperparameter search, or model selection.
- Sample sizes may be reduced for short live demonstrations but must be
  reported with results.
- Students select nested random target audits of 25, 75, and 150 labels.
- All variables/outcomes come from medsim.simulator.SimConfig.

The scenarios individually alter:
1. No change (negative control).
2. Target baseline log-odds of deterioration.
3. Measurement noise on recorded features.
4. A subgroup-specific outcome relationship.
5. Informative missing-data patterns.

We intentionally do not label scenario 3 as pure covariate shift.
Recorded measurement changes can affect P(Y|X_observed).

## Fixed methods

- **Unchanged:** develop a logistic risk model on Hospital A; use its
  probabilities at the target without alteration.
- **Intercept:** fit one shift on target-audit log odds, with weak
  regularization and a fixed original slope.
- **Platt:** fit a logistic slope and intercept to target-audit model
  logits with L2 regularization. If a target audit has only one class,
  report that Platt is not estimable and use unchanged probabilities only
  as a marked fallback.

Only target-audit labels can inform recalibration. Keep preprocessing and
source model training the same across methods.

## Metrics and interpretation

**Primary:** Brier score on independent target data, with paired difference
to unchanged.

**Secondary:** AUROC; expected calibration error; calibration-in-the-large
gap; maximum absolute group-level mean calibration gap for groups with at
least 30 evaluation observations.

AUROC cannot assess whether probability values are reliable. ECE is
bin-dependent. The group-level gap does not establish algorithmic fairness.
No metric measures actual benefit of an intervention in this simulation.

Summarize the distribution of paired differences across independent
replicates. Quantile intervals in the starter script describe variation
between runs, **not formal confidence intervals**. A publication-quality
analysis would require a power/precision plan and stronger interval
estimation.

## Leakage and protocol rules

1. Do not learn calibration parameters from the evaluation test cohort.
2. Do not select the best method using target test results and then report
   those same results as an unbiased final comparison.
3. For research-method comparison, pre-specify the three methods and
   scenarios before reading results.
4. Record random seed, dataset sizes, scenario arguments, and label budget.
5. Check that the source and target cohorts and the audit and test sets
   are independently generated.
6. Count non-estimable or degenerate small-audit cases. Do not silently
   exclude them.
7. Use a negative-control scenario to show whether unnecessary
   recalibration degrades performance.

## Minimum reproducible command

    python -m project.research_experiments --repeats 8 --seed 2026

This writes:
- project/results/method_results.csv: each replicate/condition/budget/method
- project/results/paired_summary.csv: descriptive paired contrasts
- project/results/brier_comparison.png: one focused plot at the middle budget

A faster rehearsal may use --repeats 2 and --test-size 1000.
Do not substitute the quick rehearsal for final research estimates.

## Expected workshop conclusions

The students should identify **where and why** simple recalibration helps,
hurts, or remains uncertain given the audit size. They should be able to
propose the next study. They should not be evaluated by whether they happen
to recover the simulator's hidden settings.

## Publication path beyond the workshop

Before pursuing a paper:
- Review prior literature on site adaptation, recalibration with few labels,
  calibration shift, and selective prediction.
- Specify a genuine new methodological question or empirical contribution.
- Run substantially more replicates and broader joint-shift scenarios.
- Use independent validation beyond a single simulator, ideally on
  permissioned real EHR data where appropriate.
- Reassess uncertainty, label selection, missing data, subgroup instability,
  and operational consequences.

A short educational workshop exercise alone is not sufficient for a
research manuscript.
