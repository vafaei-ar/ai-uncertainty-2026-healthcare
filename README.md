# When Can We Trust Clinical AI at a New Hospital?

**Healthcare research module | AI & Uncertainty School, Mauritius | 16–20 November 2026**

This module asks a practical question: when a clinical risk model is
transferred from Hospital A to Hospital B, how can we check its probability
estimates if Hospital B has few known outcomes?

We use **synthetic EHR-like data only**. The model and results are
educational. They are not validated for patient care.

## Start here

**For students**
- [Open the research notebook now (pre-merge preview)](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/chatgpt/mauritius-one-lecture-three-day-research-2026/notebooks/92_three_day_research_starter.ipynb)
- [Student guide and data dictionary](docs/STUDENT_START_HERE.md)
- [Open the notebook after PR #2 is merged](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb)
- [Three-day project question and milestones](project/THREE_DAY_RESEARCH_PROJECT.md)
- [Research protocol and comparison definitions](project/RESEARCH_PROTOCOL.md)
- [Optional team research questions](project/OPEN_RESEARCH_EXTENSIONS.md)

**For the lecturer and local facilitator**
- [Single integrated lecture, 23-slide PowerPoint](slides/lecture_when_can_we_trust_clinical_ai.pptx)
- [Slide-by-slide teaching notes](docs/ONE_LECTURE_PRESENTER_GUIDE.md)
- [Local facilitator and remote mentor runbook](docs/FACILITATOR_RUNBOOK.md)
- [Scientific references and further reading](docs/REFERENCES_AND_READING.md)

The current programme uses **one introductory lecture and three days of
student research**. Exact timings and local support will be confirmed
with the organisers.

## What students will study

Hospital A develops a model that predicts deterioration within 48 hours.
Hospital B wants to use it, but only a small number of local outcomes
are available. Students compare an unchanged model with two simple
calibration updates:

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
| 1 | Understand the data and model, reproduce the baseline | One baseline table or plot |
| 2 | Compare at least one calibration update across two label budgets | Paired method comparison |
| 3 | Repeat simulations, explain failure cases, present findings | One figure and three-slide group report |

The [facilitator runbook](docs/FACILITATOR_RUNBOOK.md) offers a practical
two-hour daily schedule and a fallback for participants new to Python.

## Data and code

| Path | Content |
| --- | --- |
| `medsim/` | Synthetic clinical-risk data generator and metrics |
| `project/generate_open_challenge.py` | Original 4,000 / 1,600 / 75 scenario |
| `project/research_experiments.py` | Repeatable independent-test experiments |
| `project/mimic_like_adapter.py` | Toy relational patients/admissions/vitals/labs tables |
| `notebooks/92_three_day_research_starter.ipynb` | Main student notebook |
| `slides/src/one_lecture.js` | Editable integrated PowerPoint source |

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

The original two lecture decks, optional PyMC/SBI exercises, and
two-hour challenge are retained for supplementary learning. See the
[archived programme description](docs/archive/README.md).
