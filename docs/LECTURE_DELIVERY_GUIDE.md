# Tuesday lecture delivery guide

**Lecture:** When Can We Trust Clinical AI at a New Hospital?

**Presentation:** [Tuesday lecture PDF](../slides/Tuesday_lecture_integrated.pdf) (23 pages)

**Full presenter notes:** [Slide-by-slide guide](ONE_LECTURE_PRESENTER_GUIDE.md)

**Format:** Remote. Plan approximately 45 minutes of teaching and interactive checks in the 60-minute Tuesday slot. Reserve the remaining time for questions and the project handoff.

## Sequence

| Slide pages | Theme | Main point |
| --- | --- | --- |
| 1-7 | The meaning of a 30% prediction | AUROC ranks patients, whereas calibration asks whether stated probabilities match observed frequencies. The Brier score evaluates probabilistic predictions. |
| 8-11 | Hospital transfer | Changes in the relationship between observed inputs and outcomes may occur without detectable changes in input distributions. |
| 12-15 | Uncertainty and subgroup limits | Bootstrap disagreement is a proxy for model uncertainty, not an assured drift detector. Missingness and subgroup behavior may differ by site. |
| 16-18 | Recalibration with few outcomes | Intercept and Platt updates are established methods. Small local outcome samples can make corrections unstable. |
| 19-23 | Valid evaluation and student project | Audit labels fit an update. Independent target outcomes evaluate the update. The core project has two scenarios and two label budgets. |

## Teaching checks

- Use slide 7 for a short student or chat discussion. Answers are in the presenter guide.
- On slide 17, the event-rate margins are not uncertainty intervals for recalibration parameters.
- On slide 19, repeated audits on one independent test cohort show variation across audits, not confidence intervals for all possible hospitals.
- On slide 20, the 25, 75, or 150 audited admissions are **selected from** the 1,600-record Hospital B calibration pool. There are three independent cohorts in the full protocol: source, target calibration pool, and target test cohort. The orientation exercise does not contain an independent target test cohort.
- On slide 22, Wednesday is baseline reproduction, Thursday is comparison, and Friday is interpretation and a three-slide presentation.

## Student handoff

Use the [short student workflow](SHORT_STUDENT_WORKFLOW.md) and [Colab notebook 92](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb).

The minimum compares unchanged predictions with intercept-only recalibration in two scenarios (negative control and baseline-risk shift), using 25 or 75 local outcome labels. Platt, 150 labels, additional scenarios, and independent research hypotheses are optional extensions. All data are synthetic.

Students can ask questions through the project messaging channel once they have been invited to the workshop Slack workspace. The remote mentor is in US Eastern time and cannot attend Mauritius morning standups that fall around midnight Eastern. Do not assume an in-room facilitator has been assigned.

## Reproducibility note

The distributed PDF is the reviewed teaching version. If a slide generator is retained, verify that its output matches the reviewed PDF before claiming source-to-artifact synchronization. The workshop does not claim clinical validation or methodological novelty.