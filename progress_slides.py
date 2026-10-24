# -*- coding: utf-8 -*-
"""PART VII - progress report slides. Executed inside build_ppt.py (shares its helpers and palette)."""
from PIL import Image

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coupled_misevolution", "figures", "paper")
SOFT = RGBColor(0xEC, 0xEF, 0xFB)      # light indigo panel


def pic(s, name, l, t, mw, mh):
    """Place a figure inside the box (l, t, mw, mh), keeping its aspect ratio, centred."""
    path = os.path.join(PROG, name)
    w, h = Image.open(path).size
    sc = min(mw / w, mh / h)
    pw, ph = int(w * sc), int(h * sc)
    s.shapes.add_picture(path, int(l + (mw - pw) / 2), int(t + (mh - ph) / 2), width=pw, height=ph)


def bar(s, text, y=Inches(6.3), h=Inches(0.72), color=NAVY, size=12):
    rect(s, Inches(0.6), y, Inches(12.1), h, color)
    txt(s, Inches(0.85), y, Inches(11.6), h,
        [{"text": text, "size": size, "italic": True, "color": WHITE}], anchor=MSO_ANCHOR.MIDDLE)


def tag(s, l, t, w, text, color, size=11):
    r = rect(s, l, t, w, Inches(0.34), color)
    txt(s, l, t, w, Inches(0.34), [{"text": text, "size": size, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}],
        anchor=MSO_ANCHOR.MIDDLE)


# ================================================================== divider
divider("Progress Report",
        "Does misevolution spread between the roles of a team?  Controlled experiments on six open models, run on the IITJ HPC cluster",
        0, ACC, "PART VII")

# ================================================================== summary
s = slide()
header(s, "Progress report · summary", "Where the project stands: 23 October 2026", ACC)
rect(s, Inches(0.6), Inches(1.75), Inches(5.7), Inches(4.4), LIGHT); rect(s, Inches(0.6), Inches(1.75), Inches(0.09), Inches(4.4), ACC)
txt(s, Inches(0.9), Inches(1.88), Inches(5.2), Inches(0.35), [{"text": "WHAT HAS BEEN DONE", "size": 12.5, "bold": True, "color": ACC}])
bullets(s, Inches(0.9), Inches(2.3), Inches(5.2), Inches(3.8), [
    ("A closed-loop testbed: a Worker solves maths problems, a Reviewer approves them, a Judge grades them. Each writes its own notes after every round", 0),
    ("94 closed-loop experiments (10 rounds each, about 188,000 model calls) and 21 static tests on 6 open models: Qwen3-4B, Qwen2.5-7B, Phi-4-mini, OLMo-2-7B, Granite-3.3-8B, Falcon3-7B", 0),
    ("About 56 GPU-hours on the IITJ cluster (A30 GPUs, SLURM jobs)", 0),
    ("Free APIs, Ollama and vLLM all failed on the cluster's older GPU driver; a PyTorch (CUDA 12.1) backend with request batching works", 0),
    ("Predictions are written into PLAN.md before each new test", 0)],
    size=12.5, gap=8, dot=ACC)
txt(s, Inches(6.6), Inches(1.75), Inches(6.1), Inches(0.35), [{"text": "HEADLINE FINDINGS", "size": 12.5, "bold": True, "color": ACC}])
finds = [("No reward-driven drift.", "A flawed reward behaves like an honest one in all 3 models tested over 10 rounds."),
         ("A safeguard erodes silently.", "Planted notes remove the worker's verification step in 5 of 6 models while its accuracy barely moves."),
         ("Shared notes spread leniency between roles in 3 of 4 models.", "OLMo-2, Granite and Phi-4-mini: yes, by different paths. Qwen3-4B: no (3 repeats each)."),
         ("Cutting the link protects the verifiers.", "Blind verifiers restore every case (OLMo-2 judge 63% → 31%, Granite reviewer 49% → 30%). Private notes also protect the worker.")]
