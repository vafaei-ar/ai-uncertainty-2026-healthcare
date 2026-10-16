const pptxgen = require("pptxgenjs");
const T = require("./theme");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Alireza Vafaei Sadr";
pres.company = "Penn State College of Medicine";
pres.subject = "AI & Uncertainty School and Workshop 2026, healthcare module";
pres.title = "Honest probabilities in clinical prediction";

// 1 ---------------------------------------------------------------
T.titleSlide(pres, {
  eyebrow: "HEALTHCARE AI MODULE  ·  LECTURE 1",
  title: "Honest probabilities in\nclinical prediction",
  subtitle: "AI & Uncertainty School and Workshop 2026\nMauritius, 16-20 November",
  presenter: "Alireza Vafaei Sadr",
  meta: "Penn State College of Medicine  ·  github.com/vafaei-ar/ai-uncertainty-2026-healthcare",
}).addNotes(
  "Open by asking the room: your model says 0.30 for this patient - what does that mean? " +
  "You will get ranking answers and frequency answers. That split is the whole lecture."
);

// 2 ---------------------------------------------------------------
T.statementSlide(pres, {
  claim: "A deployed model does not output a ranking.\nIt outputs a number a tired registrar at 3am\nwill read as a probability, and act on.",
  support: "This session is about whether that number deserves to be read that way.",
}).addNotes("Let the question sit for a moment before moving on. Do not answer it yet.");

// 3 ---------------------------------------------------------------
T.listSlide(pres, {
  kicker: "WHERE WE ARE GOING",
  heading: "Six ideas, one clinical question",
  twoColumn: true,
  items: [
    { title: "A point estimate is not an answer", body: "Posteriors, intervals, and what evidence actually buys you" },
    { title: "Discrimination versus calibration", body: "Neither is guaranteed to transfer across hospitals" },
    { title: "Epistemic versus aleatoric", body: "The distinction decides what you do next" },
    { title: "A synthetic EHR you can break", body: "Every failure mode is a named argument" },
    { title: "The model meets a second hospital", body: "And which monitoring check notices" },
    { title: "The information in a blank cell", body: "Missingness is a recorded clinical decision" },
  ],
}).addNotes("Everything runs on a free Colab CPU. Synthetic data, so no credentialing, and any result can be re-drawn with a new seed.");

// 4 ---------------------------------------------------------------
T.sectionSlide(pres, {
  number: 1,
  title: "A point estimate is not an answer",
  blurb: "A new sepsis alert has fired 10 times. 8 of those led to an intervention the team judged appropriate. Is the alert useful?",
});

// 5 ---------------------------------------------------------------
T.statsSlide(pres, {
  kicker: "TEN ALERTS, EIGHT OF THEM USEFUL",
  heading: "Three honest ways to report the same evidence",
  stats: [
    { value: "0.80", label: "Point estimate\nwhat gets reported" },
    { value: "0.71", label: "Posterior mean\nunder a Beta(2,2) prior" },
    { value: "0.46 - 0.91", label: "95% credible interval\nwhat you actually know" },
  ],
  footnote:
    "The point estimate says 0.80. The interval says the true rate is somewhere between roughly one in two and nine in ten. " +
    "Those two statements support very different decisions, and only one of them is honest about ten observations.",
}).addNotes(
  "Worth saying out loud: the prior did real work. Beta(2,2) plus 10 observations gives a posterior mean of 0.71, not 0.80. " +
  "Ask whether that shrinkage is a bug - it is the same mechanism that saves the small hospital in Lecture 2."
);

// 6 ---------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "BAYESIAN UPDATING",
  heading: "Evidence narrows belief, it does not settle it",
  image: "figures/l1_posterior.png",
  reading:
    "The 95% interval width falls from 0.45 at n = 10 to 0.05 at n = 1000 - roughly as 1 over the square root of n. " +
    "This is epistemic uncertainty: a statement about what you do not yet know, and data removes it.",
}).addNotes("Hold on to that shape. In section 3 we meet the kind of uncertainty that does not go away.");

// 7 ---------------------------------------------------------------
T.sectionSlide(pres, {
  number: 2,
  title: "Discrimination is not calibration",
  blurb: "One asks about order. The other asks about meaning. Deployment breaks meaning first.",
});

// 8 ---------------------------------------------------------------
T.compareSlide(pres, {
  kicker: "TWO DIFFERENT QUESTIONS",
  heading: "What each metric is actually asking",
  left: {
    title: "AUROC asks about order",
    body:
      "Given a patient who deteriorated and one who did not, how often does the model score the first one higher?\n\n" +
      "Invariant to prevalence.\nInvariant to any monotone rescaling.\n\n" +
      "Those are exactly the two things that change when you move a model to a new hospital.",
  },
  right: {
    title: "Calibration asks about meaning",
    body:
      "Among the patients you assigned a risk of 0.3, did about 30% actually deteriorate?\n\n" +
      "Measured by Brier score, log loss, expected calibration error, and the reliability curve.\n\n" +
      "This is the property a threshold, a bed allocation and a clinical conversation all depend on.",
  },
  footnote: "The metric most often reported is the metric most blind to the most common deployment failure.",
});

