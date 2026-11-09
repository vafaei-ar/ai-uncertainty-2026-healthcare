// Integrated 60-minute workshop lecture; the old two decks remain as optional references.
// Every quantitative figure is generated from the repository's synthetic simulator.
const pptxgen = require("pptxgenjs");
const T = require("./theme");
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Alireza Vafaei Sadr";
pptx.subject = "Mauritius AI & Uncertainty School, clinical AI hospital-transfer module";
pptx.title = "When Can We Trust Clinical AI at a New Hospital?";
pptx.lang = "en-US";

// The host authoring tools supply additional geometry checks when available.
// The standalone GitHub build validates slide geometry through tools/check_slides.py.
let geometry = null;
try {
  geometry = require("/home/oai/skills/slides/pptxgenjs_helpers");
} catch (_e) { /* not installed on GitHub Actions */ }
// Exact bibliographic pointers in speaker notes. Keep science readable on slides.
const REFERENCES = {
  4: ["Binuya et al. BMC Med Res Methodol. 2022. doi:10.1186/s12874-022-01801-8"],
  5: ["Van Calster et al. BMC Med. 2019. doi:10.1186/s12916-019-1466-7"],
  7: ["Binuya et al. BMC Med Res Methodol. 2022. doi:10.1186/s12874-022-01801-8"],
  14: ["Binuya et al. BMC Med Res Methodol. 2022. doi:10.1186/s12874-022-01801-8"],
  15: ["Riley et al. BMJ. 2024. doi:10.1136/bmj-2023-074821", "Van Calster et al. BMC Med. 2019. doi:10.1186/s12916-019-1466-7"],
  21: ["Riley et al. BMJ. 2024. doi:10.1136/bmj-2023-074821"],
};
let slideNumber = 0;
function add(slide, notes) {
  slideNumber += 1;
  const refs = REFERENCES[slideNumber];
  slide.addNotes(notes + (refs ? "\n\n[Sources]\n" + refs.join("\n") : ""));
  return slide;
}
function addBox(s, x, y, w, h, title, body, color) {
  s.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.09,
    line: {color: "DCE1E6", width: 1},
    fill: {color: color || "F2F5F7"},
  });
  s.addText(title, {
    x: x + 0.18, y: y + 0.17, w: w - 0.36, h: 0.45,
    fontFace: "Calibri", fontSize: 18, bold: true, color: "13293D", margin: 0,
  });
  s.addText(body, {
    x: x + 0.18, y: y + 0.72, w: w - 0.36, h: h - 0.90,
    fontFace: "Calibri", fontSize: 15, color: "3A4A59", margin: 0,
  });
}
function connect(s, x1, y1, x2, y2) {
  s.addShape(pptx.ShapeType.line, {
    x: x1, y: y1, w: x2-x1, h: y2-y1,
    line: {color:"DD5A22", width:2.5, beginArrowType:"none", endArrowType:"triangle"},
  });
}

// 1
add(T.titleSlide(pptx, {
  eyebrow:"AI & UNCERTAINTY SCHOOL 2026 · ONE INTEGRATED LECTURE",
  title:"When Can We Trust\nClinical AI at a New Hospital?",
  subtitle:"From honest probabilities to a three-day student research question\nMauritius, 16–20 November 2026",
  presenter:"Alireza Vafaei Sadr",
  meta:"Penn State College of Medicine · synthetic EHR-like teaching data only",
}), "2 min. Open with a question rather than a technical definition: imagine a doctor at 3am sees a model report 30 percent deterioration risk for a new patient. What should that doctor believe? Explain the model predicts a defined outcome within 48 hours and is not a treatment recommendation. This lecture gives students the tools needed for the research challenge.");

// 2
add(T.statsSlide(pptx, {
  kicker:"ONE FICTITIOUS PATIENT",
  heading:"What does a 30% risk actually mean?",
  stats:[
    {value:"30%",label:"Model-predicted risk\nof deterioration"},
    {value:"48 h",label:"Time horizon\nthat defines the outcome"},
    {value:"?",label:"Does this number\nmean what it claims?"},
  ],
  footnote:"If many similar admissions were assigned 30% risk, approximately 30% should have the outcome. We need outcome data to check.",
}), "3 min. Invite a student to interpret 30 percent. It does not mean the model is 30 percent confident in its own answer, and it does not guarantee the outcome for this individual. Explain calibration as a frequentist check of assigned risk. The patient is entirely fictional.");

