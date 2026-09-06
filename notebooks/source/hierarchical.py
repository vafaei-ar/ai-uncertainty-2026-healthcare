"""Notebook 3 - Hierarchical models for multi-site clinical risk."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.nbtools import BRANCH, COLAB_TOKEN, PLOT_STYLE, REPO, Notebook  # noqa: E402


def build() -> Notebook:
    nb = Notebook("Hierarchical models", colab_setup=False)

    nb.md(
        f'<a href="https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/'
        f'{COLAB_TOKEN}" target="_parent">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open this notebook in Google Colab"/></a>'
        "---\n\n"
        "**Setup.** Run this first. It installs PyMC and ArviZ if they are not already\n"
        "present, then fetches the teaching utilities. On a fresh Colab runtime it takes\n"
        "about a minute; on a machine that already has PyMC it takes seconds."
    )

    nb.code(
        """
import importlib.util, subprocess, sys, os

if importlib.util.find_spec("pymc") is None or importlib.util.find_spec("arviz") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymc", "arviz"], check=True)

REPO = "https://github.com/vafaei-ar/ai-uncertainty-2026-healthcare.git"

if importlib.util.find_spec("medsim") is None:
    if not os.path.isdir("ai-uncertainty-2026-healthcare"):
        subprocess.run(["git", "clone", "--depth", "1", REPO], check=True)
    sys.path.insert(0, os.path.abspath("ai-uncertainty-2026-healthcare"))

import medsim, pymc as pm, arviz as az
print("medsim", medsim.__version__, "| pymc", pm.__version__, "| arviz", az.__version__)
"""
    )

    nb.md(
        """
# Hierarchical models for multi-site clinical risk

*AI & Uncertainty School and Workshop 2026, healthcare module*

Lecture 2 ended with four hospitals, a hand-set prior concentration, and a promise
that a real hierarchical model estimates that number instead of assuming it. This
notebook keeps that promise.

The clinical question is the one every network faces. Six hospitals report
deterioration rates. Two of them are small enough that their reported rate is
mostly noise. You have to publish a number for each of them, and you have to
decide what to tell a seventh hospital that has no data at all.

**Where we are going**

1. Six hospitals, one register, two of them tiny
2. Three ways to estimate a site's risk: pool everything, pool nothing, or let the
   data decide
3. The pooling weight is a parameter, not a setting
4. A hierarchical logistic regression with varying intercepts and a varying slope
5. What the group-level standard deviation tells you about transferring a model

Sampling is deliberately small: 1000 draws, 1000 tuning steps, 2 chains. The whole
notebook runs in about a minute on a free Colab CPU.
"""
    )

    nb.code(
        """
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from scipy.special import expit, logit

from medsim import SimConfig, simulate_ehr
"""
        + PLOT_STYLE
        + """
SEED = 20261118
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 170)
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 1. Six hospitals, one register

Each hospital gets its own draw from the simulator, with its own baseline risk
(`site` and `prevalence_shift`) and its own relationship between lactate and
deterioration (`coefficient_drift`). Two of them are small on purpose: 60 and 30
admissions. That is not an unrealistic register - it is what an audit of a new
unit or a rural site looks like in its first year.

Because the data are simulated we also know each hospital's *true* deterioration
probability, which is the column no real audit ever has.
"""
    )

    nb.code(
        """
SITE_SPECS = [
    # name,            site, prevalence_shift, n,    seed, lactate coefficient
    ("Metro General",   "A",  0.00,           1200,  101,  0.95),
    ("Riverside",       "B",  0.30,            900,  102,  1.35),
    ("Lakeside",        "C", -0.20,            600,  103,  0.65),
    ("Fenwick",         "D",  0.10,            400,  104,  0.95),
    ("Harbour Annexe",  "A",  0.60,             60,  138,  1.10),
    ("New Unit",        "C", -0.50,             30,  134,  0.80),
]

