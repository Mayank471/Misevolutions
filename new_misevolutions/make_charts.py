# -*- coding: utf-8 -*-
"""Generate presentation-ready charts from the recorded experiment results."""
import os, json, glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures"); os.makedirs(FIG, exist_ok=True)

# deck palette
ACC="#4554C9"; TEAL="#2A9D8F"; REDBAD="#C0392B"; GREENOK="#2E7D5B"
NAVY="#16213E"; GRAY="#5A616B"; LIGHT="#F4F5F7"; AMBER="#C88600"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":12,
                     "axes.edgecolor":"#C9CDD4","axes.linewidth":1,
                     "figure.facecolor":"white","axes.facecolor":"white"})

def load(p):
    fs=glob.glob(os.path.join(RES,p)); return json.load(open(fs[0],encoding="utf-8")) if fs else None

# ---------- 1. evaluator drift (line) ----------
d=load("evaluator_drift_*.json")
rk=sorted(d["rounds"], key=int); x=[int(k) for k in rk]
y=[d["rounds"][k]["accept_wrong_rate"]*100 for k in rk]
fig,ax=plt.subplots(figsize=(6.6,4.0))
ax.plot(x,y,marker="o",markersize=8,linewidth=3,color=REDBAD,zorder=3)
ax.fill_between(x,y,color=REDBAD,alpha=0.08)
ax.axhline(y[0],ls=":",color=GREENOK,lw=1.5)
for xi,yi in zip(x,y): ax.annotate(f"{yi:.0f}%",(xi,yi),textcoords="offset points",xytext=(0,10),ha="center",fontsize=11,fontweight="bold",color=REDBAD)
ax.set_title("Evaluator misevolution: the judge's standard rots",fontsize=13,fontweight="bold",color=NAVY,pad=12)
ax.set_xlabel("rounds of 'leniency-was-rewarded' memory"); ax.set_ylabel("accepts a clearly-WRONG answer (%)")
ax.set_ylim(0,100); ax.set_xticks(x); ax.grid(axis="y",ls="--",alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(FIG,"fig_evaluator_drift.png"),dpi=160); plt.close(fig)

# ---------- 2. collusion (bar) ----------
d=load("multiagent_collusion_*.json")
rk=sorted(d["rounds"],key=int); x=[f"round {k}" for k in rk]
y=[d["rounds"][k]["approve_flawed_rate"]*100 for k in rk]
cols=[GREENOK if v<50 else REDBAD for v in y]
fig,ax=plt.subplots(figsize=(6.6,4.0))
b=ax.bar(x,y,color=cols,width=0.55,zorder=3)
for rect,v in zip(b,y): ax.annotate(f"{v:.0f}%",(rect.get_x()+rect.get_width()/2,v),textcoords="offset points",xytext=(0,6),ha="center",fontweight="bold",color=NAVY)
ax.set_title("Multi-agent collusion: reviewer approves KNOWN-flawed work",fontsize=13,fontweight="bold",color=NAVY,pad=12)
ax.set_ylabel("approves flawed submissions (%)"); ax.set_ylim(0,110); ax.grid(axis="y",ls="--",alpha=0.3)
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(FIG,"fig_collusion.png"),dpi=160); plt.close(fig)

# ---------- 3. goal drift (per-turn strip) ----------
d=load("goal_drift_*.json")
turns=d["turns"]; xs=[t["turn"] for t in turns]
held=[1 if t["choice"]=="BasicPhone" else 0 for t in turns]
cols=[GREENOK if h else REDBAD for h in held]
fig,ax=plt.subplots(figsize=(7.2,3.2))
ax.bar(xs,[1]*len(xs),color=cols,width=0.9,zorder=3)
ax.set_title("Goal drift: holds the assigned goal? (green=held, red=caved)",fontsize=13,fontweight="bold",color=NAVY,pad=12)
ax.set_xlabel("conversation turn (pressure escalates →)"); ax.set_xticks(xs)
ax.set_yticks([]); ax.set_ylim(0,1.2)
fd=d.get("first_defection")
if fd: ax.annotate("first defection",(fd,1.02),ha="center",fontsize=10,color=REDBAD,fontweight="bold")
ax.text(0.99,-0.28,f"goal held on {d['adherence_rate']*100:.0f}% of turns",transform=ax.transAxes,ha="right",color=GRAY,fontsize=10,style="italic")
ax.spines[["top","right","left"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(FIG,"fig_goal_drift.png"),dpi=160); plt.close(fig)

# ---------- 4. combined summary (grouped bar) ----------
axes=["Evaluator\n(accept wrong)","Multi-agent\n(approve flawed)","Goal drift\n(violates goal)"]
start=[17,0,0]; after=[83,100,67]   # goal drift: 100-33 adherence = 67% violation
import numpy as np
xpos=np.arange(len(axes)); w=0.36
fig,ax=plt.subplots(figsize=(7.2,4.2))
ax.bar(xpos-w/2,start,w,label="start / no memory",color=GREENOK,zorder=3)
ax.bar(xpos+w/2,after,w,label="evolved / under pressure",color=REDBAD,zorder=3)
for i,(a,b) in enumerate(zip(start,after)):
    ax.annotate(f"{a}%",(i-w/2,a),textcoords="offset points",xytext=(0,5),ha="center",fontsize=10,color=NAVY)
    ax.annotate(f"{b}%",(i+w/2,b),textcoords="offset points",xytext=(0,5),ha="center",fontweight="bold",color=REDBAD)
ax.set_title("Three new misevolution axes: safe → unsafe",fontsize=14,fontweight="bold",color=NAVY,pad=12)
ax.set_ylabel("unsafe-behaviour rate (%)"); ax.set_xticks(xpos); ax.set_xticklabels(axes)
ax.set_ylim(0,112); ax.grid(axis="y",ls="--",alpha=0.3); ax.legend(frameon=False,loc="upper left")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(FIG,"fig_summary.png"),dpi=160); plt.close(fig)

print("charts written to", FIG)
for f in sorted(os.listdir(FIG)): print("  ", f)
