---
lectra_schema: "1.0"
title: "When Can We Trust Clinical AI at a New Hospital? Condensed rehearsal"
language: en-US
style: story-driven-academic-presentation
target_duration_minutes: 20
default_pace: normal
default_tone: explanatory
---

<!-- slide: 1 -->
Imagine that a patient arrives in a hospital in the middle of the night. A computer model estimates a thirty percent chance that this patient will deteriorate in the next forty-eight hours. What should the doctor do with that number? Today we will examine what makes this kind of prediction trustworthy, why it can fail in another hospital, and how a group of students can investigate the problem using synthetic data.

<!-- slide: 2 -->
Thirty percent is not the same as a diagnosis. It is a statement about risk over a specified time period. If the model gives thirty percent risk to many similar admissions, we would expect roughly thirty percent of those people to have the outcome. The number may be useful, but only if the observed outcomes support its meaning. That is why we cannot assess everything from the predictions alone.

<!-- slide: 3 -->
There are six questions I want us to keep in mind. Can the model rank patients correctly? Do its probability numbers mean what they say? Will those properties survive another hospital? Where is the model uncertain? What happens when we act on its prediction? And what new evidence would help us make a better decision? Each question asks for something different.

<!-- slide: 4 -->
Let me introduce two important words. Discrimination tells us whether a patient who later deteriorates generally receives a higher risk score than one who does not. AUROC is a common measure of this ability. Calibration asks another question. When the model predicts thirty percent, do about thirty percent of those patients have the outcome? Ranking and probability meaning are separate.

<!-- slide: 5 -->
This plot shows three versions of the same underlying score. Their ordering of patients is almost identical, but their predicted probabilities have different relationships to observed outcomes. A risk model can therefore appear strong if we only look at ranking while giving misleading absolute risks. If the hospital uses a fixed risk threshold to trigger an action, that difference can matter.

<!-- slide: 6 -->
Now imagine we take the same program and install it at Hospital B. The code has not changed. But patients, laboratory instruments, medical practice, and documentation could be different. We should not assume that a model developed in Hospital A continues to make reliable predictions in Hospital B.

<!-- slide: 7 -->
In this synthetic example, the risk estimates change their meaning after transfer. The model may still separate patients reasonably well, yet it can underestimate or overestimate the level of risk. We should also remember that in real settings ranking may deteriorate too. The simulator illustrates one possibility, not a universal rule.

<!-- slide: 8 -->
Some hospital changes are visible without observing any outcomes. For example, we can compare the distributions of blood pressure or laboratory results. We can also compare which measurements are missing. But a hospital could have similar observed patient characteristics and still have different outcome risks for those characteristics. Input monitoring cannot establish calibration by itself.

<!-- slide: 9 -->
A dashboard can show that the new data look similar to the old data. That is useful, but it does not certify that the model remains valid. If the relationship between recorded inputs and deterioration has changed, the dashboard might not detect the problem. We need new outcome information, or a surrogate already validated against outcomes, to answer the probability question.

<!-- slide: 10 -->
Why can a model be uncertain? One reason is that we have too little information to estimate its behavior. We call that epistemic uncertainty. Another reason is that outcomes remain variable even for people with similar measured characteristics. We call that aleatoric uncertainty. More relevant training observations may help the first problem. More rows with the same variables may not solve the second.

<!-- slide: 11 -->
One practical way to look for model instability is to repeatedly retrain the model using different resamples of the training data. If its predictions change a lot, we have evidence that its estimates depend strongly on the sample. But if all models agree, that does not guarantee they are correct. The entire model family may make the same error.

<!-- slide: 12 -->
A missing laboratory result is not always an empty detail. Clinicians order tests for reasons. A test may be absent because a patient appeared less concerning, or because the hospital followed another workflow. This can create patterns related to outcomes. Missingness can help prediction, but the meaning of missingness may change at another hospital.

<!-- slide: 13 -->
Suppose we find that the model's probabilities are unreliable. Our first response should not automatically be a more complicated neural network. We might collect new outcomes, adjust the existing probabilities, defer selected predictions for human review, or keep the model in shadow mode. We need evidence before choosing among these options.

<!-- slide: 14 -->
The student research will compare three approaches. The first does nothing and uses the original Hospital A model. The second shifts the predicted risk scale using a single fitted intercept. The third uses a logistic correction that changes both the location and the spread of predicted risks. More flexibility may help, but it also gives the model more opportunity to overfit a small audit.

<!-- slide: 15 -->
How many labeled patients does a new hospital need before it can correct risk probabilities? There is no universal number. It depends on the type of change, the number of events, and the flexibility of the adjustment. Our students will explore this using audits of twenty-five, seventy-five, and one hundred fifty target outcomes in repeated simulations.

<!-- slide: 16 -->
Another idea is to refer some predictions for review. We might focus on cases close to a decision threshold, or cases for which repeated fitted models disagree. These two signals do not mean the same thing. And human review has a cost. We cannot assume that deferring more patients improves care unless we evaluate what happens next.

<!-- slide: 17 -->
This figure shows a relationship between how many predictions the model retains and how well those retained predictions perform. It is useful to compare a proposed deferral rule with random deferral. But any gain needs to be described together with the extra workload and the people excluded from automated decisions.

<!-- slide: 18 -->
An average performance measure can hide a weak subgroup. Imagine a model that works well for a large group but poorly for a smaller group with different risk patterns. A single average can look reassuring. We should inspect subgroups, but we must also be honest when the small number of events makes a subgroup estimate very uncertain.

<!-- slide: 19 -->
Sometimes the appropriate answer is to continue shadow mode. In that state, the team studies predictions without using them for patient decisions. If stronger evidence becomes available, the hospital might evaluate recalibration or a supervised review process. AUROC alone cannot decide which policy is justified.

<!-- slide: 20 -->
Here is the original project setup. Hospital A has four thousand synthetic admissions with known outcomes. Hospital B has sixteen hundred admissions, but students initially know only seventy-five outcomes. The question is what they can learn from those seventy-five labels, and what remains unknown.

<!-- slide: 21 -->
We will turn that question into an experiment. Under several synthetic hospital changes, students compare an unchanged model with two calibration corrections. They vary how many target outcomes are available. Their main score is the Brier score, which measures the squared difference between a predicted probability and the observed binary outcome. Crucially, they evaluate on different target patients from those used to fit corrections.

<!-- slide: 22 -->
The first day is about understanding the data and reproducing a baseline. The second day compares adaptation methods and outcome label budgets. The third day repeats the experiments, examines failures, and produces one clear figure and a short report. The goal is to learn to make a defensible scientific comparison, not to run the most sophisticated algorithm.

<!-- slide: 23 -->
Let us return to the thirty percent risk estimate. Can we trust it at Hospital B? The correct answer might be that we do not yet have enough evidence. That conclusion is useful if we can explain which assumption remains untested and what information would change the decision. An honest negative result can be an excellent starting point for further research.
