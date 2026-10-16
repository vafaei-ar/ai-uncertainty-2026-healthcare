# October 2026: healthcare module delivery guide (working draft)

**Existing assets:** Lecture 1 (24 slides), Lecture 2 (25 slides), matching Colab notebooks, optional PyMC/SBI deep dives, six-team synthetic-data project.
**Pending organiser confirmation:** two lecture slots, their length, whether a group project slot exists, and how remote project support would work.

## Protect three ideas per lecture

**Lecture 1: Honest probabilities in clinical prediction**
1. A predicted risk is a claim about the world: discrimination and calibration are distinct.
2. Different uncertainty sources require different responses; extra rows are not always the answer.
3. Hospital transfer can change the inputs, the risk conditional on the inputs, or both. Input monitoring alone cannot verify calibration.

**Lecture 2: Deciding under uncertainty**
1. Probability recalibration requires appropriately collected target-site outcome labels.
2. Deferral can help only when its rule and downstream clinical review are evaluated; ensemble spread is a **proxy**, not a reliability guarantee.
3. Action thresholds depend on consequences, constraints and the care pathway; always compare against a no-model policy.

## Flexible speaking plan

The following slide numbers refer to the *current* `slides/src/deck1.js` and `deck2.js` generators.

| Slot | Lecture 1 core (60 minutes) | Optional material for 90 minutes |
| --- | --- | --- |
| 0-5 | Slides 1-3, opening question | Longer group question |
| 5-20 | Slides 7-9, ranking vs calibration | Slides 4-6, brief posterior updating |
| 20-35 | Slides 10-13, sources of uncertainty | Live notebook demonstration and discussion |
| 35-50 | Slides 17-20, second hospital and monitoring | Slides 14-16, simulator and performance intervals |
| 50-60 | Slides 21-24, missingness and takeaways | Revisit discussion, questions |

| Slot | Lecture 2 core (60 minutes) | Optional material for 90 minutes |
| --- | --- | --- |
| 0-5 | Slides 1-3, reconnect to Lecture 1 | Group recap |
| 5-19 | Slides 4-7, recalibration and labels | Colab demo: intercept vs flexible fixes |
| 19-36 | Slides 8-14, ensembles and selective prediction | Compare alternative deferral rules |
| 36-48 | Slides 15-17, consequences and thresholds | Decision-curve example and sensitivity |
| 48-55 | Slides 18-19, subgroup reliability | Subgroup discussion |
| 55-60 | Slides 23-25, synthesis and project | Slides 20-22, optional PyMC/SBI bridge |

The 60-minute versions omit entire optional sections rather than speaking through all 24-25 slides too quickly. In the 90-minute versions, use notebook exercises and discussion, not extra dense slides.

## Corrections/qualifications to make before presenting

- **Measurement noise:** The simulator adds noise to *observed* readings after outcomes are generated. Such changes can affect `P(Y|X_observed)`; avoid labeling the entire Site C example as **pure covariate shift**. A feature-distribution alarm may fire here, but the general claim does not follow from feature SMD checks alone.
- **Transport:** A good AUROC can coexist with poor calibration, **but ranking does not invariably survive hospital transfer**.
- **Ensemble disagreement:** Bootstrap spread captures sensitivity to a particular resampling/model procedure. It is neither a full posterior nor a guaranteed OOD detector.
- **Clinical threshold:** `1/(1+R)` is a threshold for an idealised two-action cost model with calibrated probabilities, not an unconditional ICU rule. Workflow, resource constraints and effects of intervention also matter.
- **Deferral:** Passing a patient to review consumes capacity; safety benefit must be evaluated rather than presumed.
- **Medical representativeness:** Call the current simulator 'synthetic EHR-like', not 'validated against MIMIC-IV'.

## Remote teaching and technical checklist

1. Check one fresh Google Colab session for each student notebook and time setup. The notebooks clone the repository; the current README claims the lecture runs are short, but **Colab execution has not been independently rechecked in this review**.
2. Keep rendered slide figures and completed output examples as backup if Colab, Wi-Fi or the projector fails.
3. Rehearse 60-minute talk tracks first, then add the optional 30 minutes.
4. Have an in-room contact who can share the screen and circulate among teams, if a project is approved.
5. Preflight mic, screen sharing, live notebook, time zone and any institute/compliance clearance before the workshop.
6. Prefer no student logins beyond what Colab needs; no patient-level clinical data.

## Work order

**First:** finalise and rehearse Lecture 1's core story, correct the Site C shift phrasing, and update its speaker cues.

**Second:** run the same pass over Lecture 2, replacing universal safety claims with appropriately qualified, case-specific statements.

**Third:** build and dry-run the open challenge in `project/OPEN_RESEARCH_CHALLENGE_DRAFT.md`, keeping the existing six-team exercise as a fallback.

**Then:** confirm the programme's actual slots and in-room facilitation. The public workshop site currently notes that remote attendance may be possible for lectures but not group work; whether remote *instruction* of in-room teams is acceptable needs organiser confirmation.
