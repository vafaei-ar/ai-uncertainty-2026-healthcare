# When Can We Trust Clinical AI at a New Hospital?

**Healthcare research module | AI & Uncertainty School, Mauritius | 16–20 November 2026**

This module asks a practical question: when a clinical risk model is
transferred from Hospital A to Hospital B, how can we check its probability
estimates if Hospital B has few known outcomes?

We use **synthetic EHR-like data only**. The model and results are
educational. They are not validated for patient care.

## Start here

**Presentations (PDF)**
- [Monday project introduction, 5 slides](slides/Monday_Project_Introduction.pdf)
- [Tuesday lecture, 23 slides](slides/Tuesday_lecture_integrated.pdf)

**For students**
- [Student guide and data dictionary](docs/STUDENT_START_HERE.md)
- [Short three-day student pathway (required minimum)](docs/SHORT_STUDENT_WORKFLOW.md)
- [Open the three-day research notebook in Google Colab](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb)
- [Three-day project question and milestones](project/THREE_DAY_RESEARCH_PROJECT.md)
- [Research protocol and comparison definitions](project/RESEARCH_PROTOCOL.md)
- [Optional team research questions](project/OPEN_RESEARCH_EXTENSIONS.md)

**For the lecturer and local facilitator**
- [Tuesday lecture PDF](slides/Tuesday_lecture_integrated.pdf)
- [Monday presentation script](docs/MONDAY_PRESENTER_GUIDE.md)
- [Slide-by-slide teaching notes](docs/ONE_LECTURE_PRESENTER_GUIDE.md)
- [Local facilitator and remote mentor runbook](docs/FACILITATOR_RUNBOOK.md)
- [Scientific references and further reading](docs/REFERENCES_AND_READING.md)

The programme uses **a Monday project introduction, one Tuesday lecture, and student research on Wednesday 18 through Friday 20 November**. Monday introduces the project before students hear the technical lecture. The student workflow requires no live Colab demonstration on Monday. Local support and meeting links are arranged with the organizers.

## What students will study

Hospital A develops a model that predicts deterioration within 48 hours.
Hospital B wants to use it, but only a small number of local outcomes
are available. The **minimum exercise** compares unchanged predictions with intercept-only recalibration in two scenarios (negative control and baseline-risk shift), using 25 and 75 target labels. The **full protocol** compares an unchanged model with two calibration updates:

- Intercept-only update: move predicted probabilities up or down.
- Logistic (Platt) update: adjust both level and spread of the risks.

Using repeated synthetic simulations, students test audit sizes of
**25, 75, and 150** and several distinct hospital changes. They
evaluate methods on **independent synthetic test outcomes**, not the
labels used for updating.

The primary outcome is the **paired change in Brier score**. A smaller
Brier score means that predicted probabilities are closer, on average,
to observed binary outcomes.

The practical goal is a reproducible comparison, one clear figure,
and a transparent discussion of where methods help or fail.
[Team extensions](project/OPEN_RESEARCH_EXTENSIONS.md) allow students
to investigate questions not answered by the starting analysis.

## Three-day schedule

| Day | Main activity | Minimum output |
| --- | --- | --- |
| Wed 18 | Understand the data and model, reproduce the baseline | One baseline table or plot |
| Thu 19 | Compare unchanged versus intercept in two scenarios with 25 and 75 outcomes | Four paired Brier comparisons |
| Fri 20 | Repeat simulations, explain failure cases and present findings | One figure and three-slide group report |

The [facilitator runbook](docs/FACILITATOR_RUNBOOK.md) offers a practical
45–75 minute daily minimum and a fallback for participants new to Python.

## Data and code

| Path | Content |
| --- | --- |
| `medsim/` | Synthetic clinical-risk data generator and metrics |
| `project/generate_open_challenge.py` | Original 4,000 / 1,600 / 75 scenario |
| `project/research_experiments.py` | Repeatable independent-test experiments |
| `project/mimic_like_adapter.py` | Toy relational patients/admissions/vitals/labs tables |
| `notebooks/92_three_day_research_starter.ipynb` | Main student notebook |
| `slides/src/one_lecture.js` | Earlier lecture generator, not yet reconciled with the reviewed PDF |

Local execution, from the repository root:

```bash
python -m pip install -r requirements.txt
python -m project.research_experiments --repeats 8
```

The command saves a detailed table, a paired comparison summary,
and an example figure under `project/results/`. Checked-in results
with only **three repetitions are demonstration output**, not
publication-quality estimates.

## Connection to MIMIC-IV

The synthetic records include age, vital signs, laboratory measurements,
and medical-history indicators familiar to clinical EHR research. The
[MIMIC-inspired adapter](docs/MIMIC_TRANSLATION.md) demonstrates simplified
joins between toy relational tables. It **does not** reproduce the
real MIMIC-IV schema, item identifiers, observation windows, or clinical
outcomes.

Applying these workflow ideas to real MIMIC-IV data later will require
separate approved access and validated cohort and outcome definitions.

## Limits and possible next study

Recalibration and hospital-transfer evaluation are established research
topics. A manuscript would require a defensible new contribution,
additional independent experiments, and preferably evidence beyond
this single simulator. The workshop is intended to produce preliminary
analyses and research questions, not a finished paper.

The original two lecture source scripts, optional PyMC/SBI exercises, and
two-hour challenge materials remain for supplementary learning. The reviewed
PDFs are authoritative for the workshop. The retained slide generator may
not reproduce the current Tuesday PDF until its code is reconciled. See the
[archived programme description](docs/archive/README.md).
