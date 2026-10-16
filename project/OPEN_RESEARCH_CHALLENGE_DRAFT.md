# Open research challenge: when should a clinical risk model be trusted at a new hospital?

**Status: working draft for the November 2026 workshop. Not yet the student-facing project.**
**Format:** 2-hour core, extendable to 3 hours; 5-minute team reports if the schedule permits.
**Data:** synthetic admissions (vitals, labs, comorbidities, 48-hour deterioration). No patient data or credentialing.

## Why this question is open

Hospital A trained a model to predict deterioration in the next 48 hours. Hospital B wants to use it, but its patient mix, recording practices and risks may differ. Many patients at Hospital B have **no observed outcomes yet**, because outcomes are delayed or available only for a small audit sample.

The real question is not "which hidden failure mode did we plant?" It is:

> **With limited target-hospital labels and a finite review budget, what evidence would justify trusting, adapting, deferring, or withholding this clinical prediction system?**

No procedure can establish target-site calibration from unlabeled inputs alone without additional assumptions. Methods may produce competing answers; saying "do not deploy yet" can be a defensible result.

## Proposed challenge constraints

- **Development:** labeled data from Hospital A and a ready-to-use baseline logistic model. Teams may refit it, but are not required to.
- **New site:** feature data from Hospital B, most initially without observed outcomes. For a workshop experiment, start with a *provisional* audit budget of 75 target-site labels; this number can change.
- **Review capacity:** at most 20% of new admissions can be sent for additional clinician review. Review is a resource constraint, **not** an assumed cure for model errors.
- **Evaluation:** a held-out target outcome set is revealed during the debrief to examine which claims survived. Because this is synthetic, the reveal illustrates methods, not clinical effectiveness.
- **Safety:** nobody uses these predictions for patient care. The scenario is a shadow-mode evaluation.

The existing `medsim` simulator and six-team cohorts are useful starting points, **but the released project files currently have all target outcomes visible**. A new masked-label release and starter notebook still need to be prepared before using this brief as written.

## The teams' task

Choose a strategy, explain your assumptions, test what you can, and make a recommendation.

Possible strategies include Bayesian/hierarchical recalibration, simple intercept updates, bootstrap ensembles, subgroup audits, conformal approaches **where their assumptions hold**, identifying patients to defer, and choosing which additional outcomes to collect. These are suggestions, not required methods.

Everyone should address:

1. **Evidence:** What do you know from source-site labels, new-site inputs and the small labeled audit? Show one meaningful plot/table and uncertainty in its estimates.
2. **Unknowns:** Which failure modes cannot be ruled out with the evidence available? What assumptions does your approach make about changes in `P(X)` and `P(Y|X)`?
3. **Action:** Continue shadow mode, cautiously pilot, recalibrate, or avoid deployment? If recommending review or abstention, describe the rule and review burden.
4. **Learning plan:** Which next 50 or 100 outcome labels would be most valuable, and why? What would make you pause or reverse deployment?

**No fixed answer key, no formal grading.** Teams may reach different conclusions for defensible reasons.

## Suggested live session

| Duration | Core activity |
| --- | --- |
| 0-15 min | Clinical question, data and constraints |
| 15-40 min | Baseline model, source-site checks, unlabeled site comparison |
| 40-75 min | Explore one uncertainty/transfer strategy, using limited labeled audit |
| 75-100 min | Develop review/deployment and outcome-collection policy |
| 100-120 min | Prepare a short decision statement and discuss uncertainties |
| Extra hour (if available) | Test a second method or label-acquisition strategy; add team presentations |

**Team report:** 3 slides, 5 minutes: (1) evidence and uncertainty, (2) proposed action/review policy, (3) assumptions, next labels and stopping criteria.

## How this differs from the existing project

The original six-failure-mode exercise remains a useful *guided backup* and can still serve as a test bed. In the open version, the question is not to identify a planted fault; the student chooses the evidence, model, label allocation and safe action under uncertainty.

## Preparation still needed

- Create labeled-source / mostly-unlabeled-target / small-audit / later-reveal datasets using `medsim`, with fixed seeds and clearly documented assumptions.
- Build a new Colab starter showing data loading, a simple baseline and permitted audit labels without exposing the reveal until the discussion.
- Validate that teams can produce useful but different approaches within two hours.
- Prepare an instructor debrief showing that unchanged input distributions do not certify stable conditional risk, and that uncertainty proxies do not guarantee safe out-of-distribution detection.
- Confirm whether an in-room facilitator can support the group session if the presenter joins remotely.

**Not a validated MIMIC-IV replica.** The synthetic task uses EHR-like variable types; it does not reproduce MIMIC-IV patient distributions, temporal richness or documentation.
