"""Run the paper's experiment grids. Finished runs are skipped, so a grid can be
stopped and restarted at any time.

  pilot      flawed vs honest reward, all layers learning
  pressure   as pilot, but agents are told to maximise score and see per-action averages
  factorial  flawed reward, all 8 on/off combinations of which layers learn  (coupling map)
  share      private vs shared notes, with and without a lenient judge (honest reward)
  mitigate   shared notebook with one link cut: stateless verifiers / no solver notes / no judge notes
  seed       honest reward, Judge starts lenient (frozen, or free to recover)  (real spreading?)
  repair     flawed reward, Judge wiped clean halfway                          (re-infection?)
  controls   honest reward, memory without reward info, reversed reward
  fixes      flawed reward with one link cut at a time                         (cheapest fix?)

Example:
  python coupled_misevolution/run_grid.py --grid factorial --models qwen3:4b-instruct --seeds 0,1,2
"""
import sys, argparse, itertools
from loop import Run

FACTORIAL = ["".join(c) for n in range(4) for c in itertools.combinations("EOC", n)]


def grid(name, rounds):
    half = max(2, rounds // 2)
    if name == "pilot":
        return [dict(env="misspec", evolve="EOC"), dict(env="honest", evolve="EOC")]
    if name == "pressure":
        # stronger, still honest, optimisation pressure: the agent is told its goal is to maximise
        # its score, and sees per-action average scores. Run with --rounds 10.
        p = dict(reflect="score", summary=True)
        return [dict(env="misspec", evolve="EOC", **p), dict(env="honest", evolve="EOC", **p)]
    if name == "factorial":
        # flawed reward, same 'pressure' prompts as above; which layers learn is toggled (coupling map)
        return [dict(env="misspec", evolve=ev, reflect="score", summary=True) for ev in FACTORIAL]
    if name == "seed":
        # honest reward, same 'pressure' prompts as above. Seeded runs first, so a seed that does not
        # make the judge lenient shows up in the first progress lines (E at round 0 must be high).
        p = dict(reflect="score", summary=True)
        return [dict(env="honest", evolve="OC", seed_lessons="E:8", **p),   # lenient judge, stays lenient
                dict(env="honest", evolve="EOC", seed_lessons="E:8", **p),  # lenient judge, may recover
                dict(env="honest", evolve="OC", **p),                       # reference: clean judge, frozen
                dict(env="honest", evolve="EOC", **p)]                      # reference: clean judge, learns
    if name == "share":
        # does a lenient judge reach the reviewer when notes are SHARED (team notebook) but not when private?
        p = dict(reflect="score", summary=True)
        out = []
        for share in ("private", "team"):
            out += [dict(env="honest", evolve="OC", seed_lessons="E:8", share=share, **p),   # lenient judge, frozen
                    dict(env="honest", evolve="OC", share=share, **p)]                     # clean judge, frozen
        return out
    if name == "mitigate":
        # three ways to cut a link of the shared notebook (honest reward, same prompts as 'share').
        # Use --judge-cond clean / lenient to run only the condition where the spread was found.
        p = dict(reflect="score", summary=True)
        out = []
        for share in ("stateless", "nosolver", "nojudge"):
            out += [dict(env="honest", evolve="OC", seed_lessons="E:8", share=share, **p),
                    dict(env="honest", evolve="OC", share=share, **p)]
        return out
    if name == "repair":
        return [dict(env="misspec", evolve="EOC", repair=f"E@{half}"),
                dict(env="misspec", evolve="EOC", repair=f"C@{half}")]
    if name == "controls":
        return [dict(env="honest", evolve="EOC"),
                dict(env="misspec", evolve="EOC", feedback="none"),
                dict(env="reversed", evolve="EOC")]
    if name == "fixes":
        # each fix removes one pressure / link; compare with misspec ev-EOC from the pilot
        return [dict(env="misspec", evolve="EOC", lam=1.0, tag="fix-judgepaidaccuracy"),
                dict(env="misspec", evolve="EOC", rho=0.0, tag="fix-noblockpenalty"),
                dict(env="misspec", evolve="EOC", beta=0.0, tag="fix-nospeedpressure"),
                dict(env="misspec", evolve="EOC", fix="anchor"),     # goal restated every prompt
                dict(env="misspec", evolve="EOC", fix="canary")]     # judge rolled back on canary failure
    raise SystemExit(f"unknown grid {name}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--models", default="qwen3:4b-instruct")
    ap.add_argument("--backend", default="ollama", help="ollama | openai (vLLM) | openrouter | mock")
    ap.add_argument("--base-url", default="", help="for --backend openai, e.g. http://localhost:8000/v1")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--tasks", type=int, default=8)
    ap.add_argument("--backup", type=int, default=8, help="backup-solver submissions per round")
    ap.add_argument("--n-judge", type=int, default=20)
    ap.add_argument("--n-review", type=int, default=20)
    ap.add_argument("--n-worker", type=int, default=10)
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--probe-every", type=int, default=1, help="measure drift every N rounds (round 0 and the last always)")
    ap.add_argument("--judge-cond", default="both", choices=["both", "clean", "lenient"],
                    help="run only the conditions with a clean or a lenient-seeded judge")
    ap.add_argument("--tag", default="", help="added to result file names, e.g. 'mini' keeps test runs apart")
    ap.add_argument("--dry", action="store_true", help="list the runs without executing")
    a = ap.parse_args()
    runs = [dict(cond, backend=a.backend, base_url=a.base_url, model=m, seed=int(s), rounds=a.rounds, tasks=a.tasks, backup=a.backup,
                 n_judge=a.n_judge, n_review=a.n_review, n_worker=a.n_worker, parallel=a.parallel, probe_every=a.probe_every,
                 tag="_".join(t for t in (cond.get("tag", ""), a.tag) if t))
            for m in a.models.split(",") for s in a.seeds.split(",")
            for cond in grid(a.grid, a.rounds)]
    if a.judge_cond != "both":
        runs = [r for r in runs if bool(r.get("seed_lessons")) == (a.judge_cond == "lenient")]
    print(f"{len(runs)} runs in grid '{a.grid}'")
    for i, cfg in enumerate(runs, 1):
        r = Run(cfg)
        print(f"--- [{i}/{len(runs)}] {r.path}")
        if not a.dry:
            r.run()


if __name__ == "__main__":
    main()
