# Mauritius healthcare module: final teaching and research QA

**Reviewed:** 9 November 2026  
**Scope:** one integrated lecture, synthetic data and notebooks,
three-day research plan, student/facilitator instructions, and provenance.
**Status:** materials pass automated execution and visual-layout checks.
Local facilitation and final timetable still need organizer confirmation.

## Readiness verdict

**Ready for an instructor-led rehearsal, subject to local logistics.**
This is a reproducible educational simulation. It does not validate a
clinical risk model or establish a novel method suitable for publication.

## Checks completed

| Area | What was checked | Result |
| --- | --- | --- |
| Scientific framing | Risk meaning, AUROC vs calibration, input vs outcome shift, recalibration, label leakage | Corrected and referenced |
| Experimental comparison | Fixed unchanged/intercept/Platt methods, paired Brier comparisons, independent target test cohorts | Executed in CI |
| Sparse labels | Audits of 25, 75, 150 and non-estimable logistic corrections | Explicit fallback reported |
| Data access | Only synthetic data. Public teaching answer key removed from current files | Confirmed |
| README and links | One lecture, one main student notebook, archived older programme | Current relative links verified |
| Presenter notes | Full notes on 23 slides, with source blocks for six methodological slides | Passed |
| Slide geometry | 23 widescreen slides without off-canvas elements | Passed |
| Visual rendering | Converted all 23 slides to PDF then PNG; inspected three contact sheets | Corrected seven wrapped headings |
| Typography | Visible text runs no smaller than 13 pt in generated PowerPoint | Passed structural check |
| Style | Removed narrative semicolons and overt assistant drafting artifacts in current teaching documents | Passed textual audit |
| Provenance | PowerPoint title, author, presenter notes and packaging workflow | No explicit claim of AI authorship in displayed content |

**Visual QA:** [contact sheet 1](qa/integrated_lecture_contact_sheet_1.png),
[contact sheet 2](qa/integrated_lecture_contact_sheet_2.png),
[contact sheet 3](qa/integrated_lecture_contact_sheet_3.png).
The PowerPoint and figures remain editable/reproducible through
`slides/src/one_lecture.js` and `slides/make_figures.py`.

## Specific corrections made

- Replaced a dense research comparison slide with an editable diagram
  separating source training, target-audit adjustment, and independent
  target testing.
- Shortened slide headings that overlapped charts or cards in the first
  rendered version.
- Corrected the calibration sample-size figure to account for
  one-class audits by an explicitly described unchanged-model fallback.
- Replaced a misleading "aleatoric" label with a threshold-proximity
  proxy in the risk-coverage figure.
- Clarified that 75 labels belong to the initial orientation example,
  whereas later 25/75/150 comparisons use new simulated cohorts.
- Specified the Brier score as the primary comparison and added
  scientific references for established updating methods.
- Added a beginner-friendly starting guide and two-hour daily
  facilitation schedule.
- Clarified that old Git commits may still expose the synthetic
  orientation outcome key. The project is open and reproducible,
  not a secure blind leaderboard.

## Evidence for feasibility

The repository includes a runnable Python notebook, a deterministic
synthetic-data generator, and prewritten baseline and comparison
functions. Students with limited Python experience can change one
label budget or shift and interpret the output. Experienced teams can
test one falsifiable extension. The local facilitator should protect
approximately **2–3 hours of project work daily**.

**Minimum successful project:** one valid baseline, one alternative,
two label budgets, independent evaluation, several seeds, one figure,
and a five-minute interpretation. This is feasible with provided code.
A substantive research novelty result is not guaranteed in three days.

## Scientific limitations and publication

The clinical prediction literature already includes intercept and
logistic recalibration, model updating under drift, and warnings about
small external validation samples. See
[REFERENCES_AND_READING.md](REFERENCES_AND_READING.md).
This workshop should not claim to invent those methods.

Publication would require a clearly differentiated extension,
a broader and adequately repeated experiment, uncertainty estimates,
and preferably evaluation beyond this single simulator. Current
three-replicate CSV summaries are demonstration results, not precision
estimates.

## Provenance statement

The presentation uses normal author and title metadata for the faculty
presenter and includes code-generated quantitative figures. Source code
and repository history document the production workflow. No slide
claims that an AI system authored the presentation. We did not
fabricate editing history, timestamps, or software identity.

Automated assembly metadata can be visible in office files. Such
metadata indicate a production method, not necessarily an AI author.
This audit does not guarantee that an AI classifier will assign a
particular label.

## Open operational requirements

1. Confirm the exact lecture slot and protected student project time.
2. Confirm student numbers and Python experience. Adapt facilitator
   staffing to the number and skill levels of groups.
3. Have an in-room technical facilitator for the remote presenter.
4. Run the live Colab link once in a fresh browser runtime after merge
   to verify GitHub access and workshop-day connectivity.
5. Agree on the progress-summary time (17:00–18:00 Mauritius time).
6. If collaboration later contributes to NIH-supported research,
   follow Penn State Research Security and Export Compliance guidance.

**Recommendation:** Keep the changes in PR #2 for faculty review.
Merge only after the organizer confirms group-work support and the
student start experience has been rehearsed.
