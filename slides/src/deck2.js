const pptxgen = require("pptxgenjs");
const T = require("./theme");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Alireza Vafaei Sadr";
pres.company = "Penn State College of Medicine";
pres.subject = "AI & Uncertainty School and Workshop 2026, healthcare module";
pres.title = "Deciding under uncertainty";

// 1 ---------------------------------------------------------------
T.titleSlide(pres, {
  eyebrow: "HEALTHCARE AI MODULE  ·  LECTURE 2",
  title: "Deciding under\nuncertainty",
  subtitle: "AI & Uncertainty School and Workshop 2026\nMauritius, 16-20 November",
  presenter: "Alireza Vafaei Sadr",
  meta: "Penn State College of Medicine  ·  github.com/vafaei-ar/ai-uncertainty-2026-healthcare",
});

// 2 ---------------------------------------------------------------
T.statsSlide(pres, {
  kicker: "WHERE LECTURE 1 LEFT OFF",
  heading: "A good model, offered to a new hospital",
  stats: [
    { value: "0.26", label: "Observed event rate\non the new ward" },
    { value: "0.15", label: "Mean predicted risk\nthe model's claim" },
    { value: "0.71", label: "AUROC\nbarely moved" },
  ],
  footnote:
    "The ranking transferred. The numbers did not. The model tells site B that 15% of their ward is at risk while 26% of it deteriorates. " +
    "This lecture is about what you do next.",
});

// 3 ---------------------------------------------------------------
T.listSlide(pres, {
  kicker: "WHERE WE ARE GOING",
  heading: "From a broken number to a defensible decision",
  twoColumn: true,
  items: [
    { title: "Repairing calibration", body: "And what it costs in labelled patients from the new site" },
    { title: "Ensembles as an epistemic signal", body: "The one check you can run with no outcome data" },
    { title: "Letting the model abstain", body: "Risk-coverage curves and who gets deferred" },
    { title: "Thresholds from clinical costs", body: "Not from 0.5, and usually far lower than expected" },
    { title: "Subgroup reliability", body: "Why the aggregate number lies" },
    { title: "Hierarchy and simulators", body: "Borrowing strength, and posteriors without a likelihood" },
  ],
});

// 4 ---------------------------------------------------------------
T.sectionSlide(pres, {
  number: 1,
  title: "Recalibration, and what it costs",
  blurb: "Every repair needs labelled patients from the new site. That is the real cost of deployment, and it is usually left out of the project plan.",
});

// 5 ---------------------------------------------------------------
T.tableSlide(pres, {
  kicker: "THREE REPAIRS, INCREASING FLEXIBILITY",
  heading: "Match the fix to the labels you can actually get",
  columns: ["Method", "What it fits", "Params", "When it is the right choice"],
  widths: [2.4, 3.0, 1.1, 5.3],
  rows: [
    ["Intercept correction", "A shift on the logit scale", "1", "Prevalence changed, the risk ordering did not"],
    ["Platt scaling", "Slope and intercept on the logit scale", "2", "Ordering is right but the spread is wrong too"],
    ["Isotonic regression", "Any monotone map", "many", "Plenty of labels and a distortion of unknown shape"],
  ],
  footnote:
    "None of the three reorders anyone, so AUROC is untouched by all of them. What they repair is the meaning of the numbers.",
});

// 6 ---------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "SITE B, RECALIBRATED ON 2400 LABELLED PATIENTS",
  heading: "One parameter fixes most of it",
  image: "figures/l2_recalibration.png",
  reading:
    "A single intercept recovers most of the gain, because a single intercept is exactly the damage that was done. " +
    "Brier, log loss and ECE improve sharply; AUROC does not move at all.",
});

// 7 ---------------------------------------------------------------
T.figureWithNotes(pres, {
  kicker: "HOW MANY CHARTS DOES A FIX ACTUALLY NEED?",
  heading: "Flexibility you cannot afford makes things worse",
  image: "figures/l2_calibration_cost.png",
  blocks: [
    {
      title: "One parameter, 100 charts",
      body: "The intercept correction is close to its ceiling at around 100 labelled patients from the new site.",
    },
    {
      title: "Isotonic needs 10x more",
      body: "Below a few hundred labels it is worse than doing nothing at all - it spends its flexibility fitting noise.",
    },
    {
      title: "So plan the label budget",
      body: "A one-parameter fix on 100 charts beats a non-parametric fix on the same 100 charts, every time.",
    },
  ],
}).addNotes(
  "Ask what happens if the model is recalibrated on the first 100 patients of a seasonal wave. " +
  "The correction inherits whatever period it was estimated in - recalibration is a maintenance commitment, not a one-off task."
);

