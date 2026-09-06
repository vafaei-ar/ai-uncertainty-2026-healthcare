# Instructor answer key: team project

**Do not distribute.** Reference numbers come from a median-imputed, standardised
logistic regression on `FEATURES`, trained on a 70% split of `team_N_train.csv`
and scored on the held-out 30% ("validation") and on the shadow-mode file
`team_N_deployment.csv`.
Reproduce them with `python project/check_signatures.py`. Teams using a
different model will get different digits but the same qualitative pattern.

Baseline for orientation: a clean cohort gives validation AUROC around 0.72 and
ECE around 0.02. The achievable ceiling is roughly 0.75 - the simulator includes
an unrecorded "clinical concern" term that moves the outcome and appears in no
column. That gap is not a bug to be fixed; it is the aleatoric floor, and a team
that keeps pushing for AUROC 0.90 should be asked what they think is left to
learn.

---

## Team 1: Informative missingness (MNAR)

**Mechanism.** Creatinine and lactate are missing for 39% and 41% of patients,
and missingness is driven by the unrecorded clinical-concern variable. A blank
cell means nobody was worried enough to send the sample.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| AUROC | 0.717 | 0.720 |
| ECE | 0.016 | 0.009 |

Nothing looks wrong. That is the point of this dataset - the failure is invisible
in the headline comparison.

- Complete-case analysis: n drops from 4200 to 1999 and the event rate jumps from
  **0.145 to 0.214**. Anyone who dropped incomplete rows has silently selected
  the sickest half of the cohort.
- Adding `creatinine_missing` and `lactate_missing` indicators lifts deployment
  AUROC from **0.720 to 0.743** and improves Brier. The blank cell carries real
  information that median imputation destroys.
- Event rate among patients with creatinine observed vs missing: roughly
  **0.18 vs 0.07**.

**What a strong team says.** Missingness is not a nuisance to be imputed away; it
is a recorded clinical decision. Model it explicitly, never drop rows, and be
aware that if ordering practice changes at the new hospital, the indicator's
meaning changes with it - so this feature is itself a shift risk.

**Trap.** Teams often "fix" this with a fancier imputer (MICE, kNN). It does not
help, because the information is in the *fact* of missingness, not in the
unobserved value. That failed attempt is worth surfacing in the debrief.

---

## Team 2: Site and baseline-risk shift (conditional shift)

**Mechanism.** Trained at site A, run at site B with a +0.5 shift on the logit
intercept. Name it precisely: $P(X)$ is untouched and $P(Y \mid X)$ moved, so
this is a **conditional shift**, not label shift - label shift's assumption of a
stable $P(X \mid Y)$ is violated here. Teams who call it "prevalence shift" are
describing the symptom correctly; push them to say which distribution moved.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| Event rate | 0.142 | **0.264** |
| Mean predicted | 0.146 | **0.150** |
| AUROC | 0.753 | 0.707 |
| ECE | 0.020 | **0.114** |

The model ranks patients almost as well as before and understates everyone's
risk by roughly a factor of two. Discrimination survives; calibration collapses.

- Feature-shift report finds **nothing** - all standardised mean differences are
  under 0.03. The covariates are identical; the baseline risk is not.

**What a strong team says.** Covariate-shift monitoring could not have caught
this on inputs alone - it never had access to the thing that moved. The fix is
recalibration at the new site - an intercept correction estimated on a few hundred labelled deployment
patients restores calibration without refitting. Until that recalibration is
done, any fixed alerting threshold fires far too rarely at site B.

**Trap.** Teams see AUROC 0.707 and conclude the model "still works". Push them
to the decision level: at a 0.5 threshold the model almost never alerts, while a
quarter of the ward deteriorates.

---

## Team 3: Measurement noise / instrument drift

**Mechanism.** Deployment vitals and labs carry extra measurement error
(`measurement_noise=2.8`); the underlying physiology is unchanged.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| AUROC | 0.730 | **0.678** |
| Mean predicted | 0.134 | **0.169** |
| Event rate | 0.150 | 0.150 |
| ECE | 0.023 | **0.040** |

- The shift report is the giveaway: **lactate SMD 0.22, creatinine SMD 0.21,
  WBC 0.15**, with unchanged means for the variables that were not noised. The
  *variances* are inflated, not the centres.
- Over-prediction, because noise on log-scale labs is asymmetric and the model's
  positive coefficients pick up the fattened upper tail.

**What a strong team says.** This is regression dilution: noisier inputs attenuate
the effective signal and flatten the achievable discrimination. No amount of
retraining on the noisy data recovers the lost AUROC - the fix is upstream, in
the assay or the device. A team that proposes calibrating the analyser rather
than the model has understood it.

