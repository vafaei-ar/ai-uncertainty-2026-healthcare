# Three-day research project: When Can We Trust Clinical AI at a New Hospital?

**AI & Uncertainty School and Workshop | Mauritius | November 16–20, 2026**
**Mode:** in-person student teams with a remote research mentor; an in-room facilitator is needed.
**Status:** proposed project, not a clinical validation study or guaranteed publication.

## The question

Hospital A has trained a model that predicts deterioration within 48 hours.
Hospital B wants to use it, but it has few known outcomes. Under what changes
between hospitals, and with how many new outcome labels, does recalibration
improve the model rather than make it worse?

The students will study **probability reliability under hospital transfer with
limited target labels**. This question is narrower and more testable than
"make the AI safe." No simulation establishes clinical safety.

## Why this is research, rather than only a classroom exercise

The existing open challenge uses one source cohort, one new-hospital cohort,
and 75 audit outcomes. A single result cannot show whether a method works
reliably. The research extension makes **paired comparisons across repeated
synthetic experiments** with independent evaluation outcomes.

**Methods:** unchanged source model, intercept-only recalibration, logistic
(Platt) recalibration. Students may propose a fourth method after completing
the core study.

**Conditions:** negative control with no simulated change, baseline-risk shift,
measurement noise, changed subgroup relationship, and informative missingness.

**Label budgets:** 25, 75, and 150 randomly audited target outcomes.

**Primary endpoint:** paired change in Brier score on an independently generated
target-hospital test cohort. Lower is better.

**Supporting outcomes:** AUROC, expected calibration error, calibration-in-the-large
gap, and within-group mean risk calibration gaps. These are predictive metrics,
not clinical utility or fairness guarantees.

The study varies **one mechanism at a time** to make interpretation easier.
Real hospital changes may overlap and evolve over time.

## Three-day plan

| Day | Activities | Minimum output |
| --- | --- | --- |
| **1. Understand and reproduce** | Short common lecture, inspect the provided synthetic EHR-like data, define the target prediction task, train the unchanged model, and reproduce one negative-control and one shifted-site result. | An independent-test baseline table and one plot with a brief interpretation |
| **2. Compare methods** | Run intercept-only and Platt recalibration under multiple target label budgets. Record replicates, audit event counts, calibration failures, and alternative explanations. Keep the target test outcomes separate from recalibration fitting. | Reproducible comparison on at least two shift conditions and two label budgets |
| **3. Stress-test and present** | Expand to more seeds or one additional shift. Compare paired changes rather than isolated scores. Discuss small-audit uncertainty and subgroup limits. Prepare a 5-minute report. | One main figure, a short results table, main limitations, and concrete next experiments |

A team that starts slowly can finish a defensible minimum using **one
negative control, one real shift, two methods, and two label budgets**.
Advanced teams may run all five scenarios, all three budgets, and add an
uncertainty-based deferral analysis. Prioritize interpretable results over the
number of methods.

## How to begin

1. Open the integrated lecture and the new notebook:
   - slides/lecture_when_can_we_trust_clinical_ai.pptx
   - notebooks/92_three_day_research_starter.ipynb
2. Read project/RESEARCH_PROTOCOL.md before interpreting results.
3. Run the experiment in Colab or from the repository root:

       python -m project.research_experiments --repeats 8

4. Inspect project/results/method_results.csv and project/results/paired_summary.csv.
5. Use the plot to describe when each calibration method improves or worsens Brier score.

The notebook includes a shorter live demonstration. The full experiment
script supports reproducible repetitions and does not require a GPU.

## Datasets and the MIMIC bridge

The teaching data are synthetic, with clinical variables such as age, blood
pressure, heart rate, creatinine, lactate, white blood cell count, and medical
history. They are **not MIMIC-IV records or a validated statistical
reproduction of MIMIC-IV**.

The adapter in project/mimic_like_adapter.py shows how to represent a small
subset of these records in **MIMIC-inspired patients, admissions, chartevents,
labevents, and diagnoses tables**, then reconstruct analysis features. It uses
synthetic identifiers and item codes rather than official MIMIC item IDs.

Students can later apply the same *workflow ideas* to real MIMIC data, after
obtaining access and developing validated clinical cohort and outcome
definitions. See docs/MIMIC_TRANSLATION.md.

## Independence and outcome access

For the original 75-label challenge, students should use only:
- development.csv: labeled Hospital A training data
- new_hospital_unlabeled.csv: target features, **no outcomes**
- audit_labels.csv: random 75 target outcome labels

The public repository no longer distributes all Hospital B outcomes in a
student-accessible CSV. The simulator can regenerate the synthetic scenario
for an instructor-led debrief.

For the research experiment, the code simulates a separate target evaluation
cohort and NEVER fits or selects a method using its outcomes. Evaluation
outcomes are used only to calculate the requested metrics. Students can inspect
the open code, so this is a **reproducible simulation**, not a blinded challenge.

## Team report and success criteria

Each group gives a five-minute report with three slides:
1. **Question and comparison:** tested shift, data, methods, budget.
2. **Results:** paired Brier comparison and one supporting measure or uncertainty display.
3. **Interpretation and next step:** where the method failed, what is uncertain,
   and one test required before a stronger research claim.

**Success in three days:** a working, reproducible baseline-versus-alternative
comparison, one clear figure, and a scientifically defensible discussion of
limitations. A publishable methodological paper is a **possible subsequent
goal**, contingent on novelty assessment, further replicates, broader
scenarios, and ideally external data validation. No publication is promised.

## Facilitation and remote logistics

- A local facilitator circulates among teams, collects errors, and checks that
  students run the same study definitions.
- Teams commit code or share notebooks daily.
- A 17:00 or 18:00 Mauritius summary corresponds to 08:00 or 09:00 EST
  for the remote mentor in November.
- The mentor needs the main plots and blockers before each summary call.
- The number and experience level of students, session duration, and local
  facilitator are still to be confirmed by the organizers.

## Do not claim

- That synthetic results establish clinical validity or patient safety.
- That MIMIC-inspired tables replicate MIMIC-IV's clinical content.
- That a calibration method is universally superior.
- That an observed improvement on one simulated seed is generalizable.
- That observing an unchanged AUROC proves deployment readiness.