// 8 ---------------------------------------------------------------
T.sectionSlide(pres, {
  number: 2,
  title: "Ensembles as an epistemic signal",
  blurb: "Refit on bootstrap resamples. Where the models agree, the data pinned the answer down. Where they disagree, the prediction is an extrapolation.",
});

// 9 ---------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "A WARD WHERE 30% OF PATIENTS ARE UNLIKE ANYTHING IN DEVELOPMENT",
  heading: "In this simulation, disagreement flags unfamiliar patients",
  image: "figures/l2_ensemble_ood.png",
  reading:
    "The threshold is the 95th percentile of disagreement measured on the development data alone - so it can be set before the model goes live.",
});

// 10 --------------------------------------------------------------
T.statsSlide(pres, {
  kicker: "A GATE SET ON DEVELOPMENT DATA, APPLIED TO A NEW WARD",
  heading: "The check you can run on day one",
  stats: [
    { value: "25%", label: "of the new ward\nflagged by the gate" },
    { value: "87%", label: "of those flagged\nare genuinely out-of-distribution" },
    { value: "73%", label: "of the truly unfamiliar\npatients are caught" },
    { value: "0", label: "outcome labels\nrequired from the new site" },
  ],
  footnote:
    "This proxy needs no target outcome labels, but success in one simulated ward does not guarantee safe detection elsewhere.",
});

// 11 --------------------------------------------------------------
T.statementSlide(pres, {
  claim: "Bootstrap disagreement measures sensitivity to the training sample, not distance from the training distribution.",
  support:
    "A patient far outside the data can still receive confident, wrong, unanimous predictions if the model form extrapolates smoothly. " +
    "Treat this as a screen, not a guarantee. Ensembles, conformal prediction and input-drift checks address different questions - " +
    "conformal coverage guarantees generally depend on exchangeability; they do not certify target-site safety when that assumption fails.",
});

// 12 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 3,
  title: "Letting the model abstain",
  blurb: "A deployed model does not have to answer every question. Rank by uncertainty, hand the worst back to a clinician, and measure what remains.",
});

// 13 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "RISK-COVERAGE ON THE UNFAMILIAR WARD",
  heading: "Does the model know what it does not know?",
  image: "figures/l2_risk_coverage.png",
  reading:
    "Random deferral is the null: it shrinks the cohort and improves nothing, so its curve is flat. Any ranking worth using must beat it.",
});

// 14 --------------------------------------------------------------
T.compareSlide(pres, {
  kicker: "TWO SIGNALS, TWO DIFFERENT JOBS",
  heading: "They defer different patients, and that is the point",
  left: {
    title: "Aleatoric: distance from 0.5",
    body:
      "Defers genuinely borderline patients.\n\n" +
      "Mechanically reduces classification error, so it usually looks strongest on a risk-coverage plot.\n\n" +
      "Use it to triage the borderline cases into human review.",
  },
  right: {
    title: "Epistemic: ensemble disagreement",
    body:
      "May flag patients for whom the fitted model is unstable.\n\n" +
      "Does not detect every unfamiliar patient and cannot guarantee safe deployment.\n\n" +
      "Evaluate this signal before using it as a referral rule.",
  },
  footnote: "Do not collapse them into one score. Report both, and use them for different things.",
}).addNotes(
  "Notebook exercise: a service that can review 20% of admissions by hand builds a two-stage rule - " +
  "epistemic gate first, then spend whatever budget remains on the most borderline of the rest."
);

// 15 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 4,
  title: "The threshold is a clinical decision",
  blurb: "A default threshold of 0.5 is rarely justified without specifying the consequences of mistakes and the care pathway.",
});

// 16 --------------------------------------------------------------
T.tableSlide(pres, {
  kicker: "IDEALISED TWO-ACTION COST MODEL: ASSUMING CALIBRATED RISKS, THRESHOLD = 1 / (1 + R)",
  heading: "Where the operating point actually sits",
  columns: ["Cost ratio R", "Threshold", "Alert rate, uncorrected", "Alert rate, recalibrated"],
  widths: [2.4, 2.4, 3.5, 3.5],
  rows: [
    ["2 : 1", "0.333", "6%", "30%"],
    ["5 : 1", "0.167", "29%", "71%"],
    ["10 : 1", "0.091", "61%", "91%"],
    ["20 : 1", "0.048", "86%", "99%"],
  ],
  footnote:
    "Here the useful range is far below 0.5. These thresholds come from simplified cost assumptions and must be adapted to the clinical workflow; the uncorrected model " +
    "under-alerts worst exactly where the clinical value lives.",
});

