# Team research extensions: one open question per group

The baseline code and new research notebook are intentionally easy to run.
**Running the provided comparison alone is not a three-day research project.**
After reproducing the baseline, each team must propose and investigate one
additional, falsifiable question. The extension should change *one study
factor at a time*, keep an independent test cohort, and compare against the
unchanged-model baseline using paired differences.

Each team records the hypothesis and proposed evaluation before opening the
results. A negative result is acceptable.

## Extension A: Which 75 patients should we label?

**Question:** If outcome labels are costly, is a random audit of 75 target
admissions better or worse than an audit concentrated on particular risk ranges?

**Hypothesis to test:** Selecting cases near a risk threshold can give useful
information for some tasks but may bias a global calibration update if the
audit selection mechanism is ignored.

**Student work:**
- Keep the fixed target calibration pool and independent target test cohort.
- Compare random selection versus a pre-specified score-stratified selection.
- Fit the same intercept correction using each label set.
- Evaluate on the same independent target test data.
- Examine whether the audit's risk distribution differs from the full target.
- Consider whether sampling weights would be required for population-level
  calibration. Do not assert weighted correction works without testing it.

**Risk:** If teams cherry-pick labels based on known outcomes, the exercise
becomes label leakage and the comparison is not valid.

## Extension B: Do combinations of shifts change the answer?

**Question:** Does a method that performs well under a single simulated
baseline-risk change still help if measurement or missingness patterns change
at the same time?

**Student work:**
- Choose one baseline shift and one additional pre-defined mechanism.
- Use the same model and label budgets as the core experiment.
- Compare paired test Brier differences against the single-shift result.
- Explain why input drift may or may not detect the combined problem.

**Risk:** A combined shift can change several statistical relationships.
Do not interpret the result as an isolated causal effect.

## Extension C: Does a review budget help?

**Question:** Under a hypothetical 20% review capacity, can a model-uncertainty
rule select cases for review more effectively than random selection?

**Student work:**
- Choose a fixed threshold-based or bootstrap-disagreement-based rule.
- Define the referral fraction before examining target evaluation outcomes.
- Compare retained-patient performance and group composition against random
  referral on the same target test patients.
- Report the 20% workload and the error rate among the 80% retained.

**Risk:** Reduced error among retained cases does NOT prove the overall
clinical pathway is safer. The impact of human intervention is not modeled.

## Extension D: What happens to small subgroups?

**Question:** Do 25, 75, and 150 random target audit labels provide enough
information to recalibrate a small subgroup reliably?

**Student work:**
- Create two pre-specified subgroup proportions with the existing simulator.
- Count labeled subgroup observations and events for each audit.
- Compare global and group-specific calibration summaries on independent
  target test data.
- If attempting subgroup-specific updates, report when a fit is impossible
  or unstable.

**Risk:** Do not present a calibration gap as a clinical equity conclusion.
Sparse groups require uncertainty and a larger validation design.

## Minimum three-day workflow

- **Day 1:** Reproduce the provided negative-control and one-shift results.
  Choose one extension and write a two-sentence hypothesis.
- **Day 2:** Implement the new comparison. Keep all outcome labels used for
  fitting separate from the independent evaluation set.
- **Day 3:** Repeat across seeds, summarize paired differences, produce one
  new figure, and explain whether evidence supports the hypothesis.

Teams can use the supplied project/research_experiments.py as a starting
point. **The extension code is intentionally not provided as a solution.**
Different groups may choose different methods and reach different results.

## What counts as meaningful progress?

A reproducible new experiment, a valid comparator, one honest figure,
and an explanation of its limitations. Even if the new method fails,
identifying the failure mechanism may be a useful research contribution.

A publication would require further literature review, substantially
more experimental precision, and validation beyond the current simulator.
