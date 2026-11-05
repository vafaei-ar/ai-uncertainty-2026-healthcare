# Presenter guide: When Can We Trust Clinical AI at a New Hospital?

**AI & Uncertainty School and Workshop 2026, Mauritius**
**Presenter:** Alireza Vafaei Sadr
**Format:** one 60-minute remote lecture with time for student answers and project introduction.
**Slides:** slides/lecture_when_can_we_trust_clinical_ai.pptx (23 slides).
**Source:** slides/src/one_lecture.js and the figures under slides/figures.

## The one story to tell

Hospital A trains a model to predict deterioration in the next 48 hours.
The model says a new patient has a 30% risk. This raises three questions:
is the ranking useful, does 30% mean 30%, and does either property survive
at Hospital B? We then ask what to do if evidence is weak. The three-day
student project turns that problem into repeated comparisons of simple
recalibration methods on synthetic data.

**Scientific boundary:** This is a synthetic teaching study. It does not
establish clinical safety, replicate MIMIC-IV, or validate an intervention.

## 60-minute delivery schedule

| Minutes | Slides | Main concept |
| --- | --- | --- |
| 0–13 | 1–5 | Probability meaning, AUROC and calibration |
| 13–21 | 6–9 | Model transfer to a new hospital |
| 21–28 | 10–12 | Sources of uncertainty and missingness |
| 28–35 | 13–15 | Recalibration with limited target labels |
| 35–43 | 16–18 | Deferral, human review and subgroups |
| 43–51 | 19–21 | Deployment decisions and the research question |
| 51–60 | 22–23 | Three-day project, discussion and questions |

The timings assume interaction. If the session is shorter, protect slides
2, 4, 5, 7, 9, 14, 15, 20, 21, 22, and 23.

## Slide-by-slide teaching instructions

### 1. Opening: the problem we will solve
**Aim:** Give the audience one scenario, not an abstract list of methods.

**Say:** "Imagine a doctor at a hospital sees a model saying that a patient
has 30% risk of deteriorating within two days. What exactly does that mean?
And if we move the model to another hospital, can we trust that number?"
Explain that none of our simulated examples directly guide treatment.

**Ask:** "Would you act on the 30% number?" Do not demand an answer yet.
Return to this question at the end.

### 2. What does 30% mean?
**Aim:** Separate probability from certainty about a single outcome.

**Say:** "It does not mean the model knows 30% of the diagnosis. It means
that among many comparable cases assigned this risk, we expect about 30% to
have the outcome. We need actual outcomes to test that claim."

**Visual:** Three cards: 30%, 48-hour outcome, and the open question.
**Ask:** "Could all 100 similar patients deteriorate? Yes in principle,
though it would be extremely unlikely under an independently calibrated
30% risk model. One individual outcome does not prove calibration."

### 3. Six questions before deployment
**Aim:** Organize the lecture in ordinary language before using metrics.

Emphasize **ranking, probability meaning, transfer, uncertainty, action,
evidence**. Point out that an excellent model result in an internal paper
does not answer all six questions at a new hospital.

**Transition:** We first distinguish ranking from probability meaning.

### 4. AUROC versus calibration
**Aim:** Teach two genuinely different metrics.

**Say:** "AUROC asks whether an eventual case is usually ranked higher
than a noncase. Calibration asks whether numbers such as 20% or 30%
match observed frequencies."

**Example:** Two patients have modeled risks 80% and 60%. Their relative
rank is the same if we multiply or monotonically transform the scores,
but the stated probabilities can become wrong.

**Ask:** "If the model always doubles the odds of deterioration, can AUROC
remain unchanged?" Yes for a strictly monotone transformation; calibration
can change.

### 5. Same ranking, different calibration
**Aim:** Read a reliability diagram correctly.

**Visual:** Existing code-generated l1_calibration.png.
Explain horizontal predicted risk, vertical observed event proportion,
and the ideal diagonal before pointing to any model.

**Say:** "All curves can rank similarly while making different promises
about risk. It matters whether 30% really corresponds to about 30%."

**Caution:** This is a designed synthetic example. In a new real hospital
ranking itself may change too.

### 6. The model arrives at Hospital B
**Aim:** Move from single-site evaluation to external transport.