// 17 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "DECISION CURVE ANALYSIS",
  heading: "Is the model better than what we would do without it?",
  image: "figures/l2_net_benefit.png",
  reading:
    "At a 10:1 cost ratio the recalibrated model earns a net benefit of about 0.19 against roughly 0.19 for escalating the entire ward. " +
    "On a ward with a 26% event rate, at that cost ratio, the model is not adding much over a blanket policy.",
}).addNotes(
  "Where does R come from? Not from the data - from the service. ICU bed availability, staffing, what the escalation actually involves. " +
  "Getting a clinician to state R is often the most valuable hour of a deployment project, and the number is rarely what the modelling team assumed."
);

// 18 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 5,
  title: "The aggregate number lies",
  blurb: "A model can be well calibrated overall and badly calibrated for every subgroup in it, because the subgroup errors cancel.",
});

// 19 --------------------------------------------------------------
T.figureWithNotes(pres, {
  kicker: "A SUBGROUP THAT WAS 8% OF DEVELOPMENT DATA AND IS 39% OF THIS WARD",
  heading: "One ward, two very different models",
  image: "figures/l2_subgroup.png",
  blocks: [
    {
      title: "A coin flip for 39% of the ward",
      body: "AUROC 0.72 for the majority group, 0.54 for the minority - and their risk is understated throughout.",
    },
    {
      title: "A shift report finds nothing",
      body: "The covariate distributions are fine. What differs is the conditional relationship between labs and outcome.",
    },
    {
      title: "A sample-size problem",
      body: "657 training patients could never have identified that interaction. This is the case for the next section.",
    },
  ],
}).addNotes(
  "Always report stratified: by every categorical column, by age band, and by whether key labs were recorded. " +
  "If a stratum is too small to evaluate, that is itself the finding."
);

// 20 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 6,
  title: "Hierarchy, and simulators",
  blurb: "Four hospitals report deterioration rates. One of them saw four patients and one event.",
});

// 21 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "PARTIAL POOLING ACROSS FOUR HOSPITALS",
  heading: "How far each site is pulled is estimated, not chosen",
  image: "figures/l2_pooling.png",
  reading:
    "The large teaching hospital is barely moved; the new unit almost entirely. That is what separates hierarchical modelling from " +
    "fitting each site alone (the new unit gets a 25% rate) or one model for all sites (site differences vanish).",
}).addNotes("This is the principled answer to the subgroup problem: give the small group its own parameters, and let the data decide how far to shrink them.");

// 22 --------------------------------------------------------------
T.compareSlide(pres, {
  kicker: "WHEN THE MODEL IS A SIMULATOR",
  heading: "A posterior over parameters that mean something",
  left: {
    title: "Rejection sampling (ABC)",
    body:
      "Simulate from the prior, keep the runs whose summaries resemble what you observed.\n\n" +
      "12,000 simulations to keep 240. The acceptance rate collapses as soon as the parameter has more than one or two dimensions.",
  },
  right: {
    title: "Neural posterior estimation",
    body:
      "Train a density estimator on the simulations, so every one of them contributes.\n\n" +
      "Amortised: once trained, the posterior for a new observation comes out without rerunning the simulator.",
  },
  footnote:
    "Why a clinical audience should care: a progression rate or an effect size is something a clinician can argue with.",
}).addNotes(
  "Notebook 04 does this with the sbi package and includes a coverage check - the neural posterior is sharper but slightly over-confident, " +
  "which ties straight back to the calibration theme of Lecture 1."
);

// 23 --------------------------------------------------------------
T.listSlide(pres, {
  kicker: "LECTURE 2",
  heading: "What to take away",
  twoColumn: true,
  items: [
    { title: "Recalibrate, and budget the labels", body: "Match the flexibility of the fix to what you can collect" },
    { title: "Ensemble spread needs no outcomes", body: "The check you can run on day one" },
    { title: "Keep the two uncertainties apart", body: "They belong in different parts of an abstention rule" },
    { title: "The threshold comes from the costs", body: "And is usually far below 0.5" },
    { title: "Report everything stratified", body: "A stratum too small to evaluate is itself a finding" },
    { title: "Let the data decide the pooling", body: "Small sites and small subgroups borrow strength" },
  ],
});

// 24 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 7,
  title: "Your project",
  blurb: "One open question: can we trust a model at a new hospital with very few outcome labels?",
});

// 25 --------------------------------------------------------------
T.statementSlide(pres, {
  claim: "The task is not to raise AUROC.",
  support:
    "Teams receive 4,000 labeled source records, 1,600 unlabeled new-hospital records, and 75 randomly audited outcomes. " +
    "Decide whether to stay in shadow mode, adapt, or defer predictions and what evidence you would collect next. " +
    "No fixed answer, no formal grading. Five minutes, three slides.\n\n" +
    "Read project/OPEN_RESEARCH_CHALLENGE.md and open notebooks/91_open_research_challenge_starter.ipynb.",
  dark: true,
});

pres.writeFile({ fileName: "lecture2_deciding_under_uncertainty.pptx" }).then(() => console.log("deck 2 written"));
