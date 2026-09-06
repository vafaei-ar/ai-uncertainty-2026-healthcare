# Trustworthy medical AI under real-world uncertainty

Healthcare AI module for the **AI & Uncertainty School and Workshop 2026**,
Mauritius, 16-20 November 2026.

Two 90-minute lectures, two deep-dive notebooks, and a three-hour team project
built around one question:

> Can you build a clinical prediction system that knows when it should not be
> trusted?

Everything runs on the free Google Colab CPU tier against a synthetic EHR
simulator. No credentialed data, no GPU, no local install required.

---

## Start here

| Notebook | What it covers | Runtime |
| --- | --- | --- |
| `notebooks/01_lecture1_uncertainty_foundations_student.ipynb` | Bayesian updating, discrimination versus calibration, epistemic versus aleatoric uncertainty, distribution shift, informative missingness | ~10 s |
| `notebooks/02_lecture2_trustworthy_deployment_student.ipynb` | Recalibration, ensemble uncertainty, selective prediction, decision thresholds and net benefit, subgroup reliability, partial pooling, an SBI bridge | ~10 s |
| `notebooks/03_hierarchical_pymc_student.ipynb` | Full hierarchical logistic regression in PyMC: varying intercepts and slopes across hospitals, shrinkage, posterior predictive checks | ~1 min |
| `notebooks/04_simulation_based_inference_student.ipynb` | Neural posterior estimation with `sbi`, amortised inference, and a coverage check on the posterior | ~1 min |
| `notebooks/90_team_project_starter.ipynb` | Loads your team's data and runs the first comparison that should make you suspicious | ~5 s |

Slides for both lectures are in `slides/`, with speaker notes. They are generated
rather than hand-built - `slides/make_figures.py` renders the figures from the
same `medsim` code the notebooks use, and `slides/src/` holds the deck
generators - so a number on a slide cannot drift from the number in the notebook.

Instructor copies of the lectures and deep-dives sit alongside each student file
with worked solutions and teaching notes. Both variants are generated from a
single source in `notebooks/source/`, so they cannot drift apart.

## Repository layout

```
medsim/           simulator and evaluation metrics
notebooks/        built notebooks (student + instructor)
notebooks/source/ notebook sources; edit these, not the .ipynb files
project/          team datasets, brief, rubric, instructor answer key
slides/           lecture decks, their figures, and the generators
docs/             lecture and project plan for the organisers
tools/            notebook builder and headless runner
archive/          the September 2026 prototype, superseded
```

## Rebuilding

```bash
pip install -r requirements.txt

python notebooks/source/lecture1.py          # rebuild a notebook pair
python project/make_team_data.py             # regenerate team datasets
python project/check_signatures.py           # verify every failure mode is still detectable
python tools/run_notebook.py notebooks/01_lecture1_uncertainty_foundations_instructor.ipynb
python slides/make_figures.py                # re-render the slide figures
```

Seeds are fixed throughout, so regenerating reproduces the reference numbers in
`project/ANSWER_KEY.md`.

## The simulator

`medsim.simulate_ehr` generates admissions with vitals, labs and comorbidities
and a 48-hour deterioration outcome. Every failure mode is a named argument:

```python
from medsim import SimConfig, simulate_ehr

cohort = simulate_ehr(SimConfig(
    n=5000,
    site="B",
    prevalence_shift=0.5,       # baseline risk differs between hospitals
    measurement_noise=2.5,      # instruments and assays drift
    missingness_strength=1.4,   # labs are ordered for a reason
    label_noise=0.15,           # chart review is imperfect
    subgroup_shift=1.0,         # a subgroup carries different baseline risk
    subgroup_interaction=-1.8,  # ...or a different risk relationship entirely
    ood_fraction=0.30,          # patients unlike anything in development
))
```

Two design choices are worth knowing about. The generator includes an unrecorded
"clinical concern" variable that moves the outcome and appears in no column, so
the achievable AUROC ceiling on these features is around 0.73 rather than 1.0 -
the aleatoric floor is real and visible. And missingness is driven by that same
unrecorded variable, so a blank cell genuinely carries information that median
imputation destroys.

## Team project

Six teams, one task, six different hidden reasons the model should not be
deployed. See `project/PROJECT_BRIEF.md` for the brief and `project/RUBRIC.md`
for how it is marked.

Instructors: `project/ANSWER_KEY.md` has the mechanism, reference numbers,
expected traps and a suggested debrief order for each dataset. Do not distribute
it.

## For the organisers

`docs/lecture_and_project_plan.md` has the minute-by-minute plan, scheduling
requirements and open questions.
