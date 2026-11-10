# Mauritius healthcare module: current plan

**Event:** 16–20 November 2026  
**Presenter:** Alireza Vafaei Sadr  
**Delivery:** one remote lecture plus local student groups and remote mentoring

## Lecture

**When Can We Trust Clinical AI at a New Hospital?**

One integrated, approximately 60-minute lecture using a 48-hour
deterioration-risk example. Students learn why discrimination and
calibration differ, how hospital changes affect risk predictions,
which outcome labels are needed, and why recalibration needs
independent evaluation.

[PowerPoint](../slides/lecture_when_can_we_trust_clinical_ai.pptx) ·
[Presenter notes](ONE_LECTURE_PRESENTER_GUIDE.md) ·
[References](REFERENCES_AND_READING.md)

The original two longer lectures are background materials, not scheduled
sessions.

## Research project

**Question:** When do one-parameter and two-parameter calibration
updates help if a new hospital has few outcome labels?

Students compare an unchanged source model with intercept-only
and logistic (Platt) recalibration under multiple synthetic
shift mechanisms and label budgets of 25, 75 and 150.

**Day 1:** source/target data, baseline and plot.  
**Day 2:** paired method comparisons on independent target data.  
**Day 3:** repeated simulations, limitations and short report.

Students with time can design one additional experiment.

[Project](../project/THREE_DAY_RESEARCH_PROJECT.md) ·
[Notebook](../notebooks/92_three_day_research_starter.ipynb) ·
[Protocol](../project/RESEARCH_PROTOCOL.md) ·
[Facilitator runbook](FACILITATOR_RUNBOOK.md)

The teaching data are synthetic. Real MIMIC-IV analysis would need
approved access and an independently validated cohort pipeline.

## Dependencies and logistics

We need a local facilitator who can help with laptops and group work,
a confirmed number of students and their Python experience, and a
protected project slot for each day. Bruce proposed a progress
summary at 17:00–18:00 Mauritius time, equivalent to 08:00–09:00
US Eastern Standard Time in November.

The three-day success criterion is reproducible preliminary comparison
and a clear explanation of limitations. Publication remains a possible
subsequent goal, contingent on novelty and additional validation.
