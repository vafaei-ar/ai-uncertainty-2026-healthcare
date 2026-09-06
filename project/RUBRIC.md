# Assessment rubric: healthcare team project

Twenty points total. The weighting is deliberate: diagnosis and honesty are
worth more than modelling.

| Criterion | Points | What earns full marks |
| --- | --- | --- |
| **Diagnosis** | 5 | The failure mode is named correctly and specifically. "Distribution shift" is partial credit; "the deployment hospital has roughly double the event rate while the model's mean prediction is unchanged" is full credit. |
| **Evidence** | 4 | The claim is supported by a metric or figure that actually discriminates. A calibration curve that separates validation from deployment counts; a ROC curve alone usually does not. |
| **Calibration analysis** | 3 | Calibration reported on both sets and within at least one stratification, with the direction of the error stated. |
| **Uncertainty quantification** | 3 | Some honest measure of epistemic uncertainty (ensemble spread, posterior width, or interval), used to rank patients rather than just reported. |
| **Abstention rule** | 3 | A concrete, implementable rule with its coverage and the resulting error rate on retained patients. |
| **Deployment judgement** | 2 | A defensible recommendation with stated conditions and stated residual risk. |

## Bonus (up to 2 points)

- Identifying a **second**, smaller problem in the dataset that was not the
  headline failure mode.
- Correctly quantifying uncertainty in their own performance estimates
  (bootstrap CI on AUROC or Brier).
- Proposing a monitoring metric that would have caught the problem
  prospectively, without waiting for outcome labels.

## Marks are lost for

- Reporting only AUROC.
- Fixing the number without explaining the mechanism.
- Recommending deployment with no conditions.
- Claiming a subgroup difference from a stratum of 40 patients without an
  interval.
