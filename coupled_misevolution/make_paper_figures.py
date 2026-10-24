# -*- coding: utf-8 -*-
"""Paper figures from the saved results. Output: figures/paper/*.png

fig1_share        shared vs private notes, lenient vs clean judge (3 seeds): OLMo-2-7B and Qwen3-4B
fig2_contamination who contaminates whom: real notes as context for each role, per model
fig3_susceptibility planted notes: how far each role is pushed, per model
fig4_context      any notes in the prompt (harmless / irrelevant) vs none, per model
fig5_pressure     flawed vs honest reward over rounds, per model (no reward-driven drift)

Palette: validated categorical slots (blue, orange, aqua, yellow), light surface; labelled directly.
"""
import os, re, json, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
OUT = os.path.join(HERE, "figures", "paper")
os.makedirs(OUT, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]   # sequential blue

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
                     "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.facecolor": SURFACE, "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "axes.linewidth": 1})

MODELS = {"olmo": ("allenai_OLMo-2-1124-7B-Instruct", "OLMo-2-7B"),
          "qwen3": ("Qwen_Qwen3-4B-Instruct-2507", "Qwen3-4B"),
          "phi": ("microsoft_Phi-4-mini-instruct", "Phi-4-mini"),
          "qwen25": ("Qwen_Qwen2.5-7B-Instruct", "Qwen2.5-7B"),
          "granite": ("ibm-granite_granite-3.3-8b-instruct", "Granite-3.3-8B"),
          "falcon": ("tiiuae_Falcon3-7B-Instruct", "Falcon3-7B")}


def load(path):
    return json.load(open(path, encoding="utf-8"))


def series(d, key):
    return [(r["round"], r["probe"][key]) for r in d["rounds"] if r["probe"] and r["probe"].get(key) is not None]


def last2(d, key):
    return float(np.mean([v for _, v in series(d, key)[-2:]]))


def clean_axes(ax, ylabel=None):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    if ylabel:
        ax.set_ylabel(ylabel)