frames = []
for name, site, shift, n, seed, lactate_coef in SITE_SPECS:
    cohort = simulate_ehr(
        SimConfig(n=n, site=site, prevalence_shift=shift, seed=seed,
                  coefficient_drift={"log_lactate": lactate_coef}),
        keep_truth=True,
    )
    cohort["hospital"] = name
    frames.append(cohort)

register = pd.concat(frames, ignore_index=True)
HOSPITALS = [s[0] for s in SITE_SPECS]

counts = (
    register.groupby("hospital", sort=False)
    .agg(n=("outcome", "size"), events=("outcome", "sum"), true_rate=("true_p", "mean"))
    .reindex(HOSPITALS)
    .reset_index()
)
counts["raw_rate"] = counts["events"] / counts["n"]
counts["se"] = np.sqrt(counts["raw_rate"] * (1 - counts["raw_rate"]) / counts["n"])
display(counts.round(4))
"""
    )

    nb.md(
        """
Read the last two rows. Harbour Annexe reports 28.3% and New Unit reports 0.0%, a
gap of 28 points. Their true rates are 20.8% and 5.0%, a gap of 16 points. Most of
what separates the two reported numbers is sampling noise, not medicine.

New Unit saw no events at all, so its raw estimate is exactly zero, and the usual
standard error $\\sqrt{\\hat{p}(1-\\hat{p})/n}$ is exactly zero as well - an interval
that is both infinitely narrow and wrong.

