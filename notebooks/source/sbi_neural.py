"""Notebook 4 - Simulation-based inference for a mechanistic ward model."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.nbtools import BRANCH, COLAB_TOKEN, PLOT_STYLE, REPO, Notebook  # noqa: E402


def build() -> Notebook:
    nb = Notebook("Simulation-based inference", colab_setup=False)

    nb.md(
        f'<a href="https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/'
        f'{COLAB_TOKEN}" target="_parent">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open this notebook in Google Colab"/></a>'
        "---\n\n"
        "**Setup.** Run this first. It installs the `sbi` package if it is not already\n"
        "present, then fetches the teaching utilities. On a fresh Colab runtime the\n"
        "install takes a minute or two because it pulls PyTorch."
    )

    nb.code(
        """
import importlib.util, subprocess, sys, os

if importlib.util.find_spec("sbi") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "sbi"], check=True)

REPO = "https://github.com/vafaei-ar/ai-uncertainty-2026-healthcare.git"

if importlib.util.find_spec("medsim") is None:
    if not os.path.isdir("ai-uncertainty-2026-healthcare"):
        subprocess.run(["git", "clone", "--depth", "1", REPO], check=True)
    sys.path.insert(0, os.path.abspath("ai-uncertainty-2026-healthcare"))

import sbi, torch
print("sbi", sbi.__version__, "| torch", torch.__version__)
"""
    )

    nb.md(
        """
# Simulation-based inference for a mechanistic ward model

*AI & Uncertainty School and Workshop 2026, healthcare module*

Every model so far in this module was fitted to recorded outcomes. This one is
different. We write down how deterioration happens on a ward - a daily hazard, a
treatment that changes it, and a monitoring process that sometimes misses it - and
we ask what the parameters are, given what the ward actually recorded.

The likelihood of that model is a sum over every unobserved deterioration time and
every missed check. We are not going to write it down. We are going to simulate
instead.

**Where we are going**

1. A three-parameter ward model whose parameters a clinician can argue with
2. ABC rejection sampling, and where it starts to hurt in three dimensions
3. Neural posterior estimation with `sbi`: train once, reuse everywhere
4. ABC against NPE on accuracy, interval width and simulation budget
5. Simulation-based calibration: does the posterior have the coverage it claims?

Everything runs on CPU in about a minute.
"""
    )

    nb.code(
        """
import time
import numpy as np
import pandas as pd
import torch
from scipy.special import expit

from sbi.inference import NPE
from sbi.utils import BoxUniform
from sbi.analysis import pairplot, sbc_rank_plot
from sbi.diagnostics import run_sbc, check_sbc
"""
        + PLOT_STYLE
        + """