yy = Inches(2.15)
for i, (a, b) in enumerate(finds):
    rect(s, Inches(6.6), yy, Inches(0.5), Inches(0.92), ACC)
    txt(s, Inches(6.6), yy, Inches(0.5), Inches(0.92), [{"text": str(i + 1), "size": 18, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
    rect(s, Inches(7.1), yy, Inches(5.6), Inches(0.92), SOFT)
    txt(s, Inches(7.3), yy + Inches(0.07), Inches(5.3), Inches(0.85),
        [{"text": a, "size": 13, "bold": True, "color": NAVY}, {"text": b, "size": 11.5, "color": INK, "space_before": 2}])
    yy += Inches(1.0)
tag(s, Inches(0.6), Inches(6.3), Inches(1.9), "PREDICTIONS MET", GREENOK)
txt(s, Inches(2.65), Inches(6.27), Inches(10.05), Inches(0.7),
    [{"text": "Written before the runs: Granite needed at least +15 points and got +21; Phi-4-mini needed at least +15 and got +15, exactly at the threshold.",
      "size": 12.5, "color": INK}], anchor=MSO_ANCHOR.MIDDLE)
pagenum(s)

# ================================================================== the question
s = slide()
header(s, "The research question", "What was already known, and what is still open", ACC)
card(s, Inches(0.6), Inches(1.75), Inches(5.9), Inches(3.0), "ALREADY PUBLISHED, EACH ON ITS OWN", [
    "A judge turns lenient when it sees earlier context (arXiv 2608.16003)",
    "Agents collude over long horizons (2609.24967)",
    "Agents drift from their goal under pressure (2505.02709, 2609.09090)",
    "Bias travels one way through memory to later agents (2606.23195, 2610.04083)"], C_MODEL)
card(s, Inches(6.8), Inches(1.75), Inches(5.9), Inches(3.0), "OUR QUESTION", [
    "Put the three layers (Evaluation, Objective, Collaboration) into ONE closed loop",
    "Does drift appear on its own, with no planted fault?",
    "If a fault is planted in one layer, does it spread to the others, and through which channel?",
    "Which single link, when cut, stops it?"], ACC)
rect(s, Inches(0.6), Inches(4.95), Inches(12.1), Inches(0.8), SOFT); rect(s, Inches(0.6), Inches(4.95), Inches(0.09), Inches(0.8), ACC)
txt(s, Inches(0.9), Inches(4.95), Inches(11.6), Inches(0.8),
    [{"text": "THE GAP: to my knowledge nobody has tested whether these failures infect one another inside one self-evolving loop, "
              "or which link to cut to stop it.", "size": 13.5, "bold": True, "color": NAVY}], anchor=MSO_ANCHOR.MIDDLE)
bar(s, "Why the design changed: my earlier demos (Part VI) wrote the biased memory myself, so a reviewer could say 'you told it to'. "
       "Now the agents write their own memory, and every test has an honest-reward control.", y=Inches(5.95), h=Inches(0.95), size=13)
pagenum(s)

# ================================================================== testbed
s = slide()
header(s, "The testbed", "A Worker, a Reviewer and a Judge that learn from their own scores", ACC)
roles = [("WORKER", "Objective layer", "solves the problem and must include a 'Check:' step", C_MEM),
         ("REVIEWER", "Collaboration layer", "approves or rejects the solution before it ships", C_TOOL),
         ("JUDGE", "Evaluation layer", "grades what shipped: PASS or FAIL", C_MODEL)]
x = Inches(0.6)
for i, (n, layer, duty, c) in enumerate(roles):
    rect(s, x, Inches(1.75), Inches(3.45), Inches(1.25), c)
    txt(s, x + Inches(0.2), Inches(1.82), Inches(3.1), Inches(1.15),
        [{"text": n + "   ·   " + layer, "size": 12.5, "bold": True, "color": WHITE},
         {"text": duty, "size": 12, "color": WHITE, "space_before": 4}])
    if i < 2:
        txt(s, x + Inches(3.48), Inches(2.15), Inches(0.5), Inches(0.5), [{"text": "→", "size": 26, "bold": True, "color": NAVY, "align": PP_ALIGN.CENTER}])
    x += Inches(3.325) + Inches(0.55) if False else Inches(4.3)
rect(s, Inches(0.6), Inches(3.15), Inches(12.1), Inches(0.62), SOFT)
txt(s, Inches(0.8), Inches(3.15), Inches(11.7), Inches(0.62),
    [{"text": "NOTES: after each round every agent reads its own scores and writes up to 3 lessons into its memory.  Private: each sees only its own notes.  Shared: one team notebook that all can read.",
      "size": 12, "color": INK}], anchor=MSO_ANCHOR.MIDDLE)
rect(s, Inches(0.6), Inches(3.87), Inches(12.1), Inches(0.62), SOFT)
txt(s, Inches(0.8), Inches(3.87), Inches(11.7), Inches(0.62),
    [{"text": "REWARD:  flawed = users like PASS grades and short answers, blocking work is penalised.   honest = the judge is paid only for accurate grades.",
      "size": 12, "color": INK}], anchor=MSO_ANCHOR.MIDDLE)
card(s, Inches(0.6), Inches(4.65), Inches(5.9), Inches(2.35), "WHAT IS MEASURED (fixed test items)", [
    "Judge: % of wrong solutions it passes",
    "Reviewer: % of wrong solutions it approves",
    "Worker: % of answers that keep the 'Check:' step",
    "Also: pass rate on correct solutions, worker accuracy"], ACC)
card(s, Inches(6.8), Inches(4.65), Inches(5.9), Inches(2.35), "DATA AND SETUP", [
    "GSM8K maths; wrong solutions carry one arithmetic slip; correctness is checked by code and never shown to agents",
    "Per round: 8 worker tasks + 8 backup submissions (half wrong); 10 rounds",
    "Test items: 100 for judge, 100 for reviewer (50 wrong each), 30 worker questions"], C_MEM)
pagenum(s)

# ================================================================== experiments at a glance
s = slide()
header(s, "The experiments", "Seven experiments, each isolating one question", ACC)
cols = ["Experiment", "Question", "Setup", "Status"]
rows = [("1 · Spontaneous drift", "Does a flawed reward make agents drift on their own?", "Flawed vs honest reward, 10 rounds; Qwen3-4B, Phi-4-mini, OLMo-2-7B", "Done"),
        ("2 · Planted fault", "Does a lenient judge spread to the reviewer, or heal?", "8 lenient notes planted in the judge; private notes; Qwen3-4B", "Done"),
        ("3 · Susceptibility", "How far do planted notes push each role?", "8 planted notes per role; all 6 models", "Done"),
        ("4 · Context effect", "Do any notes in the prompt make verifiers lenient?", "No / harmless / irrelevant notes; all 6 models", "Done"),
        ("5 · Shared notebook", "Does sharing notes spread leniency inside the loop?", "Private vs shared notes × clean vs lenient judge, 3 repeats each; OLMo-2, Granite, Phi-4-mini, Qwen3-4B", "Done"),
        ("6 · Contamination matrices", "Which role's notes reach which role?", "Real and planted notes as context; 6 models, single pass", "Done"),
        ("7 · Mitigations", "Which link, when cut, stops the spread?", "Blind verifiers, no solver notes, no judge notes; Phi-4-mini, Granite, OLMo-2, 3 repeats", "Done")]
gt = s.shapes.add_table(len(rows) + 1, 4, Inches(0.6), Inches(1.8), Inches(12.1), Inches(0.6) * (len(rows) + 1)).table
for c, wd in enumerate([2.6, 3.9, 4.6, 1.0]):
    gt.columns[c].width = Inches(wd)
for c, ct in enumerate(cols):
    cell = gt.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = ACC
    r = cell.text_frame.paragraphs[0].add_run(); r.text = ct
    r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
for ri, row in enumerate(rows, 1):
    for c, val in enumerate(row):
        cell = gt.cell(ri, c); cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if ri % 2 else LIGHT
        r = cell.text_frame.paragraphs[0].add_run(); r.text = val
        r.font.size = Pt(11.5); r.font.name = FONT; r.font.color.rgb = INK
        if c == 0: r.font.bold = True; r.font.color.rgb = ACC
        if c == 3:
            r.font.bold = True; r.font.color.rgb = GREENOK if val == "Done" else AMBER
pagenum(s)

# ================================================================== result 1
s = slide()
header(s, "Result 1 · spontaneous drift", "A flawed reward does not make these agents drift", ACC)
pic(s, "fig5_pressure.png", Inches(0.45), Inches(1.7), Inches(8.2), Inches(4.5))
bullets(s, Inches(8.85), Inches(1.8), Inches(3.9), Inches(4.4), [
    ("Flawed reward (users like PASS and short answers) and honest reward give overlapping lines in Qwen3-4B and Phi-4-mini", 0),
    ("OLMo-2's judge rises from 31% to about 50% under both rewards. The honest control shows this is not reward hacking (Result 4)", 0),
    ("The agents' notes say 'double-check arithmetic': they read a low score as their own mistake, not as a hint to be lenient", 0),
    ("Why: the reviewer rejects most wrong answers, so the judge rarely meets a tempting case. The loop sits in a stable good state", 0)],
    size=12, gap=8, dot=ACC)
bar(s, "10 rounds, 100 items per measurement (50 wrong), one run per line. Qwen3-4B is measured every round, the other two every second round.", y=Inches(6.4), h=Inches(0.6))
pagenum(s)

# ================================================================== result 2
s = slide()
header(s, "Result 2 · a planted fault", "A planted lenient judge does not spread through private notes, and it heals", ACC)
bullets(s, Inches(0.6), Inches(1.85), Inches(4.6), Inches(3.4), [
    ("Eight lenient notes planted in the judge: it passes 37% of wrong answers (clean: 14%) and still accepts 96% of correct ones", 0),
    ("Judge frozen: the reviewer stays near the clean level (12% vs 8%, within noise on 50 items)", 0),
    ("Judge allowed to learn under the honest reward: it repairs itself in about 6 rounds", 0),
    ("An accurate reward heals a planted judge fault; the 'recompute before you answer' step also anchors these models", 0)],
    size=12.5, gap=9, dot=ACC)
pic(s, "fig7_seed_heal.png", Inches(5.4), Inches(1.75), Inches(7.4), Inches(3.4))
stats = [("37%", "of wrong answers passed by the judge with the planted notes (clean: 14%)", REDBAD),
         ("12% vs 8%", "reviewer approves wrong answers: lenient frozen judge vs clean judge (noise)", ACC),
         ("43% → 16%", "judge's pass rate on wrong answers after 2 and after 10 rounds of learning", GREENOK)]
x = Inches(0.6)
for big, small, col in stats:
    rect(s, x, Inches(5.3), Inches(3.95), Inches(0.95), LIGHT); rect(s, x, Inches(5.3), Inches(0.09), Inches(0.95), col)
    txt(s, x + Inches(0.2), Inches(5.3), Inches(1.55), Inches(0.95), [{"text": big, "size": 21, "bold": True, "color": col, "font": FONTL}], anchor=MSO_ANCHOR.MIDDLE)
    txt(s, x + Inches(1.8), Inches(5.3), Inches(2.05), Inches(0.95), [{"text": small, "size": 10.5, "color": INK}], anchor=MSO_ANCHOR.MIDDLE)
    x += Inches(3.95) + Inches(0.125)
bar(s, "Qwen3-4B, honest reward, 10 rounds, one run per line. An earlier seed of 4 notes was too weak to make the judge lenient and was discarded.", y=Inches(6.4), h=Inches(0.6))
pagenum(s)

# ================================================================== result 3
s = slide()
header(s, "Result 3 · susceptibility to planted notes", "A planted note erases the worker's verification step in 5 of 6 models", ACC)
pic(s, "fig3_susceptibility.png", Inches(0.5), Inches(1.65), Inches(12.3), Inches(3.45))
cw = Inches(3.95)
card(s, Inches(0.6), Inches(5.2), cw, Inches(1.8), "Worker's Check: step", [
    "Kept in 87–100% of answers when clean, 0–43% with planted notes",
    "Falcon3-7B is the exception: 97%"], C_TOOL)
card(s, Inches(0.6) + cw + Inches(0.12), Inches(5.2), cw, Inches(1.8), "The erosion is silent", [
    "Accuracy barely moves (Qwen3: 93% → 87%)",
    "A safeguard disappears with almost no visible loss"], C_MEM)
card(s, Inches(0.6) + 2 * (cw + Inches(0.12)), Inches(5.2), cw, Inches(1.8), "Judge and reviewer", [
    "Anchored in the Qwen models",
    "Strongly pushed in OLMo-2 (judge 31 → 76%) and Granite (reviewer 34 → 68%)"], C_MODEL)
pagenum(s)

# ================================================================== result 4
s = slide()
header(s, "Result 4 · notes in the prompt", "Only one model gets more lenient from notes of any kind", ACC)
pic(s, "fig4_context.png", Inches(0.45), Inches(1.75), Inches(8.0), Inches(3.9))
bullets(s, Inches(8.65), Inches(1.85), Inches(4.1), Inches(4.3), [
    ("OLMo-2 (1 of 6 models): judge 31 → 54% and reviewer 54 → 71% with six harmless notes", 0),
    ("Six irrelevant office-chat notes do it too (judge 48%, reviewer 70%): it is the presence of notes, not their content", 0),
    ("Qwen3, Qwen2.5, Phi-4-mini, Granite, Falcon3: flat or slightly stricter", 0),
    ("Matches arXiv 2608.16003 (prior context shifts verifiers toward leniency), here for some models only", 0),
    ("Consequence: keep unrelated history out of verifier prompts", 0)],
    size=12, gap=7, dot=ACC)
bar(s, "100 items per cell (50 wrong), greedy decoding. The harmless notes are the ones OLMo-2's own judge wrote.", y=Inches(6.0), h=Inches(0.6))
pagenum(s)

# ================================================================== result 5
s = slide()
header(s, "Result 5 · the shared notebook", "A shared notebook spreads leniency in 3 of 4 models", ACC)
pic(s, "fig8_share_delta.png", Inches(0.4), Inches(1.75), Inches(7.7), Inches(3.5))
bullets(s, Inches(8.3), Inches(1.8), Inches(4.45), Inches(3.6), [
    ("OLMo-2: a judge with no notes of its own passes 31% of wrong answers, and 63% once it can read its teammates' notes (+33 points)", 0),
    ("Granite: the judge's planted lenient notes reach the reviewer (+21 points); with a clean judge only +8", 0),
    ("Phi-4-mini: the judge passes 15 points more wrong answers (mechanism untested)", 0),
    ("Qwen3-4B: no spreading; the judge even gets stricter (−7, −14)", 0),
    ("With private notes the same models stay at their clean level", 0)],
    size=11.5, gap=6, dot=ACC)
rect(s, Inches(0.6), Inches(5.4), Inches(12.1), Inches(0.95), RGBColor(0xE3, 0xF1, 0xE9)); rect(s, Inches(0.6), Inches(5.4), Inches(0.09), Inches(0.95), GREENOK)
txt(s, Inches(0.9), Inches(5.4), Inches(11.6), Inches(0.95),
    [{"text": "PREDICTIONS CHECKED · written before the runs", "size": 11.5, "bold": True, "color": GREENOK},
     {"text": "Granite needed at least +15 and got +21 (per repeat +12, +26, +27). Phi-4-mini needed at least +15 and got +15 (per repeat +12, +18, +15): met, but exactly at the threshold.",
      "size": 12, "color": INK, "space_before": 2}], anchor=MSO_ANCHOR.MIDDLE)
bar(s, "Honest reward, 10 rounds, 3 repeats per model, bars = mean of the last two measurements. In OLMo-2 the planted lenient message adds nothing beyond the presence of notes.",
    y=Inches(6.45), h=Inches(0.58), size=11)
pagenum(s)

# ================================================================== result 6
s = slide()
header(s, "Result 6 · who contaminates whom", "Content crosses between roles in 4 of 6 models, along different paths", ACC)
pic(s, "fig6_planted_contamination.png", Inches(0.35), Inches(1.65), Inches(8.8), Inches(4.75))
bullets(s, Inches(9.3), Inches(1.8), Inches(3.45), Inches(4.4), [
    ("Phi-4-mini: the solver's notes push the judge (32 → 70%)", 0),
    ("Granite: the judge's lenient notes push the reviewer (30 → 55%)", 0),
    ("OLMo-2: every role's notes reach both verifiers (+16 to +47 points)", 0),
    ("Qwen3-4B: only the judge's own planted notes matter (+24)", 0),
    ("Qwen2.5-7B and Falcon3-7B: no change of 15 points or more", 0),
    ("Loop check (Result 5): the Granite and Phi-4-mini paths carry into the loop (+21 and +15 points)", 0)],
    size=11.5, gap=5, dot=ACC)
txt(s, Inches(9.3), Inches(6.0), Inches(3.45), Inches(0.8),
    [{"text": "Single pass, 100 items per cell. A difference has a standard error of about 9 points, so only changes of 15 or more are counted.",
      "size": 10.5, "italic": True, "color": GRAY}])
pagenum(s)

# ================================================================== result 7
s = slide()
header(s, "Result 7 · fixes", "Blind verifiers fix every verifier case; targeted filters fix only the model's own path", ACC)
pic(s, "fig9_mitigation.png", Inches(0.35), Inches(1.65), Inches(7.9), Inches(4.7))
bullets(s, Inches(8.4), Inches(1.8), Inches(4.35), Inches(4.5), [
    ("Blind verifiers (no notes for judge and reviewer) bring all four cases back to the private-notes level or below: Phi 45 → 30, Granite 49 → 30, OLMo-2 judge 63 → 31, OLMo-2 reviewer 78 → 54", 0),
    ("No solver notes for the verifiers fixes Phi-4-mini (45 → 34) but not Granite, and only part of OLMo-2 (63 → 52)", 0),
    ("No judge notes for the reviewer fixes Granite (49 → 32) but not OLMo-2's reviewer (72)", 0),
    ("Blind verifiers lose no throughput (correct answers still ship 95–99%), but they do not protect the worker: Granite's worker falls from 72% to 38–44% accuracy when it reads the judge's planted notes. Private notes fix both", 0),
    ("8 of 10 written predictions met; the 2 misses were 'not cut' bounds missed by 1–3 points", 0)],
    size=11.5, gap=6, dot=ACC)
bar(s, "Honest reward, 10 rounds, 3 repeats. Caveat: in the loop the verifiers approve about 90% of the worker's own wrong answers in every setup; the bars measure leniency on planted slips.",
    y=Inches(6.4), h=Inches(0.6), size=11.5)
pagenum(s)

# ================================================================== claims
s = slide()
header(s, "What the data support", "Claims, non-claims and open questions", ACC)
colw = Inches(3.95)
spec = [("SUPPORTED", GREENOK, [
            "Planted notes erase the worker's verification step in 5 of 6 models",
            "Shared notes spread leniency to the verifiers in 3 of 4 models (OLMo-2, Granite, Phi-4-mini; 3 repeats each), not in Qwen3-4B",
            "Note content crosses roles in 4 of 6 models (single pass)",
            "An honest reward heals a planted judge fault (Qwen3-4B, 1 run)",
            "Blind verifiers remove the spread in all four cases without losing throughput, but not the worker's contamination (Granite worker 72% → 38–44%); private notes do"]),
        ("NOT SUPPORTED", REDBAD, [
            "A flawed reward alone causes drift (none in 3 models)",
            "A planted lenient message spreads beyond the generic effect of notes",
            "The Part VI percentages as evidence of spontaneous drift: they used memory I wrote myself"]),
        ("OPEN", AMBER, [
            "Why the channel differs by model (context vs content); Phi-4-mini's mechanism is still a guess",
            "Other reward designs, tasks beyond maths, models above 8B, longer horizons",
            "Why verifiers miss about 90% of the worker's own errors in every setup",
            "A human audit of the agents' written lessons"])]
for i, (title, col, items) in enumerate(spec):
    x = Inches(0.6) + i * (colw + Inches(0.125))
    rect(s, x, Inches(1.75), colw, Inches(3.95), LIGHT)
    tag(s, x, Inches(1.75), colw, title, col, 12)
    bullets(s, x + Inches(0.2), Inches(2.25), colw - Inches(0.4), Inches(3.4), [(t, 0) for t in items], size=12, gap=8, dot=col)
bar(s, "Limits: models of 4–8 billion parameters; one task (grade-school maths); one flawed-reward design; 50 wrong items per measurement (about ±7 points); "
       "contamination matrices are single passes; the probes use planted slips, which verifiers catch far more often than the worker's own errors.", y=Inches(5.85), h=Inches(1.05), size=12)
pagenum(s)

# ================================================================== paper framing
s = slide()
header(s, "From results to a paper", "What the paper now says", ACC)
rect(s, Inches(0.6), Inches(1.75), Inches(12.1), Inches(0.85), SOFT)
txt(s, Inches(0.85), Inches(1.75), Inches(11.6), Inches(0.85),
    [{"text": "WORKING TITLE", "size": 10.5, "bold": True, "color": ACC},
     {"text": "Where does misevolution spread? Shared memory as a contagion channel in self-evolving agent teams", "size": 15.5, "bold": True, "color": NAVY, "space_before": 2}],
    anchor=MSO_ANCHOR.MIDDLE)
contribs = [("A closed-loop testbed", "Worker, Reviewer and Judge with agent-written memory, honest-reward controls and fixed test items", C_MEM),
            ("A susceptibility profile of six open models", "Which role erodes first, and in which model", C_MODEL),
            ("Shared memory as a contagion channel", "Seen in 3 of 4 models in the loop, absent in the fourth; blind verifiers remove it", ACC),
            ("A controlled negative result", "A flawed reward alone does not drive drift in these models over 10 rounds", C_TOOL)]
yy = Inches(2.8)
for i, (t, d, c) in enumerate(contribs):
    rect(s, Inches(0.6), yy, Inches(0.5), Inches(0.72), c)
    txt(s, Inches(0.6), yy, Inches(0.5), Inches(0.72), [{"text": str(i + 1), "size": 17, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
    rect(s, Inches(1.1), yy, Inches(6.6), Inches(0.72), LIGHT)
    txt(s, Inches(1.3), yy + Inches(0.05), Inches(6.3), Inches(0.68),
        [{"text": t, "size": 13.5, "bold": True, "color": c}, {"text": d, "size": 11, "color": INK, "space_before": 1}])
    yy += Inches(0.8)
card(s, Inches(7.95), Inches(2.8), Inches(4.75), Inches(3.15), "MITIGATIONS TESTED", [
    "Blind verifiers: fix all four verifier cases, no loss of throughput",
    "Targeted filters: fix only the model's own path",
    "Private notes: also protect the worker (Granite worker 72% vs 40%)",
    "Open: verifiers miss about 90% of the worker's own errors"], C_FLOW)
pagenum(s)

# ================================================================== next steps
s = slide()
header(s, "Next steps and timeline", "What happens until submission", ACC)
steps = [("Now – 31 Oct", "Write the paper's method and results sections; test why verifiers miss the worker's own errors; repeat the contamination tests with notes from other seeds"),
         ("1 – 15 Nov", "Add one more model family to the shared-notebook and mitigation grids; human validation of the note labels"),
         ("16 – 30 Nov", "Human audit of about 100 agent-written lessons; one more model family; bootstrap confidence intervals on every headline number"),
         ("December", "Write the paper; prepare an anonymous code release"),
         ("January", "Supervisor review, then submit (ICML 2027, deadline expected late January, date to be confirmed). Backups: ACL Rolling Review, an ICLR 2027 workshop")]
yy = Inches(1.8)
for lab, d in steps:
    rect(s, Inches(0.6), yy, Inches(1.55), Inches(0.82), ACC)
    txt(s, Inches(0.6), yy, Inches(1.55), Inches(0.82), [{"text": lab, "size": 12.5, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
    rect(s, Inches(2.15), yy, Inches(10.55), Inches(0.82), LIGHT)
    txt(s, Inches(2.4), yy, Inches(10.1), Inches(0.82), [{"text": d, "size": 13.5, "color": INK}], anchor=MSO_ANCHOR.MIDDLE)
    yy += Inches(0.92)
pagenum(s)

# ================================================================== how the work was done
s = slide()
header(s, "How the work was done", "Obstacles along the way, and what makes the results reproducible", ACC)
card(s, Inches(0.6), Inches(1.75), Inches(5.9), Inches(4.4), "OBSTACLES AND HOW THEY WERE SOLVED", [
    "Free API tier: 50 requests a day, while one run needs about 400. Moved to open models run locally",
    "The cluster's driver (535, CUDA 12.2) is too old for current Ollama and vLLM, which silently fall back to the CPU. A PyTorch (CUDA 12.1) backend with request batching works",
    "Some nodes hand out 6 GB GPU slices. Jobs now exclude them and check the GPU size first",
    "Early pilots showed nothing happens unless wrong answers reach the judge. A backup solver now supplies them"], C_TOOL)
card(s, Inches(6.8), Inches(1.75), Inches(5.9), Inches(4.4), "REPRODUCIBILITY", [
    "All code is in coupled_misevolution/: loop, prompts, model backends, analysis and the 7 figures, which regenerate from the saved results",
    "Fixed test items, seeds and prompts. Each result file keeps the configuration, per-round metrics, every agent's notes and per-item verdicts",
    "PLAN.md logs the hypotheses, predictions and every design change with dates",
    "Not yet pushed to GitHub (commit pending). Data: the GSM8K test split"], GREENOK)
bar(s, "Honest summary: the question has changed from 'does each layer drift' to 'does drift spread, and when'. The first answer is: not from a flawed reward alone, and only in some models through shared notes.",
    y=Inches(6.3), h=Inches(0.72), size=12.5)
pagenum(s)
