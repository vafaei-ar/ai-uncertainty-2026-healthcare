# Team project: build a model that knows when it should not be trusted

**AI & Uncertainty School and Workshop 2026 - healthcare module**

## The situation

A hospital group runs six hospitals. Each has built a risk model for the same
task: given routine vitals and labs recorded in the first hours of an admission,
estimate the probability that a patient will deteriorate and need critical care
escalation within 48 hours.

Each model has since been run in **shadow mode** for six months at the ward that
wants to adopt it: it scored every admission, nobody saw the scores, and care
went on exactly as it would have anyway. So you have predictions, you have the
outcomes that followed, and no patient has yet been affected by the model. This
is silent prospective validation, and it is the last checkpoint before a model
is allowed to touch care.

Every team is assigned one hospital. You receive two files:

| File | What it is |
| --- | --- |
| `team_N_train.csv` | The development records the model was built on |
| `team_N_deployment.csv` | Six months of silent prospective validation at the ward that wants to switch it on |

The columns are identical for every team. So is the task. What differs is the
reason each model should not be deployed as-is.

## Your job

You are the reviewer. The clinical director wants a yes or no, and a reason.

**The goal is not a higher AUROC.** A team that raises AUROC by 0.02 and cannot
say who the model fails for has not done the work. A team that leaves AUROC
untouched and correctly identifies which patients the model must not be used on
has done the work.

## Deliverable

A **5-minute presentation**, three or four slides, answering:

1. **What did you find?** Name the failure mode in one sentence.
2. **What exposed it?** The single metric, table, or plot that made it visible.
   Show that one figure.
3. **Was the model calibrated?** On the development data, on the deployment
   data, and within subgroups. Where did calibration break, and in which
   direction - does the model under- or over-state risk?
4. **Who is least trustworthy?** Characterise the patients the model should not
   be applied to.
5. **When should the model abstain?** Give a concrete rule and the coverage it
   implies. "Defer the most uncertain 25%" is a rule; "be careful" is not.
6. **What would reduce the uncertainty?** More data, different data, a different
   variable, a different study design?
7. **Would you deploy?** Yes, no, or yes-under-conditions. State the conditions.

## Suggested route through the three hours

| Time | Step |
| --- | --- |
| 0:00-0:20 | Read the data. Event rates, missingness per column, distributions. Do not fit anything yet. |
| 0:20-0:45 | Split train into train/validation. Fit a baseline logistic regression. Record AUROC, Brier, ECE. |
| 0:45-1:15 | Score the shadow-mode set. Compare every number to validation. Something will not match. |
| 1:15-1:50 | Chase it. Calibration curve, subgroup table, feature shift report, missingness pattern. |
| 1:50-2:20 | Quantify uncertainty: bootstrap ensemble spread, then a selective-prediction curve. |
| 2:20-2:45 | Decide the abstention rule and the deployment recommendation. |
| 2:45-3:00 | Build the slides. |

## Tools you already have

`medsim.metrics` provides `performance_table`, `calibration_table`,
`expected_calibration_error`, `subgroup_report`, `shift_report`,
`selective_risk_curve` and `bootstrap_ensemble`. The starter notebook
`notebooks/90_team_project_starter.ipynb` loads your data and runs the first
comparison. Everything after that is yours.

## Three questions that find most of these problems

1. **Does the deployment set behave like the validation set?** Compare event
   rate, mean predicted risk, and per-feature distributions. Labels are not
   needed for the last one, which is why it is the check you could actually run
   before go-live.
2. **Does the aggregate number hide a subgroup?** Split by `group`, by age band,
   by whether a lab was recorded. Recompute everything within each stratum.
3. **Is a blank cell telling you something?** Missingness is a variable. Compare
   the outcome rate among patients whose creatinine was measured against those
   whose was not.

## Rules

- Do not open the answer key. Your instructor has it.
- You may use any model you like, but a well-understood logistic regression that
  you can interrogate will serve you better in five minutes of presentation than
  a gradient-boosted model you cannot explain.
- Report uncertainty on your own numbers too. An AUROC of 0.72 on 4000 patients
  has a confidence interval, and it is wider than most people assume.