// 3
add(T.listSlide(pptx, {
  kicker:"THE QUESTIONS THAT MATTER",
  heading:"A good score is not enough for deployment",
  twoColumn:true,
  items:[
    {title:"Ranking", body:"Does the model give higher risk to patients who deteriorate?"},
    {title:"Meaning", body:"Do predicted probabilities match observed outcome rates?"},
    {title:"Transfer", body:"Does the relationship survive another hospital?"},
    {title:"Uncertainty", body:"Which cases have too little evidence?"},
    {title:"Action", body:"What happens after a prediction or referral?"},
    {title:"Evidence", body:"Which outcomes and measurements must we collect?"},
  ],
}), "2 min. Keep the lecture anchored to these six practical questions. Ranking and probability meaning differ; a new hospital may change either. Decision consequences are separate from model accuracy.");

// 4
add(T.compareSlide(pptx, {
  kicker:"TWO IDEAS",
  heading:"Ranking patients is not the same as estimating their risk",
  left:{title:"Discrimination / AUROC", body:"Can the model rank someone who deteriorates above someone who does not?\n\nUseful for prioritizing patients.\n\nDoes not say whether a 30% risk is correct."},
  right:{title:"Calibration", body:"Among people assigned 30% risk, do about 30% deteriorate?\n\nNecessary to interpret a probability.\n\nRequires observed outcomes for evaluation."},
  footnote:"Explain the clinical question first. Name the metric second.",
}), "3 min. Use two illustrative patients as a verbal example. A model can rank them correctly yet assign both excessively high probabilities. AUROC is a ranking metric, calibration is about the meaning of the predicted probabilities.");

// 5
add(T.figureSlide(pptx, {
  kicker:"SIMULATED TEACHING EXAMPLE",
  heading:"The ranking can stay the same while probabilities become misleading",
  image:"figures/l1_calibration.png",
  reading:"Three versions of the same ranking have different calibration. Look at the probabilities, not only AUROC.",
}), "3 min. Walk the audience through the axes and one line at a time. This figure is produced by the synthetic simulator. Ask which probabilities would be safe to communicate as risks. Note that real deployment may also change AUROC.");

// 6
add(T.sectionSlide(pptx, {
  number:1,
  title:"The model moves to Hospital B",
  blurb:"Same software. Different patients, measurements, and outcome relationships.",
}), "1 min. Ask: what could change when hospital B adopts a model trained at A? Wait for case mix, instruments, protocols, outcome rate, data quality. Transition to two distinct kinds of change.");

// 7
add(T.figureSlide(pptx, {
  kicker:"HOSPITAL TRANSFER IN THE SYNTHETIC SIMULATOR",
  heading:"Probabilities can fail when the hospital changes",
  image:"figures/l1_shift_calibration.png",
  reading:"The displayed scenario illustrates miscalibration after transfer. Ranking is not guaranteed to remain stable in general.",
}), "3 min. Explain this is one designed scenario, not an empirical claim about every hospital. Discuss the direction of miscalibration and why outcome labels are needed to discover it.");

// 8
add(T.figureSlide(pptx, {
  kicker:"WHAT CAN WE SEE WITHOUT TARGET OUTCOMES?",
  heading:"Monitoring recorded inputs cannot check everything",
  image:"figures/l1_shift_detection.png",
  reading:"Some measurement changes appear in input checks. A change in risk conditional on inputs may remain hidden.",
}), "3 min. Explain we can compare patient age, heart rate, and lab distributions before collecting target labels. But without outcomes those comparisons cannot establish whether 30 percent still means 30 percent. Measurement noise can also alter conditional risk for recorded measurements.");

// 9
add(T.statementSlide(pptx, {
  claim:"A green input-drift dashboard\ncannot certify a reliable risk model.",
  support:"To evaluate probability reliability at the new hospital, we need target outcomes or a surrogate already validated against those outcomes.",
  dark:true,
}), "1 min. State this strongly, then clarify it is not that input monitoring is useless. It is incomplete. This is the research motivation for studying how many target outcome labels we need.");

// 10
add(T.compareSlide(pptx, {
  kicker:"WHY DO WE DOUBT A PREDICTION?",
  heading:"Two kinds of uncertainty call for different responses",
  left:{title:"Epistemic: what we do not know", body:"Few relevant examples, uncertain model estimates, unfamiliar situations.\n\nMore appropriate data may help.\n\nBootstrap disagreement is only one proxy."},
  right:{title:"Aleatoric: what remains unpredictable", body:"Similar recorded cases can have different outcomes.\n\nMore rows with the same variables may not remove this variation.\n\nNew useful measurements may help."},
  footnote:"The same patient can have both kinds of uncertainty.",
}), "3 min. Do not imply the two types can always be cleanly separated from the data. Use examples: a rare type of patient versus real unpredictability even with complete measured information.");