**Say:** "Hospitals differ in patient populations, tests, staff, recording
processes, and treatments. Even when the code is identical, the prediction
problem may be different."

**Ask:** "Which hospital changes might be visible before we know any
patient outcomes?"

### 7. Probabilities under hospital transfer
**Aim:** Show a specific transfer failure.

**Visual:** l1_shift_calibration.png. Walk through the displayed sites,
but emphasize this is a simulator with controlled changes.

**Say:** "In this example, the prediction numbers no longer match outcome
rates. A threshold picked in Hospital A may trigger too few or too many
alerts at Hospital B."

**Caution:** Do not claim all hospital transfers preserve AUROC.

### 8. What input monitoring can detect
**Aim:** Explain why input-only drift is not an outcome validation.

**Visual:** l1_shift_detection.png. The students can compare laboratory
means or missingness without labels. But only outcomes can tell us whether
conditional risk changed.

**Teaching note:** Measurement noise in observed variables can also alter
the conditional relationship P(Y|X_observed). Do not call that example
pure covariate shift.

### 9. A green dashboard does not establish safety
**Aim:** Land the most important transfer lesson.

**Say:** "If age, blood pressure, and lab distributions look unchanged,
we still cannot conclude the probabilities are right. A hospital could
have different risk for similar recorded patients."

**Ask:** "Which additional data would help?" New-hospital outcomes or
a surrogate that has already been validated against those outcomes.

### 10. Epistemic and aleatoric uncertainty
**Aim:** Explain why uncertainty has different sources.

**Say:** "Epistemic means we do not know enough about the model. A rare
patient type may have very few training examples. Aleatoric means that
the outcome remains variable even after we consider our recorded
measurements."

**Example:** We can collect more relevant examples to reduce sampling
uncertainty. But collecting more rows with the same limited variables
cannot necessarily eliminate unpredictable outcomes.

**Caution:** These components are not automatically identifiable from
one dataset. Do not describe them as perfectly measurable quantities.

### 11. What bootstrap disagreement tells us
**Aim:** Interpret a resampling-based teaching figure.

**Visual:** l1_epistemic.png. Repeatedly train on resampled data and
compare predictions.

**Say:** "The spread shows how sensitive this modeling procedure is to
which observations it sees. It is one useful warning signal, but
agreement does not guarantee that predictions are correct."

### 12. Why a blank laboratory result matters
**Aim:** Introduce informative missingness.

**Visual:** l1_missingness.png. Clinical staff may order labs more often
for concerning patients. That decision changes the observed pattern.

**Ask:** "If we delete every patient without a lactate result, who remains
in our data?" Possibly a selected sicker group.

**Caution:** Missingness indicators may help prediction within one
hospital but change meaning in another hospital.

### 13. If the number is wrong, what next?
**Aim:** Transition to decisions.

Possible options: keep shadow mode, gather new labels, recalibrate a
model, or refer selected predictions for review. None follows
automatically from AUROC.

### 14. Three candidate methods
**Aim:** Explain the research comparison students will actually run.

**Unchanged:** Apply the original Hospital A model.
**Intercept correction:** Move predicted probabilities up or down by
fitting one log-odds offset on target outcomes.
**Platt correction:** Fit both an offset and a slope, adding flexibility
and the possibility of overfitting with a small audit.

**Ask:** "Which correction uses fewer fitted parameters?" The intercept.

### 15. How many local labels?
**Aim:** Explain the sample-size question without promising a universal threshold.

**Visual:** l2_calibration_cost.png is a separate teaching example that
illustrates why more flexible methods can overfit scarce labels.

**Say:** "We will compare 25, 75 and 150 outcome labels, not because
these are magic numbers, but to study how the information budget affects
the correction."

**Critical point:** The same labels cannot fit and independently
evaluate the final adjusted model.

### 16. Two reasons to request human review
**Aim:** Separate borderline decisions from unstable model fitting.

**Example:** A prediction near a specified clinical threshold can be
hard to classify. A model may also disagree with its own bootstrap
replicas, suggesting sensitivity to training data.

**Caution:** Neither is proof that reviewing this case prevents harm.
The project uses 20% extra review capacity as a *hypothetical*
constraint, not a care recommendation.

