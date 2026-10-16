# Healthcare AI module: lecture and project plan

**AI & Uncertainty School and Workshop 2026** | Mauritius, 16–20 November
**Presenter:** Alireza Vafaei Sadr, Penn State College of Medicine
**Mode:** remote lecturer; group-work arrangements still to be confirmed

The central question is: **Can a clinical prediction system tell us when it should not be trusted?**

Participants should know basic Python, probability and predictive modeling. No clinical background or credentialed patient data are required. All datasets are synthetic EHR-like examples, not validated MIMIC-IV replicas.

## Programme proposal

| Component | Prepared format | Can be shortened? |
| --- | --- | --- |
| Lecture 1: Honest probabilities in clinical prediction | 90 minutes | 60-minute core |
| Lecture 2: Deciding under uncertainty | 90 minutes | 60-minute core |
| Open team research challenge: hospital transfer with limited labels | 2-hour core plus optional hour/presentations | 2 hours |
| Optional notebooks on hierarchical Bayes and simulation-based inference | Self-paced | Not in core lectures |

**The organisers have not yet confirmed these durations or the remote project setup.**

## Lecture 1: honest probabilities in clinical prediction

The main ideas are that discrimination and calibration answer different questions; aleatoric, finite-sample and unmeasured-variable uncertainty require different responses; and hospital transfer may break predictions in ways input-only monitoring cannot verify.

| Approximate core minute | Topic and teaching demonstration |
| --- | --- |
| 0-5 | Opening: what does a 30% deterioration probability mean? |
| 5-20 | Three models with nearly identical AUROC but very different calibration |
| 20-35 | Bootstrap variability, data limits, and a hidden clinical factor |
| 35-50 | Hospital transfer, measurement drift, and conditional-risk change |
| 50-60 | Missingness is clinical information; three key takeaways |

For a 90-minute slot, add a short Beta-Binomial updating example, the simulator walkthrough, and notebook exercise/discussion. Slide 19's measurement-noise example must **not** be described as pure covariate shift: noise in recorded inputs can change the conditional outcome relationship for those observed inputs.

## Lecture 2: deciding under uncertainty

The main ideas are that recalibration costs target-site labels; abstention or referral requires careful evaluation and capacity; and decisions depend on consequences, not discrimination alone.

| Approximate core minute | Topic and teaching demonstration |
| --- | --- |
| 0-5 | Start from the miscalibrated transferred model |
| 5-19 | Intercept, logistic/Platt and isotonic recalibration; label requirements |
| 19-36 | Bootstrap uncertainty proxy and when predictions should be deferred |
| 36-48 | Clinical thresholds and net benefit in an explicit decision model |
| 48-55 | Subgroup reliability |
| 55-60 | Three takeaways and project question |

For a 90-minute slot, spend more time on worked examples and discussion; hierarchical Bayesian modeling and simulation-based inference are optional conceptual bridges and separately runnable notebooks.

**Important scientific qualifications:** bootstrap disagreement measures sensitivity to model training and is not a guaranteed out-of-distribution detector; a threshold computed from a cost ratio assumes calibrated risks and a simple two-action decision, not a full clinical workflow.

## Open team project: hospital B with only 75 outcome labels

Use project/OPEN_RESEARCH_CHALLENGE.md and notebooks/91_open_research_challenge_starter.ipynb.

Students receive labeled records from Hospital A, unlabeled records from Hospital B, and a random audit of 75 outcomes at B. They can explore monitoring, recalibration, uncertainty, subgroup reliability and selective prediction. The open question is whether the current evidence supports any form of deployment and what should be measured next. A decision to remain in shadow mode is valid.

This is **not** a competition to identify one predefined failure mechanism. Teams explain their assumptions and may make different recommendations. No formal grading.

The older six-team exercise (project/PROJECT_BRIEF.md) remains available as a structured alternative if the organisers want an easier or shorter task.

## Logistics and preparation

- A browser and free Google Colab CPU are enough for the core materials. Optional PyMC/SBI notebooks have additional dependencies.
- The project requires one in-room facilitator if the presenter joins by video.
- Pre-run the notebooks in a fresh Colab account, record a static backup of plots, and test projector/audio/video before the session.
- Do not use actual clinical or restricted data. Nothing in this simulated task supports patient-care recommendations.
- Confirm lecture lengths, sequence, participant background, the number of teams and the feasibility of remote project supervision with the organisers.

## Teaching materials

- Two PowerPoint decks with generated figures and speaker notes under slides/
- Two core student/instructor notebooks under notebooks/
- Optional hierarchical modeling and SBI notebooks
- Synthetic data generator under medsim/
- Open project generator under project/generate_open_challenge.py
- Optional six-hospital guided diagnostic exercise
- Detailed delivery guide under docs/LECTURE_DELIVERY_GUIDE.md

## Final checks before the school

- Ensure all notebook code cells run on a clean environment; regenerate plots and decks from source.
- Verify all numerical claims shown in slides against the exact simulator run or explicitly label them as illustrative.
- Review clinical language for unintended claims of validity or safety.
- Rehearse the 60-minute stories first; extend to 90 minutes only if the actual schedule permits.