SEED = 20261119
rng = np.random.default_rng(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(2)
pd.set_option("display.width", 170)
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 1. A ward model with three interpretable parameters

A ward admits patients for up to 14 days. Half are randomised to a treatment.

- $\\theta_1$, `log_hazard`: log-odds that an untreated patient deteriorates on any
  given day.
- $\\theta_2$, `log_or`: the treatment's log-odds ratio on that daily hazard. Below
  zero means the treatment helps.
- $\\theta_3$, `logit_detect`: log-odds that the ward notices a deterioration on any
  given day once it has happened. Below infinity means monitoring is imperfect.

The third parameter is the one that makes this a real problem. A ward with a low
hazard and perfect monitoring and a ward with a high hazard and patchy monitoring
record a similar number of events. What separates them is *when* the events get
recorded, so the summary statistics have to carry timing as well as counts.

Five summaries go to the inference: the observed event fraction in each arm, the
mean and standard deviation of the recorded event day, and the fraction of
recorded events that land in the first three days.
"""
    )

    nb.code(
        """
N_PATIENTS = 300
N_DAYS = 14
PARAM_NAMES = ["log_hazard", "log_or", "logit_detect"]
SUMMARY_NAMES = ["rate_control", "rate_treated", "mean_day", "sd_day", "frac_early"]


def ward_simulator(theta, n_patients=N_PATIENTS, n_days=N_DAYS, rng=None):
    \"\"\"Simulate one ward and return five summary statistics.\"\"\"
    rng = np.random.default_rng() if rng is None else rng
    log_hazard, log_or, logit_detect = float(theta[0]), float(theta[1]), float(theta[2])

    treated = np.zeros(n_patients, dtype=int)
    treated[: n_patients // 2] = 1

    daily_hazard = expit(log_hazard + log_or * treated)
    detect = expit(logit_detect)

    # Day of true deterioration: first day the per-day hazard fires.
    fires = rng.random((n_patients, n_days)) < daily_hazard[:, None]
    day_true = np.where(fires.any(axis=1), fires.argmax(axis=1), n_days)

    # The ward notices it some days later; a geometric wait with success prob `detect`.
    day_seen = day_true + rng.geometric(detect, n_patients) - 1
    recorded = (day_true < n_days) & (day_seen < n_days)

    if recorded.sum() < 3:
        return np.array([recorded[treated == 0].mean(), recorded[treated == 1].mean(),
                         float(n_days), 0.0, 0.0])

    days = day_seen[recorded]
    return np.array([
        recorded[treated == 0].mean(),
        recorded[treated == 1].mean(),
        days.mean(),
        days.std(),
        (days < 3).mean(),
    ])


THETA_TRUE = np.array([-2.6, -0.8, 1.4])
x_observed = ward_simulator(THETA_TRUE, rng=np.random.default_rng(999))

print("the ward we are trying to explain:")
print(pd.Series(x_observed, index=SUMMARY_NAMES).round(3).to_string())
print()
print(f"untreated daily hazard {expit(THETA_TRUE[0]):.3f}, "
      f"treated {expit(THETA_TRUE[0] + THETA_TRUE[1]):.3f}, "
      f"daily detection probability {expit(THETA_TRUE[2]):.3f}")
"""
    )

    nb.md(
        """
The prior is flat over ranges a clinician would accept as possible: a daily hazard
between about 2% and 18%, a treatment effect anywhere from a strong benefit to a
mild harm, and daily detection between 50% and 95%.
"""
    )

    nb.code(
        """
LOW = torch.tensor([-4.0, -2.0, 0.0])
HIGH = torch.tensor([-1.5, 0.5, 3.0])
prior = BoxUniform(low=LOW, high=HIGH)

print(pd.DataFrame({
    "parameter": PARAM_NAMES,
    "prior_low": LOW.numpy(),
    "prior_high": HIGH.numpy(),
    "meaning": ["daily hazard 1.8% to 18%",
                "odds ratio 0.14 to 1.65",
                "daily detection 50% to 95%"],
}).to_string(index=False))
"""
    )

    nb.note(
        "Worth saying explicitly: none of the three parameters is a regression "
        "coefficient. They are quantities a ward round can dispute. That is the "
        "whole appeal of mechanistic models in clinical work, and it is why a "
        "posterior over them is more useful than a posterior over the weights of "
        "a network."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 2. ABC rejection sampling in three dimensions

Lecture 2 did this with one parameter and 12,000 simulations. The recipe is
unchanged: draw from the prior, simulate, keep the draws whose summaries came
closest to the observed ones.

We give ABC a generous budget of 30,000 simulations, because we are about to
compare it against a method that will get one tenth of that.
"""
    )

    nb.code(
        """
N_REFERENCE = 30_000

start = time.time()
theta_reference = prior.sample((N_REFERENCE,)).numpy()
x_reference = np.array([ward_simulator(t, rng=rng) for t in theta_reference])
sim_seconds = time.time() - start
print(f"{N_REFERENCE:,} simulations in {sim_seconds:.1f}s")

summary_scale = x_reference.std(axis=0)


def abc_posterior(x_obs, tolerance=0.01):
    \"\"\"Keep the `tolerance` fraction of prior draws whose summaries are closest.\"\"\"
    distance = np.linalg.norm((x_reference - np.asarray(x_obs)) / summary_scale, axis=1)
    keep = int(round(tolerance * N_REFERENCE))
    idx = np.argpartition(distance, keep)[:keep]
    return theta_reference[idx]


rows = []
for tolerance in [0.05, 0.01, 0.002]:
    accepted = abc_posterior(x_observed, tolerance)
    rows.append({
        "tolerance": tolerance,
        "kept": len(accepted),
        **{f"{p}_mean": accepted[:, j].mean() for j, p in enumerate(PARAM_NAMES)},
        **{f"{p}_sd": accepted[:, j].std() for j, p in enumerate(PARAM_NAMES)},
    })
display(pd.DataFrame(rows).round(3))
print("true values:", dict(zip(PARAM_NAMES, THETA_TRUE)))
"""
    )

    nb.code(
        """
abc_draws = abc_posterior(x_observed, tolerance=0.01)

fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6))
for j, (ax, name) in enumerate(zip(axes, PARAM_NAMES)):
    ax.hist(theta_reference[:, j], bins=40, density=True, alpha=0.30, label="Prior")
    ax.hist(abc_draws[:, j], bins=30, density=True, alpha=0.75, label="ABC posterior")
    ax.axvline(THETA_TRUE[j], ls="--", c="0.15", label="True value")
    ax.set_xlabel(name)
axes[0].set_ylabel("Density")
axes[0].legend(fontsize=9)
fig.suptitle("ABC rejection posterior, 30,000 simulations, 1% kept", y=1.02)
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
Look at what the tolerance table costs you. Going from a 5% tolerance to 0.2%
narrows the `log_hazard` posterior from a standard deviation of 0.24 to 0.14 and
cuts the sample representing it from 1500 draws to 60. The estimate of the
posterior gets noisier exactly as the posterior itself gets better, and there is
no setting that fixes both.

`logit_detect` does not narrow at all: its standard deviation is 0.80 at every
tolerance. Tightening the tolerance cannot manufacture information the summaries
do not contain, and this parameter is going to keep telling us that.

Two structural problems, neither of which is a tuning issue:

- **99% of the simulations are discarded.** They contain information about the
  parameter-to-data map, and rejection sampling throws all of it away.
- **A new ward starts the accounting again.** The reference table can be reused,
  but every new observation gets its own pass over it and its own 300 surviving
  draws.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 3. Neural posterior estimation

Neural posterior estimation turns the problem around. Instead of asking which
simulations resemble the observation, it fits a conditional density estimator
$q_\\phi(\\theta \\mid x)$ to the pairs $(\\theta_i, x_i)$ that the simulator already
produced. Every simulation contributes to the fit, including the ones ABC would
have thrown away.

The estimator here is a masked autoregressive flow. Once trained, evaluating it on
a new $x$ is a forward pass, so a posterior for a ward it has never seen costs
milliseconds and no new simulations. That property is called **amortisation**, and
it is the reason this scales where rejection sampling does not.

We train on 3,000 simulations - one tenth of the ABC budget.
"""
    )

    nb.code(
        """
N_TRAIN = 3_000

theta_train = prior.sample((N_TRAIN,))
x_train = torch.as_tensor(
    np.array([ward_simulator(t.numpy(), rng=rng) for t in theta_train]), dtype=torch.float32
)

start = time.time()
inference = NPE(prior=prior, density_estimator="maf", show_progress_bars=False)
density_estimator = inference.append_simulations(theta_train, x_train).train(
    training_batch_size=200, show_train_summary=False
)
posterior = inference.build_posterior(density_estimator)
train_seconds = time.time() - start
print(f"trained on {N_TRAIN:,} simulations in {train_seconds:.1f}s")
"""
    )

    nb.code(
        """
x_obs_t = torch.as_tensor(x_observed, dtype=torch.float32)

start = time.time()
npe_draws = posterior.sample((5_000,), x=x_obs_t, show_progress_bars=False).numpy()
print(f"5,000 posterior draws in {time.time() - start:.2f}s")

summary = pd.DataFrame({
    "parameter": PARAM_NAMES,
    "true": THETA_TRUE,
    "ABC mean": abc_draws.mean(axis=0),
    "ABC sd": abc_draws.std(axis=0),
    "NPE mean": npe_draws.mean(axis=0),
    "NPE sd": npe_draws.std(axis=0),
})
summary["sd ratio (NPE / ABC)"] = summary["NPE sd"] / summary["ABC sd"]
display(summary.round(3))

correlations = pd.DataFrame(np.corrcoef(npe_draws.T), index=PARAM_NAMES, columns=PARAM_NAMES)
print("posterior correlations:")
display(correlations.round(3))
"""
    )

    nb.code(
        """
fig, axes = pairplot(
    npe_draws,
    points=THETA_TRUE.reshape(1, -1),
    limits=list(zip(LOW.numpy(), HIGH.numpy())),
    labels=PARAM_NAMES,
    figsize=(7.2, 7.2),
    points_colors=["#C44E52"],
    upper="contour",
    diag="hist",
)
fig.suptitle("NPE posterior for one observed ward (red: true parameters)", y=1.01)
plt.show()
"""
    )

    nb.md(
        """
Two things to read off.

The NPE marginals are roughly half the width of the ABC ones on `log_hazard` and
`log_or`, from one tenth of the simulations. That is what using every simulation
instead of 1% buys you. Hold the question of whether that extra sharpness is
*earned* until section 5, because it is the whole subject of section 5.

The off-diagonal panels are not blobs, and the printed correlations put numbers on
them. The strongest is $-0.59$ between `log_hazard` and `log_or`: the control arm
pins down the hazard, but the treated arm only constrains the two together, so
raising one and lowering the other leaves the record unchanged. `log_hazard`
against `logit_detect` tilts more gently at $-0.27$, in the direction you would
expect, since a slightly sicker ward that notices slightly less often writes down
the same numbers.

Those tilts are facts about the ward model and the summaries, not failures of the
method, and a point estimate would have hidden both.

Now the property that ABC does not have.
"""
    )

    nb.code(
        """
new_wards = {
    "Ward A (fast, untreated benefit)": np.array([-2.2, -0.3, 2.2]),
    "Ward B (slow, strong treatment)":  np.array([-3.4, -1.6, 1.8]),
    "Ward C (patchy monitoring)":       np.array([-2.4, -0.9, 0.3]),
}

start = time.time()
rows = []
for label, theta in new_wards.items():
    x_new = torch.as_tensor(ward_simulator(theta, rng=rng), dtype=torch.float32)
    draws = posterior.sample((2_000,), x=x_new, show_progress_bars=False).numpy()
    for j, name in enumerate(PARAM_NAMES):
        rows.append({
            "ward": label,
            "parameter": name,
            "true": theta[j],
            "posterior_mean": draws[:, j].mean(),
            "hdi_5%": np.quantile(draws[:, j], 0.05),
            "hdi_95%": np.quantile(draws[:, j], 0.95),
        })
elapsed = time.time() - start

display(pd.DataFrame(rows).round(3))
print(f"three complete posteriors in {elapsed:.2f}s, using zero new simulations")
"""
    )

    nb.md(
        """
Three wards, three posteriors, in under a tenth of a second. The simulator was
called three times to *create* the observations; the inference used it zero times.
The training cost is paid once and the network is then a function from ward
summaries to a posterior. In a hospital network that is the difference between an
inference you run once and one you run per site, per month, forever.

Ward C is worth a second look. Its true `logit_detect` is 0.3 and its 90% interval
starts at about 0.43, so the interval misses. One miss out of nine is not
evidence of anything on its own, which is exactly why the next two sections stop
looking at individual wards.
"""
    )

    nb.note(
        "The honest version of the amortisation claim: ABC can also reuse its "
        "reference table for a new observation. What it cannot do is reuse the "
        "*fit*. Each new ward costs another pass over 30,000 stored simulations "
        "and yields only the 300 draws that survive, while NPE returns as many "
        "draws as you ask for from a fixed forward pass."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 4. ABC against NPE, on the same wards

One observation proves nothing. We draw 200 wards from the prior, simulate each,
hand both methods the same summaries, and score them against the parameters we
know.

Three numbers per method: root mean squared error of the posterior mean, mean
width of the central 90% interval, and how often that interval actually contains
the truth.
"""
    )

    nb.code(
        """
N_TEST = 200
theta_test = prior.sample((N_TEST,)).numpy()
x_test = np.array([ward_simulator(t, rng=rng) for t in theta_test])

start = time.time()
abc_test = np.stack([abc_posterior(x, tolerance=0.01) for x in x_test])
abc_seconds = time.time() - start

start = time.time()
npe_test = posterior.sample_batched(
    (500,), x=torch.as_tensor(x_test, dtype=torch.float32), show_progress_bars=False
).numpy().transpose(1, 0, 2)
npe_seconds = time.time() - start

print(f"ABC over {N_TEST} wards: {abc_seconds:.1f}s   NPE over {N_TEST} wards: {npe_seconds:.1f}s")


def score(draws, label, n_simulations):
    mean = draws.mean(axis=1)
    lo = np.quantile(draws, 0.05, axis=1)
    hi = np.quantile(draws, 0.95, axis=1)
    out = []
    for j, name in enumerate(PARAM_NAMES):
        out.append({
            "method": label,
            "simulations": n_simulations,
            "parameter": name,
            "rmse": np.sqrt(((mean[:, j] - theta_test[:, j]) ** 2).mean()),
            "width_90": (hi[:, j] - lo[:, j]).mean(),
            "coverage_90": ((theta_test[:, j] >= lo[:, j]) & (theta_test[:, j] <= hi[:, j])).mean(),
        })
    return out


scores = pd.DataFrame(score(abc_test, "ABC rejection", N_REFERENCE)
                      + score(npe_test, "NPE", N_TRAIN))
display(scores.round(3))
"""
    )

    nb.code(
        """
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6), sharex=True, sharey=True)
for j, (ax, name) in enumerate(zip(axes, PARAM_NAMES)):
    ax.scatter(theta_test[:, j], abc_test[:, :, j].mean(axis=1), s=14, alpha=0.6,
               label="ABC")
    ax.scatter(theta_test[:, j], npe_test[:, :, j].mean(axis=1), s=14, alpha=0.6,
               label="NPE")
    lims = [LOW[j].item(), HIGH[j].item()]
    ax.plot(lims, lims, ls="--", c="0.35", lw=1.2)
    ax.set_xlabel(f"true {name}")