### 17. Risk and coverage
**Aim:** Teach students to read a deferral-policy curve.

**Visual:** l2_risk_coverage.png. The horizontal axis is the proportion
of cases for which the model still makes a prediction. Compare performance
on retained patients with a random-deferral reference.

**Ask:** "What else must we report?" The number referred for review,
the workload, and ideally downstream outcomes.

### 18. Subgroup reliability
**Aim:** An aggregate metric can hide heterogeneity.

**Visual:** l2_subgroup.png. Explain performance in different groups
one at a time. The simulator has a simplified binary group indicator,
not a validated clinical demographic taxonomy.

**Caution:** Small group counts and events lead to unstable estimates.
A mean calibration gap does not establish fairness.

### 19. Three defensible actions
**Aim:** Show that withholding deployment can be scientifically responsible.

**Say:** "With uncertain target performance, it can be reasonable to
stay in shadow mode. Recalibration might help, but we must test it.
Reviewing cases can also be considered, but it requires a real workflow."

**Ask:** "Can you tell which action is best from a single AUROC?" No.

### 20. The data students receive
**Aim:** Explain the 4,000 / 1,600 / 75 numbers.

Hospital A has 4,000 labeled synthetic admissions. Hospital B has
1,600 synthetic admissions with input variables but only 75 randomly
audited outcomes. The outcomes of the other target cases are not
distributed in student-facing files.

**Ask:** "What can we learn immediately? What requires labels?"

### 21. A testable question, not an AI contest
**Aim:** State the experiment before showing code.

**Question:** With a limited outcome audit, does intercept-only or Platt
recalibration improve target probability accuracy relative to no update?

The model is challenged under no shift, baseline-risk shift, measurement
noise, subgroup interaction, and missingness. Label budgets are 25, 75,
and 150. The main metric is the Brier score, the average squared difference
between predicted probability and binary outcome.

**Critical point:** Each method is evaluated on an **independently
generated target test cohort**, never the same outcomes used for fitting.

### 22. Three days and three milestones
**Aim:** Make the workshop achievable.

**Visual:** Three connected boxes:
- Day 1: understand data and reproduce unchanged baseline.
- Day 2: compare the two recalibration methods.
- Day 3: repeat experiments and present one main figure and limitations.

**Say:** "A team does not need ten methods. A clear baseline and one
well-evaluated alternative are better than many methods tested poorly."

The optional adapter demonstrates MIMIC-inspired relational tables.
Real MIMIC-IV analysis requires separate credentialed access, valid
cohorts, outcomes, and temporal feature definitions.

### 23. A scientifically useful negative result
**Aim:** Return to the opening question.

**Say:** "The answer might be that 75 outcomes are insufficient to decide.
That is a result if we show why, how unstable the estimates are, and what
additional evidence would change our recommendation."

Invite each team to state one prediction about which shift will be
hardest for calibration and explain how they would test it.

## Project questions students may ask

**Why not just use AUROC?** AUROC measures ranking, not the reliability
of a 30% or 60% probability. The project focuses on probability transport.

**Why do we simulate outcomes for the experiment?** Simulation allows
independent target evaluation under known data-generating scenarios.
The original 75-label exercise cannot give precise unbiased evaluation
after using those same 75 labels for adaptation.

**Is a simulation study publishable?** Possibly, but only with a novel
question, adequate repeated experiments, proper comparisons, and ideally
validation beyond one synthetic generator. Three days produce preliminary
results, not a completed paper.

**Can we move directly to real MIMIC data?** The analytic logic can be
transferred, but cohort selection, event timing, item codes, outcomes,
missing-data handling, and approvals must be built and validated separately.

## Final rehearsal checklist

- Can you explain AUROC versus calibration without a formula?
- Can you say what an unlabeled hospital comparison cannot detect?
- Can you separate model uncertainty from genuine outcome variability?
- Can you explain what intercept and Platt adjustments do?
- Can you describe why fitting and evaluation labels must be separate?
- Can you explain the three-day study in under two minutes?
- Can you demonstrate one source-vs-target comparison in Colab?
- Does an in-room facilitator have the final notebook and data links?