// 11
add(T.figureSlide(pptx, {
  kicker:"SYNTHETIC LEARNING CURVES",
  heading:"More data can reduce model uncertainty, not all uncertainty",
  image:"figures/l1_epistemic.png",
  reading:"Bootstrap spread captures sensitivity to refitting, not a formal posterior or guaranteed out-of-distribution detector.",
}), "2 min. Explain what resampling does without equations. Show how model predictions vary across fitted samples. The plot is illustrative and does not prove universal behavior.");

// 12
add(T.figureSlide(pptx, {
  kicker:"MISSING DATA",
  heading:"A missing laboratory result can be information",
  image:"figures/l1_missingness.png",
  reading:"Tests are ordered for clinical reasons. Missingness patterns can predict outcomes but may change across hospitals.",
}), "2 min. Example: a physician may order lactate more often for concerning cases. Dropping untested patients or blindly filling values can distort the cohort. A missingness indicator may help, but ordering behavior differs by hospital.");

// 13
add(T.sectionSlide(pptx, {
  number:2,
  title:"If the probabilities are wrong, what can we do?",
  blurb:"Adapt them, ask for human review, or stay in shadow mode until evidence improves.",
}), "1 min. Distinguish correcting numbers from changing decisions. An adaptation can worsen performance when the local sample is small.");

// 14
add(T.tableSlide(pptx, {
  kicker:"THREE OPTIONS TO TEST",
  heading:"Start with the simplest adjustment",
  columns:["Method","What it does","Main risk"],
  widths:[3.2,4.3,4.3],
  rows:[
    ["No change","Use Hospital A probabilities at B","The probabilities may be wrong"],
    ["Intercept update","Shift probability levels using local outcomes","Small audits can make the correction noisy"],
    ["Platt update","Fit both a slope and intercept at B","More flexibility can overfit few labels"],
  ],
  footnote:"The study compares these fixed methods on independently generated test patients.",
}), "3 min. Explain intercept with plain words: move the entire risk scale up or down without changing ranking. Platt may also adjust how spread out the risks are. Both require labeled target outcomes.");

// 15
add(T.figureSlide(pptx, {
  kicker:"SEPARATE CALIBRATION DEMONSTRATION",
  heading:"The more flexible repair is not always better with few labels",
  image:"figures/l2_calibration_cost.png",
  reading:"This simulator example motivates comparing label budgets. It does not establish a universal sample-size requirement.",
}), "3 min. Describe what changes when the new hospital supplies 25, 75, or 150 outcomes. Warn that a method tuned and tested on the same 75 observations looks artificially good.");

// 16
add(T.compareSlide(pptx, {
  kicker:"SOMETIMES THE RIGHT ACTION IS TO DEFER",
  heading:"Review capacity matters, not just confidence",
  left:{title:"Predictions near the decision threshold", body:"A borderline case may need closer human review.\n\nThe rule depends on the decision threshold and available staff."},
  right:{title:"Model instability", body:"Different bootstrap models may disagree for a case.\n\nThis is a signal to evaluate, not proof that a prediction is unsafe."},
  footnote:"Deferring 20% of admissions uses resources. Safety benefit cannot be assumed.",
}), "3 min. Distinguish probability near 0.5 from epistemic model disagreement. Explain 20 percent review capacity is a hypothetical budget in this project.");

// 17
add(T.figureSlide(pptx, {
  kicker:"SIMULATED SELECTIVE PREDICTION",
  heading:"A review rule must beat random deferral",
  image:"figures/l2_risk_coverage.png",
  reading:"Compare retained-patient performance as more cases receive review. Always report how many patients are deferred.",
}), "2 min. Reading the plot: horizontal is proportion retained; vertical is performance. A rule that sends many cases to review is not automatically useful. Review conditions and workload.");

// 18
add(T.figureSlide(pptx, {
  kicker:"PERFORMANCE IS NOT ONE NUMBER",
  heading:"Check whether reliability differs across groups",
  image:"figures/l2_subgroup.png",
  reading:"Overall performance can hide weak performance in a subgroup. Small group sizes also limit what we can conclude.",
}), "3 min. Avoid claiming subgroup analysis establishes fairness. Explain one average can hide different errors. Group variables in this synthetic simulator are simplified indicators, not real patient demographic categories.");

// 19
add(T.listSlide(pptx, {
  kicker:"A DEPLOYMENT DECISION",
  heading:"Three defensible recommendations",
  twoColumn:false,
  items:[
    {title:"Stay in shadow mode", body:"Predictions are recorded but do not guide patient care until stronger evidence exists."},
    {title:"Recalibrate with outcome evidence", body:"Compare adjusted and unchanged models on independent data before relying on estimates."},
    {title:"Consider supervised review", body:"Define which predictions get referred, the workload, and how the pathway will be evaluated."},
  ],
}), "2 min. Ask which choice is best. The answer depends on target outcomes, consequences, staffing, and external evaluation. The model does not control treatment.");