This is the situation partial pooling exists for.
"""
    )

    nb.note(
        "Ask the room what they would report for New Unit. Someone will say 0%, "
        "someone will say 'not enough data'. Both are answers you cannot put in a "
        "network dashboard. The hierarchical model gives you the third answer."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 2. Three models of the same six numbers

Write $y_j$ for the events at hospital $j$ out of $n_j$ admissions, and
$\\alpha_j$ for its log-odds of deterioration.

- **Complete pooling.** One rate for the network: $\\alpha_j = \\alpha$ for all $j$.
  Nothing to estimate per site, and site differences are asserted not to exist.
- **No pooling.** Each site gets its own $\\alpha_j$ with a wide independent prior.
  Site differences are real and nothing is shared, so a site with 30 admissions is
  estimated from 30 admissions.
- **Partial pooling.** $\\alpha_j \\sim \\mathrm{Normal}(\\mu, \\sigma)$, with $\\mu$
  and $\\sigma$ estimated from the data. Sites are different, and how different
  is itself a question the data answers.

We fit all three and compare them against the truth the simulator knows.
"""
    )

    nb.code(
        """
n_obs = counts["n"].to_numpy()
y_obs = counts["events"].to_numpy()
K = len(counts)

sample_kwargs = dict(draws=1000, tune=1000, chains=2, cores=1,
                     progressbar=False, random_seed=SEED)

with pm.Model() as complete_pooling:
    p = pm.Beta("p", 1.0, 1.0)
    pm.Binomial("y", n=n_obs, p=p, observed=y_obs)
    idata_complete = pm.sample(**sample_kwargs)

with pm.Model() as no_pooling:
    alpha = pm.Normal("alpha", mu=-1.6, sigma=2.5, shape=K)
    pm.Binomial("y", n=n_obs, logit_p=alpha, observed=y_obs)
    idata_none = pm.sample(**sample_kwargs)

with pm.Model() as partial_pooling:
    mu = pm.Normal("mu", mu=-1.6, sigma=1.0)
    sigma = pm.HalfNormal("sigma", 1.0)
    z = pm.Normal("z", 0.0, 1.0, shape=K)                 # non-centred
    alpha = pm.Deterministic("alpha", mu + sigma * z)
    pm.Binomial("y", n=n_obs, logit_p=alpha, observed=y_obs)
    idata_partial = pm.sample(target_accept=0.95, **sample_kwargs)

print("partial pooling, group-level parameters:")
display(az.summary(idata_partial, var_names=["mu", "sigma"]).round(3))
print(f"max r_hat across all parameters: {az.summary(idata_partial)['r_hat'].max():.3f}")
"""
    )

    nb.md(
        """
`r_hat` compares the variance between chains with the variance within them. At
1.00 the chains are exploring the same distribution; above about 1.01 they are
not, and no amount of interpretation will rescue the numbers underneath.

Report the maximum over all parameters, never the one for the parameter you care
about. And note that with two chains and 1000 draws the diagnostic is itself
estimated from very little: a maximum sitting on the 1.01 line, as it does here,
is a reason to look at the trace rather than to move on.
"""
    )

    nb.code(
        """
est_complete = np.repeat(float(idata_complete.posterior["p"].mean()), K)
est_none = expit(idata_none.posterior["alpha"].mean(("chain", "draw")).to_numpy())
est_partial = expit(idata_partial.posterior["alpha"].mean(("chain", "draw")).to_numpy())

comparison = pd.DataFrame({
    "hospital": counts["hospital"],
    "n": counts["n"],
    "raw": counts["raw_rate"],
    "truth": counts["true_rate"],
    "complete_pooling": est_complete,
    "no_pooling": est_none,
    "partial_pooling": est_partial,
})
display(comparison.round(4))

errors = {c: np.abs(comparison[c] - comparison["truth"]).mean()
          for c in ["complete_pooling", "no_pooling", "partial_pooling"]}
small = comparison["n"] < 100
errors_small = {c: np.abs(comparison.loc[small, c] - comparison.loc[small, "truth"]).mean()
                for c in ["complete_pooling", "no_pooling", "partial_pooling"]}

display(pd.DataFrame({"mean abs error, all six sites": errors,
                      "mean abs error, two small sites": errors_small}).round(4))
"""
    )

    nb.md(
        """
Now the picture. Each hospital's raw rate, its partially pooled posterior with a
94% interval, and the truth.
"""
    )

    nb.code(
        """
alpha_draws = idata_partial.posterior["alpha"].stack(sample=("chain", "draw")).to_numpy()
p_draws = expit(alpha_draws)
lo, hi = np.quantile(p_draws, [0.03, 0.97], axis=1)

network_mean = expit(float(idata_partial.posterior["mu"].mean()))
intervals = pd.DataFrame({
    "hospital": comparison["hospital"],
    "n": comparison["n"],
    "raw": comparison["raw"],
    "partial_pooling": comparison["partial_pooling"],
    "94%_low": lo,
    "94%_high": hi,
    "interval_width": hi - lo,
    "moved_toward_mean": (comparison["partial_pooling"] - comparison["raw"])
                         / (network_mean - comparison["raw"]),
})
print(f"network mean rate = {network_mean:.4f}")
display(intervals.round(4))

fig, ax = plt.subplots(figsize=(8.4, 4.6))
x = np.arange(K)
ax.plot(x - 0.12, comparison["raw"], "o", ms=9, label="Raw site rate")
ax.errorbar(x + 0.12, comparison["partial_pooling"],
            yerr=[comparison["partial_pooling"] - lo, hi - comparison["partial_pooling"]],
            fmt="s", ms=9, capsize=4, label="Partial pooling (94% interval)")
ax.plot(x, comparison["truth"], "x", ms=11, mew=2, c="0.15", label="True site rate")
ax.axhline(network_mean, ls="--", c="0.5", label="Network mean")
ax.set_xticks(x)
ax.set_xticklabels([f"{h}\\nn={n}" for h, n in zip(comparison["hospital"], comparison["n"])],
                   fontsize=9)
ax.set_ylabel("Deterioration rate")
ax.set_title("Shrinkage is proportional to how little a site knows about itself")
ax.legend(fontsize=9)
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
The four large hospitals sit on top of their raw rates: the model has no reason to
move them, and it does not. The two small ones move, and the smaller the site the
further it travels toward the network mean.

Note what happened to New Unit. Its raw rate was zero and its pooled estimate is
not, because the model knows what the other five hospitals look like and knows
that zero events in 30 admissions is entirely compatible with the network's usual
rate. Its 94% interval is several times wider than Metro General's, which is the
model saying the same thing the sample size said.

The error table is the summary that matters. Against the truth the simulator knows,
mean absolute error across the six sites is **0.061 for complete pooling, 0.023 for
no pooling and 0.013 for partial pooling**. Restricted to the two small sites it is
0.079, 0.056 and 0.028. Partial pooling wins everywhere, and it wins by the most
where the data are thinnest.
"""
    )

    nb.note(
        "The complete-pooling row is worth dwelling on: it is exactly what a "
        "single model fitted on the concatenated register does. Every deployment "
        "that trains one model on pooled multi-site data has silently chosen the "
        "first column of that table."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 3. The pooling weight is a parameter, not a setting

For a normal approximation on the logit scale the partially pooled estimate is a
precision-weighted average of the site's own estimate and the network mean:

$$\\hat{\\alpha}_j \\approx w_j\\,\\hat{\\alpha}_j^{\\text{raw}} + (1 - w_j)\\,\\mu,
\\qquad w_j = \\frac{\\sigma^2}{\\sigma^2 + v_j},
\\qquad v_j \\approx \\frac{1}{n_j\\,\\bar{p}_j(1 - \\bar{p}_j)}$$

$v_j$ is how noisy the site's own estimate is; $\\sigma$ is how different sites
genuinely are. The weight is the ratio of the two, and $\\sigma$ is estimated from
the same six numbers.
"""
    )

    nb.code(
        """
sigma_hat = float(idata_partial.posterior["sigma"].mean())
p_bar = comparison["partial_pooling"].to_numpy()
v_j = 1.0 / (counts["n"].to_numpy() * p_bar * (1 - p_bar))

weights = pd.DataFrame({
    "hospital": counts["hospital"],
    "n": counts["n"],
    "sampling variance v_j": v_j,
    "weight on own data w_j": sigma_hat**2 / (sigma_hat**2 + v_j),
})
print(f"posterior mean sigma = {sigma_hat:.3f}")
display(weights.round(4))
"""
    )

    nb.md(
        """
Metro General puts 99% of the weight on its own 1200 admissions. New Unit puts 54%
on its own 30 and takes the rest from the network. Nothing in that table was
chosen: $\\sigma$ came out of the posterior, $v_j$ came out of the sample sizes,
and the weights follow. **A hierarchical model does not pick an amount of pooling;
it infers one, and it infers a different one for every site.**

The posterior for $\\sigma$ is the object that carries the whole argument, so it
deserves a plot rather than a summary line.
"""
    )

    nb.code(
        """
az.plot_posterior(idata_partial, var_names=["sigma"], hdi_prob=0.94, figsize=(6.4, 3.6))
plt.title("Between-hospital standard deviation on the log-odds scale")
plt.show()

sigma_draws = idata_partial.posterior["sigma"].values.ravel()
print(f"P(sigma < 0.1)  = {(sigma_draws < 0.1).mean():.3f}   "
      "(sites are effectively identical: complete pooling would do)")
print(f"P(sigma > 1.0)  = {(sigma_draws > 1.0).mean():.3f}   "
      "(sites differ enough that a single number is misleading)")
"""
    )

    nb.exercise(
        """
### Exercise 3.1

Show that complete pooling and no pooling are the two ends of one dial.

Refit the partial-pooling model twice with $\\sigma$ **fixed** instead of estimated:
once at 0.02 and once at 5.0. Use `pm.ConstantData` or simply write the constant
into the model. Then put the three sets of site estimates side by side with the
complete-pooling and no-pooling estimates from section 2.

Which fixed value reproduces which extreme, and what does the estimated
$\\sigma \\approx 0.95$ buy you that neither extreme does?
""",
        """
def fixed_sigma_fit(sigma_value, seed=SEED):
    with pm.Model():
        mu_f = pm.Normal("mu", mu=-1.6, sigma=1.0)
        z_f = pm.Normal("z", 0.0, 1.0, shape=K)
        alpha_f = pm.Deterministic("alpha", mu_f + sigma_value * z_f)
        pm.Binomial("y", n=n_obs, logit_p=alpha_f, observed=y_obs)
        idata = pm.sample(draws=1000, tune=1000, chains=2, cores=1,
                          progressbar=False, random_seed=seed)
    print(f"sigma fixed at {sigma_value}: max r_hat "
          f"{az.summary(idata)['r_hat'].max():.3f}, "
          f"min ess_bulk {az.summary(idata)['ess_bulk'].min():.0f}")
    return expit(idata.posterior["alpha"].mean(("chain", "draw")).to_numpy())

est_tight = fixed_sigma_fit(0.02)
est_loose = fixed_sigma_fit(5.0)

dial = pd.DataFrame({
    "hospital": counts["hospital"],
    "n": counts["n"],
    "sigma = 0.02": est_tight,
    "complete pooling": est_complete,
    "sigma estimated": est_partial,
    "sigma = 5.0": est_loose,
    "no pooling": est_none,
    "truth": counts["true_rate"],
})
display(dial.round(4))

print("sigma -> 0 reproduces complete pooling: every site gets the network mean.")
print("sigma -> large reproduces no pooling: every site gets its own raw rate,")
print("and New Unit is pushed back down to essentially zero.")
print()
print("The estimated value sits between them, and the position is chosen by the")
print("data rather than by us. That is the only one of the three that gives the")
print("small sites a defensible number and the large sites their own.")
print()
print("Compare the two diagnostic lines printed above the table. Forcing a large")
print("sigma on a site that saw no events pushes its intercept toward minus")
print("infinity with nothing to stop it, and the sampler says so.")
""",
        stub="""
def fixed_sigma_fit(sigma_value, seed=SEED):
    # Same model as `partial_pooling`, but with sigma held at `sigma_value`
    # instead of given a HalfNormal prior. Return the posterior mean rate per site.
    ...

# Fit at 0.02 and at 5.0, then tabulate against est_complete, est_partial, est_none.

""",
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 4. A hierarchical logistic regression

Site-level rates are a warm-up. The model a network actually deploys uses patient
features, and the question becomes whether the *relationship* between a feature
and risk is the same everywhere.

We fit, on all patients at once:

$$\\mathrm{logit}\\,\\Pr(y_i = 1) = \\alpha_{s[i]} + \\beta_{\\text{age}} x_{\\text{age},i}
+ \\beta_{\\text{resp}} x_{\\text{resp},i} + \\beta^{\\text{lac}}_{s[i]} x_{\\text{lac},i}$$

with

$$\\alpha_j \\sim \\mathrm{Normal}(\\mu_\\alpha, \\sigma_\\alpha), \\qquad
\\beta^{\\text{lac}}_j \\sim \\mathrm{Normal}(\\mu_{\\text{lac}}, \\sigma_{\\text{lac}})$$

Two group-level standard deviations, and they answer two different clinical
questions. $\\sigma_\\alpha$ is how much baseline risk varies between hospitals.
$\\sigma_{\\text{lac}}$ is how much the lactate-risk gradient varies. A model can
transfer badly on one and fine on the other.

Both varying terms use the non-centred form ($\\alpha_j = \\mu + \\sigma z_j$ with
$z_j \\sim \\mathrm{Normal}(0,1)$), which is what keeps NUTS out of the funnel when
a site contributes almost no information.
"""
    )

    nb.code(
        """
work = register.copy()
work["log_lactate"] = np.log(work["lactate"].fillna(work["lactate"].median()))

PREDICTORS = ["age", "respiratory_rate", "log_lactate"]
X = ((work[PREDICTORS] - work[PREDICTORS].mean()) / work[PREDICTORS].std()).to_numpy()
site_idx = pd.Categorical(work["hospital"], categories=HOSPITALS).codes
y = work["outcome"].to_numpy()

print(f"{len(work)} admissions across {K} hospitals, {y.mean():.3f} overall event rate")

coords = {"hospital": HOSPITALS, "fixed": ["age", "respiratory_rate"]}

with pm.Model(coords=coords) as varying_slopes:
    mu_alpha = pm.Normal("mu_alpha", -1.6, 1.0)
    sigma_alpha = pm.HalfNormal("sigma_alpha", 1.0)
    z_alpha = pm.Normal("z_alpha", 0.0, 1.0, dims="hospital")
    alpha_j = pm.Deterministic("alpha_site", mu_alpha + sigma_alpha * z_alpha, dims="hospital")

    beta = pm.Normal("beta", 0.0, 1.0, dims="fixed")

    mu_lac = pm.Normal("mu_lactate", 0.5, 1.0)
    sigma_lac = pm.HalfNormal("sigma_lactate", 0.5)
    z_lac = pm.Normal("z_lactate", 0.0, 1.0, dims="hospital")
    beta_lac = pm.Deterministic("beta_lactate", mu_lac + sigma_lac * z_lac, dims="hospital")

    eta = (alpha_j[site_idx]
           + beta[0] * X[:, 0]
           + beta[1] * X[:, 1]
           + beta_lac[site_idx] * X[:, 2])
    pm.Bernoulli("y", logit_p=eta, observed=y)

    idata_hier = pm.sample(target_accept=0.95, **sample_kwargs)

display(az.summary(idata_hier,
                   var_names=["mu_alpha", "sigma_alpha", "mu_lactate", "sigma_lactate", "beta"]
                   ).round(3))
diagnostics = az.summary(idata_hier)
print(f"max r_hat: {diagnostics['r_hat'].max():.3f}   "
      f"min ess_bulk: {diagnostics['ess_bulk'].min():.0f}   "
      f"divergences: {int(idata_hier.sample_stats['diverging'].values.sum())}")
"""
    )

    nb.code(
        """
az.plot_trace(idata_hier, var_names=["mu_alpha", "sigma_alpha", "mu_lactate", "sigma_lactate"],
              figsize=(11, 6.5))
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
The trace panels are the second half of the convergence check that `r_hat`
started: two chains overlapping, no drift, no long flat stretches.

Now the site-level parameters.
"""
    )

    nb.code(
        """
az.plot_forest(idata_hier, var_names=["alpha_site", "beta_lactate"],
               combined=True, hdi_prob=0.94, figsize=(8.0, 6.0))
plt.title("Varying intercepts and varying lactate slopes")
plt.tight_layout()
plt.show()

site_table = az.summary(idata_hier, var_names=["alpha_site", "beta_lactate"], hdi_prob=0.94)
site_table["hdi_width"] = site_table["hdi_97%"] - site_table["hdi_3%"]
display(site_table[["mean", "sd", "hdi_3%", "hdi_97%", "hdi_width"]].round(3))
"""
    )

    nb.md(
        """
The intercept panel spreads out: site intercepts run from about $-3.2$ to $-1.1$
on the log-odds scale. The slope panel does not: site slopes run from 0.26 to
0.46 around a network mean of 0.36.

The two small sites are the interesting rows. Harbour Annexe and New Unit have
slope intervals roughly three times wider than Metro General's, wide enough to
cover every other hospital's slope. That is the model saying it has learned a
baseline for each hospital and has not learned a separate lactate gradient for the
small ones, so it has handed them something close to the network's gradient. With
30 admissions that is exactly the right thing to do.

A posterior predictive check asks whether the fitted model can reproduce the thing
we asked it about: the event rate at each hospital.
"""
    )

    nb.code(
        """
with varying_slopes:
    ppc = pm.sample_posterior_predictive(idata_hier, random_seed=SEED, progressbar=False)

y_rep = ppc.posterior_predictive["y"].stack(sample=("chain", "draw")).to_numpy()  # patients x draws

rows = []
for j, hospital in enumerate(HOSPITALS):
    mask = site_idx == j
    rep_rate = y_rep[mask].mean(axis=0)
    rows.append({
        "hospital": hospital,
        "n": int(mask.sum()),
        "observed_rate": y[mask].mean(),
        "ppc_mean": rep_rate.mean(),
        "ppc_3%": np.quantile(rep_rate, 0.03),
        "ppc_97%": np.quantile(rep_rate, 0.97),
        "observed_inside": bool(np.quantile(rep_rate, 0.03) <= y[mask].mean() <= np.quantile(rep_rate, 0.97)),
    })
display(pd.DataFrame(rows).round(4))

fig, ax = plt.subplots(figsize=(8.0, 4.2))
tab = pd.DataFrame(rows)
xs = np.arange(K)
ax.errorbar(xs, tab["ppc_mean"],
            yerr=[tab["ppc_mean"] - tab["ppc_3%"], tab["ppc_97%"] - tab["ppc_mean"]],
            fmt="s", ms=8, capsize=4, label="Posterior predictive (94%)")
ax.plot(xs, tab["observed_rate"], "o", ms=9, c="#C44E52", label="Observed")
ax.set_xticks(xs)
ax.set_xticklabels(HOSPITALS, rotation=15, fontsize=9)
ax.set_ylabel("Deterioration rate")
ax.set_title("Posterior predictive check, by hospital")
ax.legend(fontsize=9)
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
All six observed rates fall inside their 94% predictive intervals, including New
Unit's zero. The interval for New Unit runs from 0 to about 17%, which is what 30
admissions buys you, and the interval for Metro General is narrow enough that a
real misfit would have shown.

Widths like these are the reason a posterior predictive check is a weak test at a
small site and a sharp one at a large site. Passing at New Unit says almost
nothing; passing at Metro General says something.
"""
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## 5. What $\\sigma$ says about the seventh hospital

A hospital with no data at all is not outside the model. Its intercept is a draw
from the group distribution, so the posterior predictive for a new site is

$$\\alpha_{\\text{new}} \\sim \\mathrm{Normal}(\\mu_\\alpha, \\sigma_\\alpha)$$

integrated over the posterior for $\\mu_\\alpha$ and $\\sigma_\\alpha$. That is a
usable prior for a hospital you have never seen, and its width is set by
$\\sigma_\\alpha$.
"""
    )

    nb.code(
        """
mu_draws = idata_hier.posterior["mu_alpha"].values.ravel()
sigma_a_draws = idata_hier.posterior["sigma_alpha"].values.ravel()
sigma_l_draws = idata_hier.posterior["sigma_lactate"].values.ravel()

alpha_new = rng.normal(mu_draws, sigma_a_draws)
rate_new = expit(alpha_new)

print(f"sigma_alpha   posterior mean {sigma_a_draws.mean():.3f}   "
      f"94% HDI [{np.quantile(sigma_a_draws, 0.03):.3f}, {np.quantile(sigma_a_draws, 0.97):.3f}]")
print(f"sigma_lactate posterior mean {sigma_l_draws.mean():.3f}   "
      f"94% HDI [{np.quantile(sigma_l_draws, 0.03):.3f}, {np.quantile(sigma_l_draws, 0.97):.3f}]")
print()
print(f"predicted baseline rate at an unseen hospital: median {np.median(rate_new):.3f}   "
      f"94% interval [{np.quantile(rate_new, 0.03):.3f}, {np.quantile(rate_new, 0.97):.3f}]")

fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.8))
axes[0].hist(rate_new, bins=60, density=True, alpha=0.8)
for r in counts["raw_rate"]:
    axes[0].axvline(r, ls=":", c="0.45", lw=1.2)
