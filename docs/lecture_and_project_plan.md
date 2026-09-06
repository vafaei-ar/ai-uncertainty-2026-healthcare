# Healthcare AI module - lecture and project plan

**AI & Uncertainty School and Workshop 2026, Mauritius, 16-20 November**
Alireza Vafaei Sadr, Penn State College of Medicine. Delivered remotely.

Draft for the organisers. Everything described here is built and tested; timings
come from running the material rather than from estimating it.

---

## What the module is for

Participants arrive able to fit models. The gap this module addresses is the one
between a model that scores well and a model that can be switched on in a
hospital. The organising question is:

> **Can you build a clinical prediction system that knows when it should not be
> trusted?**

The healthcare setting is not decoration. Distribution shift is a transfer
between hospitals; informative missingness is a clinician deciding not to order a
lab; the cost asymmetry that sets a decision threshold is an ICU bed. Every
abstract idea in the school's syllabus has a concrete referent here, which is
what makes the medical module a useful complement to the astronomy and cosmology
material rather than a parallel track.

## Shape of the contribution

| Component | Length | Format |
| --- | --- | --- |
| Lecture 1 - Honest probabilities in clinical prediction | 90 min | Live notebook, remote |
| Lecture 2 - Deciding under uncertainty | 90 min | Live notebook, remote |
| Team project - hidden failure modes | 3 h + 45 min presentations | Teams work locally, I join remotely |
| Optional deep-dive notebooks | self-paced | Hierarchical PyMC, neural SBI |

## Prerequisites

Python, numpy/pandas, a fitted logistic regression. No clinical background is
assumed - the medical context is explained where it matters. No credentialed data
access is needed: everything runs on a synthetic EHR simulator, on the free Colab
CPU tier, in seconds.

---

## Lecture 1 - Honest probabilities in clinical prediction

*Notebook: `01_lecture1_uncertainty_foundations`. Full run time under 10 seconds.*

| Time | Section | The point |
| --- | --- | --- |
| 0-10 | A point estimate is not an answer | Beta-Binomial updating on a clinical alert; watch the interval narrow as $1/\sqrt{n}$ |
| 10-30 | Discrimination versus calibration | Three models, **identical AUROC to four decimals**, wildly different claims about the world. Exercise: recover the temperature that broke one of them |
| 30-50 | Epistemic versus aleatoric | Bootstrap bands shrink with training size, outcome noise does not. Then the sharp version: the simulator holds an unrecorded clinical impression, so the ceiling for *any* model on these columns is AUROC 0.73 while the oracle reaches 0.78 |
| 50-70 | A synthetic EHR you can break on purpose | Baseline model, bootstrap CI on AUROC (the interval spans 0.06 - wider than most published "improvements") |
| 70-85 | The model meets a second hospital | Site B: ranking survives, calibration collapses, and **no covariate-shift check can see it**. Site C: instrument drift, which a covariate check catches immediately |
| 85-90 | The information in a blank cell | Complete-case analysis silently selects the sickest half of the ward |

**The line I want them to leave with.** Input-drift dashboards - which is what most
deployed monitoring actually is - catch one of the two common failures and are
structurally blind to the other. Prospective label collection is not optional
infrastructure; it is the monitoring system.

## Lecture 2 - Deciding under uncertainty

*Notebook: `02_lecture2_trustworthy_deployment`. Full run time under 10 seconds.*

| Time | Section | The point |
| --- | --- | --- |
| 0-20 | Recalibration and what it costs | Intercept, Platt, isotonic. A learning curve over the number of labelled patients: one parameter is near its ceiling at ~100 charts, isotonic needs an order of magnitude more before it beats doing nothing |
| 20-35 | Ensembles as an epistemic signal | A disagreement threshold set on development data alone flags 25% of a new ward, of which **87% are genuinely out-of-distribution** - with no outcome labels required |
| 35-55 | Selective prediction | Risk-coverage curves. Epistemic and aleatoric rankings defer *different patients*; the exercise builds a two-stage rule under a fixed 20% review budget |
| 55-70 | The threshold is a clinical decision | $t^{*} = 1/(1+R)$ and net benefit. At a 10:1 cost ratio the operating point is 0.09, not 0.5 - and the model barely beats "escalate everyone", which is the comparison a clinical director actually makes |
| 70-80 | The aggregate number lies | One ward, two subgroups: AUROC 0.76 and 0.56. The whole-ward figure describes neither |
| 80-90 | Hierarchy and simulators | Partial pooling with estimated shrinkage; ABC as the bridge to the SBI notebook; project briefing |

