# From synthetic teaching data to real MIMIC-style EHR analysis

## What this repository means by MIMIC-inspired

The current teaching generator produces a **flat, synthetic analysis cohort**,
one admission per row, with age, vital signs, lab values, comorbidities,
a synthetic group indicator, and a simulated 48-hour deterioration outcome.

MIMIC-IV is a real-world relational database and is more complicated than
this cohort. Our synthetic data are **not drawn from MIMIC-IV**, are not a
validated replica, and do not carry clinically established event definitions.

To give students a concrete bridge, project/mimic_like_adapter.py creates
the following toy relational tables, using synthetic IDs and codes:

| Teaching table | Concept in a real EHR | Teaching content |
| --- | --- | --- |
| patients | Person-level demographics | synthetic subject ID, age, synthetic group |
| admissions | Hospital encounters | synthetic admission ID, pseudo admission time, site |
| chartevents | Bedside observations | heart rate, systolic BP, respiratory rate |
| labevents | Laboratory measurements | creatinine, lactate, WBC |
| diagnoses_icd | Coded diagnoses | synthetic prior stroke/diabetes flags |
| outcomes | Research label (kept separate) | simulated 48-hour deterioration |

This mimics *table separation and joins*, not the full official schema,
coding systems, timestamps, provenance, or clinical workflow.

The programmatic adapter uses item codes starting SYN_. **These are not
valid MIMIC item IDs or billing codes**. The times are illustrative. The
adapter does not define observation windows or model prediction timestamps.

## Conceptual extraction pipeline

1. Select an admission cohort and define an exact prediction time.
2. Join person, admission, vital-sign, laboratory, and diagnosis sources
   using the correct identifiers and encounter times.
3. Aggregate only observations available *before* the prediction time.
4. Define a clinically defensible deterioration outcome after prediction.
5. Exclude information that would leak the future outcome into features.
6. Use admission- or patient-aware source/target splits where necessary.
7. Repeat the same calibration/transfer evaluation with valid labels.

The toy adapter only demonstrates joins in step 2. It does not implement
a real MIMIC-IV cohort pipeline. Applying the workshop workflow to real MIMIC
requires its own cohort definition, data-access permissions, validated
coding, preprocessing, outcome ascertainment, and scientific review.

## Important distinctions

- A 30% predicted risk means something only if the outcome, time horizon,
  target population, and calibration have been specified.
- Synthetic hospital shift shows a possible failure mechanism, not its
  empirical prevalence in any actual hospital.
- Real MIMIC data have variable observation frequency and complex temporal
  provenance. A flat synthetic row ignores most of that information.
- Success with a simulator is evidence about the simulation, not about
  the clinical effectiveness of a deployment.

## Usage

    python -m project.mimic_like_adapter --demo

The command makes a small synthetic relational demonstration, reconstructs
selected analysis features, and checks values against the starting flat
records. This is a teaching artifact only.
