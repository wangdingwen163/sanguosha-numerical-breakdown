# -*- coding: utf-8 -*-
"""
生成 5 张图表（PNG 300dpi，中文字体 Microsoft YaHei）

运行：python scripts/make_charts.py
输入：data/deck_counts.json, data/probability_results.json, data/curves.json, data/general_matrix.json
输出：charts/fig1..fig5*.png
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

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

C = {
    "basic": "#C0392B",   # 基本牌
    "trick": "#2E86C1",   # 锦囊牌
    "equip": "#7D3C98",   # 装备牌
    "std": "#F5B041",
    "jz": "#5DADE2",
    "grey": "#7F8C8D",
    "ink": "#1B2631",
    "accent": "#1E8449",
}


def load(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as f:
        return json.load(f)


def save(fig, name):
    p = os.path.join(CHARTS, name)
    fig.savefig(p, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[已生成] {os.path.normpath(p)}")


# ==========================================================================
# fig1 牌堆结构树状图
# ==========================================================================
def fig1():
    deck = load("deck_counts.json")["统计"]
    fig = plt.figure(figsize=(13.2, 7.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 108)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, fs=9, tc="white", bold=False):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.15,rounding_size=0.6",
                           linewidth=1.0, edgecolor=ec, facecolor=fc, zorder=3)
        ax.add_patch(b)
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc, zorder=4,
                fontweight="bold" if bold else "normal", linespacing=1.5)

    def link(x1, y1, x2, y2):
        ax.add_line(plt.Line2D([x1, x2], [y1, y2], color="#95A5A6", lw=1.1, zorder=1,
                               solid_capstyle="round"))

    total = deck["合计"]["总数"]
    box(11, 50, 17, 9, f"身份局牌堆\n{total} 张", C["ink"], C["ink"], fs=12, bold=True)

    box(36, 71, 21, 10, f"标准版（含 4 张 EX）\n{deck['标准版(含EX)']['总数']} 张",
        C["std"], "#B9770E", fs=10.5, tc="#3E2723", bold=True)
    box(36, 28, 21, 10, f"军争篇\n{deck['军争篇']['总数']} 张",
        C["jz"], "#1F618D", fs=10.5, tc="#0B2E4F", bold=True)
    link(19.5, 52, 25.5, 71)
    link(19.5, 48, 25.5, 28)

    cats = [("基本牌", C["basic"]), ("锦囊牌", C["trick"]), ("装备牌", C["equip"])]
    ys_std = [86, 71, 56]
    ys_jz = [42, 27, 12]
    for (cat, col), y0, y1 in zip(cats, ys_std, ys_jz):
        n0 = deck["标准版(含EX)"]["分类"][cat]
        n1 = deck["军争篇"]["分类"][cat]
        box(61, y0, 15, 8, f"{cat} {n0}", col, col, fs=10)
        box(61, y1, 15, 8, f"{cat} {n1}", col, col, fs=10, tc="#EAF2F8")
        link(46.5, 71, 53.5, y0)
        link(46.5, 28, 53.5, y1)

    def detail(x, y, lines, col, fs=8.2, w=25):
        h = 3.2 + 3.5 * (len(lines) - 1)
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.2,rounding_size=0.5",
                           linewidth=0.9, edgecolor=col, facecolor="white", zorder=3,
                           linestyle=(0, (4, 2)))
        ax.add_patch(b)
        ax.text(x, y, "\n".join(lines), ha="center", va="center", fontsize=fs,
                color=C["ink"], zorder=4, linespacing=1.6)

    detail(83, 90, ["杀 30 · 闪 15 · 桃 8"], C["basic"])
    detail(83, 74, ["过河拆桥6 顺手牵羊5", "无中生有4 无懈可击4",
                    "南蛮3 决斗3 借刀杀人2", "乐不思蜀3 闪电2 桃园1 万箭1"], C["trick"])
    detail(83, 58, ["武器10 防具3 坐骑6"], C["equip"])
    link(68.5, 86, 70.5, 90)
    link(68.5, 71, 70.5, 74)
    link(68.5, 56, 70.5, 58)

    detail(83, 40, ["火杀5 · 雷杀9 · 闪9", "桃4 · 酒5", "→ 基本牌共 32"], C["basic"])
    detail(83, 26, ["铁索连环6 无懈可击3", "火攻3 兵粮寸断2"], C["trick"])
    detail(83, 13, ["古锭刀1 朱雀羽扇1", "藤甲2 白银狮子1 骅骝1"], C["equip"])
    link(68.5, 42, 70.5, 40)
    link(68.5, 27, 70.5, 26)
    link(68.5, 12, 70.5, 13)

    keyp = load("probability_results.json")["牌堆张数"]
    ax.text(50, 100.5,
            f"核心派生：杀系 {keyp['杀系(含属性杀)']} 张（普通30＋火5＋雷9） · "
            f"闪 {keyp['闪']} 张 · 桃 {keyp['桃']} 张 · 无懈可击 {keyp['无懈可击']} 张 ｜ "
            f"杀 : 闪 = {keyp['杀系(含属性杀)']/keyp['闪']:.2f} : 1",
            ha="center", va="center", fontsize=11, color=C["accent"], fontweight="bold")

    ax.text(50, 3.0,
            "数据来源：三国杀WIKI_BWIKI《标准包卡牌》《军争篇卡牌》逐张表（本图由 scripts/deck_data.py 统计生成）",
            ha="center", va="center", fontsize=8, color=C["grey"])
    ax.text(1, 106.5, "图1  三国杀身份局牌堆结构（标准版108＋军争篇52＝160张）",
            ha="left", va="center", fontsize=13.5, fontweight="bold", color=C["ink"])
    save(fig, "fig1_牌堆结构树状图.png")


# ==========================================================================
# fig2 关键牌概率与期望
# ==========================================================================
def fig2():
    pr = load("probability_results.json")
    rows = {r["牌名"]: r for r in pr["起手与累计摸牌概率"]}
    order = ["杀系(含属性杀)", "闪", "桃", "无懈可击", "借刀杀人",
             "武器", "坐骑合计", "过河拆桥", "顺手牵羊", "无中生有"]
    labels = [o.replace("(含属性杀)", "\n(含属性杀)") for o in order]

    fig = plt.figure(figsize=(14.5, 8.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.05], hspace=0.32)

    ax1 = fig.add_subplot(gs[0])
    x = np.arange(len(order))
    w = 0.27
    v1 = [rows[o]["起手4张至少1张%"] for o in order]
    v2 = [rows[o]["首轮6张至少1张%"] for o in order]
    v3 = [rows[o]["第3回合10张至少1张%"] for o in order]
    b1 = ax1.bar(x - w, v1, w, label="起手4张至少1张", color="#2874A6")
    b2 = ax1.bar(x, v2, w, label="首轮6张至少1张", color="#5DADE2")
    b3 = ax1.bar(x + w, v3, w, label="第3回合累计10张至少1张", color="#AED6F1")
    for bars in (b1, b2, b3):
        for b in bars:
            ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2,
                     f"{b.get_height():.0f}", ha="center", va="bottom", fontsize=7.4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.6)
    ax1.set_ylabel("抽到至少 1 张的概率（%）", fontsize=10)
    ax1.set_ylim(0, 108)
    ax1.legend(fontsize=9, ncol=3, frameon=False, loc="upper right")
    ax1.set_title("A. 关键牌「抽得到」的概率（超几何分布，牌堆 160 张，不放回）",
                  fontsize=11.5, color=C["ink"], loc="left", pad=8)
    ax1.grid(axis="y", ls=":", color="#B0B0B0", alpha=0.6)
    ax1.set_axisbelow(True)
    ax1.spines[["top", "right"]].set_visible(False)

    ax2 = fig.add_subplot(gs[1])
    ax2.axis("off")
    ev = pr["单卡期望收益(作者参数模型)"]["按k取值的结果"]
    names = [r["牌"] for r in ev["k=1.5"]]
    formulas = [r["公式"] for r in ev["k=1.5"]]
    col_k1 = [r["净收益(张)"] for r in ev["k=1.0"]]
    col_k15 = [r["净收益(张)"] for r in ev["k=1.5"]]
    col_k2 = [r["净收益(张)"] for r in ev["k=2.0"]]
    cell = [[n, f, f"{a:+.3f}", f"{b:+.3f}", f"{c:+.3f}"]
            for n, f, a, b, c in zip(names, formulas, col_k1, col_k15, col_k2)]
    tbl = ax2.table(cellText=cell,
                    colLabels=["牌", "净收益公式（单位：张牌）", "k=1", "k=1.5", "k=2"],
                    colWidths=[0.15, 0.39, 0.1533, 0.1533, 0.1533],
                    loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.2)
    tbl.scale(1, 1.55)
    for (r, c), cellobj in tbl.get_celld().items():
        cellobj.set_edgecolor("#BDC3C7")
        if r == 0:
            cellobj.set_facecolor("#34495E")
            cellobj.set_text_props(color="white", fontweight="bold")
        elif c == 0:
            cellobj.set_facecolor("#ECF0F1")
            cellobj.set_text_props(fontweight="bold")
        else:
            val = None
            try:
                val = float(cell[r - 1][c])
            except Exception:
                pass
            if val is not None:
                if val > 0.05:
                    cellobj.set_facecolor("#D4EFDF")
                elif val < -0.05:
                    cellobj.set_facecolor("#FADBD8")
                else:
                    cellobj.set_facecolor("#FDEBD0")
    ax2.set_title("B. 单张牌「期望收益」（作者参数模型：k = 1 点体力折算的牌数；绿=正 红=负 橙=中性）\n"
                  "　  关键中间量：对手 4 张手牌时被闪概率 48.15%，故【杀】命中率 51.85%",
                  fontsize=11.5, color=C["ink"], loc="left", pad=16)
    ax2.text(0.5, -0.09,
             "口径：概率为超几何精确值（scripts/calc_probability.py）；期望收益为作者显式假设的参数模型，非官方数值。",
             ha="center", va="top", fontsize=8.2, color=C["grey"], transform=ax2.transAxes)
    save(fig, "fig2_关键牌概率与期望.png")


# ==========================================================================
# fig3 手牌输出期望曲线 + 边际收益递减
# ==========================================================================
def fig3():
    cv = load("curves.json")
    hs = cv["手牌曲线"]
    m = [r["手牌数"] for r in hs]
    p_sha = [r["P(至少1张杀)%"] for r in hs]
    p_shan = [r["P(至少1张闪)%"] for r in hs]
    p_tao = [r["P(至少1张桃)%"] for r in hs]
    d_sha = [r["边际:P(能出杀)增量(百分点)"] for r in hs]
    d_shan = [r["边际:P(有闪)增量(百分点)"] for r in hs]
    d_tao = [r["边际:P(有桃)增量(百分点)"] for r in hs]
    waste = [r["溢出率%"] for r in hs]
    out = {r["我的手牌数"]: r["对手4张手牌时的期望伤害"] for r in cv["输出期望"]["结果"]}

    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4))

    ax = axes[0]
    ax.plot(m, p_sha, "-o", color="#C0392B", lw=2, ms=5, label="P(手中有【杀】)")
    ax.plot(m, p_shan, "-s", color="#2E86C1", lw=2, ms=5, label="P(手中有【闪】)")
    ax.plot(m, p_tao, "-^", color="#1E8449", lw=2, ms=5, label="P(手中有【桃】)")
    ax.axvline(4, color=C["grey"], ls="--", lw=1)
    ax.text(4.12, 8, "起手 4 张", fontsize=8.5, color=C["grey"])
    ax.axhline(72.77, color="#C0392B", ls=":", lw=1, alpha=0.7)
    ax.text(5.6, 74.6, "起手有杀 72.8%", fontsize=8.4, color="#C0392B")
    ax.axhline(48.15, color="#2E86C1", ls=":", lw=1, alpha=0.7)
    ax.text(5.6, 39.0, "起手有闪 48.2%（一半以上的人没有闪）", fontsize=8.4, color="#2E86C1")
    ax.set_xlabel("手牌数（张）", fontsize=10)
    ax.set_ylabel("概率（%）", fontsize=10)
    ax.set_title("A. 手牌越多，越接近「必有」——但收敛很快", fontsize=11.2, loc="left")
    ax.set_ylim(0, 105)
    ax.legend(fontsize=9, frameon=True, framealpha=0.95, edgecolor="#CCCCCC",
              loc="lower right")
    ax.grid(ls=":", color="#B0B0B0", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    ax.plot(m, d_sha, "-o", color="#C0392B", lw=2, ms=4.5, label="ΔP(能出杀)")
    ax.plot(m, d_shan, "-s", color="#2E86C1", lw=2, ms=4.5, label="ΔP(有闪)")
    ax.plot(m, d_tao, "-^", color="#1E8449", lw=2, ms=4.5, label="ΔP(有桃)")
    ax.fill_between(m, d_sha, color="#C0392B", alpha=0.08)
    ax.set_xlabel("手牌数（张）", fontsize=10)
    ax.set_ylabel("每多摸 1 张带来的概率增量（百分点）", fontsize=10)
    ax.set_title("B. 边际收益递减：第 10 张牌几乎买不到新能力", fontsize=11.2, loc="left")
    ax.annotate("第1张 → +27.5pp\n（从「不能出杀」到「可能出杀」）",
                xy=(1, d_sha[0]), xytext=(2.9, 23.5),
                arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.2),
                fontsize=8.6, color="#C0392B")
    ax.annotate("第12张 → +0.75pp\n（几乎无增量）",
                xy=(12, d_sha[-1]), xytext=(6.6, 6.0),
                arrowprops=dict(arrowstyle="->", color="#7F8C8D", lw=1.2),
                fontsize=8.6, color="#7F8C8D")
    ax.legend(fontsize=9, frameon=True, framealpha=0.95, edgecolor="#CCCCCC",
              loc="upper right")
    ax.grid(ls=":", color="#B0B0B0", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    xs = sorted(out)
    ys = [out[k] for k in xs]
    ax.bar(m, [w / 100 for w in waste], width=0.55, color="#F5B041", alpha=0.45,
           label="「用不掉的杀」溢出率（右轴）")
    ax.plot(xs, ys, "-o", color="#7D3C98", lw=2, ms=5, label="期望伤害/回合（对手4张手牌）")
    ax.set_xlabel("手牌数（张）", fontsize=10)
    ax.set_ylabel("期望伤害（点/回合）", fontsize=10)
    ax.set_ylim(0, 0.62)
    ax2 = ax.twinx()
    ax2.set_ylim(0, 115)
    ax2.set_ylabel("溢出率（%）", fontsize=10, color="#B9770E")
    ax2.tick_params(axis="y", colors="#B9770E")
    ax2.spines["top"].set_visible(False)
    ax.axvline(4, color=C["grey"], ls="--", lw=1)
    ax.text(4.35, 0.545, "起手 4 张：期望伤害 0.377", fontsize=8.6, color="#7D3C98",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#D2B4DE", lw=0.8))
    ax.set_title("C. 每回合只能出 1 张【杀】→ 多出来的杀全部作废", fontsize=11.2, loc="left")
    h1, l1 = ax.get_legend_handles_labels()
    ax.legend(h1, l1, fontsize=8.6, frameon=True, framealpha=0.95,
              edgecolor="#CCCCCC", loc="upper left")
    ax.grid(ls=":", color="#B0B0B0", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top"]].set_visible(False)

    fig.suptitle("图3  手牌输出期望曲线与边际收益递减（牌堆160张：杀系44 / 闪24 / 桃12）",
                 fontsize=13.5, fontweight="bold", color=C["ink"], x=0.012, ha="left", y=1.03)
    fig.text(0.012, -0.075,
             "由 scripts/calc_curves.py 生成。模型：每回合摸2张；出牌阶段默认限1张【杀】；弃牌阶段手牌上限=当前体力值。"
             "「溢出率」= 抽到却因次数上限用不掉的【杀】占抽到【杀】的比例。",
             fontsize=8.2, color=C["grey"], ha="left")
    fig.tight_layout()
    save(fig, "fig3_手牌输出期望曲线.png")


# ==========================================================================
# fig4 反馈循环图
# ==========================================================================
def fig4():
    fig, ax = plt.subplots(figsize=(14.0, 9.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def node(x, y, w, h, title, sub, fc, ec, fs=12.5, subfs=9.0, tc="white"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.5,rounding_size=1.4",
                                    linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=3))
        ax.text(x, y + h * 0.24, title, ha="center", va="center", fontsize=fs,
                color=tc, fontweight="bold", zorder=4)
        ax.text(x, y - h * 0.24, sub, ha="center", va="center", fontsize=subfs,
                color=tc, zorder=4, linespacing=1.5)

    def arrow(p1, p2, color, label=None, rad=0.0, lw=2.2, ls="-", lx=0, ly=0, fs=9.2):
        ax.add_patch(FancyArrowPatch(p1, p2, connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-|>", mutation_scale=20,
                                     linewidth=lw, color=color, zorder=2, linestyle=ls))
        if label:
            mx, my = (p1[0] + p2[0]) / 2 + lx, (p1[1] + p2[1]) / 2 + ly
            ax.text(mx, my, label, ha="center", va="center", fontsize=fs,
                    color=color, fontweight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=color, lw=0.7))

    # ---- 主循环（四个节点） ----
    node(25, 78, 23, 13, "摸　牌", "每回合摸牌阶段 +2 张\n（牌是唯一的行动资源）",
         "#1F618D", "#154360")
    node(75, 78, 23, 13, "出　牌", "手牌 → 【杀】/锦囊/装备\n默认每回合限 1 张【杀】",
         "#7D3C98", "#5B2C6F")
    node(75, 40, 23, 13, "压　制", "造成伤害 → 对方体力↓\n→ 对方手牌上限↓（弃牌变多）",
         "#C0392B", "#7B241C")
    node(25, 40, 23, 13, "收　益", "击杀反贼 +3 张牌\n压制 = 更多资源",
         "#1E8449", "#145A32")

    arrow((36.5, 78), (63.5, 78), "#1F618D", "资源 → 行动", ly=3.6)
    arrow((75, 71.5), (75, 46.5), "#7D3C98", "行动 → 结果", lx=12.2)
    arrow((63.5, 40), (36.5, 40), "#C0392B", "优势 → 滚雪球", ly=-3.6)
    arrow((25, 46.5), (25, 71.5), "#1E8449", "奖励 → 再投入", lx=-12.2)

    # ---- 循环中心 ----
    ax.text(50, 62.0, "正 反 馈 循 环\n（赢的人越赢）", ha="center", va="center",
            fontsize=13.5, fontweight="bold", color="#7B241C", zorder=5,
            bbox=dict(boxstyle="round,pad=0.6", fc="#FDEDEC", ec="#C0392B", lw=1.8))
    ax.text(50, 53.0, "伤害 → 体力↓ → 手牌上限↓\n→ 防御牌被迫弃掉 → 更容易被打",
            ha="center", va="center", fontsize=9.4, color="#7B241C", zorder=5,
            linespacing=1.6)

    # ---- 三条刹车（底部横排） ----
    brakes = [
        ("刹车①  每回合 1 张【杀】",
         "出牌阶段默认只能使用 1 张【杀】\n→ 抽到再多【杀】也用不掉\n（【诸葛连弩】是唯一的例外通道）"),
        ("刹车②  手牌上限 = 体力值",
         "弃牌阶段必须弃到「体力值」张\n→ 不能囤牌过冬\n→ 资源无法无限叠加"),
        ("刹车③  防御牌天然稀缺",
         "闪 24 张 vs 杀系 44 张（1 : 1.83）\n→ 起手有闪只有 48.15%\n→ 被闪掉是常态，不是意外"),
    ]
    xs = [19.5, 50, 80.5]
    for (t, s), cx in zip(brakes, xs):
        ax.add_patch(FancyBboxPatch((cx - 14.6, 6.0), 29.2, 14.5,
                                    boxstyle="round,pad=0.4,rounding_size=0.9",
                                    linewidth=1.5, edgecolor="#F39C12",
                                    facecolor="#FEF9E7", zorder=3))
        ax.text(cx, 17.6, t, ha="center", va="center", fontsize=10.4,
                color="#7E5109", fontweight="bold", zorder=4)
        ax.text(cx, 11.0, s, ha="center", va="center", fontsize=8.4,
                color="#7E5109", zorder=4, linespacing=1.6)

    # 刹车 ⇢ 循环 的抑制关系
    arrow((50, 21.0), (50, 32.0), "#B9770E", "刹车抑制循环", lw=1.8, ls=(0, (5, 3)),
          lx=0, ly=0, fs=9.4)

    ax.text(50, 97.5, "图4  三国杀身份局的核心反馈循环：一个被三条刹车压住的正反馈",
            ha="center", va="center", fontsize=14, fontweight="bold", color=C["ink"])
    ax.text(50, 2.0,
            "循环结构由作者依据官方规则集3.0（回合阶段／回合流程／死亡奖惩）绘制；"
            "「起手48.15%」「1:1.83」为 scripts/calc_probability.py 的计算结果。",
            ha="center", va="center", fontsize=8.4, color=C["grey"])
    save(fig, "fig4_反馈循环图.png")


# ==========================================================================
# fig5 武将强度四维框架
# ==========================================================================
def fig5():
    gm = load("general_matrix.json")["武将四维"]
    by = {r["武将"]: r for r in gm}
    pick = ["吕布(标)", "马超(标)", "界关羽", "赵云(标)", "司马懿(标)",
            "诸葛亮(标)", "华佗(标)", "貂蝉(标)"]
    pick = [p for p in pick if p in by]

    axes_labels = ["输出", "防御", "控制", "支援"]
    N = 4
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(15.5, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.05], wspace=0.18)

    ax = fig.add_subplot(gs[0], polar=True)
    colors = ["#C0392B", "#E67E22", "#B7950B", "#1E8449",
              "#17A2B8", "#2E86C1", "#7D3C98", "#17202A"]
    markers = ["o", "s", "^", "D", "v", "P", "X", "*"]
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, fontsize=12.5, fontweight="bold")
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(["1", "2", "3", "4"], fontsize=8, color=C["grey"])
    ax.grid(color="#B0B0B0", ls=":", alpha=0.8)
    for i, name in enumerate(pick):
        r = by[name]
        vals = [r["输出"], r["防御"], r["控制"], r["支援"]]
        vals += vals[:1]
        ax.plot(angles, vals, "-", lw=1.8, marker=markers[i % len(markers)], ms=6,
                color=colors[i % len(colors)], label=name, alpha=0.95)
        ax.fill(angles, vals, color=colors[i % len(colors)], alpha=0.05)
    ax.set_title("A. 四维雷达：典型武将的「动作构成」\n（等权计数，0~4 分）",
                 fontsize=11.8, loc="left", pad=26, color=C["ink"])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), fontsize=9.2,
              frameon=False, ncol=3)

    ax2 = fig.add_subplot(gs[1])
    ax2.axis("off")
    rows = sorted(gm, key=lambda r: (-(r["输出"] + r["防御"] + r["控制"] + r["支援"]),
                                     r["武将"]))[:14]
    cell = [[r["武将"], r["输出"], r["防御"], r["控制"], r["支援"],
             r["输出"] + r["防御"] + r["控制"] + r["支援"], r["归类型"]] for r in rows]
    tbl = ax2.table(cellText=cell,
                    colLabels=["武将", "输出", "防御", "控制", "支援", "动作总数", "归类"],
                    colWidths=[0.20, 0.10, 0.10, 0.10, 0.10, 0.15, 0.15],
                    loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.4)
    tbl.scale(1, 1.62)
    cat_color = {"输出": "#FADBD8", "防御": "#D6EAF8", "控制": "#E8DAEF", "支援": "#D5F5E3"}
    for (r, c), cellobj in tbl.get_celld().items():
        cellobj.set_edgecolor("#BDC3C7")
        if r == 0:
            cellobj.set_facecolor("#34495E")
            cellobj.set_text_props(color="white", fontweight="bold")
        elif c == 0:
            cellobj.set_facecolor("#ECF0F1")
            cellobj.set_text_props(fontweight="bold")
        elif c == 6:
            cellobj.set_facecolor(cat_color.get(cell[r - 1][6], "#FFFFFF"))
        elif c in (1, 2, 3, 4):
            v = cell[r - 1][c]
            if v:
                cellobj.set_facecolor("#FDF2E9")
                cellobj.set_text_props(fontweight="bold")
    ax2.set_title("B. 编码明细（动作条数 = 分数；等权是作者的简化假设）",
                  fontsize=11.8, loc="left", pad=18, color=C["ink"])
    ax2.text(0.5, -0.06,
             "编码规则：把官方规则集3.0 的技能效果文本逐条拆成动作 → 归入 输出/防御/控制/支援 四类。\n"
             "分数是「机制动作的数量」，不是官方强度值，也不是胜率。",
             ha="center", va="top", fontsize=8.8, color=C["grey"], transform=ax2.transAxes)

    fig.suptitle("图5  武将强度四维框架（基于三国杀官方规则集3.0 技能文本的动作编码）",
                 fontsize=13.5, fontweight="bold", color=C["ink"], x=0.012, ha="left", y=1.02)
    fig.text(0.5, -0.10,
             "由 scripts/general_matrix.py 生成。用途：给「强度膨胀」一个可量化的观察角度——"
             "老武将是 1~2 个动作、单维度；新武将是 3 个以上动作、跨 3~4 个维度。",
             fontsize=8.6, color=C["grey"], ha="center")
    save(fig, "fig5_武将强度四维框架.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print("\n全部图表已生成到 charts/ 目录。")
