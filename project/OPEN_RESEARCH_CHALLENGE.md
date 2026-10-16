# Open research challenge: when should a clinical risk model be trusted at a new hospital?

AI & Uncertainty School and Workshop 2026 | Healthcare module

**Length:** 2 hours of core team work, with an optional third hour and short presentations.
**Assessment:** exploratory, no formal grading, no fixed correct answer.
**Data:** entirely synthetic EHR-like admissions, never used for clinical decisions.

## The question

Hospital A has trained a model to predict whether a patient will deteriorate in the first 48 hours after admission. Hospital B wants to use it, but its patients and its clinical data recording practices may differ. The model is currently in **shadow mode**: nobody sees or acts on its predictions.

**How much evidence is enough to decide when to trust, recalibrate, defer, or withhold the model at Hospital B?**

There may be **no method that can guarantee safe transfer under arbitrary conditional shift with only unlabeled target data**. Identifying this limitation and designing what to measure next is as valuable as fitting a better model.

## The data students receive

Generated reproducibly by project/generate_open_challenge.py and stored in project/open_data:

| File | What it contains |
| --- | --- |
| development.csv | 4,000 labeled synthetic hospital-A admissions |
| new_hospital_unlabeled.csv | 1,600 hospital-B admissions; **no target outcomes** |
| audit_labels.csv | Outcome labels for a random audit of **75** of those 1,600 records |
| instructor_outcomes_for_debrief.csv | Target outcomes for **post-project debrief only**; do not use during exploration |

The records have routine vital signs, lab values, comorbidities and a binary deterioration outcome. The observed records were generated with a transparent simulator that can vary outcome risk, missingness, measurement error and subgroup relationships. They are **not** a validated reproduction of MIMIC-IV. The point is methodological reasoning, not biomedical realism.

Open the student notebook: notebooks/91_open_research_challenge_starter.ipynb.

## Constraints for the exercise

- There is a provisional **20% additional clinical-review budget** for new admissions; this is a resource limit, not a guarantee that review prevents harm.
- Your team can use the source data, all **unlabeled** target features, and only the 75 audit outcomes during your investigation.
- The 75 labels were selected at random. They may give weak evidence about rare patients or subgroups.
- If you tune an intervention on the 75 labels, evaluating it on those same 75 is optimistic. Report that limitation.
- You may train or refit a model, update calibration, define abstention, or conclude more monitoring is necessary. You may also propose how the next 50-100 target outcomes should be collected.
- Because this is a simulated case, recommendations are **not** clinical guidance.

## Questions for teams

1. **Evidence.** What is reassuring and what is concerning? Which checks need outcomes? Show one plot/table with an honest indication of uncertainty.
2. **Decision.** Should the model remain in shadow mode, be recalibrated, be used only with review, or not be deployed? Explain how many patients your review rule would affect.
3. **Unknowns.** Which changes cannot be ruled out by the available evidence? What additional outcomes or measurements would change your recommendation? What would trigger a pause?

**Do not optimise only AUROC.** Calibration, subgroups, missingness, cost of action, and consequences of uncertainty matter too. Methods are not prescribed; different well-reasoned recommendations are welcome.

## Suggested session (adjustable to Bruce's programme)

| Time | Activity |
| --- | --- |
| 0-15 minutes | Explain the 48-hour prediction task and data access limits |
| 15-40 minutes | Look at development and target data; build a baseline if useful |
| 40-75 minutes | Investigate uncertainty, calibration, monitoring or a review rule |
| 75-100 minutes | Choose a defensible recommendation and label-collection plan |
| 100-120 minutes | Prepare three slides, compare remaining uncertainties |
| Optional hour | Try alternative methods, group debrief and short presentations |

**Five-minute presentation:** one slide on evidence, one on proposed action, and one on assumptions/next labels.

## Instructor debrief

Once teams finish, use instructor_outcomes_for_debrief.csv to discuss what can change when unseen outcomes are made available. Do not score teams based on whether they guessed the synthetic generating parameters. A good negative conclusion ("not enough evidence to go live") is legitimate.

The existing six-team project in PROJECT_BRIEF.md remains available as a **guided backup**. It is useful if the group prefers a more structured exercise, but it is not the default open research challenge.

## Logistics

Students need a browser and a Python-capable Colab session, not MIMIC credentials. If delivered remotely, the activity needs an in-room facilitator to help groups while the lecturer joins by video. Exact timing and the remote arrangement still require organiser confirmation.