axes[0].set_xlim(0, 0.6)
axes[0].set_xlabel("Baseline deterioration rate")
axes[0].set_ylabel("Density")
axes[0].set_title("Predictive rate for a hospital with no data\\n(dotted: the six observed sites)")

axes[1].hist(sigma_a_draws, bins=50, density=True, alpha=0.8, label="sigma_alpha (intercept)")
axes[1].hist(sigma_l_draws, bins=50, density=True, alpha=0.8, label="sigma_lactate (slope)")
axes[1].set_xlabel("Group-level standard deviation")
axes[1].set_title("Baseline varies more than the gradient")
axes[1].legend(fontsize=9)
plt.tight_layout()
plt.show()
"""
    )

    nb.md(
        """
Read the two standard deviations as a deployment brief.

- **$\\sigma_\\alpha \\approx 0.97$ on the log-odds scale is large.** Baseline risk
  really does differ between these hospitals, so a probability calibrated at one
  site will not be calibrated at another. This is Lecture 1's site B, restated as
  a parameter, and it is the reason recalibration is the first thing you do at a
  new site.
- **$\\sigma_{\\text{lac}} \\approx 0.17$ against a mean slope of 0.36 is small.**
  The lactate-risk gradient is close to shared, and its interval reaches down to
  nearly zero. The part of the model that does the ranking transfers; the part
  that sets the level does not.