axes[0].set_ylabel("posterior mean")
axes[0].legend(fontsize=9)
fig.suptitle("Posterior mean against truth over 200 simulated wards", y=1.02)
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
Read the table one column at a time, because the three columns do not agree.

**Accuracy.** NPE wins on the two identified parameters: RMSE 0.120 against 0.148
on `log_hazard` and 0.222 against 0.275 on `log_or`, from 3,000 simulations rather
than 30,000. On `logit_detect` the two methods tie at about 0.75, because neither
can extract information that is not in the summaries.

**Interval width.** NPE's 90% intervals are roughly half the width of ABC's on the
identified parameters: 0.36 against 0.65, and 0.57 against 1.14.

**Coverage.** This is where the story turns. ABC's 90% intervals contain the truth
96%, 95% and 90% of the time - too often on two of the three, which is what a
finite tolerance does to a rejection posterior. NPE's contain it 84%, 80% and 82%
of the time. **NPE's intervals are not just narrower, they are narrower than they
are entitled to be.**

With 200 test wards the standard error on a coverage estimate is about 0.02, so a
90% interval delivering 80% is a real shortfall and not noise. Nothing in the
first two columns would have told you this. A method can be more accurate and
less honest at the same time, which is why the next section exists.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 5. Does the posterior have the coverage it claims?

