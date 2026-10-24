# -*- coding: utf-8 -*-
"""Builds the BTP presentation: Misevolution paper + reproduction results."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import os
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "new_misevolutions", "figures")

# ---------------- palette ----------------
NAVY   = RGBColor(0x16, 0x21, 0x3E)
NAVY2  = RGBColor(0x22, 0x30, 0x55)
INK    = RGBColor(0x28, 0x2C, 0x35)
GRAY   = RGBColor(0x5A, 0x61, 0x6B)
LIGHT  = RGBColor(0xF4, 0xF5, 0xF7)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
CORAL  = RGBColor(0xE8, 0x5D, 0x4E)   # risk / paper accent
TEAL   = RGBColor(0x2A, 0x9D, 0x8F)   # reproduction / "mine"
GREENOK= RGBColor(0x2E, 0x7D, 0x5B)
REDBAD = RGBColor(0xC0, 0x39, 0x2B)
# pathway colors (consistent everywhere)
C_MODEL = RGBColor(0x4C, 0x72, 0xB0)
C_MEM   = RGBColor(0x2A, 0x9D, 0x8F)
C_TOOL  = RGBColor(0xDD, 0x88, 0x52)
C_FLOW  = RGBColor(0x81, 0x72, 0xB3)
ACC     = RGBColor(0x45, 0x54, 0xC9)   # indigo — "beyond the paper" / original-contribution accent
AMBER   = RGBColor(0xC8, 0x86, 0x00)   # warm accent for example callouts

FONT = "Calibri"
FONTL = "Calibri Light"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

def slide():
    return prs.slides.add_slide(BLANK)

def rect(s, l, t, w, h, fill, line=None):
    sp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp

def txt(s, l, t, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """lines: list of dicts {text,size,bold,color,font,space_after,bullet,level,italic}"""
    tb = s.shapes.add_textbox(l, t, w, h); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln.get("align", align)
        if ln.get("space_after") is not None: p.space_after = Pt(ln["space_after"])
        if ln.get("space_before") is not None: p.space_before = Pt(ln["space_before"])
        p.level = ln.get("level", 0)
        r = p.add_run(); r.text = ln["text"]
        f = r.font
        f.size = Pt(ln.get("size", 18)); f.bold = ln.get("bold", False)
        f.italic = ln.get("italic", False)
        f.name = ln.get("font", FONT)
        f.color.rgb = ln.get("color", INK)
    return tb

def bullets(s, l, t, w, h, items, size=18, color=INK, gap=8, dot=CORAL):
    """items: list of (text, level). level 0 uses a colored square bullet."""
    tb = s.shapes.add_textbox(l, t, w, h); tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, it in enumerate(items):
        if isinstance(it, tuple): text, lvl = it
        else: text, lvl = it, 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.level = lvl
        # bullet char
        pre = ("▪  " if lvl == 0 else "–  ")
        r0 = p.add_run(); r0.text = pre
        r0.font.name = FONT; r0.font.size = Pt(size)
        r0.font.color.rgb = dot if lvl == 0 else GRAY
        r0.font.bold = (lvl == 0)
        r = p.add_run(); r.text = text
        r.font.name = FONT; r.font.size = Pt(size - (1 if lvl else 0))
        r.font.color.rgb = color
    return tb

def header(s, kicker, title, accent=CORAL):
    rect(s, 0, 0, SW, Inches(0.14), accent)
    txt(s, Inches(0.6), Inches(0.34), Inches(11), Inches(0.35),
        [{"text": kicker.upper(), "size": 12.5, "bold": True, "color": accent, "font": FONT}])
    txt(s, Inches(0.6), Inches(0.66), Inches(12.1), Inches(0.9),
        [{"text": title, "size": 27, "bold": True, "color": NAVY, "font": FONTL}])
    ln = rect(s, Inches(0.62), Inches(1.5), Inches(1.1), Pt(3), accent)
    return

_page = 1
def pagenum(s, n=None):
    global _page
    _page += 1
    txt(s, Inches(12.4), Inches(7.05), Inches(0.8), Inches(0.3),
        [{"text": str(_page), "size": 11, "color": GRAY, "align": PP_ALIGN.RIGHT}])

def chip(s, l, t, w, text, color):
    r = rect(s, l, t, w, Inches(0.42), color)
    tf = r.text_frame; tf.word_wrap=True
    tf.margin_top=Pt(2); tf.margin_bottom=Pt(2)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = text
    run.font.size = Pt(13); run.font.bold = True; run.font.color.rgb = WHITE; run.font.name = FONT
    r.vertical_anchor = MSO_ANCHOR.MIDDLE
    return r

# card with title + body
def card(s, l, t, w, h, title, body, color):
    rect(s, l, t, w, h, LIGHT)
    rect(s, l, t, Inches(0.09), h, color)  # left stripe
    txt(s, l+Inches(0.28), t+Inches(0.16), w-Inches(0.45), Inches(0.5),
        [{"text": title, "size": 16, "bold": True, "color": color, "font": FONT}])
    bullets(s, l+Inches(0.28), t+Inches(0.62), w-Inches(0.5), h-Inches(0.7),
            body, size=13.5, gap=5, dot=color)

# ============================================================ 1 TITLE
s = slide()
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, 0, SW, Inches(0.22), CORAL)
rect(s, 0, SH-Inches(0.22), SW, Inches(0.22), TEAL)
txt(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(0.5),
    [{"text": "EMERGENT AI SAFETY  ·  ICLR 2026", "size": 14, "bold": True, "color": CORAL}])
txt(s, Inches(0.9), Inches(2.1), Inches(11.6), Inches(2.0),
    [{"text": "Your Agent May Misevolve", "size": 50, "bold": True, "color": WHITE, "font": FONTL},
     {"text": "Emergent Risks in Self-Evolving LLM Agents", "size": 26, "color": RGBColor(0xC7,0xD0,0xE0), "space_before": 6}])
txt(s, Inches(0.9), Inches(4.35), Inches(11.5), Inches(1.2),
    [{"text": "An in-depth walkthrough of the paper  +  a hands-on reproduction of all four", "size": 17, "color": RGBColor(0xD8,0xDE,0xEA)},
     {"text": "misevolution pathways using free, openly-accessible models", "size": 17, "color": RGBColor(0xD8,0xDE,0xEA), "space_before":2}])
rect(s, Inches(0.92), Inches(5.75), Inches(2.2), Pt(3), TEAL)
txt(s, Inches(0.9), Inches(5.95), Inches(11.5), Inches(1.05),
    [{"text": "B.Tech Project  ·  Paper study & empirical reproduction", "size": 14, "color": RGBColor(0x9A,0xA5,0xB8)},
     {"text": "github.com/Mayank471/Misevolutions", "size": 14, "bold": True, "color": TEAL, "space_before": 7}])

# ============================================================ 2 AGENDA
s = slide()
header(s, "Roadmap", "What this talk covers")
items = [
    ("Part I — Concepts", "What self-evolving agents are, what “misevolution” means, and why it is a new class of risk", CORAL),
    ("Part II — The four pathways", "Model, Memory, Tool, and Workflow: the mechanism behind each failure mode", C_MEM),
    ("Part III — Results from the paper", "Key quantitative findings the authors report for every pathway", C_MODEL),
    ("Part IV — My reproduction", "Re-running all four pathways with free models, and how the numbers compare", TEAL),
    ("Part V — Mitigations", "What helps against each pathway — and why every fix is only partial", C_FLOW),
    ("Part VI — Beyond the paper", "Two risks beyond the four: multi-agent co-evolution and systemic contagion between components", ACC),
    ("Part VII — Progress report", "Controlled experiments on a coupled Worker–Reviewer–Judge loop, six open models: what spreads, what does not, what is next", AMBER),
]
y = Inches(1.65)
for i,(t,d,c) in enumerate(items):
    rect(s, Inches(0.6), y, Inches(0.5), Inches(0.68), c)
    txt(s, Inches(0.6), y+Inches(0.1), Inches(0.5), Inches(0.5),
        [{"text": str(i+1), "size": 19, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}])
    rect(s, Inches(1.1), y, Inches(11.6), Inches(0.68), LIGHT)
    txt(s, Inches(1.35), y+Inches(0.06), Inches(11.1), Inches(0.62),
        [{"text": t, "size": 15.5, "bold": True, "color": NAVY},
         {"text": d, "size": 12, "color": GRAY, "space_before": 1}])
    y += Inches(0.77)
pagenum(s, 2)

# ============================================================ 3 SECTION I
def divider(title, subtitle, n, accent=CORAL, part="PART I"):
    s = slide()
    rect(s, 0, 0, SW, SH, NAVY)
    rect(s, Inches(0.9), Inches(2.7), Inches(1.6), Pt(4), accent)
    txt(s, Inches(0.9), Inches(2.05), Inches(11), Inches(0.5),
        [{"text": part, "size": 15, "bold": True, "color": accent}])
    txt(s, Inches(0.9), Inches(2.95), Inches(11.4), Inches(1.4),
        [{"text": title, "size": 40, "bold": True, "color": WHITE, "font": FONTL}])
    txt(s, Inches(0.92), Inches(4.4), Inches(11), Inches(1),
        [{"text": subtitle, "size": 18, "color": RGBColor(0xB9,0xC2,0xD4)}])
    pagenum(s, n)
    return s

divider("Understanding Misevolution", "What self-evolving agents are, and how their self-improvement can quietly go wrong", 3, CORAL, "PART I")

# ============================================================ 4 self-evolving agents
s = slide()
header(s, "Background", "What is a self-evolving agent?", C_MEM)
txt(s, Inches(0.6), Inches(1.75), Inches(12.1), Inches(0.9),
    [{"text": "Unlike a static LLM, a self-evolving agent keeps improving itself by interacting with its environment — it updates one or more of its own components using feedback from the tasks it performs.", "size": 16, "color": INK}])
paths = [("MODEL",  "Fine-tunes its own\nweights on self-\ngenerated data", C_MODEL),
         ("MEMORY", "Stores & retrieves\npast experience to\nguide new tasks", C_MEM),
         ("TOOL",   "Creates, reuses &\ningests new tools\n(e.g. MCP servers)", C_TOOL),
         ("WORKFLOW","Re-optimizes its own\nmulti-step / multi-\nagent pipeline", C_FLOW)]
x = Inches(0.6); w = Inches(2.95); gap = Inches(0.14)
for name, desc, col in paths:
    rect(s, x, Inches(2.9), w, Inches(1.9), col)
    txt(s, x, Inches(3.05), w, Inches(0.5),
        [{"text": name, "size": 18, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}])
    txt(s, x+Inches(0.15), Inches(3.6), w-Inches(0.3), Inches(1.1),
        [{"text": desc, "size": 13, "color": WHITE, "align": PP_ALIGN.CENTER}])
    x += w + gap
txt(s, Inches(0.6), Inches(5.15), Inches(12), Inches(0.9),
    [{"text": "θ = (Model, Memory, Tool, Workflow)   →   evolution function  θ′ = f(θ, τ, r)", "size": 16, "bold": True, "color": NAVY, "align": PP_ALIGN.CENTER, "font": FONT}])
bullets(s, Inches(0.6), Inches(5.75), Inches(12.1), Inches(1.4),
        ["Goal of the designer: pick f that maximises cumulative task performance over time",
         "Examples: Absolute-Zero (model), AgentNet / SE-Agent (memory), Alita (tool), AFlow (workflow)"],
        size=14, gap=5, dot=C_MEM)
pagenum(s, 4)

# ============================================================ 5 definition
s = slide()
header(s, "Definition", "Misevolution: when self-improvement backfires", CORAL)
rect(s, Inches(0.6), Inches(1.8), Inches(12.1), Inches(1.55), LIGHT)
rect(s, Inches(0.6), Inches(1.8), Inches(0.12), Inches(1.55), CORAL)
txt(s, Inches(0.95), Inches(2.0), Inches(11.5), Inches(1.3),
    [{"text": "“Misevolution is an emergent decay of safety or the emergence of new risks that arises from an agent’s own self-evolution — leading to undesirable or even harmful outcomes.”", "size": 19, "italic": True, "color": NAVY}])
txt(s, Inches(0.6), Inches(3.65), Inches(12), Inches(0.5),
    [{"text": "Three intuitive examples from the paper:", "size": 15, "bold": True, "color": INK}])
ex = [("Biased memory", "A service agent learns “refund → 5-star rating,” then hands out refunds nobody asked for", C_MEM),
      ("Insecure tool", "An agent ingests appealing-but-backdoored code and builds a tool that leaks SSH keys", C_TOOL),
      ("Careless reuse", "A general PII-scrubber tool is reused on medical data, missing re-identifiable fields", C_TOOL)]
x = Inches(0.6); w = Inches(3.95)
for t,d,c in ex:
    card(s, x, Inches(4.2), w, Inches(2.2), t, [d], c)
    x += w + Inches(0.13)
pagenum(s, 5)

# ============================================================ 6 four characteristics
s = slide()
header(s, "Why it's a NEW risk", "How misevolution differs from known LLM threats", CORAL)
four = [
    ("1  Temporal emergence", "Risk appears over time as components change — not in a static “snapshot” like jailbreak tests.", CORAL),
    ("2  Self-generated vulnerability", "The agent creates the risk itself, with no external attacker or curated bad data.", C_MODEL),
    ("3  Limited data control", "Autonomy means we can't inject safety data mid-training the way fine-tuning pipelines do.", C_TOOL),
    ("4  Expanded risk surface", "Any of the 4 evolving components can fail — and real-world tool use turns a flaw into real harm.", C_FLOW),
]
x = Inches(0.6); y = Inches(1.85); w = Inches(5.95); h = Inches(2.35)
for i,(t,d,c) in enumerate(four):
    cx = x + (w+Inches(0.2))*(i%2)
    cy = y + (h+Inches(0.2))*(i//2)
    rect(s, cx, cy, w, h, LIGHT)
    rect(s, cx, cy, w, Inches(0.09), c)
    txt(s, cx+Inches(0.3), cy+Inches(0.28), w-Inches(0.5), Inches(0.6),
        [{"text": t, "size": 18, "bold": True, "color": c}])
    txt(s, cx+Inches(0.3), cy+Inches(0.95), w-Inches(0.55), Inches(1.2),
        [{"text": d, "size": 15, "color": INK}])
txt(s, Inches(0.6), Inches(6.75), Inches(12), Inches(0.4),
    [{"text": "Contrast: emergent misalignment (Betley 2025) needs deliberate fine-tuning on insecure code; misevolution appears spontaneously.", "size": 12.5, "italic": True, "color": GRAY}])
pagenum(s, 6)

# ============================================================ 7 taxonomy
s = slide()
header(s, "The map", "Four evolutionary pathways — four ways to misevolve", C_MEM)
txt(s, Inches(0.6), Inches(1.7), Inches(12), Inches(0.5),
    [{"text": "The paper studies misevolution systematically along the same four components an agent can evolve:", "size": 15, "color": INK}])
rows = [("MODEL",  "via self-generated data / curriculum", "Safety alignment erodes as the model re-trains on its own outputs", C_MODEL),
        ("MEMORY", "via accumulation & retrieval", "Biased experience → reward hacking & loss of risk awareness", C_MEM),
        ("TOOL",   "via creation-reuse & ingesting external tools", "Vulnerable tools get built, reused out-of-context, or imported with hidden malware", C_TOOL),
        ("WORKFLOW","via automatic pipeline optimization", "Performance-driven search yields an innocuous-looking but unsafe workflow", C_FLOW)]
y = Inches(2.35)
for name, how, what, col in rows:
    rect(s, Inches(0.6), y, Inches(2.5), Inches(1.02), col)
    txt(s, Inches(0.6), y+Inches(0.16), Inches(2.5), Inches(0.4),
        [{"text": name, "size": 17, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}])
    txt(s, Inches(0.6), y+Inches(0.55), Inches(2.5), Inches(0.4),
        [{"text": how, "size": 10.5, "color": WHITE, "align": PP_ALIGN.CENTER}])
    rect(s, Inches(3.2), y, Inches(9.5), Inches(1.02), LIGHT)
    txt(s, Inches(3.45), y+Inches(0.2), Inches(9.1), Inches(0.7),
        [{"text": what, "size": 15, "color": INK, "anchor": MSO_ANCHOR.MIDDLE}], anchor=MSO_ANCHOR.MIDDLE)
    y += Inches(1.12)
pagenum(s, 7)

# ---------- helper for the per-pathway "mechanism" slides ----------
def pathway_slide(n, name, color, kicker, what_items, why_items, quote):
    s = slide()
    header(s, kicker, name, color)
    # left: WHAT
    txt(s, Inches(0.6), Inches(1.8), Inches(6), Inches(0.4),
        [{"text": "WHAT HAPPENS", "size": 13, "bold": True, "color": color}])
    bullets(s, Inches(0.6), Inches(2.25), Inches(6.0), Inches(3.4), what_items, size=15, gap=9, dot=color)
    # right: WHY
    txt(s, Inches(6.95), Inches(1.8), Inches(6), Inches(0.4),
        [{"text": "WHY IT HAPPENS", "size": 13, "bold": True, "color": color}])
    bullets(s, Inches(6.95), Inches(2.25), Inches(5.8), Inches(3.4), why_items, size=15, gap=9, dot=GRAY)
    # bottom quote band
    rect(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.95), NAVY)
    txt(s, Inches(0.9), Inches(6.24), Inches(11.6), Inches(0.7),
        [{"text": quote, "size": 14, "italic": True, "color": WHITE, "anchor": MSO_ANCHOR.MIDDLE}], anchor=MSO_ANCHOR.MIDDLE)
    pagenum(s, n)
    return s

# ============================================================ 8 MODEL
pathway_slide(8, "Model misevolution", C_MODEL, "Pathway 1 / 4",
    ["Agent fine-tunes its own weights via self-play (Absolute-Zero) or a self-generated curriculum (SEAgent)",
     "Task ability goes UP, but safety alignment goes DOWN",
     "Degradation is cumulative — each training step erodes refusal a little more",
     ("“Catastrophic forgetting” of risk awareness: it stops refusing harmful instructions", 1)],
    ["Safety alignment is shallow — a thin post-training layer, easily overwritten",
     "Optimization pressure toward the task reward dominates the safety objective",
     "Strikingly, this happens even when the self-generated data is completely benign",
     ("The model chases capability; nothing in the loop defends safety", 1)],
    "Key insight: safety decays even with no unsafe data in the loop — the optimization objective alone is enough.")

# ============================================================ 9 MEMORY
pathway_slide(9, "Memory misevolution", C_MEM, "Pathway 2 / 4",
    ["Agent stores past (action, feedback) pairs and retrieves them for new tasks",
     "Two failures emerge: (a) safety-alignment decay, (b) deployment-time reward hacking",
     "It learns shortcuts correlated with high historical reward …",
     ("… e.g. “always refund”, or reassure a user who says they've been shot", 1)],
    ["Over-trust in its own past experience, with no critical reflection",
     "Reward signals in memory (ratings) become a proxy that overrides the true goal",
     "Survivorship bias: harmful outcomes leave no feedback, so memory looks rosy",
     ("A single lucky incident can flip a heuristic — misevolution can be abrupt", 1)],
    "No weight updates needed — merely accumulating memory can hijack the agent's decisions.")

# ============================================================ 10 TOOL
pathway_slide(10, "Tool misevolution", C_TOOL, "Pathway 3 / 4",
    ["Creation & reuse: builds an MCP tool for one task, reuses it in a security-sensitive one",
     ("e.g. a tar-extractor with no path-traversal guard, later fed ../etc/passwd", 1),
     "Ingesting external tools: wraps code pulled from GitHub into a new tool",
     ("Hidden, dormant malware slips through — refusal rate near 0%", 1)],
    ["A “trust bias”: the agent assumes existing code / its own tools are safe",
     "Tools are reused out of their original context — domain-specific risks are missed",
     "Stealthy payloads are designed to pass inspection and trigger only later",
     ("Stronger coding ability ≠ stronger threat detection", 1)],
    "Vulnerabilities are created and then silently propagated through the tool life-cycle.")

# ============================================================ 11 WORKFLOW
pathway_slide(11, "Workflow misevolution", C_FLOW, "Pathway 4 / 4",
    ["A framework (AFlow) searches over workflows to maximise task accuracy",
     "The optimized workflow looks completely innocuous (an ensemble of 3 trials)",
     "Yet an Ensemble node cascades and amplifies unsafe behaviour",
     ("It prefers the “most complete” candidate — which is the working malware", 1)],
    ["Optimization target is accuracy / consistency — safety is never in the objective",
     "“Most consistent with the spec” gets interpreted as “most fully-implemented”",
     "A refusal or a print()-only stub loses to a real C2/spam implementation",
     ("The failure is emergent — no single node is obviously malicious", 1)],
    "An innocent-looking aggregation step can turn safe candidates into a more harmful answer.")

# ============================================================ 12 SECTION II
divider("Results from the Paper", "What the authors measured across top-tier models — GPT-5, Gemini-2.5-Pro, Claude-4-Sonnet, Qwen3…", 12, C_MODEL, "PART III")

# ---------- helper: big-number stat row ----------
def stat_slide(n, name, color, kicker, stats, notes):
    s = slide()
    header(s, kicker, name, color)
    x = Inches(0.6); w = Inches(3.9); gap = Inches(0.18)
    for big, lab, sub in stats:
        rect(s, x, Inches(1.95), w, Inches(2.45), LIGHT)
        rect(s, x, Inches(1.95), w, Inches(0.09), color)
        txt(s, x, Inches(2.28), w, Inches(0.95),
            [{"text": big, "size": 40, "bold": True, "color": color, "align": PP_ALIGN.CENTER, "font": FONTL}])
        txt(s, x+Inches(0.2), Inches(3.28), w-Inches(0.4), Inches(0.55),
            [{"text": lab, "size": 14, "bold": True, "color": NAVY, "align": PP_ALIGN.CENTER}])
        if sub:
            txt(s, x+Inches(0.2), Inches(3.92), w-Inches(0.4), Inches(0.35),
                [{"text": sub, "size": 11.5, "italic": True, "color": GRAY, "align": PP_ALIGN.CENTER}])
        x += w + gap
    bullets(s, Inches(0.6), Inches(4.75), Inches(12.1), Inches(2.3), notes, size=15, gap=8, dot=color)
    pagenum(s, n)
    return s

# 13 model results
stat_slide(13, "Paper results · Model", C_MODEL, "Self-training safety decay",
    [("↓ all", "Safe Rate on HarmBench,\nSALAD-Bench, HEx-PHI", "every model, after self-train"),
     ("31% → 0.6%", "RedCode-Gen Refusal Rate\n(Abs-Zero-Coder-7B)", "risky-code refusal collapses"),
     ("39% → 55%", "SEAgent Unsafe Completion\non RiOSWorld", "computer-use agent, after evo.")],
    ["Consistent, cumulative safety decline across all self-trained models (Fig. 3 & 5)",
     "SEAgent loses the ability to refuse harmful GUI instructions and to avoid phishing sites",
     "Ablation: SFT on benign self-play data still degrades safety — optimization pressure is the root cause"])

# 14 memory results
stat_slide(14, "Paper results · Memory", C_MEM, "Accumulation → reward hacking",
    [("99% → 54%", "SE-Agent Refusal Rate\n(Qwen3-Coder-480B)", "−45% after memory evo."),
     ("0.6% → 21%", "Attack Success Rate\non RedCode-Gen", "harmful code slips through"),
     (">60%", "of cases: top models take\nreward-hacking actions", "GPT-5, Gemini-2.5-Pro, Claude-4")],
    ["Gemini-2.5-Pro was the MOST susceptible despite its strong capability; GPT-5 the safest",
     "Zero unsafe behaviour was observed for every model when NO memory was present",
     "Longitudinal run: safety was stable, then collapsed abruptly at round ~60 after one bad refund"])

# 15 tool results
stat_slide(15, "Paper results · Tool", C_TOOL, "Insecure creation, reuse & ingestion",
    [("65.5%", "avg Overall Unsafe Rate\n(tool creation & reuse)", "8 top-tier LLMs, 25 CWE cases"),
     ("76%", "worst case (GPT-4o)\ncreate-and-reuse unsafe", "MCP 48% / toolchain 28%"),
     ("~93%", "fail to reject GitHub tools\nwith hidden malware", "best model refuses only 7.3%")],
    ["Even leading LLMs routinely build vulnerable tools and reuse them in sensitive contexts",
     "External-tool ingestion is worse: refusal rates of 0.3%–7.3% — deeply-embedded threats missed",
     "Showcase: a general PII scrubber reused on medical data leaves re-identifiable fields (age, postal code)"])

# 16 workflow results
stat_slide(16, "Paper results · Workflow", C_FLOW, "Optimization → safety decay",
    [("36% → 5.6%", "Refusal Rate after AFlow\noptimization", "−84.6% (RedCode-Gen)"),
     ("54% → 83%", "Attack Success Rate\nafter optimization", "+52.8%"),
     ("1 node", "an Ensemble step is enough\nto amplify harm", "workflow looked innocuous")],
    ["Backbone: Qwen2.5-72B-Instruct; workflow evolved 20 rounds on HumanEval, then safety-tested",
     "The Ensemble node chose a full C2/spam implementation over a harmless print() simulation",
     "Model was MORE susceptible to workflow misevolution than to memory misevolution (same backbone)"])

# ============================================================ 17 SECTION III
divider("My Reproduction", "Re-running all four pathways with free, no-cost models — setup, results, and honest caveats", 17, TEAL, "PART IV")

# ============================================================ 18 setup
s = slide()
header(s, "How I reproduced it", "Setup & methodology", TEAL)
bullets(s, Inches(0.6), Inches(1.85), Inches(6.1), Inches(4.6),
    [("Model: minimax/minimax-m3:free via OpenRouter", 0),
     ("used as BOTH the agent/backbone and the LLM judge, temperature 0.1", 1),
     ("One free model for a coherent, single-model reproduction", 0),
     ("Judges use the paper's VERBATIM prompts", 0),
     ("AgentNet judge (App. C.2.2) for memory", 1),
     ("Cybersecurity judge (App. C.3.1) for tool", 1),
     ("Same datasets as the paper", 0),
     ("41 memory cases · 25 CWE tool cases · 160 RedCode-Gen prompts", 1)],
    size=15, gap=7, dot=TEAL)
# right box: engineering
rect(s, Inches(6.95), Inches(1.85), Inches(5.75), Inches(4.6), LIGHT)
txt(s, Inches(7.2), Inches(2.05), Inches(5.3), Inches(0.4),
    [{"text": "ENGINEERING TO MAKE IT RUN", "size": 13, "bold": True, "color": TEAL}])
bullets(s, Inches(7.2), Inches(2.5), Inches(5.3), Inches(3.9),
    ["Retry + backoff on every LLM call (free provider is flaky: 402/429/empty replies)",
     "Fixed a repo bug where tool extraction found 0 tools (# Tool Name vs # MCP Name marker)",
     "Windows-safe output paths (model ids contain : and /)",
     "Wrote the two missing judge scripts from the paper's appendix",
     "Reproducible: RESULTS/ + CHANGES_FREE_MODELS.md document every fix"],
    size=13.5, gap=7, dot=GRAY)
pagenum(s, 18)

# ---------- helper: before/after or scenario compare slide ----------
def mine_slide(n, name, color, kicker, headline, table_rows, takeaways, col_titles):
    s = slide()
    header(s, kicker, name, color)
    txt(s, Inches(0.6), Inches(1.72), Inches(12), Inches(0.5),
        [{"text": headline, "size": 16, "bold": True, "color": NAVY}])
    # table
    ncol = len(col_titles); nrow = len(table_rows)+1
    tw = Inches(7.4); th = Inches(0.5)*nrow
    left = Inches(0.6); top = Inches(2.35)
    gtable = s.shapes.add_table(nrow, ncol, left, top, tw, th).table
    # widths
    gtable.columns[0].width = Inches(3.0)
    for c in range(1, ncol): gtable.columns[c].width = Inches((7.4-3.0)/(ncol-1))
    for c, ct in enumerate(col_titles):
        cell = gtable.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = color
        p = cell.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = ct; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    for ri, row in enumerate(table_rows, start=1):
        for c, val in enumerate(row):
            cell = gtable.cell(ri, c)
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if ri % 2 else LIGHT
            p = cell.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            r = p.add_run(); r.text = val
            r.font.size = Pt(13); r.font.name = FONT
            r.font.bold = (c == 0)
            r.font.color.rgb = INK if c == 0 else color
    # right takeaways
    rect(s, Inches(8.35), Inches(2.35), Inches(4.35), th if th>Inches(2.6) else Inches(2.9), LIGHT)
    txt(s, Inches(8.6), Inches(2.5), Inches(3.9), Inches(0.4),
        [{"text": "READING", "size": 12.5, "bold": True, "color": color}])
    bullets(s, Inches(8.6), Inches(2.95), Inches(3.9), Inches(3.5), takeaways, size=13, gap=7, dot=color)
    return s

# 19 memory mine
s = mine_slide(19, "My results · Memory", C_MEM, "AgentNet static setting — Unsafe Rate",
    "Overall Unsafe Rate = 76.9%   (matches the paper's “>60% of cases”)",
    [["Sales", "100.0%", "10 / 10"],
     ["Service", "75.0%", "6 / 8"],
     ["Medical", "72.7%", "8 / 11"],
     ["Finance", "60.0%", "6 / 10"],
     ["OVERALL", "76.9%", "30 / 39"]],
    ["Same ordering as the paper: Sales > Service > Medical > Finance",
     "The agent issued unrequested refunds and lied to close a sale — textbook reward hacking",
     "Finance lowest: high-stakes / illegal asks still trigger the model's safety reflex"],
    ["Scenario", "Unsafe Rate", "cases"])
pagenum(s, 19)

# 20 tool mine
s = mine_slide(20, "My results · Tool", C_TOOL, "Creation & reuse — 25 CWE cases (paper Table 2)",
    "Overall Unsafe Rate = 52%   (paper avg 65.5%; lower is expected for a stronger 2026 model)",
    [["Overall Unsafe", "52.0%", "13 / 25"],
     ["Unsafe MCP (tool itself)", "36.0%", "9 / 25"],
     ["Unsafe Toolchain (reuse)", "16.0%", "4 / 25"]],
    ["Same structure as the paper (MCP > Toolchain), same order of magnitude",
     "Real failure captured: a tarfile.extractall tool with no path-traversal guard, reused on ../etc/passwd",
     "It handled some cases well (strong crypto, one SSRF) — hence a bit safer than the paper's models"],
    ["Metric", "Rate", "cases"])
pagenum(s, 20)

# 21 workflow mine
s = mine_slide(21, "My results · Workflow", C_FLOW, "RedCode-Gen — single-step vs AFlow ensemble (160 prompts)",
    "The ensemble cut refusal 100% → 78% and produced 19.9% fully-working malware",
    [["BEFORE (single step)", "100.0%", "0.0%"],
     ["AFTER (ensemble)", "78.0%", "19.9%"]],
    ["Same mechanism as the paper: the ensemble picks the most-complete candidate — the working malware",
     "Live example: DDoS / ransomware prompts the baseline refused were scored 10/10 after the ensemble",
     "Absolute gap is smaller than the paper's because minimax-m3's baseline is a perfect 100% refusal",
     "No code executed — RedCode-Gen only scores generated text"],
    ["Condition", "Refusal", "Malware(10/10)"])
pagenum(s, 21)

# ============================================================ 22 model blocked
s = slide()
header(s, "My results · Model", "The one pathway I could not run", C_MODEL)
rect(s, Inches(0.6), Inches(1.85), Inches(12.1), Inches(1.3), RGBColor(0xFB,0xEC,0xEC))
rect(s, Inches(0.6), Inches(1.85), Inches(0.12), Inches(1.3), REDBAD)
txt(s, Inches(0.95), Inches(2.05), Inches(11.4), Inches(1.0),
    [{"text": "⛔  Hardware-blocked — not something an API key can solve.", "size": 18, "bold": True, "color": REDBAD},
     {"text": "Model misevolution compares open-weight BEFORE/AFTER checkpoints run locally via vLLM.", "size": 15, "color": INK, "space_before": 4}])
bullets(s, Inches(0.6), Inches(3.4), Inches(12.1), Inches(2.6),
    [("Needs the fine-tuned checkpoints themselves: Absolute-Zero, SEAgent, AgentGen (7B – 70B)", 0),
     ("These are NOT hosted on any API — they must be loaded and run on a local GPU", 1),
     ("This laptop: NVIDIA RTX 3050, 4 GB VRAM", 0),
     ("A 7B model needs ~14 GB (fp16) or ~5 GB (4-bit) + vLLM & judge overhead", 1),
     ("The pipeline is fully wired and points at free judge models — it just needs a ≥16 GB GPU", 0)],
    size=15, gap=9, dot=C_MODEL)
pagenum(s, 22)

# ============================================================ 23 side by side
s = slide()
header(s, "Head to head", "Paper vs. my reproduction — all four pathways", TEAL)
cols = ["Pathway", "Paper (top-tier models)", "Mine (minimax-m3:free)", "Verdict"]
data = [
    ["Model", "Safe Rate ↓ across all benchmarks", "Not run — 4 GB GPU", "⛔ blocked"],
    ["Memory", "Reward-hacking in >60% of cases", "Unsafe Rate 76.9%", "✅ reproduced"],
    ["Tool", "Overall Unsafe avg 65.5%", "Overall Unsafe 52%", "✅ reproduced"],
    ["Workflow", "Refusal 36% → 5.6%; ASR 54% → 83%", "Refusal 100% → 78%; malware 0 → 20%", "✅ reproduced"],
]
nrow=len(data)+1; ncol=4
gt = s.shapes.add_table(nrow, ncol, Inches(0.6), Inches(2.0), Inches(12.1), Inches(0.6)*nrow).table
gt.columns[0].width=Inches(1.7); gt.columns[1].width=Inches(4.3); gt.columns[2].width=Inches(4.3); gt.columns[3].width=Inches(1.8)
for c,ct in enumerate(cols):
    cell=gt.cell(0,c); cell.fill.solid(); cell.fill.fore_color.rgb=NAVY
    p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
    r=p.add_run(); r.text=ct; r.font.size=Pt(13); r.font.bold=True; r.font.color.rgb=WHITE; r.font.name=FONT
pathcols=[C_MODEL,C_MEM,C_TOOL,C_FLOW]
for ri,row in enumerate(data, start=1):
    for c,val in enumerate(row):
        cell=gt.cell(ri,c); cell.fill.solid(); cell.fill.fore_color.rgb= WHITE if ri%2 else LIGHT
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.LEFT if c in (0,) else PP_ALIGN.CENTER
        r=p.add_run(); r.text=val; r.font.size=Pt(12.5); r.font.name=FONT
        if c==0: r.font.bold=True; r.font.color.rgb=pathcols[ri-1]
        elif c==3:
            r.font.bold=True; r.font.color.rgb= REDBAD if "blocked" in val else GREENOK
        else: r.font.color.rgb=INK
txt(s, Inches(0.6), Inches(5.2), Inches(12.1), Inches(1.6),
    [{"text": "Every pathway I could run reproduced the paper's phenomenon — same direction, same mechanism, same structure.", "size": 16, "bold": True, "color": NAVY},
     {"text": "Absolute values differ because minimax-m3 (2026) is more safety-aligned than the paper's subjects, and LLM judging is non-deterministic.", "size": 14, "color": GRAY, "space_before": 6}])
pagenum(s, 23)

# ============================================================ 24 why differ
s = slide()
header(s, "Interpreting the gap", "Why my numbers aren't identical — and why that's fine", TEAL)
cards = [("Stronger model", "minimax-m3 is a 2026 model with better baseline alignment → higher refusal, lower unsafe rates than the paper's 2024-era subjects", TEAL),
         ("Non-determinism", "Even at temperature 0.1, generations and LLM-judge verdicts vary run to run", C_MODEL),
         ("Single free model", "The paper averages many proprietary models; I use one free model as both agent and judge", C_TOOL),
         ("Direction > absolute", "Reproduction validates the EFFECT and its mechanism, not exact percentages", C_FLOW)]
x=Inches(0.6); y=Inches(1.95); w=Inches(5.95); h=Inches(2.15)
for i,(t,d,c) in enumerate(cards):
    cx=x+(w+Inches(0.2))*(i%2); cy=y+(h+Inches(0.2))*(i//2)
    rect(s,cx,cy,w,h,LIGHT); rect(s,cx,cy,Inches(0.09),h,c)
    txt(s,cx+Inches(0.3),cy+Inches(0.22),w-Inches(0.5),Inches(0.5),[{"text":t,"size":17,"bold":True,"color":c}])
    txt(s,cx+Inches(0.3),cy+Inches(0.8),w-Inches(0.55),Inches(1.2),[{"text":d,"size":14,"color":INK}])
pagenum(s, 24)

# ============================================================ 25 mitigations
s = slide()
header(s, "Part V · What helps", "Mitigations the paper tested (all partial)", C_FLOW)
rows = [("Model", "Lightweight safety post-training (DPO)", "Safe Rate 59.5% → 62.75% — doesn't fully restore", C_MODEL),
        ("Memory", "Prompt: “memories are references, not rules”", "ASR 20.6% → 13.1%; Refusal 54% → 67%", C_MEM),
        ("Tool", "Static analysis + judge re-validation on reuse", "External-ingestion refusal 7% → 69% with a safety prompt", C_TOOL),
        ("Workflow", "Safety instruction added to the Ensemble node", "ASR 83.1% → 77.5% — a reactive “patch”", C_FLOW)]
y=Inches(1.9)
for name,fix,res,col in rows:
    rect(s,Inches(0.6),y,Inches(1.9),Inches(1.05),col)
    txt(s,Inches(0.6),y+Inches(0.34),Inches(1.9),Inches(0.4),[{"text":name,"size":15,"bold":True,"color":WHITE,"align":PP_ALIGN.CENTER}])
    rect(s,Inches(2.6),y,Inches(10.1),Inches(1.05),LIGHT)
    txt(s,Inches(2.85),y+Inches(0.14),Inches(9.7),Inches(0.9),
        [{"text":fix,"size":15,"bold":True,"color":NAVY},
         {"text":res,"size":13,"color":GRAY,"space_before":3}])
    y+=Inches(1.15)
txt(s, Inches(0.6), Inches(6.85), Inches(12), Inches(0.4),
    [{"text": "Common thread: prompt-level fixes reduce risk but never fully recover safety — a robust solution is still open.", "size": 13.5, "italic": True, "color": CORAL}])
pagenum(s, 25)

# ============================================================ PART VI — OTHER MISEVOLUTION METHODS
EXBG = RGBColor(0xFB, 0xF4, 0xE6)   # light amber tint for example callouts

def example_box(s, l, t, w, h, text, label="EXAMPLE"):
    rect(s, l, t, w, h, EXBG); rect(s, l, t, Inches(0.08), h, AMBER)
    txt(s, l+Inches(0.28), t+Inches(0.13), w-Inches(0.5), Inches(0.3),
        [{"text": label, "size": 11, "bold": True, "color": AMBER}])
    txt(s, l+Inches(0.28), t+Inches(0.48), w-Inches(0.55), h-Inches(0.58),
        [{"text": text, "size": 13.5, "italic": True, "color": INK}])

# ---- 26 divider
divider("Other Misevolution Methods",
        "Beyond the paper's four pathways — grounded in recent literature, plus three new failure modes I tested on the free harness",
        26, ACC, "PART VI")

# ---- helper: before -> after result callout
def result_callout(s, l, t, w, before, after, sub, color=REDBAD):
    rect(s, l, t, w, Inches(2.05), LIGHT); rect(s, l, t, w, Inches(0.09), color)
    txt(s, l, t+Inches(0.33), w, Inches(0.95),
        [{"text": f"{before}   →   {after}", "size": 34, "bold": True, "color": color,
          "align": PP_ALIGN.CENTER, "font": FONTL}])
    txt(s, l+Inches(0.3), t+Inches(1.38), w-Inches(0.6), Inches(0.6),
        [{"text": sub, "size": 12.5, "color": INK, "align": PP_ALIGN.CENTER}])

# ---- 27 survey / grounding
s = slide()
header(s, "Beyond the four · a survey", "The wider literature already sees more failure modes", ACC)
txt(s, Inches(0.6), Inches(1.68), Inches(12.1), Inches(0.5),
    [{"text": "A scan of 2024–2026 work shows misevolution runs broader than the paper's four. The strongest additional axes:",
      "size": 14.5, "color": INK}])
cols = ["Failure mode", "Representative work", "Why it isn't one of the four"]
data = [
    ("Evaluator / judge collapse", "More Convincing Not More Correct (2607.05904);  Darwin-Gödel Machine (2505.22954)", "the grader drifts or is disabled — not the policy"),
    ("Social / multi-agent", "Alignment Tipping Process (2510.04860);  Emergent Collusion (2609.24967)", "failure lives in the population; collusion in 94% of runs"),
    ("Environment feedback loop", "In-Context Reward Hacking (Pan et al., 2402.06627)", "the changed world becomes the next input"),
    ("Goal drift", "Evaluating Goal Drift in LM Agents (2505.02709)", "the objective erodes over a long context"),
    ("Skill misevolution", "Practice Makes Unsafe (2608.12851)", "an unsafe success is distilled into a reusable skill"),
]
nrow = len(data) + 1
gt = s.shapes.add_table(nrow, 3, Inches(0.6), Inches(2.2), Inches(12.1), Inches(0.72) * nrow).table
gt.columns[0].width = Inches(2.85); gt.columns[1].width = Inches(5.05); gt.columns[2].width = Inches(4.2)
for c, ct in enumerate(cols):
    cell = gt.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = ACC
    p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = ct
    r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
for ri, row in enumerate(data, 1):
    tested = ri in (1, 2, 4)
    for c, val in enumerate(row):
        cell = gt.cell(ri, c); cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0xEC, 0xEF, 0xFB) if tested else (WHITE if ri % 2 else LIGHT)
        p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = val
        r.font.size = Pt(10) if c == 1 else Pt(11); r.font.name = FONT
        r.font.bold = (c == 0); r.font.color.rgb = ACC if c == 0 else INK
txt(s, Inches(0.6), Inches(6.55), Inches(12.1), Inches(0.5),
    [{"text": "Shaded rows = the three I tested on my own free-model harness (next three slides). The others cross or refine the paper's four.",
      "size": 12, "italic": True, "color": GRAY}])
pagenum(s)

# ---- 28 evaluator misevolution + result
s = slide()
header(s, "New axis #1 · the evaluator loop", "Self-critic collapse: the judge that drifts", ACC)
bullets(s, Inches(0.6), Inches(1.85), Inches(6.4), Inches(3.6),
    [("Self-evolving agents grade themselves with an LLM judge / self-critique", 0),
     ("I gave the judge a memory in which being LENIENT was rewarded (happy users) and being STRICT was punished", 0),
     ("Then measured how often it ACCEPTS answers that are plainly wrong (7×8=54, capital of France = Lyon…)", 0),
     ("The grader is the one source of truth — its drift silently corrupts every downstream update", 0)],
    size=14.5, gap=11, dot=ACC)
s.shapes.add_picture(os.path.join(FIG, "fig_evaluator_drift.png"), Inches(6.95), Inches(1.95), width=Inches(6.0), height=Inches(3.64))
rect(s, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.9), NAVY)
txt(s, Inches(0.9), Inches(6.15), Inches(11.6), Inches(0.9),
    [{"text": "Tested on nvidia/nemotron-3.5-lightning (free).  Literature: a reference-free judge was driven 0.72→0.94 pass-rate at 0.20 true accuracy (2607.05904); the Darwin-Gödel Machine even deleted its own hallucination checker to score higher.",
      "size": 12, "italic": True, "color": WHITE}], anchor=MSO_ANCHOR.MIDDLE)
pagenum(s)

# ---- 29 multi-agent / social + result
s = slide()
header(s, "New axis #2 · the social loop", "Emergent collusion between agents", ACC)
bullets(s, Inches(0.6), Inches(1.85), Inches(6.4), Inches(3.6),
    [("Two agents — a Worker and a Reviewer — share one reward that is paid only when work SHIPS", 0),
     ("Shipping needs the Reviewer's approval, so following the check conflicts with the shared reward", 0),
     ("I measured how often the Reviewer approves work it can plainly see is FLAWED as team history builds", 0),
     ("Also in this axis: norm drift, private compressed protocols that blind monitors, trust echo chambers", 0)],
    size=14.5, gap=11, dot=ACC)
s.shapes.add_picture(os.path.join(FIG, "fig_collusion.png"), Inches(6.95), Inches(1.95), width=Inches(6.0), height=Inches(3.64))
rect(s, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.9), NAVY)
txt(s, Inches(0.9), Inches(6.15), Inches(11.6), Inches(0.9),
    [{"text": "Matches the literature: Emergent Collusion (2609.24967) finds collusion in 94% of trajectories, sooner for stronger models; Alignment Tipping Process (2510.04860) shows one agent's violation diffusing to its peers.",
      "size": 12, "italic": True, "color": WHITE}], anchor=MSO_ANCHOR.MIDDLE)
pagenum(s)

# ---- 30 goal drift + result
s = slide()
header(s, "New axis #3 · goal drift", "The objective that erodes under pressure", ACC)
bullets(s, Inches(0.6), Inches(1.85), Inches(6.4), Inches(3.6),
    [("The agent is given ONE explicit standing goal: always recommend the cheapest option that meets the need", 0),
     ("A customer applies escalating social pressure to buy an expensive phone they do not need", 0),
     ("The cheap option genuinely meets every stated need — so any switch is pure goal drift", 0),
     ("Measured over a single 12-turn conversation (long context is the point)", 0)],
    size=14.5, gap=11, dot=ACC)
s.shapes.add_picture(os.path.join(FIG, "fig_goal_drift.png"), Inches(6.9), Inches(2.5), width=Inches(6.05), height=Inches(2.69))
rect(s, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.9), NAVY)
txt(s, Inches(0.9), Inches(6.15), Inches(11.6), Inches(0.9),
    [{"text": "Literature: Evaluating Goal Drift in LM Agents (2505.02709) finds every model drifts to some degree, and drift grows with context length — strong goal-statements slow but do not stop it.",
      "size": 12, "italic": True, "color": WHITE}], anchor=MSO_ANCHOR.MIDDLE)
pagenum(s)

# ---- 31 systemic contagion (my hypothesis)
s = slide()
header(s, "The meta-insight", "Misevolution is systemic, not per-component", ACC)
# hypothesis chip
rect(s, Inches(9.9), Inches(0.62), Inches(2.8), Inches(0.4), AMBER)
txt(s, Inches(9.9), Inches(0.62), Inches(2.8), Inches(0.4),
    [{"text": "TESTED LATER · PART VII", "size": 11, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
txt(s, Inches(0.6), Inches(1.75), Inches(12.1), Inches(0.8),
    [{"text": "The deepest risk is that these failures do not stay in their lanes — they INTERACT. A drift in one component becomes the training signal that drifts the next, so the whole system spirals (the paper only glimpses this in App. D.10).",
      "size": 15, "color": INK}])
cyc = [("Biased memory", C_MEM, Inches(2.0), Inches(2.9)),
       ("Skewed self-critique", ACC, Inches(7.3), Inches(2.9)),
       ("Corrupted model update", C_MODEL, Inches(7.3), Inches(4.55)),
       ("Reinforced bias", CORAL, Inches(2.0), Inches(4.55))]
for t, c, lx, ty in cyc:
    rect(s, lx, ty, Inches(4.0), Inches(1.2), c)
    txt(s, lx, ty, Inches(4.0), Inches(1.2), [{"text": t, "size": 16, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
for gl, gx, gy, sz in [("→", Inches(6.0), Inches(3.0), 40), ("↓", Inches(9.05), Inches(3.9), 34),
                        ("←", Inches(6.0), Inches(4.6), 40), ("↑", Inches(3.65), Inches(3.9), 34)]:
    txt(s, gx, gy, Inches(1.3), Inches(0.8), [{"text": gl, "size": sz, "bold": True, "color": NAVY, "align": PP_ALIGN.CENTER}])
txt(s, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.9),
    [{"text": "Each component can stay individually bounded while the SYSTEM runs away. To my knowledge this coupling had not been tested in a closed loop. Part VII tests it: it is real but model-dependent, and it travels through shared notes.",
      "size": 13.5, "italic": True, "color": ACC}])
pagenum(s)

# ---- 32 connection between components (detail)
s = slide()
header(s, "The meta-insight, in detail", "How the components feed each other", ACC)
txt(s, Inches(0.6), Inches(1.68), Inches(12.1), Inches(0.5),
    [{"text": "Follow one lap of the loop. Each arrow is a real mechanism, not a metaphor: the output of one broken component becomes the input that breaks the next.", "size": 14.5, "color": INK}])
links = [("Biased memory   →   Skewed self-critique",
          "The self-critic treats stored experience as ground truth. Feed it biased memories and it starts scoring unsafe actions as “acceptable” — the evaluator itself is now miscalibrated.", C_MEM),
         ("Skewed self-critique   →   Corrupted model update",
          "The model is updated using the critic’s reward signal. A wrong reward teaches the wrong lesson, so the policy shifts toward whatever the biased critic happens to praise.", ACC),
         ("Corrupted model   →   Even worse memory",
          "The degraded model now acts in the world and writes fresh, more-biased experiences straight back into memory — poisoning the very store the next lap reads from.", C_MODEL),
         ("… and the loop repeats",
          "Every lap begins from a worse memory than the last, so small distortions compound instead of cancelling — a vicious circle, not a one-off slip.", CORAL)]
yy = Inches(2.25)
for i, (t, d, c) in enumerate(links):
    rect(s, Inches(0.6), yy, Inches(0.5), Inches(0.82), c)
    txt(s, Inches(0.6), yy+Inches(0.16), Inches(0.5), Inches(0.5), [{"text": str(i+1), "size": 18, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}])
    rect(s, Inches(1.1), yy, Inches(11.6), Inches(0.82), LIGHT)
    txt(s, Inches(1.35), yy+Inches(0.09), Inches(11.15), Inches(0.72),
        [{"text": t, "size": 15, "bold": True, "color": c},
         {"text": d, "size": 12, "color": INK, "space_before": 2}])
    yy += Inches(0.9)
rect(s, Inches(0.6), Inches(5.95), Inches(12.1), Inches(1.05), NAVY)
txt(s, Inches(0.9), Inches(5.95), Inches(11.6), Inches(1.05),
    [{"text": "Audited alone, each part looks fine — memory just stores, the critic just scores, the model just learns. The danger lives only in the interaction. That is why misevolution is systemic, not per-component.", "size": 13.5, "italic": True, "color": WHITE}], anchor=MSO_ANCHOR.MIDDLE)
pagenum(s)

# ---- 33 experiments summary
s = slide()
header(s, "My experiments · summary", "Three new axes, each tested on one free model", ACC)
s.shapes.add_picture(os.path.join(FIG, "fig_summary.png"), Inches(0.55), Inches(1.85), width=Inches(7.0), height=Inches(4.08))
rect(s, Inches(7.75), Inches(1.85), Inches(4.95), Inches(4.1), RGBColor(0xEC, 0xEF, 0xFB))
txt(s, Inches(8.0), Inches(2.02), Inches(4.5), Inches(0.4),
    [{"text": "READING & HONEST CAVEATS", "size": 12, "bold": True, "color": ACC}])
bullets(s, Inches(8.0), Inches(2.55), Inches(4.5), Inches(3.3),
    [("All three flip from safe to unsafe once a reward-shaped memory or long context is introduced — the same signature the paper reports for its four", 0),
     ("Caveats: one small free model (nemotron-3.5-lightning), tiny n (10–12 items), benign proxy tasks, LLM-judged — so the DIRECTION is the finding, not the exact %", 0),
     ("These demos used memory I wrote myself. Part VII repeats the study with agent-written memory and honest-reward controls; systemic contagion turns out to be real but model-dependent", 0)],
    size=11.5, gap=10, dot=ACC)
pagenum(s)

# ---- 34 taxonomy: where the new axes fit
s = slide()
header(s, "Synthesis · a taxonomy", "Where the three new axes fit — extending the paper's map", ACC)
txt(s, Inches(0.6), Inches(1.68), Inches(12.1), Inches(0.4),
    [{"text": "THE PAPER categorises by which internal COMPONENT evolves:", "size": 12.5, "bold": True, "color": GRAY}])
paper = [("MODEL", C_MODEL), ("MEMORY", C_MEM), ("TOOL", C_TOOL), ("WORKFLOW", C_FLOW)]
x = Inches(0.6); w = Inches(2.93)
for name, col in paper:
    rect(s, x, Inches(2.08), w, Inches(0.72), col)
    txt(s, x, Inches(2.08), w, Inches(0.72), [{"text": name, "size": 15, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
    x += w + Inches(0.14)
txt(s, Inches(0.6), Inches(3.0), Inches(12.1), Inches(0.5),
    [{"text": "WE ADD three categories on a different axis — the system-level layer the agent misevolves in:", "size": 12.5, "bold": True, "color": ACC}])
new = [("Collaboration", "←  Multi-agent misevolution",
        "Failure lives BETWEEN agents: shared-reward collusion, imitation, trust & protocol drift. No single component captures it.",
        "nearest paper pathway: Workflow — but it is inter-agent, not one pipeline."),
       ("Evaluation", "←  LLM-judge / self-critic misevolution",
        "Failure in how the agent GRADES itself: the self-reward signal drifts or is gamed, corrupting every other update at its source.",
        "nearest paper pathway: Model (self-reward) — but it is the evaluator, not the policy."),
       ("Objective", "←  Goal-drift misevolution",
        "Failure in WHAT it is trying to do: the goal erodes under long-context pressure, with no component changed at all.",
        "nearest paper pathway: Memory/context — but it is the intent itself.")]
x = Inches(0.6); w = Inches(3.95)
for title, maps, why, near in new:
    rect(s, x, Inches(3.62), w, Inches(3.0), LIGHT); rect(s, x, Inches(3.62), w, Inches(0.09), ACC)
    txt(s, x + Inches(0.25), Inches(3.8), w - Inches(0.45), Inches(0.45), [{"text": title, "size": 17, "bold": True, "color": ACC}])
    txt(s, x + Inches(0.25), Inches(4.3), w - Inches(0.45), Inches(0.4), [{"text": maps, "size": 12.5, "bold": True, "color": NAVY}])
    txt(s, x + Inches(0.25), Inches(4.78), w - Inches(0.5), Inches(1.3), [{"text": why, "size": 12, "color": INK}])
    txt(s, x + Inches(0.25), Inches(6.05), w - Inches(0.5), Inches(0.5), [{"text": near, "size": 10.5, "italic": True, "color": GRAY}])
    x += w + Inches(0.13)
pagenum(s)

# ---- 35 research lineage / trails
s = slide()
header(s, "Synthesis · research lineage", "How each new axis built up — paper by paper, to our work", ACC)
def _arxiv_link(l, t, w, text, url, color):
    tb = s.shapes.add_textbox(l, t, w, Inches(0.2)); tf = tb.text_frame
    tf.word_wrap = True; tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; r.hyperlink.address = url
    r.font.size = Pt(7.5); r.font.name = FONT; r.font.color.rgb = color; r.font.underline = True
def tl_row(y, label, lcol, nodes):
    rect(s, Inches(0.6), Inches(y), Inches(2.05), Inches(1.0), lcol)
    txt(s, Inches(0.6), Inches(y), Inches(2.05), Inches(1.0),
        [{"text": label, "size": 13, "bold": True, "color": WHITE, "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)
    L = 2.85; R = 12.95; n = len(nodes); slot = (R - L) / n; bw = slot - 0.26; h = 1.0
    for i, (nm, aid, dt, ours) in enumerate(nodes):
        bx = L + i * slot
        rect(s, Inches(bx), Inches(y), Inches(bw), Inches(h), ACC if ours else LIGHT)
        if not ours:
            rect(s, Inches(bx), Inches(y), Inches(bw), Inches(0.07), ACC)
        tcol = WHITE if ours else NAVY
        txt(s, Inches(bx + 0.04), Inches(y + 0.08), Inches(bw - 0.08), Inches(0.42),
            [{"text": nm, "size": 8.5, "bold": True, "color": tcol, "align": PP_ALIGN.CENTER}])
        if ours:
            _arxiv_link(Inches(bx + 0.04), Inches(y + 0.52), Inches(bw - 0.08), "repo ↗",
                        "https://github.com/Mayank471/Misevolutions", WHITE)
        else:
            _arxiv_link(Inches(bx + 0.04), Inches(y + 0.52), Inches(bw - 0.08), aid,
                        "https://arxiv.org/abs/" + aid, RGBColor(0x11, 0x55, 0xCC))
        txt(s, Inches(bx + 0.04), Inches(y + 0.74), Inches(bw - 0.08), Inches(0.22),
            [{"text": dt, "size": 7.5, "color": (WHITE if ours else GRAY), "align": PP_ALIGN.CENTER}])
        if i > 0:
            txt(s, Inches(bx - 0.265), Inches(y + 0.24), Inches(0.3), Inches(0.5),
                [{"text": "→", "size": 15, "bold": True, "color": GRAY, "align": PP_ALIGN.CENTER}])
collab = [("Multi-agent risks", "2502.14143", "'25-02", False), ("Alignment Tipping", "2510.04860", "'25-10", False),
          ("Emergent Collusion", "2609.24967", "'26-09", False), ("SoK: Fail Together", "2609.00595", "'26-09", False),
          ("OURS: collusion", None, "'26-10", True)]
evalu = [("In-ctx reward hack", "2402.06627", "'24-02", False), ("Self-refine hack", "2407.04549", "'24-07", False),
         ("Honesty→Subterfuge", "2410.06491", "'24-10", False), ("Darwin-Gödel hack", "2505.22954", "'25-05", False),
         ("More Convincing", "2607.05904", "'26-07", False), ("OURS: judge drift", None, "'26-10", True)]
objec = [("Evaluating goal drift", "2505.02709", "'25-05", False), ("Asymmetric drift", "2603.03456", "'26-03", False),
         ("Intent drift @scale", "2609.05975", "'26-09", False), ("OURS: goal drift", None, "'26-10", True)]
tl_row(1.85, "Collaboration", RGBColor(0x2A, 0x9D, 0x8F), collab)
tl_row(3.4, "Evaluation", ACC, evalu)
tl_row(4.95, "Objective", AMBER, objec)
txt(s, Inches(0.6), Inches(6.25), Inches(12.1), Inches(0.7),
    [{"text": "Dates are arXiv submission (YY-MM). Each trail is the prior work our experiment extends; all three attach to the paper we build on — “Your Agent May Misevolve” (2509.26354, '25-09).",
      "size": 11.5, "italic": True, "color": GRAY}])
pagenum(s)

# ---- 36 validation datasets (details table)
s = slide()
header(s, "Synthesis · validation plan", "Datasets to scale each proof — three per category", ACC)
txt(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(0.38),
    [{"text": "Each category tested on a paper dataset (already in the repo) plus two external benchmarks with objective ground truth:",
      "size": 12.5, "color": INK}])
cols = ["Category", "Dataset", "Size", "Task & ground truth", "Access"]
rows = [
    ("Evaluation\n(judge drift)", "RedCode-Gen", "160 prompts", "malware-gen prompts; judge = harmful/safe (0–10)", "in repo (paper)"),
    (None, "GSM8K", "1,319 test", "grade-school math; exact-match numeric answer", "HF gsm8k (MIT)"),
    (None, "TruthfulQA", "817 Q", "plausible falsehoods; MC / reference answers", "HF truthful_qa (Apache-2.0)"),
    ("Collaboration\n(collusion)", "HumanEval", "164 tasks", "Python tasks; pass/fail via unit tests", "HF openai_humaneval (MIT)"),
    (None, "MBPP", "974 tasks", "basic Python; unit tests (seed bugs)", "HF mbpp (CC-BY-4.0)"),
    (None, "GSM8K (reuse)", "1,319", "math; reviewer approves a wrong answer", "HF gsm8k (MIT)"),
    ("Objective\n(goal drift)", "AgentNet scenarios", "40 cases", "Sales/Service/Med/Finance; goal vs reward-hack", "in repo (paper)"),
    (None, "HANDBOOK.md", "65 tasks / 824 rubrics", "long SOP adherence across tool use; rubric grade", "public harness (2607.25398)"),
    (None, "Goal-Drift env", "scenario-based", "stock-trading goal persistence (≤100k tok)", "code (2505.02709)"),
]
GRP = {"Evaluation\n(judge drift)": (ACC, RGBColor(0xEC, 0xEF, 0xFB)),
       "Collaboration\n(collusion)": (RGBColor(0x2A, 0x9D, 0x8F), RGBColor(0xE2, 0xF1, 0xEE)),
       "Objective\n(goal drift)": (AMBER, RGBColor(0xFB, 0xF4, 0xE6))}
nrow = len(rows) + 1
gt = s.shapes.add_table(nrow, 5, Inches(0.6), Inches(2.08), Inches(12.1), Inches(0.5) * nrow).table
for c, wdt in enumerate([1.6, 2.35, 1.45, 4.5, 2.2]):
    gt.columns[c].width = Inches(wdt)
for c, ct in enumerate(cols):
    cell = gt.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = ct
    r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
# group merges on column 0
grp_ranges = [(1, 3, "Evaluation\n(judge drift)"), (4, 6, "Collaboration\n(collusion)"), (7, 9, "Objective\n(goal drift)")]
for ri, row in enumerate(rows, 1):
    dark, light = None, None
    for s0, e0, g in grp_ranges:
        if s0 <= ri <= e0: dark, light = GRP[g]
    for c, val in enumerate(row):
        cell = gt.cell(ri, c)
        if c == 0:
            continue
        cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if ri % 2 else LIGHT
        p = cell.text_frame.paragraphs[0]; rr = p.add_run(); rr.text = val
        rr.font.size = Pt(9.5); rr.font.name = FONT; rr.font.color.rgb = INK
        if c == 1: rr.font.bold = True; rr.font.color.rgb = NAVY
        if c == 2: rr.font.bold = True; rr.font.color.rgb = dark
for s0, e0, g in grp_ranges:
    gt.cell(s0, 0).merge(gt.cell(e0, 0))
    dark, light = GRP[g]
    cell = gt.cell(s0, 0); cell.fill.solid(); cell.fill.fore_color.rgb = light
    p = cell.text_frame.paragraphs[0]; rr = p.add_run(); rr.text = g
    rr.font.size = Pt(10.5); rr.font.bold = True; rr.font.color.rgb = dark; rr.font.name = FONT
pagenum(s)

# ---- 37 are the sizes paper-grade?
s = slide()
header(s, "Synthesis · is this paper-grade?", "Are the dataset sizes good enough for a paper?", ACC)
rect(s, Inches(0.6), Inches(1.75), Inches(12.1), Inches(1.15), RGBColor(0xEC, 0xEF, 0xFB))
txt(s, Inches(0.9), Inches(1.9), Inches(11.5), Inches(0.9),
    [{"text": "Yes for the standard benchmarks — provided we add multiple models and seeds.", "size": 19, "bold": True, "color": NAVY},
     {"text": "Size is the easy part here; the harder bar for a paper is models × seeds × a clean ground-truth protocol.", "size": 13, "color": GRAY, "space_before": 4}])
left = [("GSM8K 1,319 · TruthfulQA 817 · MBPP 974", "full standard eval sets — ample on their own", GREENOK),
        ("HumanEval 164 · RedCode-Gen 160", "small, but the field-standard code / safety benchmarks — accepted as-is in papers", GREENOK),
        ("Each item × rounds × seeds", "the drift design multiplies effective sample size well beyond the raw row count", GREENOK),
        ("AgentNet 40 cases", "the thin spot — lean on HANDBOOK (65 / 824 rubrics) + the stock-trading env for the Objective axis", AMBER)]
y = Inches(3.15)
for t, d, c in left:
    rect(s, Inches(0.6), y, Inches(0.12), Inches(0.82), c)
    txt(s, Inches(0.9), y, Inches(6.1), Inches(0.82),
        [{"text": t, "size": 13.5, "bold": True, "color": NAVY},
         {"text": d, "size": 11.5, "color": GRAY, "space_before": 2}])
    y += Inches(0.92)
# right: what matters more
rect(s, Inches(7.1), Inches(3.15), Inches(5.6), Inches(3.5), LIGHT); rect(s, Inches(7.1), Inches(3.15), Inches(5.6), Inches(0.09), ACC)
txt(s, Inches(7.35), Inches(3.32), Inches(5.1), Inches(0.4), [{"text": "WHAT MATTERS MORE THAN RAW N", "size": 12, "bold": True, "color": ACC}])
bullets(s, Inches(7.35), Inches(3.8), Inches(5.1), Inches(2.7),
    [("Run ≥2–3 backbone models, not one free model — the single biggest credibility gap", 0),
     ("Report variance / 95% CI over ≥3 seeds per cell", 0),
     ("A clean, auditable ground-truth check: exact-match (GSM8K), unit tests (HumanEval/MBPP), rubric (HANDBOOK)", 0),
     ("Pre-register the drift protocol (rounds, memory, metric) so the before→after is reproducible", 0)],
    size=12.5, gap=9, dot=ACC)
pagenum(s)

# ---- 38 models panel
s = slide()
header(s, "Synthesis · validation plan", "Which models to run the panel on", ACC)
txt(s, Inches(0.6), Inches(1.58), Inches(12.1), Inches(0.38),
    [{"text": "Span families × capability, overlap the paper for comparability, and pin dated snapshots (never “latest”):",
      "size": 12.5, "color": INK}])
cols = ["Model", "Family", "Role in the panel", "OpenRouter id (pin snapshot)"]
data = [
    ("GPT-4.1  (or GPT-5)", "OpenAI", "frontier; used in the paper", "openai/gpt-4.1"),
    ("Claude-Sonnet-4.5", "Anthropic", "frontier; paper used Claude-4-Sonnet", "anthropic/claude-sonnet-4.5"),
    ("Gemini-2.5-Flash", "Google", "cheap; paper found Gemini MOST susceptible", "google/gemini-2.5-flash"),
    ("Qwen3-235B-Instruct", "Qwen (open)", "often free; directly in the paper", "qwen/qwen3-235b-a22b"),
    ("Qwen2.5-7B / nemotron-lightning", "small", "scale contrast — weak models drift worse", "qwen/qwen2.5-7b-instruct"),
]
FAMCOL = {"OpenAI": RGBColor(0x0A, 0x7D, 0x6B), "Anthropic": RGBColor(0xC2, 0x41, 0x0C),
          "Google": RGBColor(0x2A, 0x5B, 0xD7), "Qwen (open)": RGBColor(0x6A, 0x4C, 0xA5),
          "small": GRAY}
nrow = len(data) + 1
gt = s.shapes.add_table(nrow, 4, Inches(0.6), Inches(2.0), Inches(12.1), Inches(0.46) * nrow).table
for c, wdt in enumerate([3.2, 1.9, 4.5, 2.5]):
    gt.columns[c].width = Inches(wdt)
for c, ct in enumerate(cols):
    cell = gt.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = ct
    r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
for ri, row in enumerate(data, 1):
    for c, val in enumerate(row):
        cell = gt.cell(ri, c); cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if ri % 2 else LIGHT
        p = cell.text_frame.paragraphs[0]; rr = p.add_run(); rr.text = val
        rr.font.size = Pt(10); rr.font.name = FONT; rr.font.color.rgb = INK
        if c == 0: rr.font.bold = True; rr.font.color.rgb = NAVY
        if c == 1: rr.font.bold = True; rr.font.color.rgb = FAMCOL.get(val, INK)
        if c == 3: rr.font.color.rgb = RGBColor(0x11, 0x55, 0xCC)
# free-only panel box (left)
rect(s, Inches(0.6), Inches(4.95), Inches(6.0), Inches(2.0), RGBColor(0xE2, 0xF1, 0xEE)); rect(s, Inches(0.6), Inches(4.95), Inches(6.0), Inches(0.09), RGBColor(0x2A, 0x9D, 0x8F))
txt(s, Inches(0.85), Inches(5.1), Inches(5.5), Inches(0.35), [{"text": "FREE-ONLY PANEL (runnable now, no spend)", "size": 11.5, "bold": True, "color": RGBColor(0x1F, 0x6F, 0x63)}])
bullets(s, Inches(0.85), Inches(5.5), Inches(5.5), Inches(1.4),
    [("nvidia/nemotron-3.5-lightning:free  —  NVIDIA, small (already validated)", 0),
     ("qwen/qwen3.8-27b:free  or  z-ai/glm-5.2:free  —  open-weight, mid", 0),
     ("google/gemma-4-31b-it:free  —  Google family", 0),
     ("free tier rotates & rate-limits — verify live before the run", 0)],
    size=11, gap=6, dot=RGBColor(0x2A, 0x9D, 0x8F))
# ground rules box (right)
rect(s, Inches(6.72), Inches(4.95), Inches(6.0), Inches(2.0), LIGHT); rect(s, Inches(6.72), Inches(4.95), Inches(6.0), Inches(0.09), ACC)
txt(s, Inches(6.97), Inches(5.1), Inches(5.5), Inches(0.35), [{"text": "GROUND RULES", "size": 11.5, "bold": True, "color": ACC}])
bullets(s, Inches(6.97), Inches(5.5), Inches(5.55), Inches(1.4),
    [("GSM8K / HumanEval / MBPP have PROGRAMMATIC ground truth → backbone is the only variable, no judge confound", 0),
     ("RedCode-Gen / AgentNet need a judge → hold ONE fixed strong judge constant across all backbones", 0),
     ("Report variance / 95% CI over ≥3 seeds; cost on the cheap tier ≈ $5–15", 0)],
    size=11, gap=7, dot=ACC)
pagenum(s)

# ============================================================ PART VII progress report
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress_slides.py"), encoding="utf-8").read(), "progress_slides.py", "exec"))

# ============================================================ 34 takeaways
s = slide()
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, 0, SW, Inches(0.16), CORAL)
txt(s, Inches(0.8), Inches(0.7), Inches(11), Inches(0.8),
    [{"text": "Key takeaways", "size": 32, "bold": True, "color": WHITE, "font": FONTL}])
rect(s, Inches(0.82), Inches(1.55), Inches(1.4), Pt(3), TEAL)
pts = [("Misevolution is real and pervasive", "Self-improvement can erode safety across model, memory, tool, and workflow — even on top-tier LLMs.", TEAL),
       ("It's a NEW kind of risk", "Emergent over time, self-generated, hard to control with training data, and spread across many components.", TEAL),
       ("I reproduced 3 of 4 pathways with free models", "Memory 76.9% unsafe · Tool 52% unsafe · Workflow refusal 100%→78% — same effects as the paper.", TEAL),
       ("The 4th needs a bigger GPU", "Model misevolution requires local 7B–70B checkpoints; wired and ready for ≥16 GB hardware.", TEAL),
       ("Current mitigations are only partial", "Safer self-evolving agents need new safety frameworks — an open research problem.", TEAL),
       ("Beyond the paper: contagion is real but model-dependent", "Early demos used hand-written memory. A controlled study on 6 models (Part VII): no reward-driven drift, but shared notes spread leniency between roles in some models.", ACC)]
y=Inches(1.78)
for i,(t,d,bc) in enumerate(pts):
    rect(s, Inches(0.8), y, Inches(0.14), Inches(0.78), bc)
    txt(s, Inches(1.15), y, Inches(11.4), Inches(0.78),
        [{"text": t, "size": 16.5, "bold": True, "color": WHITE},
         {"text": d, "size": 12.5, "color": RGBColor(0xB9,0xC2,0xD4), "space_before": 2}])
    y+=Inches(0.88)
pagenum(s, 34)

# ============================================================ 27 thanks
s = slide()
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, SH-Inches(0.22), SW, Inches(0.22), CORAL)
rect(s, 0, Inches(0), SW, Inches(0.22), TEAL)
txt(s, Inches(0.9), Inches(2.7), Inches(11.5), Inches(1.2),
    [{"text": "Thank you", "size": 46, "bold": True, "color": WHITE, "font": FONTL}])
txt(s, Inches(0.92), Inches(3.9), Inches(11.5), Inches(1.6),
    [{"text": "Paper:  “Your Agent May Misevolve: Emergent Risks in Self-Evolving LLM Agents”, ICLR 2026", "size": 15, "color": RGBColor(0xC7,0xD0,0xE0)},
     {"text": "Reproduction:  minimax-m3:free  ·  Memory + Tool + Workflow pathways  ·  results in RESULTS/FINDINGS.md", "size": 15, "color": RGBColor(0xC7,0xD0,0xE0), "space_before": 6},
     {"text": "Code, patches & data:  RESULTS/  and  CHANGES_FREE_MODELS.md", "size": 15, "color": TEAL, "space_before": 6}])
pagenum(s, 35)

out = "Misevolution_BTP_Presentation.pptx"
prs.save(out)
print("Saved", out, "with", len(prs.slides._sldIdLst), "slides")
