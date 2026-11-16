# Presenter notes: When Can We Trust Clinical AI at a New Hospital?

**AI & Uncertainty School 2026, Mauritius. Tuesday 17 November 2026.**

**Reviewed presentation:** [Tuesday lecture (PDF)](../slides/Tuesday_lecture_integrated.pdf)

**Timing:** approximately 45 minutes of teaching and interaction in a 60-minute slot, leaving time for questions. Figures and clinical examples use synthetic data only.

These notes follow all 23 pages of the reviewed lecture PDF. The PDF version corrects slide 20 to show that the calibration audit is a subset of the Hospital B pool.

## Slide 1: When Can We Trust Clinical AI at a New Hospital?

1 min. Introduce yourself and the plan: about 45 minutes of lecture with two short pauses for answers, then questions and the start of the project. Every patient, hospital and number comes from the simulator in the course repository. Nothing in this lecture is evidence about a real clinical model.

## Slide 2: Patient 417: the model says 30% risk

2 min. Patient 417 is a synthetic admission from Hospital A's validation set. The model is a logistic regression trained on 5,600 simulated admissions, with validation AUROC 0.73.

Ask: "What does 30% mean to you?" Take two or three answers. Steer toward the frequency reading: among many patients given 30%, about 30 in 100 should deteriorate. It is not the model's confidence in a diagnosis, and it is not an instruction to act. A weather forecast is a good comparison: it should rain on about 30% of the days that get a 30% forecast.

## Slide 3: Five questions, then your project

1 min. Read the five questions quickly. Tell students that each part ends in something they will do in the project: compute a Brier score, simulate a hospital change, fit an intercept or Platt update, and compare methods on independent test patients.

## Slide 4: Ranking patients and stating the right risk are different skills

2 min. Explain the pair game for AUROC in words before naming the metric. Then calibration as the frequency check from the previous slide.

Key point: AUROC is unchanged by any transformation that keeps the order of the scores. A model can rank perfectly and still state risks that are far too high or too low. A hospital that uses a fixed risk threshold, or tells a patient a number, needs calibration as well as ranking.

[Sources]
Van Calster B et al. Calibration: the Achilles heel of predictive analytics. BMC Med 2019;17:230. doi:10.1186/s12916-019-1466-7

## Slide 5: How to read a calibration plot

2 min. Walk through one point: the top group of 300 patients had average predicted risk 37% and observed rate 38%. That point is consistent with calibration within sampling uncertainty: the interval for the observed rate comfortably includes the predicted value. One group cannot prove calibration, and agreement in one group says nothing about the others.

The vertical bars matter. With 300 patients per group the bars are already several points wide. In the project, Hospital B gives you 25 to 150 outcomes, so a calibration plot built from the audit alone would be very noisy. This is one reason the project uses the Brier score on a large independent test set.

## Slide 6: Same ranking, three different claims about risk

3 min. This is a separate toy cohort, not the Hospital A model, so its AUROC differs from 0.73.

Brier score worked example: a patient given 0.30 who deteriorates contributes (0.30 minus 1) squared = 0.49. One who does not contributes 0.30 squared = 0.09. The Brier score averages these over all patients. Here the honest model scores 0.124, the overconfident 0.140 and the timid 0.143. AUROC cannot tell these models apart, and the Brier score can.

Tell students that the Brier score is the primary endpoint of their project. Differences between methods will often be in the third decimal place, so they should compare methods on the same patients rather than eyeball separate scores.

[Sources]
Van Calster B et al. Calibration: the Achilles heel of predictive analytics. BMC Med 2019;17:230. doi:10.1186/s12916-019-1466-7
Brier GW. Verification of forecasts expressed in terms of probability. Mon Weather Rev 1950;78:1-3.

## Slide 7: Check your understanding

3 min. Ask students to discuss with a neighbour for one minute, then take answers. In a remote session, ask for answers in the chat.

Answers:
1. Calibrated, yes: the one stated risk matches the observed rate. Ranking, no: every patient has the same score, so AUROC is 0.5. Calibration alone is not enough.
2. AUROC does not change, because the square root keeps the order of patients. Calibration changes, and whether it improves or worsens depends on the original predictions and the observed outcomes. Every risk below 1 goes up (0.09 becomes 0.30), so a model that understated risk could become better calibrated and one that was already calibrated or overstated risk would become worse. Only outcome data can tell which.
3. No. One outcome cannot refute a probability. If 30% is right, about 70 of 100 patients like her do not deteriorate. In the simulation, Patient 417 did not deteriorate.

