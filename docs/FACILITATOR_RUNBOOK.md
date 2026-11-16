# Mauritius workshop: local facilitator and remote mentor runbook

**Use with:** [student start guide](STUDENT_START_HERE.md) and
[three-day project](../project/THREE_DAY_RESEARCH_PROJECT.md).

The required minimum can fit shorter sessions of approximately 45 to 75 minutes each day. The detailed schedule below shows an optional 120-minute session if protected time is available. The final allotment and in-room technical support need confirmation from the organizers. The [short student workflow](SHORT_STUDENT_WORKFLOW.md) defines the minimum.

## Before students arrive

1. If available, arrange a local technical facilitator with projector,
   Wi-Fi and video-call access. The organizer should confirm who can help
   groups on site.
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

## Confirmed workshop sequence and remote support

Monday 16 November is the project introduction and initial team organization. Tuesday 17 November is the clinical AI lecture. Student research is scheduled for Wednesday 18 through Friday 20 November, with final presentations on Friday afternoon. Thursday has other programmed activities, so the required minimum should be achievable in a shorter session. Keep the optional 120-minute session blocks below only when time is available.

The remote mentor is in the US Eastern time zone. Early morning Mauritius meetings occur around midnight Eastern and should not require the mentor to attend live. Identify a student group contact and use a mutually accessible messaging channel for one result, one blocker and the next action. A local coordinator should help with Colab and group logistics where available. Do not assume that such a coordinator has already been assigned.

## One-minute explanation to read aloud

"We will use a fictional hospital-risk model to study whether a simple
probability correction works at a new hospital. On Day 1, we learn
the data and reproduce a baseline. On Day 2, we compare unchanged
and intercept-only risks in two scenarios with 25 or 75 local labels.
On Day 3, we repeat the analysis and present one clear finding.
We are not developing a clinical tool."

## Wednesday, 18 November: Day 1 (optional 120-minute session)

| Time | What happens | Facilitator check |
| --- | --- | --- |
| 0–15 min | Short reminder of the question and instructions | Everyone opens the correct notebook |
| 15–40 min | Run Colab and inspect source/target data | Teams can explain which outcomes are hidden |
| 40–75 min | Read baseline results and one plot | Students can distinguish AUROC and calibration |
| 75–105 min | Assign a specific comparison and define a hypothesis | No use of test outcomes for model fitting |
| 105–120 min | Share one result and one question | Save notebook and record blockers |

## Thursday, 19 November: Day 2 (keep the minimum short)

| Time | What happens | Facilitator check |
| --- | --- | --- |
| 0–15 min | Recall the hypothesis | The comparison has an unchanged baseline |
| 15–60 min | Filter the notebook output to unchanged versus intercept with 25 and 75 labels in two scenarios | Same independent test set per comparison |
| 60–95 min | Compare the four paired Brier differences and discuss audit event counts | Do not interpret three repetitions as precision estimates |
| 95–120 min | Decide on one extra comparison, if time | Keep the extension small enough to complete |

## Friday, 20 November: Day 3 (finish before presentations)

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

Each group shares three short items in a shared channel, without requiring a live midnight US call:
- Completed: baseline/contrast, seed count, one figure.
- Blocker: precise error or scientific question.
- Next step: one achievable test.

Use the daily summary to prioritize help, not to score student groups.