This is the module's question again, asked of a posterior instead of a risk score.
A 90% credible interval that contains the truth 70% of the time is a
miscalibrated model, and the fact that it came out of a neural network rather than
a logistic regression changes nothing.

Simulation-based calibration is the general test. Draw
$\\theta \\sim p(\\theta)$, simulate $x \\sim p(x \\mid \\theta)$, sample the posterior
$q(\\theta \\mid x)$, and record the rank of the true $\\theta$ among the posterior
draws. If the posterior is correct those ranks are uniform, for every parameter.
Systematic deviations have readable shapes: a U tells you the posterior is too
narrow, an inverted U that it is too wide, a slope that it is biased.
"""
    )

    nb.code(
        """
N_SBC = 300
N_SBC_DRAWS = 500

theta_sbc = prior.sample((N_SBC,))
x_sbc = torch.as_tensor(
    np.array([ward_simulator(t.numpy(), rng=rng) for t in theta_sbc]), dtype=torch.float32
)

start = time.time()
ranks, dap_samples = run_sbc(theta_sbc, x_sbc, posterior,
                             num_posterior_samples=N_SBC_DRAWS, show_progress_bar=False)
stats = check_sbc(ranks, theta_sbc, dap_samples, num_posterior_samples=N_SBC_DRAWS)
print(f"SBC over {N_SBC} datasets in {time.time() - start:.1f}s")