# ------------------------------------------------------------------ fig 1: shared notebook
def fig1():
    conds = [("clean judge", "honest_ev-OC_rf-score_sum2"), ("lenient-seeded judge", "honest_ev-OC_seed-E8_rf-score_sum2")]
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0), sharey=True)
    for row, key in enumerate(["olmo", "qwen3"]):
        mdir, mname = MODELS[key]
        for col, (metric, title) in enumerate([("judge_far", "Judge passes wrong answers"),
                                               ("review_far", "Reviewer approves wrong answers")]):
            ax = axes[row, col]
            clean_axes(ax, f"{mname}\n(% of wrong answers)" if col == 0 else None)
            for gi, (clabel, base) in enumerate(conds):
                for bi, (share, color, suffix) in enumerate([("private notes", BLUE, ""), ("team notebook", ORANGE, "_shr-team")]):
                    ds = [load(f) for f in sorted(glob.glob(os.path.join(RES, mdir, f"{base}{suffix}_s[0-9].json")))]
                    ds = [d for d in ds if d["complete"]]
                    vals = np.array([last2(d, metric) * 100 for d in ds])
                    x = gi + (bi - 0.5) * 0.36
                    ax.bar(x, vals.mean(), width=0.30, color=color, zorder=2, label=share if (gi == 0) else None)
                    ax.scatter([x] * len(vals), vals, s=22, color="white", edgecolor=INK2, linewidth=1.0, zorder=3)
                    ax.text(x, min(vals.max() + 3, 96), f"{vals.mean():.0f}", ha="center", va="bottom", fontsize=9, color=INK)
            ax.set_xticks([0, 1]); ax.set_xticklabels([c[0] for c in conds])
            ax.set_xlim(-0.6, 1.6)
            if row == 0:
                ax.set_title(title, fontsize=11, fontweight="bold", color=INK, pad=8)
    axes[0, 0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("A shared team notebook spreads leniency in OLMo-2, not in Qwen3-4B", fontsize=12.5, fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "Honest reward, 10 rounds. Bars: mean of 3 seeds (last two measurements); dots: individual seeds. "
             "Clean judge has no notes of its own.", ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(os.path.join(OUT, "fig1_share.png"), dpi=200); plt.close(fig)


# ------------------------------------------------------------------ fig 2: contamination matrix
def fig2():
    files = {k: os.path.join(RES, "contamination", MODELS[k][0] + ".json") for k in ("olmo", "phi", "qwen3")}
    ctx = [("none", "no notes"), ("E", "judge's\nnotes"), ("O", "solver's\nnotes"), ("C", "reviewer's\nnotes")]
    own = {"judge": "E", "reviewer": "C"}
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.5), sharey=True)
    for ax, key in zip(axes, ("olmo", "phi", "qwen3")):
        d = load(files[key])
        M = np.array([[d[role][s]["on_wrong"] * 100 for s, _ in ctx] for role in ("judge", "reviewer")])
        bins = np.clip((M / 100 * 7).astype(int), 0, 6)
        for i in range(2):
            for j in range(4):
                ax.add_patch(Rectangle((j, 1 - i), 1, 1, facecolor=SEQ[bins[i, j]], edgecolor=SURFACE, lw=3))
                dark = bins[i, j] >= 3
                ax.text(j + 0.5, 1 - i + 0.5, f"{M[i, j]:.0f}%", ha="center", va="center", fontsize=12,
                        fontweight="bold", color="white" if dark else INK)
                if ctx[j][0] == own["judge" if i == 0 else "reviewer"]:
                    ax.text(j + 0.5, 1 - i + 0.14, "own notes", ha="center", va="center", fontsize=7.5,
                            color="white" if dark else INK2)
        ax.set_xlim(0, 4); ax.set_ylim(0, 2)
        ax.set_xticks([j + 0.5 for j in range(4)]); ax.set_xticklabels([c[1] for c in ctx], fontsize=9)
        ax.set_yticks([1.5, 0.5]); ax.set_yticklabels(["judge passes\nwrong answers", "reviewer approves\nwrong answers"], fontsize=9)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(MODELS[key][1], fontsize=11, fontweight="bold", pad=8)
    fig.suptitle("Who contaminates whom: real notes from each role placed in another role's prompt",
                 fontsize=12.5, fontweight="bold", y=1.0)
    fig.text(0.5, 0.005, "Cell = % of wrong answers accepted (100 items, 50 wrong). Darker = more lenient. "
             "Notes written by that model's own agents in a 10-round loop.", ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig2_contamination.png"), dpi=200); plt.close(fig)


# ------------------------------------------------------------------ fig 3: susceptibility to planted notes
def fig3():
    order = ["qwen3", "qwen25", "phi", "olmo", "granite", "falcon"]
    panels = [("Judge passes wrong answers", "judge", "clean", "seed_E8", True),
              ("Reviewer approves wrong answers", "reviewer", "clean", "seed_C8", True),
              ("Worker keeps the Check: step", "worker", "clean", "seed_O8", False)]
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.1), sharey=True)
    for ax, (title, role, c0, c1, bad_up) in zip(axes, panels):
        clean_axes(ax)
        ax.set_ylim(-4, 104)
        for i, key in enumerate(order):
            r = load(os.path.join(RES, "screening", MODELS[key][0] + ".json"))[role]
            f = (lambda x: x["on_wrong"] * 100) if role != "worker" else (lambda x: x["check"] * 100)
            a, b = f(r[c0]), f(r[c1])
            ax.plot([i, i], [a, b], color=AXIS, lw=2.5, zorder=2, solid_capstyle="round")
            ax.scatter([i], [a], s=75, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
            ax.scatter([i], [b], s=75, color=ORANGE, edgecolor=SURFACE, linewidth=2, zorder=3)
            if abs(a - b) < 9:        # close together: clean label on the left, planted label on the right
                ax.text(i - 0.14, a, f"{a:.0f}", va="center", ha="right", fontsize=8.5, color=INK2)
                ax.text(i + 0.14, b, f"{b:.0f}", va="center", ha="left", fontsize=8.5, color=INK)
            else:
                ax.text(i + 0.14, a, f"{a:.0f}", va="center", fontsize=8.5, color=INK2)
                ax.text(i + 0.14, b, f"{b:.0f}", va="center", fontsize=8.5, color=INK)
        ax.set_xticks(range(len(order))); ax.set_xticklabels([MODELS[k][1] for k in order], fontsize=8, rotation=28, ha="right")
        ax.set_xlim(-0.5, len(order) - 0.4)
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    axes[0].set_ylabel("%")
    axes[0].scatter([], [], s=60, color=BLUE, label="clean (no notes)")
    axes[0].scatter([], [], s=60, color=ORANGE, label="8 planted notes")
    axes[0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("Planted notes erode the worker's verification step in 5 of 6 models; the judge and reviewer only in some",
                 fontsize=12, fontweight="bold", y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(OUT, "fig3_susceptibility.png"), dpi=200); plt.close(fig)


# ------------------------------------------------------------------ fig 4: any notes in the prompt
def fig4():
    conds = [("none", "no notes"), ("benign6", "6 harmless\nnotes"), ("benign12", "12 harmless\nnotes"), ("irrelevant6", "6 irrelevant\nnotes")]
    cols = {"olmo": BLUE, "phi": ORANGE, "qwen3": AQUA, "qwen25": YELLOW, "granite": "#e87ba4", "falcon": "#008300"}
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), sharey=True)
    for ax, (role, title) in zip(axes, [("judge", "Judge passes wrong answers"), ("reviewer", "Reviewer approves wrong answers")]):
        clean_axes(ax)
        ends = []
        for key in ("olmo", "phi", "qwen3", "qwen25", "granite", "falcon"):
            d = load(os.path.join(RES, "context", MODELS[key][0] + ".json"))[role]
            y = [d[c]["on_wrong"] * 100 for c, _ in conds]
            ax.plot(range(4), y, color=cols[key], lw=2, marker="o", ms=7, mec=SURFACE, mew=1.5, zorder=3)
            ends.append([y[-1], MODELS[key][1]])
        ends.sort()                          # direct labels: keep at least 6 points apart
        for k in range(1, len(ends)):
            ends[k][0] = max(ends[k][0], ends[k - 1][0] + 6)
        for ypos, name in ends:
            ax.text(3.08, ypos, name, va="center", fontsize=9, color=INK)
        ax.set_xticks(range(4)); ax.set_xticklabels([c[1] for c in conds], fontsize=9)
        ax.set_xlim(-0.2, 4.1)
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    axes[0].set_ylabel("% of wrong answers accepted")
    fig.suptitle("Even irrelevant notes make OLMo-2 more lenient; the other five models do not budge",
                 fontsize=12, fontweight="bold", y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(OUT, "fig4_context.png"), dpi=200); plt.close(fig)