## Slide 8: The code does not change. The hospital does.

2 min. Before showing the cards, ask: "What could be different at another hospital?" Expect case mix, laboratory instruments, testing habits, treatment protocols, documentation and outcome rates.

In the lecture simulation, Hospital B adds 0.95 to every patient's log-odds of deterioration. Nothing in the recorded columns explains it, so the inputs look unchanged. Hospital C records vital signs and labs with measurement-noise setting 2.8. The project's scenarios are milder: a log-odds shift of 0.85 and a noise setting of 2.5.

Use the words carefully. Covariate shift means P(X) changes while P(Y given X) stays fixed. Label shift means P(Y) changes while P(X given Y) stays fixed. Neither describes Hospital B or Hospital C exactly.

[Sources]
Binuya MAE et al. Methodological guidance for the evaluation and updating of clinical prediction models. BMC Med Res Methodol 2022;22:316. doi:10.1186/s12874-022-01801-8

## Slide 9: The same 30% score matches different outcome rates

2 min. Patient 417 is the reason we look at this band, but the bars describe groups. At each hospital we take every patient the model scored between 25% and 35% (198 at A, 428 at B, 494 at C) and count how many deteriorated. Say clearly that 50% is the observed rate in that group at Hospital B. It is not Patient 417's individual risk, which no group rate can give us. Error bars are 95% intervals for each observed rate.

Across all Hospital B patients the model predicts 14% on average while 26% deteriorate. At Hospital C both ranking and calibration changed, so a transfer can damage either property or both.

## Slide 10: Monitoring without outcomes cannot establish calibration

2 min. Before outcomes arrive, a hospital can monitor several things: the distribution of each input, the distribution of predicted risks, and operational indicators such as data completeness, missing-feed alerts, alert volumes and how clinicians respond to them. These can catch broken data pipelines and changes in case mix. None of them can establish calibration, because calibration compares predictions with outcomes. That needs valid outcome evidence from the new hospital. A standardised mean difference above 0.1 is a common alarm line for inputs.

Hospital C triggers an alarm on the labs, mainly through their spread (up to about 1.8 times wider). Hospital B triggers nothing. Even the predicted risks look the same (average 15% at A, 14% at B), while the observed rate is 14% at A and 26% at B. The change lies in the risk that goes with the inputs, which only outcomes reveal. Matching averages and spreads also do not prove that whole distributions match.

## Slide 11: It shows only that what we chose to watch did not visibly change. Establishing calibration at a new hospital needs valid outcome evidence from that hospital. That is why your project asks how many outcomes are enough.

1 min. Say the claim, pause, then add that monitoring is still useful. It can catch instrument problems like Hospital C and broken data feeds. It is incomplete, not worthless. Absence of input or prediction drift is not evidence of validity.

## Slide 12: Two reasons to be unsure about Patient 417

2 min. The distinction decides what to do next. Epistemic uncertainty calls for more relevant data, or caution with patients unlike the training set. Uncertainty that remains given the recorded columns calls for better measurement, not a more complex model.

The ceiling: the simulator contains a "clinical concern" variable that raises risk but appears in no column, like something a nurse notices at the bedside. Our fitted model reaches AUROC 0.719, the best possible from the recorded columns is about 0.725, and a model that could also see the concern variable would reach 0.781. Treat these numbers as a property of this simulator. They say nothing about the ceiling of real deterioration models.

In real data the two kinds of uncertainty cannot always be separated cleanly.

## Slide 13: More data shrinks disagreement, not outcome variability

1.5 min. Explain bootstrap resampling without equations: draw a new training set of the same size with replacement, refit, and compare the predictions. Where refits agree, the data pinned the answer down. Where they disagree, the answer depends on which patients happened to be sampled.

Do not present bootstrap disagreement as an out-of-distribution detector. A smooth model can extrapolate confidently and wrongly for patients far from the training data, and all refits will agree.

## Slide 14: A missing lab result can carry information

1.5 min. In this simulated cohort, patients with a creatinine result deteriorated at 19.1%, those without one at 7.2%. This is missing not at random: in the simulator, whether a lab is sent depends on unrecorded clinical concern and on the patient's underlying risk.