---

## Team 4: Label noise in the training records

**Mechanism.** Development labels were flipped asymmetrically (22% of true events
recorded as non-events, 2.2% the other way). Deployment labels are clean.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| AUROC | **0.648** | **0.714** |
| Mean predicted | 0.116 | 0.115 |
| Event rate | 0.121 | 0.132 |

The inversion is the tell: **the model performs better in the field than it did
in validation.** That essentially never happens for an honest pipeline, and it
means the validation labels, not the model, are the broken component.

- Systematic under-prediction on deployment (0.115 predicted vs 0.132 observed),
  because the model learned a base rate suppressed by missed events.

**What a strong team says.** Validation metrics are a measurement of the model
*against the labels*, and the labels are an instrument with their own error. The
first move is a chart-review audit of a sample of the development labels, not a
model change. Note that the team can only see this inversion because shadow mode
supplied outcomes alongside predictions - which is exactly the argument for
running a model silently before letting it act.

**Trap.** Some teams will conclude the deployment set is "easier". Ask them what
would make it easier - the covariate distributions are identical.

---

## Team 5: Subgroup shift with a different risk relationship

**Mechanism.** `group` makes up 8% of the development data and 42% of the
deployment ward, and within that subgroup the lactate-risk relationship is
largely absent (`subgroup_interaction=-1.8`) rather than merely shifted.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| AUROC | 0.723 | 0.663 |
| ECE | 0.019 | 0.025 |

Aggregate numbers look mediocre, not alarming. The subgroup table is where it
breaks open:

| Subgroup | n | AUROC | ECE | Mean predicted | Observed |
| --- | --- | --- | --- | --- | --- |
| group = 0 | 2287 | **0.756** | 0.022 | 0.133 | 0.140 |
| group = 1 | 1713 | **0.564** | 0.058 | 0.106 | 0.154 |

For 43% of the deployment ward the model is barely better than a coin flip, and
it understates their risk by a third.

- The shift report finds nothing, because the covariate *distributions* are fine.
  Only the conditional relationship differs.

**What a strong team says.** A main-effects model cannot represent a subgroup
whose risk structure differs, and 480 training patients in that subgroup would
not identify the interaction even if it were specified. This is the case for
hierarchical modelling: partial pooling gives the small subgroup its own
parameters while shrinking them toward the population. Until then the model
should not be applied to `group = 1` at all.

**Trap.** Teams that only stratify by age or by site will miss it. Prompt them to
stratify by every categorical column they were given.

---

## Team 6: Out-of-distribution patients at deployment

**Mechanism.** 30% of the deployment ward is a referral stream absent from
development: younger, tachycardic, hypotensive, with much higher creatinine and
lactate.

**Signature.**

| | Validation | Shadow mode |
| --- | --- | --- |
| AUROC | 0.725 | **0.776** |
| Mean predicted | 0.142 | **0.264** |
| Event rate | 0.134 | 0.228 |
| ECE | 0.022 | **0.045** |

**AUROC goes up while the model becomes less usable.** The OOD patients are
genuinely sicker, so ranking is easy; the probabilities are badly overstated.

- Shift report is unambiguous: **creatinine SMD 0.63, lactate 0.58, age −0.55,
  respiratory rate 0.49**.
- Bootstrap ensemble spread is the highest of all six teams (mean SD 0.030,
  95th percentile 0.088) and concentrates on the OOD patients.
- Abstention pays off most here: deferring the most uncertain patients takes the
  error rate from **0.215 at full coverage to 0.132 at 70% and 0.074 at 40%**.

**What a strong team says.** This is the dataset where epistemic uncertainty
earns its keep: the model's own disagreement identifies the patients it was never
trained for, without needing their labels. Deploy with an OOD gate on the
extrapolation region, not with a global threshold change.

**Trap.** A team fixated on AUROC will report this as the *best*-performing
model in the room. That contrast is the single most useful moment in the
debrief - put team 6 and team 2 on screen together.

---

## Debrief plan (final 20 minutes)

Run the teams in this order; each one sets up the next.

1. **Team 2** - calibration can fail while discrimination holds.
2. **Team 6** - and discrimination can *improve* while the model gets worse.
3. **Team 5** - aggregate metrics hide subgroups; this is why hierarchy matters.
4. **Team 1** - the absent value is a value.
5. **Team 4** - your labels are an instrument with error.
6. **Team 3** - sometimes the fix is not in the model at all.

**Closing line for the module.** Every team was given the same task, the same
columns and a model with roughly the same AUROC. The number that mattered was
never AUROC. It was whether the model's stated confidence survived contact with
a new hospital.
