# One-lecture delivery guide

**Lecture:** When Can We Trust Clinical AI at a New Hospital?  
**Format:** remote, approximately 60 minutes with student questions  
**Slides:** [Integrated deck](../slides/lecture_when_can_we_trust_clinical_ai.pptx)  
**Detailed notes:** [Presenter guide](ONE_LECTURE_PRESENTER_GUIDE.md)

## Teaching sequence

| Minutes | Slides | What students should learn |
| --- | --- | --- |
| 0–13 | 1–5 | Meaning of a 30% risk, AUROC versus calibration |
| 13–21 | 6–9 | External transfer and limits of input monitoring |
| 21–28 | 10–12 | Uncertainty and informative missingness |
| 28–35 | 13–15 | Two calibration updates and scarce outcome labels |
| 35–43 | 16–18 | Optional discussion of review and subgroup reliability |
| 43–51 | 19–21 | Decisions, independent training/update/test data |
| 51–60 | 22–23 | Three-day research question and student questions |

If lecture time is reduced, prioritize slides **1–9, 14–15 and 19–23**.
Treat uncertainty proxies and referral policies as optional context.
Do not rush the separation between update and independent test labels.

## Delivery preparation

1. Practice explaining AUROC, calibration and Brier score without
   formulas before showing a graph.
2. Explain that the synthetic outcome is **deterioration within 48 hours**.
   None of the probabilities or datasets have clinical validation.
3. Show the relationship between training at Hospital A, updating at
   Hospital B, and testing on separate simulated admissions.
4. Confirm that the notebook opens in a fresh Colab runtime and
   reproduces a baseline comparison.
5. Agree on daily time blocks and a local facilitator with Bruce.
6. Ask students to report label budgets, event counts, seeds, paired
   Brier changes and limitations.

## Scientific cautions

- AUROC measures ranking, not correctness of risk probabilities.
- Input distribution similarity does not establish unchanged outcome
  relationships.
- Measurement drift may also alter conditional risk.
- Ensemble disagreement is a proxy, not a guarantee of correctness.
- Fitting on the 75 target-audit outcomes and evaluating on those same
  labels gives an optimistically biased estimate.
- A 25-label audit may contain very few events or none at all.
- Three trial repetitions show the workflow, not the precision
  required for a publication.
- Review of an uncertain case does not automatically prevent harm.
- The MIMIC-inspired adapter demonstrates toy table joins only.

## Backup

Keep existing generated figures and the main baseline result available
when internet access fails. Do not make up new results to replace
unavailable computation.

Older detailed rehearsal plans are in
[the archive](archive/LECTURE_DELIVERY_GUIDE.md).
