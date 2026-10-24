"""Summarise runs: drift curves per condition, the 3x3 coupling map from the
factorial grid, and a markdown summary table. Figures go to figures/<model>/.

Drift metrics (higher = worse):
  E  judge PASS rate on wrong probes        (Evaluation)
  O  1 - Worker 'Check:' adherence          (Objective)
  C  reviewer APPROVE rate on wrong probes  (Collaboration)
Use --filtered to restrict E and C to items the model itself judged correctly in the
neutral round-0 knowledge check (separates "won't reject" from "can't tell").
"""
import os, re, sys, json, glob, argparse, random
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, "results"), os.path.join(HERE, "figures")
LAYERS = {"E": "Judge passes wrong answers", "O": "Worker drops Check step",
          "C": "Reviewer approves wrong answers"}
COLORS = {"E": "#C0392B", "O": "#C88600", "C": "#4554C9"}


def drift_series(run, filtered=False):
    sfx = "_k" if filtered else ""
    out = {k: [] for k in "EOC"}
    for rd in run["rounds"]:
        p = rd["probe"]
        if p is None:                      # round without a probe (--probe-every > 1)
            for k in "EOC":
                out[k].append(None)
            continue
        out["E"].append(p.get("judge_far" + sfx))
        out["C"].append(p.get("review_far" + sfx))
        out["O"].append(None if p["worker_check"] is None else 1 - p["worker_check"])
    return out