// 20
add(T.statsSlide(pptx, {
  kicker:"THE STUDENT PROJECT",
  heading:"Hospital B gives us very little outcome information",
  stats:[
    {value:"4,000",label:"Labeled synthetic admissions\nHospital A"},
    {value:"1,600",label:"Target synthetic admissions\nHospital B"},
    {value:"75",label:"Random target-audit\noutcomes revealed"},
  ],
  footnote:"Can we estimate when simple calibration repair helps without fooling ourselves by reusing the same outcomes for evaluation?",
}), "3 min. Explain what labeled means: we know if the outcome occurred. Hospital B's 1600 records show features; only 75 outcomes are known. Students will test methods with new simulations and independent held-out outcomes.");

// 21
{
  const s = T.contentSlide(pptx,
    "Keep training, adjustment and evaluation separate", "THE STUDY DESIGN");
  addBox(s, 0.65, 1.95, 3.6, 2.90,
    "Hospital A: train", "Use 4,000 synthetic labeled records to fit the original model.",
    "E7F0FA");
  addBox(s, 4.87, 1.95, 3.6, 2.90,
    "Hospital B: adjust", "Use only 25, 75 or 150 target audit outcomes to fit the calibration update.",
    "F7EEE3");
  addBox(s, 9.08, 1.95, 3.6, 2.90,
    "Independent B: test", "Use different simulated admissions to compare Brier scores and model performance.",
    "E6F3EB");
  connect(s, 4.25, 3.42, 4.77, 3.42);
  connect(s, 8.47, 3.42, 8.98, 3.42);
  s.addText("Never use the same target outcomes to fit an update and claim independent performance.", {
    x: 0.85, y: 5.55, w: 11.65, h: 0.85, margin: 0, fontFace: "Calibri",
    fontSize: 21, color: "13293D", bold: true, align: "center"
  });
  add(s, "3 min. These are three different data roles. Source labels train the model. Small target audits adjust its probabilities. Separately generated target outcomes estimate performance. In a simulation, the evaluator can generate fully labeled test admissions, but in real hospital research we would need a valid independent outcome dataset. Reuse of the same audit labels for fitting and apparent evaluation makes the result optimistic. The primary comparison is paired Brier score difference on these independent test admissions.");
}

// 22
{
  const s=T.contentSlide(pptx,"Three days, three concrete milestones","STUDENT WORKFLOW");
  addBox(s,0.75,1.95,3.5,3.15,"Day 1","Inspect synthetic data, train baseline, identify one failure condition.");
  addBox(s,4.9,1.95,3.5,3.15,"Day 2","Compare unchanged, intercept, and Platt across label budgets.");
  addBox(s,9.05,1.95,3.5,3.15,"Day 3","Repeat, interpret limits, create one figure and a short report.");
  connect(s,4.25,3.50,4.80,3.50);
  connect(s,8.40,3.50,8.95,3.50);
  s.addText("Students use Python/Colab and MIMIC-inspired synthetic tables. No clinical data or GPU required.",{
    x:0.95,y:5.7,w:11.45,h:0.7,margin:0,fontFace:"Calibri",
    fontSize:18,color:"3A4A59",align:"center"
  });
  add(s,"3 min. Set clear milestones and ask each group to choose one scenario and one contrast before expanding. The relational adapter illustrates how flat features can be assembled from MIMIC-inspired tables. It is not a validated MIMIC-IV extract. Emphasize student groups will need a facilitator in the room.");
}

// 23
add(T.statementSlide(pptx,{
  claim:"A strong result can be:\nWe still do not know enough.",
  support:"Your job is to show what the available evidence supports, where a method fails, and what data or experiments would change the conclusion. A paper is a possible later outcome, not a three-day deliverable.",
  dark:true,
}), "2 min. Return to the 30% prediction. Ask whether students would use it at Hospital B. End with the research standard: honest uncertainty, independent evaluation, and a reproducible failure analysis. Invite questions and direct the class to the new Colab starter.");

// Optional local authoring verification where installed.
if (geometry) {
  for (const slide of pptx._slides) {
    geometry.warnIfSlideElementsOutOfBounds(slide, pptx);
  }
}
pptx.writeFile({fileName:"lecture_when_can_we_trust_clinical_ai.pptx"}).then(
  () => console.log("Integrated workshop lecture written")
);