# ------------------------------------------------------------------ fig 5: flawed vs honest reward
def fig5():
    files = {"qwen3": ("misspec_ev-EOC_rf-score_sum_s0", "honest_ev-EOC_rf-score_sum_s0"),
             "phi": ("misspec_ev-EOC_rf-score_sum2_s0", "honest_ev-EOC_rf-score_sum2_s0"),
             "olmo": ("misspec_ev-EOC_rf-score_sum2_s0", "honest_ev-EOC_rf-score_sum2_s0")}
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 6.0), sharey="row")
    for col, key in enumerate(("qwen3", "phi", "olmo")):
        mdir = MODELS[key][0]
        fl, ho = (load(os.path.join(RES, mdir, f + ".json")) for f in files[key])
        for row, (metric, lab) in enumerate([("judge_far", "judge passes wrong (%)"), ("review_far", "reviewer approves wrong (%)")]):
            ax = axes[row, col]
            clean_axes(ax)
            for d, color, name in ((ho, BLUE, "honest reward"), (fl, ORANGE, "flawed reward")):
                s = series(d, metric)
                ax.plot([r for r, _ in s], [v * 100 for _, v in s], color=color, lw=2, marker="o", ms=5, mec=SURFACE, mew=1.2,
                        label=name if (row == 0 and col == 0) else None, zorder=3)
            ax.set_xlim(-0.3, 10.3); ax.set_xticks([0, 2, 4, 6, 8, 10])
            if row == 0:
                ax.set_title(MODELS[key][1], fontsize=11, fontweight="bold", pad=8)
            if row == 1:
                ax.set_xlabel("round")
            if col == 0:
                ax.set_ylabel(lab)
    axes[0, 0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("No reward-driven drift: the flawed reward behaves like the honest one (OLMo-2 rises in both: a context effect)",
                 fontsize=12, fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "One run per line, 10 rounds, 100 items per measurement (50 wrong).", ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(os.path.join(OUT, "fig5_pressure.png"), dpi=200); plt.close(fig)


# ------------------------------------------------------------------ fig 6: planted notes, who contaminates whom (six models)
def fig6():
    keys = ["qwen3", "qwen25", "phi", "olmo", "granite", "falcon"]
    ctx = [("none", "no notes"), ("E", "judge's\nplanted"), ("O", "solver's\nplanted"), ("C", "reviewer's\nplanted")]
    own = {"judge": "E", "reviewer": "C"}
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 6.4))
    for ax, key in zip(axes.flat, keys):
        d = load(os.path.join(RES, "contamination_planted", MODELS[key][0] + ".json"))
        M = np.array([[d[role][s]["on_wrong"] * 100 for s, _ in ctx] for role in ("judge", "reviewer")])
        bins = np.clip((M / 100 * 7).astype(int), 0, 6)
        for i in range(2):
            for j in range(4):
                ax.add_patch(Rectangle((j, 1 - i), 1, 1, facecolor=SEQ[bins[i, j]], edgecolor=SURFACE, lw=3))
                dark = bins[i, j] >= 3
                ax.text(j + 0.5, 1 - i + 0.55, f"{M[i, j]:.0f}%", ha="center", va="center", fontsize=12,
                        fontweight="bold", color="white" if dark else INK)
                delta = M[i, j] - M[i, 0]
                if j > 0 and abs(delta) >= 15:
                    ax.text(j + 0.5, 1 - i + 0.22, f"{delta:+.0f}", ha="center", va="center", fontsize=8.5,
                            color="white" if dark else INK2)
                if ctx[j][0] == own["judge" if i == 0 else "reviewer"]:
                    ax.text(j + 0.5, 1 - i + 0.90, "own", ha="center", va="center", fontsize=7.5,
                            color="white" if dark else INK2)
        ax.set_xlim(0, 4); ax.set_ylim(0, 2)
        ax.set_xticks([j + 0.5 for j in range(4)]); ax.set_xticklabels([c[1] for c in ctx], fontsize=8.5)
        ax.set_yticks([1.5, 0.5]); ax.set_yticklabels(["judge", "reviewer"], fontsize=9)
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(MODELS[key][1], fontsize=11, fontweight="bold", pad=6)
    fig.suptitle("A planted note travels between roles in some models: share of wrong answers accepted",
                 fontsize=12.5, fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "Each cell: % of wrong answers accepted by the row's role with the column's planted notes in its prompt "
             "(100 items, 50 wrong). Small number: change vs no notes, shown when 15 points or more.",
             ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(os.path.join(OUT, "fig6_planted_contamination.png"), dpi=200); plt.close(fig)



# ------------------------------------------------------------------ fig 7: planted judge fault, frozen vs learning (Qwen3-4B)
def fig7():
    mdir = MODELS["qwen3"][0]
    runs = [("clean judge, frozen", "honest_ev-OC_rf-score_sum2_s0", BLUE),
            ("clean judge, learning", "honest_ev-EOC_rf-score_sum2_s0", AQUA),
            ("lenient judge, frozen", "honest_ev-OC_seed-E8_rf-score_sum2_s0", ORANGE),
            ("lenient judge, learning", "honest_ev-EOC_seed-E8_rf-score_sum2_s0", YELLOW)]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), sharey=True)
    for ax, (metric, title) in zip(axes, [("judge_far", "Judge passes wrong answers"), ("review_far", "Reviewer approves wrong answers")]):
        clean_axes(ax)
        ends = []
        for label, name, color in runs:
            d = load(os.path.join(RES, mdir, name + ".json"))
            sr = series(d, metric)
            ax.plot([r for r, _ in sr], [v * 100 for _, v in sr], color=color, lw=2, marker="o", ms=6, mec=SURFACE, mew=1.3, zorder=3)
            ends.append([sr[-1][1] * 100, label])
        ends.sort()
        for k in range(1, len(ends)):
            ends[k][0] = max(ends[k][0], ends[k - 1][0] + 6)
        for ypos, label in ends:
            ax.text(10.25, ypos, label, va="center", fontsize=8.5, color=INK)
        ax.set_xlim(-0.3, 10.3); ax.set_xticks([0, 2, 4, 6, 8, 10]); ax.set_xlabel("round")
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    axes[0].set_ylabel("% of wrong answers accepted")
    fig.suptitle("Qwen3-4B: a planted lenient judge heals itself and does not drag the reviewer along",
                 fontsize=12, fontweight="bold", y=1.0)
    fig.tight_layout(rect=(0, 0, 0.93, 0.94))
    fig.savefig(os.path.join(OUT, "fig7_seed_heal.png"), dpi=200); plt.close(fig)