// 9 ---------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "THREE MONOTONE TRANSFORMATIONS OF ONE SCORE",
  heading: "Same ranking. Same AUROC to four decimals.",
  image: "figures/l1_calibration.png",
  reading:
    "The overconfident model promises a risk far above what the ward delivers, so a fixed threshold floods the ICU. " +
    "The timid model does the opposite and lets patients through. AUROC cannot tell them apart; Brier, log loss and ECE separate them immediately.",
}).addNotes(
  "Exercise in the notebook: recover the temperature that broke the overconfident model. " +
  "It lands near 2.4 because that is how the damage was generated - recalibration works when you have correctly guessed the shape of the damage."
);

// 10 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 3,
  title: "Epistemic and aleatoric uncertainty",
  blurb: "Two reasons a prediction can be uncertain, and only one of them is a modelling problem.",
});

// 11 --------------------------------------------------------------
T.compareSlide(pres, {
  kicker: "THE DISTINCTION IS NOT ACADEMIC",
  heading: "It determines what you should do next",
  left: {
    title: "Epistemic",
    body:
      "You are unsure about the model, because you have seen few patients like this one.\n\n" +
      "Shrinks as you collect more of the same kind of data.\n\n" +
      "Response: collect more records. Or refuse to answer for patients outside the region you have covered.",
  },
  right: {
    title: "Aleatoric",
    body:
      "The outcome is genuinely stochastic given everything you recorded. Two identical charts, different outcomes.\n\n" +
      "Does not shrink with more of the same data.\n\n" +
      "Response: measure something new. No amount of extra rows on the same columns will help.",
  },
  footnote: "Collapse them into one number and you lose the ability to say which response is the right one.",
});

// 12 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "BOOTSTRAP ENSEMBLE OVER FOUR TRAINING SIZES",
  heading: "More data removes one of these, not the other",
  image: "figures/l1_epistemic.png",
  reading:
    "Bootstrap spread - our proxy for epistemic uncertainty - falls steadily from 250 to 16,000 training patients. The aleatoric " +
    "term barely moves; it is a property of the cohort, not of your sample size.",
});

// 13 --------------------------------------------------------------
T.figureWithNotes(pres, {
  kicker: "THE ALEATORIC FLOOR, MADE VISIBLE",
  heading: "The gap to a perfect model was never in your columns",
  image: "figures/l1_ceiling.png",
  blocks: [
    {
      title: "An unrecorded impression",
      body: "The simulator holds a clinical-concern variable that moves the outcome and appears in no column - exactly like the thing the nurse noticed at the bedside.",
    },
    {
      title: "Our model is at the ceiling",
      body: "0.719 fitted against a 0.725 ceiling on the recorded features. There is almost nothing left to extract from these columns.",
    },
    {
      title: "Not a deeper network",
      body: "Moving the ceiling means recording something new. When a reviewer asks why AUROC is not 0.90, that is a claim about the data, not an apology.",
    },
  ],
}).addNotes("If the room only takes one thing from Lecture 1, make it this: know your aleatoric floor before you promise anyone an improvement.");

// 14 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 4,
  title: "A synthetic EHR you can break on purpose",
  blurb: "Vitals, labs, comorbidities and a 48-hour deterioration outcome. Every failure mode is a named argument.",
});

// 15 --------------------------------------------------------------
T.tableSlide(pres, {
  kicker: "THE SIMULATOR'S FAILURE-MODE KNOBS",
  heading: "Turn one on, watch what it does, turn it off",
  columns: ["Argument", "What it represents in a hospital"],
  widths: [3.6, 8.2],
  rows: [
    ["prevalence_shift", "Baseline risk differs between hospitals"],
    ["measurement_noise", "Instruments and assays drift"],
    ["missingness_strength", "Labs get ordered for a reason"],
    ["label_noise", "Chart review is imperfect"],
    ["subgroup_shift", "A subgroup carries different baseline risk"],
    ["subgroup_interaction", "...or a different risk relationship entirely"],
    ["ood_fraction", "Patients unlike anything in development"],
  ],
  footnote: "Each of the six becomes one team's hidden problem in the project block this afternoon.",
});