Two common responses both have problems. Dropping incomplete rows changes who is studied. Filling blanks with the median hides the information in the blank. A missingness indicator can help at home but may not transfer to a hospital with different testing habits. The project's informative-missingness scenario changes these patterns at Hospital B.

## Slide 15: One overall number can hide a subgroup the model fails

1.5 min. The overall calibration curve can look acceptable while one group is badly served. Here the subgroup's outcome depends on its labs in a different way, and the model saw too few such patients to learn it.

In the project, the subgroup-relationship scenario creates this problem at Hospital B, and the protocol reports the largest group-level calibration gap as a secondary measure. A group-level gap is descriptive. It does not establish or rule out algorithmic fairness.

## Slide 16: Two simple repairs: shift the risks, or shift and rescale them

3 min. Introduce log-odds in one line: odds = p / (1 minus p), and log-odds is the logarithm of that. A 30% risk is odds of 3 to 7. The logistic model's score is a log-odds.

Intercept update: new log-odds = old log-odds + b. One number is learned from local outcomes. Every patient moves in the same direction, so the ranking is unchanged.
Platt update: new log-odds = a times old log-odds + b. Two numbers are learned. A slope below 1 pulls extreme risks toward the middle. With a positive slope the ranking is unchanged.

Both curves here were fitted on 2,400 Hospital B or C outcomes from the lecture simulation. That is more than any project audit, and more than the project's whole pool of 1,600. At Hospital B the fitted Platt slope is 0.96, close to 1, so the second parameter adds little. At Hospital C the slope is 0.54, and the intercept alone cannot fix that.

These are established methods from the clinical prediction literature. The project compares them under controlled conditions. It does not introduce a new method.

[Sources]
Janssen KJM et al. Updating methods improved the performance of a clinical prediction model in new patients. J Clin Epidemiol 2008;61:76-86.
Platt J. Probabilistic outputs for support vector machines. In: Advances in Large Margin Classifiers. MIT Press, 1999.
Binuya MAE et al. Methodological guidance for the evaluation and updating of clinical prediction models. BMC Med Res Methodol 2022;22:316. doi:10.1186/s12874-022-01801-8

## Slide 17: How well do 25, 75 or 150 outcomes pin down a rate?

2 min. The three numbers are approximate 95% margins of error for one event rate near 26%: 1.96 times the square root of p(1 minus p)/n. They show how little a small audit says about even the simplest quantity.

Recalibration precision is a different question. It depends on the number of events, the spread of predicted risks in the audit, the number of parameters fitted and any penalty. We measured it directly by refitting each update on 200 random audits from the Hospital B pool and recording Patient 417's updated risk (middle 95% of results):
- 25 outcomes: intercept 27% to 64%, Platt 15% to 74%.
- 75 outcomes: intercept 34% to 61%, Platt 29% to 69%.
- 150 outcomes: intercept 37% to 55%, Platt 35% to 63%.
With 25 outcomes the fitted Platt slope ranged from -0.03 to 1.57. A slope below zero would reverse the ranking.

With very few events, a Platt fit may be impossible. The protocol then falls back to the unchanged model and counts the case. It is never silently dropped.

Event counts are lower in scenarios with lower risk. Near the Hospital A rate of about 14%, an audit of 25 contains about 4 events on average, and occasionally none. That is when the Platt fallback is triggered.

The cited BMJ paper is about sample size for validation studies. It is not a minimum sample size for recalibration, so do not quote it as one.

[Sources]
Riley RD et al. Evaluation of clinical prediction models (part 3): sample size for external validation. BMJ 2024;384:e074821. doi:10.1136/bmj-2023-074821

## Slide 18: With 75 outcomes, repairs vary from sample to sample

2 min. Point to the black line in each panel, the fit on the full pool, then to the spread of thin lines around it. The intercept lines stay close together. The Platt lines fan out, especially at high risks where few audited patients sit. For Patient 417 the middle 95% of intercept updates spans 34% to 61%, and of Platt updates 29% to 69%.

Ask: "If the true change is a pure shift, what does the extra slope buy you? If the true change also compresses risks, as at Hospital C, which method do you expect to win with 25 outcomes? With 150?" Do not answer. These are hypotheses for the project.

## Slide 19: Paired comparison on new patients: did the repair help?

3 min. Each dot is one random audit of 75 Hospital B outcomes. For each audit we fit the update, apply it to 3,600 separately simulated test patients, and subtract the unchanged model's Brier score (0.184) on those same patients. Pairing reduces the noise that comes from which test patients were drawn.

