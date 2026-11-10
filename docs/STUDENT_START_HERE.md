# When can we trust clinical AI at a new hospital?

**AI & Uncertainty School, Mauritius | Healthcare research project**

## Our question

Hospital A developed a model that estimates the chance that a patient
will deteriorate in the next 48 hours after admission. Hospital B wants to
use it. The two hospitals may have different patients, laboratory
measurements, or relationships between patient information and outcomes.

We will test **when a small number of new-hospital outcomes is enough to
improve the model's probability estimates**.

The data are synthetic. None of the examples is a real patient or a
validated prediction for clinical care.

## What you need

- A laptop and browser that can open Google Colab.
- Basic familiarity with Python variables, tables, and plots helps.
  You do not need machine-learning experience or a GPU.
- [Open the research notebook in Colab before the PR is merged](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/chatgpt/mauritius-one-lecture-three-day-research-2026/notebooks/92_three_day_research_starter.ipynb).
- [Permanent Colab link, available after merge](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb).
- The [study question and methods](../project/RESEARCH_PROTOCOL.md).

**First setup check:** Open the notebook, select *Runtime → Run all*, and
check that the first cells print the record counts without errors. If setup
fails, show the error message to the local facilitator. Do not attempt
to install restricted clinical datasets.

## Data dictionary

| Field | Meaning in this simulation |
| --- | --- |
| record_id | Synthetic admission identifier, not a patient identifier from MIMIC |
| age | Simulated age |
| heart_rate | Simulated beats per minute |
| systolic_bp | Simulated systolic blood pressure |
| respiratory_rate | Simulated breaths per minute |
| creatinine, lactate, wbc | Simulated laboratory measurements |
| prior_stroke, diabetes | Simulated binary medical-history indicators |
| group | Synthetic group used to examine heterogeneous model behavior |
| site | Synthetic site label |
| outcome | 1 if simulated deterioration occurs within 48 hours, otherwise 0 |

Some laboratory values are missing. Do not assume that every missing
result means a normal test. In the provided 75-record target audit,
11 synthetic admissions have the deterioration outcome. This is too
little information for precise subgroup calibration estimates.

## Three basic ideas

**A predicted risk is a probability, not a diagnosis.** If many comparable
admissions receive 30% risk, calibration asks whether about 30% experience
the outcome.

**AUROC measures ranking.** It does not tell us whether 30% is the right
probability.

**We need independent outcomes to evaluate an adjusted model.** If we
use the same 75 outcomes both to recalibrate and to measure success, the
result can look better than it really is.

## What you will compare

| Method | Plain-language idea |
| --- | --- |
| Unchanged | Use Hospital A predictions at the new hospital |
| Intercept update | Move the predicted risk levels up or down |
| Logistic (Platt) update | Also change the spread of predictions |

The first orientation example provides **75** target audit outcomes.
For the research comparisons, the simulator creates new, independent
synthetic cohorts and lets us sample **25, 75, or 150** target outcomes.
You are not expected to find another 75 real outcomes in the provided
orientation file. These are two connected teaching activities.

The **Brier score** is the average squared difference between the
predicted probability and the outcome (0 or 1). Lower is better.
Compare each updated method with the unchanged model on the **same
independent test cases**.

If an update gives a *negative* change in Brier score, it performed
better than the unchanged model on those test cases. One seed is not
enough to establish that the improvement is reliable.

## Your three-day minimum

**Day 1:** Run the provided notebook. Explain one Hospital A versus
Hospital B difference. Produce a baseline result and one plot.

**Day 2:** Compare unchanged predictions with at least one adjustment
under one simulated hospital change and two label budgets. Keep the
test outcomes separate from adjustment fitting.

**Day 3:** Repeat the comparison with different random seeds. Explain
one finding and one limitation. Prepare three slides for a five-minute
group presentation.

If time and skills allow, pick one [open research
question](../project/OPEN_RESEARCH_EXTENSIONS.md). You do not need to
finish every extension.

## Your five-minute presentation

1. **Question:** Which hospital change, label budgets, and methods did
   you compare?
2. **Evidence:** Show one readable plot and the number of repeated
   simulations. Describe what happened and how variable the results were.
3. **Conclusion:** Under which conditions did the adjustment help or
   hurt? What remains unknown and what would you test next?

A failure to improve is a valid result. Please do not claim that your
simulated results demonstrate safety for real patients.

## Questions to ask your team

- What is the difference between *ranking* and *calibration*?
- How many positive outcomes appear in a small audit? Is that enough
  to support a more flexible adjustment?
- What could remain wrong even if recorded inputs look the same?
- How would you know if your apparent improvement was due to chance?
- Which additional outcome data would help?

## After the school

Real MIMIC-IV data require separate access and a validated study
design. The [synthetic table adapter](MIMIC_TRANSLATION.md) demonstrates
how patients, admissions, vital signs, and lab tests relate, but does
not implement a real MIMIC-IV cohort extraction.