# ------------------------------------------------------------------ fig 8: shared notebook minus private notes, four models
def fig8():
    models = ["olmo", "granite", "phi", "qwen3"]
    conds = [("clean judge", "honest_ev-OC_rf-score_sum2", BLUE), ("lenient-seeded judge", "honest_ev-OC_seed-E8_rf-score_sum2", ORANGE)]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4), sharey=True)
    for ax, (metric, title) in zip(axes, [("judge_far", "Judge passes wrong answers"), ("review_far", "Reviewer approves wrong answers")]):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0); ax.set_axisbelow(True)
        ax.axhline(0, color=AXIS, lw=1.2, zorder=1)
        ax.axhline(15, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
        ax.text(3.62, 16.5, "+15 threshold", ha="right", va="bottom", fontsize=8, color=MUTED)
        for mi, key in enumerate(models):
            mdir, mname = MODELS[key]
            for ci, (clabel, base, color) in enumerate(conds):
                diffs = []
                for sd in range(3):
                    fp = os.path.join(RES, mdir, f"{base}_s{sd}.json"); ft = os.path.join(RES, mdir, f"{base}_shr-team_s{sd}.json")
                    if os.path.exists(fp) and os.path.exists(ft):
                        dp, dt = load(fp), load(ft)
                        if dp["complete"] and dt["complete"]:
                            diffs.append((last2(dt, metric) - last2(dp, metric)) * 100)
                diffs = np.array(diffs)
                x = mi + (ci - 0.5) * 0.36
                ax.bar(x, diffs.mean(), width=0.30, color=color, zorder=2, label=clabel if mi == 0 else None)
                ax.scatter([x] * len(diffs), diffs, s=22, color="white", edgecolor=INK2, linewidth=1.0, zorder=3)
                ax.text(x, (diffs.max() + 2.5) if diffs.mean() >= 0 else (diffs.min() - 2.5), f"{diffs.mean():+.0f}",
                        ha="center", va="bottom" if diffs.mean() >= 0 else "top", fontsize=9, color=INK)
        ax.set_xticks(range(len(models))); ax.set_xticklabels([MODELS[k][1] for k in models])
        ax.set_xlim(-0.6, 3.6); ax.set_ylim(-24, 46)
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    axes[0].set_ylabel("change with team notebook\n(percentage points)")
    axes[0].legend(frameon=False, loc="upper right", fontsize=9)
    fig.suptitle("Sharing notes spreads leniency in 3 of 4 models, along different paths", fontsize=12.5, fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "Team notebook minus private notes, honest reward, 10 rounds; bars: mean of 3 repeats (last two measurements), dots: individual repeats.",
             ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig8_share_delta.png"), dpi=200); plt.close(fig)



# ------------------------------------------------------------------ fig 9: mitigations, shared notebook with one link cut
def fig9():
    modes = [("private", "private notes", BLUE), ("team", "team notebook", ORANGE), ("stateless", "blind verifiers", AQUA),
             ("nosolver", "no solver notes", YELLOW), ("nojudge", "no judge notes", "#e87ba4")]
    base = {"clean": "honest_ev-OC_rf-score_sum2", "lenient": "honest_ev-OC_seed-E8_rf-score_sum2"}
    panels = [("phi", "clean", "judge_far", "Phi-4-mini: judge passes wrong answers"),
              ("granite", "lenient", "review_far", "Granite-3.3-8B: reviewer approves wrong answers (lenient judge)"),
              ("olmo", "clean", "judge_far", "OLMo-2-7B: judge passes wrong answers"),
              ("olmo", "lenient", "review_far", "OLMo-2-7B: reviewer approves wrong answers (lenient judge)")]
    fig, axes = plt.subplots(2, 2, figsize=(11.6, 7.4), sharey=True)
    for ax, (key, cond, metric, title) in zip(axes.flat, panels):
        clean_axes(ax)
        mdir = MODELS[key][0]
        for i, (mode, label, color) in enumerate(modes):
            name = base[cond] if mode == "private" else base[cond] + "_shr-" + mode
            vals = []
            for sd in range(3):
                fp = os.path.join(RES, mdir, name + "_s" + str(sd) + ".json")
                if os.path.exists(fp):
                    d = load(fp)
                    if d["complete"]:
                        vals.append(last2(d, metric) * 100)
            vals = np.array(vals)
            ax.bar(i, vals.mean(), width=0.62, color=color, zorder=2)
            ax.scatter([i] * len(vals), vals, s=20, color="white", edgecolor=INK2, linewidth=1.0, zorder=3)
            ax.text(i, min(vals.max() + 3, 96), "%.0f" % vals.mean(), ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.set_xticks(range(len(modes)))
        ax.set_xticklabels([m[1] for m in modes], fontsize=8.5, rotation=14, ha="right")
        ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("% of wrong answers accepted")
    fig.suptitle("Cutting the notebook link: blind verifiers fix every case, targeted filters fix only the model's own path",
                 fontsize=12, fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "Honest reward, 10 rounds; bars: mean of 3 repeats (last two measurements); dots: individual repeats.",
             ha="center", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.025, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig9_mitigation.png"), dpi=200); plt.close(fig)



if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9):
        try:
            fn()
            print("ok", fn.__name__)
        except Exception as e:              # keep going so one missing result does not block the rest
            print("FAILED", fn.__name__, repr(e))
    print("figures in", OUT)