Why independent: if you fit the update on the 75 audit outcomes and then judge it on those same 75, the result is optimistic. The update has already seen the answers.

This is one easy case: a pure risk shift with a moderate audit. It also differs from the project in its sizes. Here one model trained on 5,600 patients, audits came from a pool of 2,400, and one test cohort of 3,600 was reused. Only the audit changed between dots. In the full protocol the model trains on 4,000, the pool holds 1,600 and the test cohort 2,400. Notebook 92's faster demonstration uses 2,000, 1,600 and 1,200. In both, each replicate draws new source, pool and test cohorts. Expect project results to be noisier.

Ask before moving on: "What would this plot look like in the negative control, where nothing changed?" Collect predictions and do not answer. It is one of the first things students will test.

[Sources]
Davis SE et al. A nonparametric updating method to correct clinical prediction model drift. J Am Med Inform Assoc 2019. PMID 31397478.

## Slide 20: Three cohorts, four analytical roles

2.5 min. Three sets of sizes, all read from the code:
- Full protocol (python -m project.research_experiments): 4,000 Hospital A records, a 1,600-record Hospital B pool and a 2,400-record independent test cohort in every repeat.
- Notebook 92 demonstration: the same design made faster, with 2,000, 1,600 and 1,200, and 3 repeats by default.
- Day 1 orientation example: fixed files with 4,000 Hospital A records, 1,600 Hospital B records and 75 revealed outcomes. It has no independent test set, so its 75 outcomes must not be reused to judge a method.

The lecture figures used a fourth, larger set (model 5,600, pool 2,400, test 3,600) so that patterns were easy to see. Students should expect noisier results.

The audits are nested: the 25 audited patients are part of the 75, and the 75 are part of the 150, so budgets are compared on overlapping evidence. In a simulation we can generate a fully labelled test hospital. In real research that would be a separate, valid outcome dataset, which is expensive.

The primary endpoint is the paired Brier difference on the independent test cohort. AUROC, expected calibration error, calibration-in-the-large and the group-level gap are secondary measures.

**Clarification:** The 25, 75 or 150 audited records are selected from the 1,600-record Hospital B pool. The audit is not a separate independent cohort.

## Slide 21: Five scenarios, one change at a time

2 min. Every team does the two minimum scenarios. The other three are extensions, and together they make the full study in project/RESEARCH_PROTOCOL.md, which still has all three methods and five scenarios. We simplified the minimum deliverable, not the study.

Changing one mechanism at a time makes results interpretable. Real hospitals can change in several ways at once, and that is a limitation students should state.

Ask each team to write predictions before running anything, especially for the negative control. Pre-specifying methods, scenarios and budgets is part of the protocol. It prevents choosing the comparison after seeing the results.

## Slide 22: Three days, three concrete milestones

1.5 min. Research runs from Wednesday 18 to Friday 20 November, with team presentations on Friday afternoon. Thursday has other workshop activities, so the minimum is deliberately short. I support teams remotely from US Eastern time through a messaging channel agreed with the organizer, so live calls in the Mauritius early morning are not expected. A local coordinator may help with Colab where one is available.

Every team should finish the minimum: the unchanged model versus the intercept update, in the negative control and the baseline-risk shift, with 25 and 75 audited outcomes. Notebook 92 has a minimum-comparison cell that shows exactly these rows and a figure.

Extensions are Platt, 150 outcomes and the other three scenarios. The minimum is an educational exercise, and rerunning the provided code is not an original research contribution. Teams that want one can test a single new, falsifiable question from project/OPEN_RESEARCH_EXTENSIONS.md, writing the hypothesis down before they see the results.

The three report slides are: question and comparison, results with a paired Brier display, and interpretation with one next experiment. Students should start from docs/SHORT_STUDENT_WORKFLOW.md.

The MIMIC-inspired tables in the repository show how features are assembled from relational tables. They are synthetic and do not reproduce MIMIC-IV.

## Slide 23: Show what the evidence supports, where a method fails, and what data would change your conclusion. These are established methods on synthetic data. No clinical validation and no new method is claimed. A paper is a possible later step, not a three-day deliverable.

1.5 min. Return to Patient 417: would you use her 30% at Hospital B today? What evidence would you want first? Then open questions.

After questions, share the Colab link to notebooks/92_three_day_research_starter.ipynb and ask every team to run the first cell before the session ends.