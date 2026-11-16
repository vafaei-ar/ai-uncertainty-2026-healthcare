# Monday project introduction | Presenter script

**Presenter:** Alireza Vafaei Sadr, Penn State College of Medicine
**Session:** Monday, 16 November 2026, project presentations
**Slot:** Up to 10 minutes per project (exact speaking order to be confirmed)
**Plan:** About 7 minutes speaking, with 2 to 3 minutes for questions. No live coding.
**Audience:** MSc and PhD students with some Python experience.

The two-slide introduction from the earlier package remains an optional short backup.

## Slide 1: The question

**Target:** 76 seconds

Hi everyone. I am Alireza Vafaei Sadr from Penn State College of Medicine. I will introduce a research problem that looks simple, but becomes difficult when we move a prediction model from one hospital to another. Suppose a model predicts a thirty percent chance that a patient will deteriorate during the next forty-eight hours. This number is meaningful only if it is reliable. Across many patients who receive a prediction near thirty percent, roughly thirty in one hundred should have the outcome. The model was developed at Hospital A. What happens if we give its predictions to Hospital B? We will use this question to study reliability and uncertainty. Everything in our exercise comes from simulated data, so none of the examples supports patient care decisions.

**Presenter cue:** Pause after the final question. Students have not yet heard Tuesday's lecture. Do not introduce formulas.

## Slide 2: Why transfer matters

**Target:** 78 seconds

Two hospitals may have different patients, lab instruments, testing habits, and treatment practices. Even when the computer code does not change, the numbers can stop meaning what we think they mean. One way to check is to compare predicted risks with outcomes from the new hospital. But this creates a practical problem. What if Hospital B has almost no labeled outcomes yet? Imagine that only a small sample of local patients has an outcome we can examine. Looking only at age, blood pressure, and other recorded inputs may help us find some differences, but it cannot prove that the risk predictions are calibrated. I want you to think about that distinction. We can have a very sophisticated model, but the critical missing ingredient may be local evidence.

**Presenter cue:** Students can answer: What else might differ between hospitals? Take one or two short responses.

## Slide 3: The minimum experiment

**Target:** 105 seconds

Our experiment will compare two options. The first leaves the Hospital A risk predictions unchanged. The second uses a small number of Hospital B outcomes to move the predicted risk level up or down. We will test that simple correction in two settings. First, a negative control where nothing important changes between the hospitals. If a correction is unnecessary, could it make the predictions worse? Second, a setting where patients at Hospital B have a higher baseline risk, even though their recorded characteristics can look similar. In each setting, we will try learning the correction from twenty-five or seventy-five local outcomes. We then evaluate both options on different simulated patients whose outcomes were not used to fit the correction. This separation is important. An apparent improvement on the same patients used to fit the change can be misleading. We will examine how much the correction helps or hurts, using a probability error measure that we will explain in Tuesday's lecture.

**Presenter cue:** No live coding. Point from the start card to the new test patients. Clarify the orientation dataset is different from independent experimental replicates.

## Slide 4: The student workflow

**Target:** 84 seconds

The project is designed to fit the three research days after Tuesday's lecture. On Wednesday, students open the prepared notebook, check the synthetic data, reproduce the unchanged model, and write down what they predict. On Thursday, the team compares the unchanged model with the simple update across the two hospital situations and two sample sizes. They should also look at how the answer varies when we repeat the simulation. Thursday has other workshop activities, so the minimum is deliberately short. On Friday, they finalize one main figure, explain one limitation, and give a five-minute presentation with three slides. The output is not a finished clinical product or a promised publication. The output is a reproducible, scientifically honest answer to a precise question. A result showing that a correction makes the model worse is perfectly valid. If time allows, students may test one new question, but they should not sacrifice the minimum comparison to do that.

**Presenter cue:** The slides need no students to run Colab on Monday. Student work begins after Tuesday.

## Slide 5: Invitation and close

**Target:** 91 seconds

At the end of the three days, I would like each group to tell one compact scientific story. What did you test? What did the simulated results show? And what remains uncertain? You will be able to do the minimum exercise using a prepared notebook on a normal laptop with Google Colab. You do not need a GPU or access to real patient records. If you have basic Python experience, you have enough to start. An AI coding assistant can help explain an error or a code cell, if one is available, but every reported number must come from code you executed and checked. I will be joining remotely from the United States. Once groups are assigned, we will agree on a messaging channel for questions and a practical way to review your results each day. So I will leave you with our opening question. Before believing a thirty percent risk at Hospital B, what evidence would you want?

**Presenter cue:** Ask for one question or one answer to the final prompt. Reserve two to three minutes for discussion or organizer Q&A.

## Short backup for a two-minute slot

My project asks whether we can trust a hospital risk model after moving it to another hospital. Imagine the model predicts a 30 percent chance that a patient will deteriorate within 48 hours. Does that 30 percent still mean the same thing at the new hospital? We will use only simulated data. Students will compare the original predictions with one simple correction based on 25 or 75 local outcomes, in a setting where nothing changed and one where patients have higher risk. Then they will test both approaches on separate simulated patients. Wednesday is for reproducing the baseline, Thursday is for comparing methods, and Friday is for presenting one figure and a short, three-slide report. No GPU or real patient data is needed. We will introduce the necessary statistics in Tuesday's lecture.

## Handling questions

- **Is this real patient data?** No. It is simulated educational data.
- **Is the correction a new method?** No. The study tests a standard updating method under restricted labels.
- **What is a good finding?** A reproducible comparison, including when the update fails.
- **Do I need advanced machine learning?** No. We start with prepared code.
- **Can we publish this in three days?** Not based on the minimum exercise alone. A later study would require a new question and deeper validation.