display(pd.DataFrame({
    "parameter": PARAM_NAMES,
    "ks_pvalue": stats["ks_pvals"].numpy(),
    "c2st_ranks": stats["c2st_ranks"].numpy(),
    "c2st_dap": stats["c2st_dap"].numpy(),
}).round(3))
"""
    )

    nb.code(
        """
fig, axes = sbc_rank_plot(ranks=ranks, num_posterior_samples=N_SBC_DRAWS,
                          plot_type="cdf", parameter_labels=PARAM_NAMES,
                          figsize=(10.5, 3.4))
plt.show()

rank_fraction = ranks.numpy() / N_SBC_DRAWS
coverage = pd.DataFrame({
    "parameter": PARAM_NAMES,
    "nominal_50%": 0.50,
    "empirical_50%": [((rank_fraction[:, j] > 0.25) & (rank_fraction[:, j] < 0.75)).mean()
                      for j in range(3)],
    "nominal_90%": 0.90,
    "empirical_90%": [((rank_fraction[:, j] > 0.05) & (rank_fraction[:, j] < 0.95)).mean()
                      for j in range(3)],
})
display(coverage.round(3))
print(f"binomial standard error on a coverage estimate from {N_SBC} datasets: "
      f"{np.sqrt(0.9 * 0.1 / N_SBC):.3f} at the 90% level")
