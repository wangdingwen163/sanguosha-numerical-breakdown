# -*- coding: utf-8 -*-
"""
生成 P0/P1 增补图：fig6 平衡方案对照图（PNG 300dpi，中文字体 Microsoft YaHei）

运行：python scripts/make_charts_p0.py
输入：data/balance_scenarios.json
输出：charts/fig6_平衡方案对照图.png

三个子图：
 (a) 方案A：减杀 vs 加闪 —— 柱=起手无闪率(%)，折线=对局时长变化%
 (b) 方案C：【杀】使用上限 1/2/3 —— 柱=静态期望输出，折线=供给约束下的对局时长代理(轮)
 (c) 身份局：主公手牌 2/4/5/6/8 —— 柱=盲打EV(张牌)，标注保本手牌 4.25 张

注意：本脚本不改动 make_charts.py 与 fig1~fig5。
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# ---------- 中文字体 ----------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DengXian"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#444444"
plt.rcParams["axes.linewidth"] = 0.8

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
CHARTS = os.path.join(HERE, "..", "charts")
os.makedirs(CHARTS, exist_ok=True)

BAR = "#2E86C1"
BAR2 = "#7D3C98"
LINE = "#C0392B"
GREY = "#7F8C8D"
INK = "#1B2631"


def load(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    bs = load("balance_scenarios.json")

    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6))
    fig.suptitle("图6 · 平衡方案对照：改动方向、副作用与身份局收益结构",
                 fontsize=15.5, fontweight="bold", color=INK, x=0.012, ha="left", y=1.02)

    # ---------------- (a) 方案A ----------------
    ax = axes[0]
    a = bs["方案A_减杀还是加闪"]["对照表"]
    labels = ["基准\n(杀44/闪24)", "减杀38\n(A1)", "加闪30\n(A2)", "同时做\n(杀38/闪30)"]
    noshan = [r["起手4张无闪%"] for r in a]
    dur = [r.get("对局时长变化%", 0.0) for r in a]
    x = range(len(labels))
    b1 = ax.bar(x, noshan, width=0.55, color=BAR, alpha=0.9, label="起手 4 张无闪率（%）")
    for xi, v in zip(x, noshan):
        ax.text(xi, v + 0.6, "%.2f" % v, ha="center", va="bottom", fontsize=9.2,
                color=INK, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9.2)
    ax.set_ylabel("起手 4 张无闪率（%）", fontsize=10.5, color=BAR)
    ax.set_ylim(0, 62)
    ax.yaxis.set_major_locator(MultipleLocator(10))

    ax2 = ax.twinx()
    l1, = ax2.plot(list(x), dur, marker="o", markersize=6.5, linewidth=2.0,
                   color=LINE, label="对局时长变化（%）")
    for xi, v in zip(x, dur):
        ax2.annotate("%+.2f%%" % v if v else "0", (xi, v), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=9.0, color=LINE)
    ax2.set_ylabel("对局时长变化（%）", fontsize=10.5, color=LINE)
    ax2.set_ylim(-8, 90)
    ax2.axhline(0, color=GREY, linewidth=0.9, linestyle=":")

    ax.set_title("A. 减杀动不了「开局没闪」，加闪才行——但两者都拖长对局",
                 fontsize=11.2, loc="left", pad=10)
    ax.legend([b1, l1], ["起手 4 张无闪率（%）", "对局时长变化（%）"],
              fontsize=8.8, frameon=False, loc="upper left")

    # ---------------- (b) 方案C ----------------
    ax = axes[1]
    c = bs["方案C_杀的使用上限"]
    stat = c["静态结果"]
    sup = c["供给约束结果"]
    labels = ["上限 1 张\n(现行)", "上限 2 张", "上限 3 张"]
    out = [r["静态期望输出(沿用固定命中率)"] for r in stat]
    rounds = [r["对局时长代理(供给约束)"] for r in sup]
    x = range(len(labels))
    b2 = ax.bar(x, out, width=0.55, color=BAR2, alpha=0.9, label="静态期望输出（点/回合）")
    for xi, v in zip(x, out):
        ax.text(xi, v + 0.012, "%.4f" % v, ha="center", va="bottom", fontsize=9.2,
                color=INK, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9.2)
    ax.set_ylabel("静态期望输出（点/回合）", fontsize=10.5, color=BAR2)
    ax.set_ylim(0, 0.68)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))

    ax2 = ax.twinx()
    l2, = ax2.plot(list(x), rounds, marker="s", markersize=6.5, linewidth=2.0,
                   color=LINE, label="供给约束下的对局时长代理（轮）")
    for xi, v in zip(x, rounds):
        ax2.annotate("%.1f 轮" % v, (xi, v), textcoords="offset points",
                     xytext=(0, 10), ha="center", fontsize=9.0, color=LINE)
    ax2.set_ylabel("供给约束下的对局时长代理（轮）", fontsize=10.5, color=LINE)
    ax2.set_ylim(0, 18)

    ax.set_title("B. 放开上限：输出涨了，但对局被压到 7 轮——崩在闪供给",
                 fontsize=11.2, loc="left", pad=10)
    ax.legend([b2, l2], ["静态期望输出（点/回合）", "供给约束下的对局时长代理（轮）"],
              fontsize=8.8, frameon=False, loc="upper left")

    # ---------------- (c) 身份局 ----------------
    ax = axes[2]
    ident = bs["身份局收益结构"]["盲打模型"]
    rows = ident["表格"]
    labels = [str(r["主公手牌数"]) for r in rows]
    ev = [r["盲打一个未知目标的EV(张牌)"] for r in rows]
    x = range(len(labels))
    colors = ["#27AE60" if v >= 0 else "#C0392B" for v in ev]
    b3 = ax.bar(x, ev, width=0.55, color=colors, alpha=0.9)
    for xi, v in zip(x, ev):
        off = 0.05 if v >= 0 else -0.05
        va = "bottom" if v >= 0 else "top"
        ax.text(xi, v + off, "%+.3f" % v, ha="center", va=va, fontsize=9.2,
                color=INK, fontweight="bold")
    ax.axhline(0, color=GREY, linewidth=1.4, linestyle="-")
    ax.text(len(labels) - 1, 0.06, "EV = 0（保本线）", ha="right", va="bottom",
            fontsize=9.0, color=GREY)
    ax.set_xticks(list(x))
    ax.set_xticklabels(["%s 张" % t for t in labels], fontsize=9.2)
    ax.set_xlabel("主公手牌数（张）", fontsize=10.5)
    ax.set_ylabel("盲打一个未知目标的 EV（张牌）", fontsize=10.5)
    ax.set_ylim(-1.35, 0.95)
    ax.yaxis.set_major_locator(MultipleLocator(0.25))

    ax.annotate("保本手牌 4.25 张",
                xy=(1.35, 0.0), xytext=(0.35, -0.85),
                arrowprops=dict(arrowstyle="->", color=INK, linewidth=1.4),
                fontsize=10.2, color=INK, fontweight="bold")
    ax.axvline(1.35, color=INK, linewidth=1.2, linestyle="--", alpha=0.75)

    ax.set_title("C. 手牌少时盲打小赚、手牌多时倒亏——期望被焊在 0 附近",
                 fontsize=11.2, loc="left", pad=10)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    p = os.path.join(CHARTS, "fig6_平衡方案对照图.png")
    fig.savefig(p, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[已生成] %s" % os.path.normpath(p))

    print("(b) 供给约束下对局时长代理(轮): %s" % rounds)
    print("(c) 保本手牌数: %s" % ident["保本手牌数"])


if __name__ == "__main__":
    main()
