# Mauritius workshop: local facilitator and remote mentor runbook

**Use with:** [student start guide](STUDENT_START_HERE.md) and
[three-day project](../project/THREE_DAY_RESEARCH_PROJECT.md).

This schedule assumes **approximately 2–3 hours of protected project work
per day**, not full-day research immersion. The final allotment, student
numbers, and in-room contact need confirmation from the organizers.

## Before students arrive

1. Have one local technical facilitator with projector, Wi-Fi, and
   video-call access. Identify a second helper if groups are large.
2. Open the [three-day research notebook](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb) in **a fresh Colab session**. Confirm
   the first cells fetch the repo and print 4,000 source records,
   1,600 unlabeled target records, and 75 audit labels.
3. Run the quick research comparison on a regular CPU, confirm
   it writes a paired summary and figure, and keep screenshots
   for a network failure.
4. Give each group a folder to save its notebook, code, one figure,
   and three-slide report. Ensure names do not contain personal data.
5. Confirm with Bruce when the remote instructor will join and when
   students will be in the room. A 17:00–18:00 Mauritius progress
   summary is 08:00–09:00 US Eastern Standard Time in November.
6. Keep the two older lecture notebooks as background only.
   The current project uses the **92** notebook.

## One-minute explanation to read aloud

"We will use a fictional hospital-risk model to study whether simple
probability corrections work at a new hospital. On Day 1, we learn
the data and reproduce a baseline. On Day 2, we compare methods.
On Day 3, we repeat the analysis and present one clear finding.
We are not developing a clinical tool."

## Day 1: ~120 minutes

| Time | What happens | Facilitator check |
| --- | --- | --- |
| 0–15 min | Short reminder of the question and instructions | Everyone opens the correct notebook |
| 15–40 min | Run Colab and inspect source/target data | Teams can explain which outcomes are hidden |
| 40–75 min | Read baseline results and one plot | Students can distinguish AUROC and calibration |
| 75–105 min | Assign a specific comparison and define a hypothesis | No use of test outcomes for model fitting |
| 105–120 min | Share one result and one question | Save notebook and record blockers |

## Day 2: ~120 minutes

| Time | What happens | Facilitator check |
| --- | --- | --- |
| 0–15 min | Recall the hypothesis | The comparison has an unchanged baseline |
| 15–60 min | Test correction methods at two label budgets | Same independent test set per comparison |
| 60–95 min | Compare paired Brier differences and audit event counts | Report non-estimable small-audit fits |
| 95–120 min | Decide on one extra comparison, if time | Keep the extension small enough to complete |

## Day 3: ~120 minutes

| Time | What happens | Facilitator check |
| --- | --- | --- |
| 0–45 min | Repeat simulations with more random seeds | Seeds and sample sizes are recorded |
| 45–75 min | Prepare figure and results table | No misleading confidence-interval labels |
| 75–105 min | Five-minute group presentations | Require evidence, comparison and limitation |
| 105–120 min | Discuss next experiments and share code | Collect the report and reproducible notebook |

## If students are new to Python

Use the prewritten baseline notebook. Ask them to explain a plot and
change **one variable** (label budget or simulated shift) rather than
writing a new method from scratch. Completing the minimum analysis is
more valuable than unfinished complex code.

## If students are advanced

Assign one of the four [extensions](../project/OPEN_RESEARCH_EXTENSIONS.md).
The students must propose and implement their own comparison and
record a hypothesis before inspecting new results. Extensions C and D
require substantially more statistical or programming support.

## If the internet or Colab fails

Show the pre-generated synthetic plots and results. Have groups reason
through which predictions should be trusted and how they would test
a calibration update. Do not replace unavailable computations with
invented numerical results.

## Do not allow these research mistakes

- Fitting and evaluating a correction on the same audit labels.
- Calling a percentile range a formal confidence interval.
- Declaring an approach best from one random seed.
- Treating Brier improvements as a proof of safer patient care.
- Interpreting synthetic subgroup labels as real race, ethnicity, or sex.
- Calling the toy data a validated copy of MIMIC-IV.
- Changing several scenario assumptions and attributing the result to
  only one without an appropriate comparison.

## Daily progress report for the remote mentor

Each group shares three short items:
- Completed: baseline/contrast, seed count, one figure.
- Blocker: precise error or scientific question.
- Next step: one achievable test.

Use the daily summary to prioritize help, not to score student groups.