"""
    )

    nb.md(
        """
The grey band on the rank CDF is where a correctly calibrated posterior should
fall. `log_hazard` and `log_or` leave it slightly; `logit_detect` leaves it
comprehensively, and its KS p-value against uniformity is 0.000.

The coverage table says the same thing in units a clinical reviewer can use.
Intervals advertised at 90% deliver 85%, 86% and 77%. Intervals advertised at 50%
deliver 45%, 44% and 31%. With 300 SBC datasets the standard error on a 90%
coverage estimate is 0.017, so all three shortfalls are real and the detection
parameter's is severe.

**This is the same failure as an overconfident risk score in Lecture 1, one level
up.** There a model promised risks the ward did not deliver. Here a posterior
promises a 90% interval and delivers 77%. In both cases the ordering is fine, the
sharpness is not earned, and only a calibration check finds it.

What it is not is a reason to distrust NPE in general. The detection parameter is
the one the summaries barely constrain, and a density estimator asked to represent
a nearly flat posterior from 3,000 simulations will tend to make it too tight. The
remedies are more simulations, a more flexible estimator, or better summaries. The
exercise tests the last of these.
"""
    )

    nb.exercise(
        """
### Exercise 5.1

The detection parameter is the one the summaries constrain least, and it is the
one whose calibration is worst. Test the mechanism.

Retrain NPE on the same simulations but with the **timing summaries removed** -
keep only `rate_control` and `rate_treated`. Then:

1. Sample the posterior for `x_observed` and compare the width of the
   `logit_detect` marginal with the full-summary posterior.
2. Re-run SBC on the reduced model.

The point to reach: what SBC detects here is not a bug in the network. Say in one
line what it is instead, and what you would change if you saw this in a real
analysis.
""",
        """
RATE_ONLY = [0, 1]

inference_reduced = NPE(prior=prior, density_estimator="maf", show_progress_bars=False)
estimator_reduced = inference_reduced.append_simulations(
    theta_train, x_train[:, RATE_ONLY]
).train(training_batch_size=200, show_train_summary=False)
posterior_reduced = inference_reduced.build_posterior(estimator_reduced)

reduced_draws = posterior_reduced.sample(
    (5_000,), x=x_obs_t[RATE_ONLY], show_progress_bars=False
).numpy()

prior_sd = ((HIGH - LOW) / np.sqrt(12)).numpy()

widths = pd.DataFrame({
    "parameter": PARAM_NAMES,
    "prior sd": prior_sd,
    "sd, five summaries": npe_draws.std(axis=0),
    "sd, event rates only": reduced_draws.std(axis=0),
})
widths["ratio"] = widths["sd, event rates only"] / widths["sd, five summaries"]
widths["fraction of prior sd"] = widths["sd, event rates only"] / widths["prior sd"]
display(widths.round(3))

ranks_r, dap_r = run_sbc(theta_sbc, x_sbc[:, RATE_ONLY], posterior_reduced,
                         num_posterior_samples=N_SBC_DRAWS, show_progress_bar=False)
