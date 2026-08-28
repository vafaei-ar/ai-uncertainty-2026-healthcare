# AI Uncertainty 2026 Healthcare

Prototype repository for the healthcare AI module of the **AI & Uncertainty School and Workshop 2026** in Mauritius.

## Core contents
- Bayesian updating and posterior uncertainty
- calibration and proper scoring rules
- epistemic vs aleatoric uncertainty
- site and prevalence shift
- informative missingness
- subgroup reliability
- selective prediction / abstention
- hierarchical thinking
- a simple simulation-based inference bridge
- team project with hidden failure modes

## Main notebook
`01_trustworthy_medical_ai_uncertainty_demo.ipynb`

The notebook is designed for **Google Colab** and the free CPU tier. It currently uses synthetic EHR-like data so participants can run everything immediately without credentialing or protected data access. The same workflow can later be adapted to MIMIC-IV or another open clinical dataset.

## Planned expansion
- PyMC hierarchical model notebook
- neural SBI notebook with `sbi`
- GPyTorch emulator notebook
- MIMIC-IV transfer notebook
- student and instructor versions
- pre-generated team datasets with hidden failure modes