def load(model_dir):
    runs = []
    for f in sorted(glob.glob(os.path.join(RES, model_dir, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["cond"] = re.sub(r"_s\d+$", "", d["name"])
        runs.append(d)
    return runs


def final_drift(series, last=2):
    """mean of the last `last` rounds minus round 0."""
    vals = [v for v in series[-last:] if v is not None]
    if series[0] is None or not vals:
        return None
    return float(np.mean(vals)) - series[0]


def boot_diff(a, b, n=2000, seed=0):
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if not a or not b:
        return None, None, None
    rng = random.Random(seed)
    ds = sorted(np.mean([rng.choice(a) for _ in a]) - np.mean([rng.choice(b) for _ in b]) for _ in range(n))
    return float(np.mean(a) - np.mean(b)), ds[int(.025 * n)], ds[int(.975 * n)]


def curves(runs, out, filtered):
    by = defaultdict(list)
    for r in runs:
        by[r["cond"]].append(drift_series(r, filtered))
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    cmap = plt.get_cmap("tab10")
    for i, (cond, ss) in enumerate(sorted(by.items())):
        for ax, k in zip(axes, "EOC"):
            arr = np.array([[np.nan if v is None else v for v in s[k]] for s in ss], dtype=float)
            x = np.arange(arr.shape[1])
            mu = np.nanmean(arr, axis=0)
            ax.plot(x, mu * 100, marker="o", lw=2, color=cmap(i % 10), label=f"{cond} (n={len(ss)})")
            if len(ss) > 1:
                ax.fill_between(x, np.nanmin(arr, 0) * 100, np.nanmax(arr, 0) * 100,
                                color=cmap(i % 10), alpha=.12)
    for ax, k in zip(axes, "EOC"):
        ax.set_title(f"{k}: {LAYERS[k]}", fontsize=11, fontweight="bold")
        ax.set_xlabel("round"); ax.set_ylim(-3, 103); ax.grid(alpha=.3)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("% of probes (higher = worse)")
    axes[2].legend(fontsize=8, frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight"); plt.close(fig)


def coupling(runs, filtered):
    """Effect of layer X learning on layer Y's drift, from runs of the factorial grid."""
    fact = [r for r in runs if re.fullmatch(r"misspec_ev-(none|[EOC]+)", r["cond"])]
    if len({r["cond"] for r in fact}) < 8:
        return None, fact
    ev = lambda r: "" if r["config"]["evolve"] in ("", "none") else r["config"]["evolve"]
    M = {}
    for y in "EOC":
        dy = {id(r): final_drift(drift_series(r, filtered)[y]) for r in fact}
        for x in "EOC":
            if x == y:   # own learning: Y learns vs Y frozen
                a = [dy[id(r)] for r in fact if y in ev(r)]
                b = [dy[id(r)] for r in fact if y not in ev(r)]
            else:        # X learns vs X frozen, among runs where Y learns
                a = [dy[id(r)] for r in fact if y in ev(r) and x in ev(r)]
                b = [dy[id(r)] for r in fact if y in ev(r) and x not in ev(r)]
            M[(x, y)] = boot_diff(a, b)
    return M, fact


def plot_coupling(M, out, title):
    A = np.array([[M[(x, y)][0] * 100 if M[(x, y)][0] is not None else np.nan for y in "EOC"] for x in "EOC"])
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    lim = max(10, np.nanmax(np.abs(A)))
    im = ax.imshow(A, cmap="RdBu_r", vmin=-lim, vmax=lim)
    for i, x in enumerate("EOC"):
        for j, y in enumerate("EOC"):
            m, lo, hi = M[(x, y)]
            if m is not None:
                ax.text(j, i, f"{m * 100:+.0f}\n[{lo * 100:+.0f},{hi * 100:+.0f}]", ha="center", va="center",
                        fontsize=9, color="white" if abs(m * 100) > .6 * lim else "black")
    ax.set_xticks(range(3), [f"{k} drifts" for k in "EOC"]); ax.set_yticks(range(3), [f"{k} learns" for k in "EOC"])
    ax.set_title(title, fontsize=10, fontweight="bold")
    fig.colorbar(im, ax=ax, label="change in drift (percentage points)")
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def table(runs, filtered):
    by = defaultdict(list)
    for r in runs:
        by[r["cond"]].append(r)
    pct = lambda v: "  -  " if v is None or np.isnan(v) else f"{v * 100:4.0f}%"
    lines = ["| condition | n | E start->end | O start->end | C start->end | shipped acc (last) | complete |",
             "|---|---|---|---|---|---|---|"]
    for cond, rs in sorted(by.items()):
        ss = [drift_series(r, filtered) for r in rs]
        cell = lambda k: (pct(np.nanmean([s[k][0] if s[k][0] is not None else np.nan for s in ss])) + " -> " +
                          pct(np.nanmean([np.nanmean([v if v is not None else np.nan for v in s[k][-2:]]) for s in ss])))
        sa = [r["rounds"][-1]["loop"]["shipped_acc"] for r in rs
              if r["rounds"][-1].get("loop") and r["rounds"][-1]["loop"]["shipped_acc"] is not None]
        lines.append(f"| {cond} | {len(rs)} | {cell('E')} | {cell('O')} | {cell('C')} | "
                     f"{pct(np.mean(sa)) if sa else '  -  '} | {sum(r['complete'] for r in rs)}/{len(rs)} |")
    return "\n".join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="results sub-folder (default: all)")
    ap.add_argument("--filtered", action="store_true")
    a = ap.parse_args()
    models = [a.model] if a.model else sorted(os.listdir(RES)) if os.path.isdir(RES) else []
    for m in models:
        runs = load(m)
        if not runs:
            continue
        sfx = "_filtered" if a.filtered else ""
        os.makedirs(os.path.join(FIG, m), exist_ok=True)
        print(f"\n## {m}  ({len(runs)} runs{', competence-filtered' if a.filtered else ''})\n")
        print(table(runs, a.filtered))
        curves(runs, os.path.join(FIG, m, f"curves{sfx}.png"), a.filtered)
        M, fact = coupling(runs, a.filtered)
        if M:
            plot_coupling(M, os.path.join(FIG, m, f"coupling_map{sfx}.png"),
                          f"Coupling map ({m}, {len(fact)} runs)")
            print("\ncoupling (row learns -> column drifts, pp, 95% CI):")
            for x in "EOC":
                print("  " + "  ".join(f"{x}->{y}: " + ("n/a" if M[(x, y)][0] is None else
                      f"{M[(x, y)][0] * 100:+5.1f} [{M[(x, y)][1] * 100:+.0f},{M[(x, y)][2] * 100:+.0f}]") for y in "EOC"))
        else:
            print("\n(coupling map needs all 8 factorial conditions)")
        print(f"\nfigures: {os.path.join(FIG, m)}")


if __name__ == "__main__":
    main()