stats_r = check_sbc(ranks_r, theta_sbc, dap_r, num_posterior_samples=N_SBC_DRAWS)
rank_fraction_r = ranks_r.numpy() / N_SBC_DRAWS

display(pd.DataFrame({
    "parameter": PARAM_NAMES,
    "ks_pvalue, five summaries": stats["ks_pvals"].numpy(),
    "ks_pvalue, rates only": stats_r["ks_pvals"].numpy(),
    "coverage_90, rates only": [((rank_fraction_r[:, j] > 0.05) & (rank_fraction_r[:, j] < 0.95)).mean()
                                for j in range(3)],
}).round(3))

fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.4))
for j, (ax, name) in enumerate(zip(axes, PARAM_NAMES)):
    ax.hist(npe_draws[:, j], bins=40, density=True, alpha=0.65, label="five summaries")
    ax.hist(reduced_draws[:, j], bins=40, density=True, alpha=0.65, label="event rates only")
    ax.axvline(THETA_TRUE[j], ls="--", c="0.15")
    ax.set_xlabel(name)
axes[0].set_ylabel("Density")
axes[0].legend(fontsize=9)
plt.tight_layout()
plt.show()

print("Two event rates cannot separate a low hazard from poor detection: both")
print("push the recorded rate down in the same way. Without the timing summaries")
print("the hazard posterior widens by a factor of about 5.6 and the treatment")
print("effect by about 3.6, and the detection posterior sits at roughly 87% of")
print("its prior standard deviation, which is close to saying nothing at all.")
print()
print("Now the part worth arguing about. The reduced model is BETTER calibrated")
print("on log_hazard - its KS p-value rises from 0.04 to 0.52 and its 90%")
print("coverage from 0.85 to 0.90 - because a posterior that is honestly vague")
print("is easier to get right than one that is trying to be sharp. Calibration")
print("and informativeness are separate axes, and SBC only checks the first.")
print()
print("So SBC is reporting a property of the summary statistics, not a defect of")
print("the network. The fix is a better summary or a longer record, not a bigger")
print("model.")
""",
        stub="""
RATE_ONLY = [0, 1]

# 1. Train a second NPE on x_train[:, RATE_ONLY] with the same prior and settings.
# 2. Sample its posterior at x_obs_t[RATE_ONLY] and compare marginal standard
#    deviations with npe_draws.
# 3. Re-run run_sbc / check_sbc with x_sbc[:, RATE_ONLY].

""",
    )

    nb.note(
        "This is the section to protect if the room is short on time. Simulation-"
        "based calibration is the only tool in the module that checks a posterior "
        "without a held-out outcome, and it is the direct analogue of the "
        "calibration curve from Lecture 1. Same question, same failure mode, "
        "different object."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## What to take away

1. When you can simulate a clinical process but cannot write its likelihood, you
   can still have a posterior. The parameters are quantities a clinician can
   argue with, which is not true of a fitted regression coefficient.
2. ABC rejection sampling discards almost every simulation it runs, and the
   tolerance dial trades bias against Monte Carlo noise with no setting that
   escapes both. It degrades quickly as the parameter count grows.
3. Neural posterior estimation uses every simulation and amortises: train once,
   then a posterior for a new ward is a forward pass with no new simulator calls.
   Here it beat ABC on accuracy with one tenth of the simulation budget.
4. Amortisation is what makes this deployable across a hospital network. The
   expensive step happens once, offline.
5. A ridge in the posterior pairplot is information, not noise. It says which
   parameters the data cannot separate, and it is invisible in a point estimate.
6. Sharper is not the same as better. NPE's intervals were half the width of
   ABC's and delivered 80 to 84% coverage where they promised 90%, while ABC's
   were too wide and over-covered. Neither error is visible in an RMSE column.
7. Check the coverage. Simulation-based calibration is cheap, it needs no real
   outcomes, and a neural posterior can be confidently wrong in exactly the way a
   miscalibrated risk score is.
8. When SBC fails for one parameter, suspect the summary statistics before the
   network. Information that is not in the summaries cannot be recovered by a
   larger model, and a posterior that is honestly vague can be better calibrated
   than one that is trying to be sharp.
"""
    )

    return nb


if __name__ == "__main__":
    paths = build().write(ROOT / "notebooks", "04_simulation_based_inference")
    for path in paths:
        print("wrote", path.relative_to(ROOT))