The predictive interval makes the consequence concrete. Before a seventh hospital
sends you a single patient, the model says its baseline deterioration rate is
somewhere between about 2% and 52%. That is not a failure of the model, it is the
honest width of what five other hospitals can tell you about a sixth, and it is
the number that should decide how many local labels you collect before switching
anything on.

If both were small, one pooled model would be defensible everywhere. If both were
large, no model fitted on other hospitals would be worth shipping to a new one
without local data. Most real networks look like this notebook: the intercept
moves, the slopes mostly do not, and that is precisely why AUROC survives the move
and calibration does not.
"""
    )

    nb.note(
        "Tie this back to Lecture 1 section 5 explicitly. The hierarchical model "
        "gives a number to the thing that was diagnosed there by eye: shifted "
        "prevalence with a stable risk relationship. It also gives the honest "
        "answer to 'can we use this at hospital seven' - yes for the ordering, "
        "not for the probabilities, until you have local labels."
    )

    # ------------------------------------------------------------------
    nb.md(
        """
---
## What to take away

1. A small site's raw rate is mostly noise, and its usual standard error can be
   zero while its estimate is badly wrong. Partial pooling gives it a defensible
   number and an honest interval.
2. Complete pooling and no pooling are the two ends of one dial. Fitting one model
   on concatenated multi-site data is a choice of one extreme, usually made by
   accident.
3. The amount of pooling is estimated, not chosen. The weight a site puts on its
   own data is $\\sigma^2/(\\sigma^2 + v_j)$, and both terms come from the data.
4. Always report `r_hat` and effective sample size alongside a posterior. A
   hierarchical model that has not converged looks exactly like one that has.
5. Non-centred parameterisation is not a stylistic preference. With sites that
   contribute little information it is the difference between a sampler that
   explores the posterior and one that stalls in the funnel.
6. The group-level standard deviations are the transfer report. A large
   $\\sigma_\\alpha$ with a small slope $\\sigma$ means the ranking travels and the
   probabilities do not, which tells you exactly what to fix at the new hospital.
7. A hospital with no data still has a posterior. It is the group distribution,
   and its width is a decision-relevant quantity rather than an inconvenience.
"""
    )

    return nb


if __name__ == "__main__":
    paths = build().write(ROOT / "notebooks", "03_hierarchical_pymc")
    for path in paths:
        print("wrote", path.relative_to(ROOT))
