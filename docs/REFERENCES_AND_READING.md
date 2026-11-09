# References and further reading

These references support the main teaching concepts. They do **not**
establish that this workshop's simulation comparison is a new method.

1. Van Calster B, McLernon DJ, van Smeden M, et al. Calibration: the
   Achilles heel of predictive analytics. *BMC Medicine*. 2019;17:230.
   DOI: [10.1186/s12916-019-1466-7](https://doi.org/10.1186/s12916-019-1466-7).
   PMID: [31842878](https://pubmed.ncbi.nlm.nih.gov/31842878/).
   **Use for:** calibration meaning, calibration assessment,
   and overinterpretation of risk probabilities.

2. Binuya MAE, Engelhardt EG, Schats W, et al. Methodological guidance
   for the evaluation and updating of clinical prediction models:
   a systematic review. *BMC Medical Research Methodology*.
   2022;22:316. DOI:
   [10.1186/s12874-022-01801-8](https://doi.org/10.1186/s12874-022-01801-8).
   PMID: [36510134](https://pubmed.ncbi.nlm.nih.gov/36510134/).
   **Use for:** discrimination versus calibration, external validation,
   recalibration, and model updating strategies.

3. Riley RD, Archer L, Snell KIE, et al. Evaluation of clinical
   prediction models (part 3): calculating the sample size required for
   an external validation study. *BMJ*. 2024;384:e074821.
   DOI: [10.1136/bmj-2023-074821](https://doi.org/10.1136/bmj-2023-074821).
   PMID: [38253388](https://pubmed.ncbi.nlm.nih.gov/38253388/).
   **Use for:** why small external-validation samples produce uncertain
   discrimination and calibration estimates. This article addresses
   validation sample size, not a universal minimum for recalibration.

4. A nonparametric updating method to correct clinical prediction model
   drift. *Journal of the American Medical Informatics Association*.
   2019. PMID:
   [31397478](https://pubmed.ncbi.nlm.nih.gov/31397478/).
   **Use for:** precedent that updating methods can be compared under
   population shift, including the possibility that simpler updates
   outperform more complex ones. This article is important when judging
   whether the proposed student comparison is methodologically novel.

## Scientific positioning for the Mauritius project

Simple intercept and logistic recalibration already exist in the clinical
prediction literature. **Comparing those two methods alone is educational,
not automatically publishable.** Any research manuscript needs a specific
new question, a literature-based gap, broader and repeated simulations,
and preferably external evaluation on a different data source.

This repository supplies reproducible synthetic examples and student
research training, not clinical evidence or a claim of novelty.