---

## Team project - same task, six hidden failure modes

Every team receives development data and six months of deployment data from one
hospital, with identical columns and an identical task. Each hospital hides a
different reason the model should not be trusted:

| Team | Hidden failure mode | Signature that exposes it |
| --- | --- | --- |
| 1 | Informative missingness | Nothing looks wrong in aggregate. Complete-case analysis moves the event rate from 0.145 to 0.217 |
| 2 | Site and prevalence shift | Observed 0.264 against predicted 0.150; ECE 0.114; **every covariate check comes back clean** |
| 3 | Instrument drift | Feature-shift report lights up (lactate SMD 0.22) while means barely move; AUROC falls 0.73 to 0.68 |
| 4 | Label noise in development | Deployment AUROC 0.71 *beats* internal validation 0.65. The labels are the broken instrument, not the model |
| 5 | Subgroup with a different risk relationship | Aggregate looks mediocre; group 0 AUROC 0.76, group 1 AUROC 0.56 on 43% of the ward |
| 6 | Out-of-distribution patients | AUROC *improves* to 0.78 while the model becomes unusable. Ensemble spread and abstention pay off most here |

Deliverable is a **five-minute presentation**: what did you find, what exposed it,
was it calibrated, who is least trustworthy, when should it abstain, what would
reduce the uncertainty, would you deploy. Marked against a rubric that weights
diagnosis and honesty above modelling - `project/RUBRIC.md`.

**The debrief is the payoff.** Teams present in a deliberate order, and the module
closes by putting team 2 and team 6 on screen together: same task, same columns,
one model with a *worse* AUROC that is safe to deploy and one with a better AUROC
that is not.

Datasets, brief, rubric and a full instructor answer key with reference numbers
for every team are in `project/`. `python project/check_signatures.py` reproduces
every number in the key.

---

## What I need from the organisers

1. **Placement.** Both lectures work best after the school's Bayesian foundations
   session and before or alongside the SBI material. The two lectures should be
   on the same day or consecutive days; Lecture 2 opens where Lecture 1 closed.
2. **Project block.** Three hours of working time plus 45 minutes of
   presentations. Teams of three or four, six teams if numbers allow - fewer is
   fine, the failure modes are independent and any subset works.
3. **Room support.** Since I am remote, one person in the room during the project
   block to circulate between teams. I will be available on a call throughout and
   will join for the debrief.
4. **Kit.** Participants need a browser and a Google account for Colab, or a local
   Python 3.10+ environment. Nothing else. No clinical data, no credentialing, no
   GPU.
5. **A question about the audience.** How much clinical exposure should I assume?
   The material currently assumes none and explains the medical context as it
   goes. If a substantial share of participants are already working with health
   data, I would trade some of that explanation for more depth on hierarchical
   models and on prospective monitoring design.

## Materials

Repository: `github.com/vafaei-ar/ai-uncertainty-2026-healthcare`

Every notebook ships in student and instructor variants, generated from one
source so they cannot drift apart. Instructor copies carry worked solutions and
teaching notes. All notebooks execute end to end on CPU; the two lecture
notebooks take under ten seconds each, the PyMC and SBI deep-dives about a minute.

## Open questions I would value your view on

- Is 90 minutes per lecture right, or would the school prefer 60 with more
  project time? Lecture 1 has an obvious cut point at 70 minutes.
- Should the team project run against MIMIC-IV for groups who want it? The
  simulator is designed so the same workflow transfers, but that adds a
  credentialing step that would need to start well before November.
- Would a short pre-workshop notebook be useful, so participants arrive with a
  working environment and the Bayesian basics fresh?