// 16 --------------------------------------------------------------
T.statsSlide(pres, {
  kicker: "THE ROW THAT GETS REPORTED IN A PAPER",
  heading: "A respectable internal validation - with an interval on it",
  stats: [
    { value: "0.727", label: "Validation AUROC\nthe number that gets published" },
    { value: "0.699 - 0.754", label: "95% bootstrap interval\non 2400 patients" },
    { value: "0.056", label: "Interval width\nwider than most claimed gains" },
  ],
  footnote:
    "Two models whose AUROCs differ by 0.01, or by 0.02, are indistinguishable on this much data. " +
    "A large share of reported improvements in the clinical ML literature are narrower than this interval, and are reported without one.",
}).addNotes("Ask how many papers they have read that report a 0.01 AUROC gain as an improvement, and how many reported an interval.");

// 17 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 5,
  title: "The model meets a second hospital",
  blurb: "Site B has higher risk for similar recorded inputs. Site C has noisier measurements. The fitted model is unchanged.",
});

// 18 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "SAME MODEL, THREE HOSPITALS",
  heading: "Here ranking holds, but risk estimates do not.",
  image: "figures/l1_shift_calibration.png",
  reading:
    "At site B, AUROC holds up and the model understates risk by roughly a factor of two across the whole range. " +
    "Leave the alert threshold at 0.5 and the model essentially stops firing on a ward where a quarter of patients deteriorate.",
});

// 19 --------------------------------------------------------------
T.figureWithNotes(pres, {
  kicker: "COULD YOU HAVE SEEN IT COMING, WITHOUT WAITING FOR OUTCOMES?",
  heading: "Input monitoring sees only part of the problem",
  image: "figures/l1_shift_detection.png",
  blocks: [
    {
      title: "Site C has measurement drift",
      body: "Some measured labs change because instruments are noisier. Input checks can detect a change, but this is not necessarily pure covariate shift.",
    },
    {
      title: "Site B is a conditional shift",
      body: "Every standardised mean difference is under 0.03. The inputs are unchanged; the risk they carry moved. Not label shift - that assumes a stable P(X given Y), which fails here.",
    },
    {
      title: "So the gap is structural",
      body: "Input monitoring watches the inputs. It cannot license a claim about the risk attached to them, however green the dashboard looks.",
    },
  ],
});

// 20 --------------------------------------------------------------
T.statementSlide(pres, {
  claim: "The absence of observed input drift is not\nevidence that the model is still valid.",
  support:
    "Input monitoring never had access to the thing that moved at site B, so it cannot establish that the conditional risk has held. " +
    "Confirming that takes outcome data, or a surrogate you have validated against outcomes. Most deployed monitoring is an " +
    "input-drift dashboard, which makes a green dashboard a much weaker statement than the people reading it believe.",
  dark: true,
}).addNotes("If time is short, this is the slide to protect. It is the one finding in the lecture that changes what people build on Monday.");

// 21 --------------------------------------------------------------
T.sectionSlide(pres, {
  number: 6,
  title: "The information in a blank cell",
  blurb: "A lab is missing because nobody ordered it, and nobody ordered it because nobody was worried.",
});

// 22 --------------------------------------------------------------
T.figureSlide(pres, {
  kicker: "MISSING NOT AT RANDOM",
  heading: "Two standard responses, both wrong",
  image: "figures/l1_missingness.png",
  reading:
    "Patients whose creatinine was never sent deteriorate at well under half the rate of those whose was. " +
    "Drop the incomplete rows and you keep 46% of the ward - silently selected toward the sickest, with an event rate of 0.217 against 0.150 overall.",
}).addNotes(
  "In the notebook exercise, adding explicit missingness indicators recovers most of what median imputation destroys. " +
  "Caution to carry forward: the indicator encodes local ordering practice, so it is a useful feature and a fragile one at the same time."
);

// 23 --------------------------------------------------------------
T.listSlide(pres, {
  kicker: "LECTURE 1",
  heading: "What to take away",
  twoColumn: true,
  items: [
    { title: "Report a distribution, or an interval", body: "A point estimate on ten observations is not a finding" },
    { title: "AUROC measures order, not meaning", body: "Deployment breaks meaning first" },
    { title: "Separate the two uncertainties", body: "They call for different responses" },
    { title: "Know your aleatoric floor", body: "Some of the gap was never in your columns" },
    { title: "A green input dashboard proves little", body: "It cannot license a claim about conditional risk" },
    { title: "Missingness is a recorded decision", body: "Model it. Never drop the rows." },
  ],
});

// 24 --------------------------------------------------------------
T.statementSlide(pres, {
  claim: "In Lecture 2: what you do about all this.",
  support:
    "Repairing calibration at a new site and what it costs in labelled patients. Using ensemble disagreement to decide when a model " +
    "should refuse to answer. Choosing an operating threshold from clinical costs rather than from 0.5. Borrowing strength across " +
    "hospitals with hierarchical models. Then an open project: should we trust a model at a new hospital with only a small outcome audit?",
  dark: true,
});

pres.writeFile({ fileName: "lecture1_honest_probabilities.pptx" }).then(() => console.log("deck 1 written"));
