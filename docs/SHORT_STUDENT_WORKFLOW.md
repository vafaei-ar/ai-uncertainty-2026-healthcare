# Short three-day student pathway

**AI & Uncertainty School, Mauritius | Synthetic data only | No GPU needed**

## Your research question

A risk model developed at Hospital A predicts deterioration within 48 hours. At Hospital B, patients or clinical practices may differ. Can a small number of local outcomes help correct the model's probabilities?

**Required minimum:** Compare unchanged predictions against **intercept-only recalibration**, in **negative_control** (no hospital change) and **baseline_risk** (higher risk at Hospital B), with **25 and 75** target outcome labels. Repeat the comparisons and explain the results.

**Optional extensions:** Platt recalibration, 150 outcome labels, measurement noise, subgroup interaction, informative missingness, or one new falsifiable question. The full protocol keeps all three methods, five scenarios and three label budgets.

## Open the notebook

[Open notebook 92 in Google Colab](https://colab.research.google.com/github/vafaei-ar/ai-uncertainty-2026-healthcare/blob/main/notebooks/92_three_day_research_starter.ipynb).

You can use the notebook without writing a model from scratch. Run its cells in order using a CPU runtime. The first cell clones the workshop code and installs dependencies. It should say **Workshop simulation ready**.

The fixed orientation example has **4,000 labeled Hospital A records**, **1,600 Hospital B records**, and **75 revealed Hospital B outcomes**. Those 75 labels are not an independent evaluation set.

### Simulation sizes

| Step | Hospital A source | Hospital B calibration pool | Target labels for updating | Independent test |
| --- | ---: | ---: | --- | ---: |
| Orientation example | 4,000 | 1,600 | 75 revealed | None |
| Fast notebook experiment | 2,000 | 1,600 | 25, 75, 150 | 1,200 |
| Full study | 4,000 | 1,600 | 25, 75, 150 | 2,400 |

Each simulated replicate generates new cohorts. Never reuse the orientation labels as the final evaluation set.

## Minimum workflow

| Day | Approximate work time | Task | Save |
| --- | --- | --- | --- |
| **1: Understand** | 45 to 60 minutes | Run the notebook, inspect the record counts and the unchanged baseline, and write one prediction. | Your notebook and baseline result |
| **2: Compare** | 45 to 75 minutes | Run the full Day 2 calculation. Use the notebook's **Minimum comparison** cell to display the four required intercept versus unchanged comparisons. | The four-row table and paired Brier figure |
| **3: Repeat and explain** | 45 to 75 minutes | Try increasing `repeats=3` to `repeats=8`, interpret the variability, and prepare three slides. | One figure, one limitation and a reproducible notebook |

The supplied Day 2 computation evaluates the complete grid. **The minimum comparison cell filters the already computed results.** It does not change which models are fitted. The full grid remains available for more advanced groups.

## Reading the results

The paired Brier change is the updated model's Brier score minus the unchanged model's score **on the same independent target test patients**. Negative values favor updating. Positive values favor leaving the model unchanged.

The figure reports averages across simulated replicates. Three or eight replicates provide only preliminary descriptive evidence, not a reliable confidence interval or proof that one method is universally better.

The `fraction_replicates_improved` column shows how often the correction helped in the simulated repeats. Treat it cautiously when the number of repeats is small.

## Use AI for help, not for invented answers

You can ask Colab's AI assistant, if available, to explain Python code and error messages. Run every suggested change yourself. Do not copy numerical results that the assistant invents, and do not share actual patient data.

A useful question is: "Explain this Colab error, suggest the smallest code change, and tell me how to check it. Do not mix the audit outcomes used for recalibration with the independent test outcomes."

If the Colab assistant is unavailable, the prepared cells still work without it.

## Final presentation: five minutes, three slides

1. **Question:** Your comparison, outcome budgets and prediction.
2. **Evidence:** One paired Brier figure, number of repeats, and whether updating helped or hurt.
3. **Meaning:** One limitation, what remains uncertain, and one next experiment.

For daily progress updates, provide one result, one question or blocker, and your next action in less than one minute.

## Going further

Simply running the supplied notebook is an **educational exercise, not an original research result**. If you want to contribute to a research extension, write one falsifiable hypothesis before examining new results. Change one factor at a time, preserve an independent test cohort, and compare with the unchanged baseline. See [Team research extensions](../project/OPEN_RESEARCH_EXTENSIONS.md).

## Scientific boundaries

- Use only synthetic data. These results do not validate a clinical model.
- Audit labels can fit a correction, but they cannot also serve as an independent test.
- Do not select a winning method using test outcomes and then describe that test as unbiased.
- A null or unfavorable result can be informative.
- The synthetic tables are only MIMIC-inspired, not a copy of MIMIC-IV.
