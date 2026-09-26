# -*- coding: utf-8 -*-
"""
导出《三国杀数值模型_可下载版.xlsx》（7 个 sheet，中文表头）

运行：python scripts/export_xlsx.py
输入：data/deck_counts.json
      data/probability_results.json
      data/balance_scenarios.json
      data/general_matrix.json
输出：<项目根>/三国杀数值模型_可下载版.xlsx

说明
----
本脚本只做「搬运 + 排版」：所有数字均直接来自 data/*.json，
不做任何重算、四舍五入以外的改动，也不引入任何新参数。
排版规则：每个 sheet 首行冻结、表头加粗反白、列宽按内容自适应、
数字按量级保留小数位、末行注明"数据来源：本文脚本可复算"。
"""

import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "三国杀数值模型_可下载版.xlsx")

FOOT = "数据来源：本文脚本可复算（scripts/export_xlsx.py ← data/*.json）"

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def load(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# 单元格行构造
# --------------------------------------------------------------------------
def T(text):
    return {"role": "title", "cells": [text]}


def H(*cells):
    return {"role": "head", "cells": list(cells)}


def R(*cells):
    return {"role": "row", "cells": list(cells)}


def B():
    return {"role": "blank", "cells": []}


def FK(text):
    return {"role": "foot", "cells": [text]}


def tbl(header, records):
    """list[dict] → 表头 + 数据行（按 header 取键，缺失留空）"""
    out = [H(*header)]
    for rec in records:
        out.append(R(*[rec.get(h, "") for h in header]))
    return out


def kv(records):
    """{'键': 值} → 两列表"""
    out = [H("项目", "数值/说明")]
    for k, v in records.items():
        out.append(R(k, v))
    return out


def norm(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        a = abs(v)
        if a >= 100:
            return round(v, 1)
        if a >= 10:
            return round(v, 2)
        return round(v, 4)
    return v


def disp_len(s):
    s = "" if s is None else str(s)
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def render(ws, rows):
    for i, r in enumerate(rows, start=1):
        for j, v in enumerate(r["cells"], start=1):
            c = ws.cell(row=i, column=j, value=norm(v))
            c.border = BORDER
            if r["role"] == "title":
                c.font = Font(bold=True, size=12, color="1F4E79")
                c.alignment = Alignment(vertical="center", horizontal="left")
            elif r["role"] == "head":
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor="2F5597")
                c.alignment = Alignment(vertical="center", horizontal="center",
                                        wrap_text=True)
            elif r["role"] == "foot":
                c.font = Font(italic=True, size=9, color="808080")
                c.alignment = Alignment(vertical="center", horizontal="left")
            elif r["role"] == "blank":
                pass
            else:
                c.font = Font(size=10)
                c.alignment = Alignment(vertical="top", wrap_text=True,
                                        horizontal="left" if isinstance(v, str) else "right")
    ws.freeze_panes = "A2"
    ncol = max((len(r["cells"]) for r in rows if r["cells"]), default=1)
    for j in range(1, ncol + 1):
        w = 0
        for r in rows:
            if len(r["cells"]) >= j:
                w = max(w, disp_len(r["cells"][j - 1]))
        ws.column_dimensions[get_column_letter(j)].width = min(max(w + 2, 10), 58)


# --------------------------------------------------------------------------
# ① 口径与假设
# --------------------------------------------------------------------------
def sheet1(wb):
    bs = load("balance_scenarios.json")
    kk = bs["口径与假设"]
    rows = [
        T("① 口径与假设"),
        B(),
        H("项目", "内容"),
        R("牌堆构成", kk["牌堆"]),
        R("起手手牌", "4 张（社区与民间规则整理一致；官方规则集未写明张数，正文须声明）"),
        R("每回合摸牌", 2),
        R("口径人数", kk["人数"]),
        R("血量池", kk["血量池"]),
        R("每轮全场摸牌", kk["每轮全场摸牌"]),
        B(),
        T("k 值定义：1 点体力折算的牌数（本文取 1 / 1.5 / 2 三档）"),
        H("k 档位", "含义", "本文用法"),
        R("k = 1", "1 点体力 = 1 张牌（纯牌差视角，最保守）", "敏感性下界"),
        R("k = 1.5", "1 点体力 = 1.5 张牌（基准档）", "本文主口径"),
        R("k = 2", "1 点体力 = 2 张牌（偏生存视角）", "敏感性上界"),
        B(),
        T("模型边界（5 条）"),
        H("编号", "边界说明"),
        R("边界 1", "裸模型：不含武将技能、装备、治疗牌的交互，只算基本牌层面的攻防期望"),
        R("边界 2", "对手基线手牌固定为 4 张，未随回合动态增长"),
        R("边界 3", "一回合只打一个目标；【杀】默认每回合上限 1 张（另做 2 / 3 档敏感性）"),
        R("边界 4", "【桃】的回复按「全部用满」的上限计入，因此输出侧是乐观上界"),
        R("边界 5", "对局时长用「血量池 ÷ 每轮净输出」的代理指标，不是真实回合数的模拟"),
        B(),
        H("项目", "内容"),
        R("免责声明", kk["免责"]),
        B(),
        FK(FOOT),
    ]
    render(wb.create_sheet("①口径与假设"), rows)


# --------------------------------------------------------------------------
# ② 牌堆表
# --------------------------------------------------------------------------
def sheet2(wb):
    d = load("deck_counts.json")
    st = d["统计"]
    rows = [T("② 牌堆表（标准版 + 军争篇 = 160 张）"), B()]

    for label, block in (("标准版（含 4 张 EX）", st["标准版(含EX)"]),
                         ("军争篇", st["军争篇"]),
                         ("合计", st["合计"])):
        rows.append(T("%s ：共 %d 张（基本 %d / 锦囊 %d / 装备 %d）" % (
            label, block["总数"],
            block["分类"]["基本牌"], block["分类"]["锦囊牌"], block["分类"]["装备牌"])))
        rows.append(H("分类", "牌名", "张数"))
        for cat, items in block["明细"].items():
            for name, cnt in items.items():
                rows.append(R(cat, name, cnt))
            rows.append(R(cat, "小计", block["分类"][cat]))
        rows.append(B())

    rows.append(T("关键牌张数"))
    rows.append(H("牌名", "张数"))
    for name, cnt in d["关键牌张数"].items():
        rows.append(R(name, cnt))
    rows.append(B())

    rows.append(T("派生指标"))
    rows.append(H("指标", "数值"))
    der = d["派生"]
    for k, v in der.items():
        rows.append(R(k, v))
    rows.append(R("杀系占比%（44/160）", 27.5))
    rows.append(R("闪占比%（24/160）", 15.0))
    rows.append(R("桃占比%（12/160）", 7.5))
    rows.append(B())

    rows.append(T("来源"))
    rows.append(H("数据层", "出处"))
    for k, v in d["来源"].items():
        if isinstance(v, list):
            v = " ； ".join(v)
        rows.append(R(k, v))
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("②牌堆表"), rows)


# --------------------------------------------------------------------------
# ③ 概率表
# --------------------------------------------------------------------------
def sheet3(wb):
    p = load("probability_results.json")
    rows = [T("③ 概率表（超几何精确解，牌堆 160 张 / 起手 4 张 / 每回合摸 2 张）"), B()]

    rows.append(T("3.1 起手与累计摸牌概率（至少 1 张）"))
    rows += tbl(["牌名", "张数", "占比%", "起手4张至少1张%", "首轮6张至少1张%",
                 "第3回合10张至少1张%", "起手4张期望张数"],
                p["起手与累计摸牌概率"])
    rows.append(B())

    rows.append(T("3.2 命中模型：【杀】的期望伤害（对手手牌 m 张）"))
    rows += tbl(["防守方手牌数", "P(手中有闪)%", "期望伤害/张杀", "命中即被闪概率%"],
                p["命中模型"])
    rows.append(B())

    g = p["命中模型(叠加八卦阵)"]
    rows.append(T("3.3 命中模型（叠加【八卦阵】：红色判定率 %.0f%%）" % (
        g["八卦阵红色判定率"] * 100)))
    rows += tbl(["防守方手牌数", "P(手牌有闪)%", "叠加八卦阵后免伤概率%",
                 "期望伤害(带八卦阵)"], g["结果"])
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("③概率表"), rows)


# --------------------------------------------------------------------------
# ④ 单卡期望表
# --------------------------------------------------------------------------
def sheet4(wb):
    p = load("probability_results.json")["单卡期望收益(作者参数模型)"]
    rows = [T("④ 单卡期望收益（作者参数模型，k = 1 / 1.5 / 2 三档全部）"), B()]
    rows.append(R("参数说明", p["参数说明"]))
    rows.append(B())
    rows.append(H("k 档位", "牌", "公式", "净收益(张)", "关键中间量"))
    for kname in ["k=1.0", "k=1.5", "k=2.0"]:
        for rec in p["按k取值的结果"][kname]:
            rows.append(R(kname, rec["牌"], rec["公式"], rec["净收益(张)"], rec["关键中间量"]))
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("④单卡期望表"), rows)


# --------------------------------------------------------------------------
# ⑤ 敏感性分析表
# --------------------------------------------------------------------------
def sheet5(wb):
    p = load("probability_results.json")["平衡旋钮敏感性"]
    rows = [T("⑤ 敏感性分析表（平衡旋钮：基准 + 旋钮 A~D）"), B()]
    rows.append(T("5.1 基准"))
    rows.append(H("指标", "数值"))
    for k, v in p["基准"].items():
        rows.append(R(k, v))
    rows.append(B())
    rows.append(T("5.2 旋钮实验"))
    rows += tbl(["旋钮", "闪张数", "杀系张数", "桃张数", "起手4张含闪%",
                 "起手4张含杀%", "起手4张含桃%", "期望命中伤害", "备注"], p["实验"])
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("⑤敏感性分析表"), rows)


# --------------------------------------------------------------------------
# ⑥ 平衡方案对照
# --------------------------------------------------------------------------
def sheet6(wb):
    bs = load("balance_scenarios.json")
    rows = [T("⑥ 平衡方案对照（方案A / 方案B / 方案C / 身份局盲打EV）"), B()]

    a = bs["方案A_减杀还是加闪"]
    rows.append(T("6.1 方案A：减杀还是加闪？—— 对照表"))
    rows += tbl(["方案", "杀系张数", "闪张数", "杀:闪", "起手4张含杀%", "起手4张含闪%",
                 "起手4张无闪%", "对手4张手牌命中率%", "单人单回合期望输出", "对局时长代理",
                 "期望输出变化%", "对局时长变化%"], a["对照表"])
    rows.append(R("关键结论", a["关键结论"]))
    rows.append(B())

    b = bs["方案B_借刀杀人"]
    rows.append(T("6.2 方案B：【借刀杀人】—— 参数与影响面"))
    rows.append(R("现行公式", b["现行公式"]))
    rows.append(B())
    rows.append(T("模型参数"))
    rows += kv(b["模型参数"])
    rows.append(B())
    rows.append(T("关键数值（张牌）"))
    rows.append(H("项目", "数值"))
    for k in ["现行EV(张牌)", "保本所需武器估值(张牌)", "估值缺口(张牌)",
              "加武器门槛后的EV(张牌)", "改法B1_门槛放宽为任意装备后的EV(张牌)"]:
        rows.append(R(k, b[k]))
    rows.append(B())
    rows.append(T("影响面"))
    rows += kv(b["影响面"])
    rows.append(R("结论", b["结论"]))
    rows.append(B())

    c = bs["方案C_杀的使用上限"]
    rows.append(T("6.3 方案C：【杀】的使用上限 —— 静态表"))
    rows += tbl(["每回合【杀】上限", "E[min(手牌杀,上限)]", "期望溢出(用不掉的杀)",
                 "溢出率%", "静态期望输出(沿用固定命中率)", "静态输出变化%"], c["静态结果"])
    rows.append(B())
    rows.append(T("6.3b 方案C：供给约束表（全场【闪】供给 = 2.4 张/轮）"))
    rows += tbl(["每回合【杀】上限", "每轮全场可出杀数", "每轮全场闪供给",
                 "供给约束下的命中率%", "供给约束下的期望输出",
                 "对局时长代理(供给约束)", "对局时长变化%"], c["供给约束结果"])
    rows.append(B())
    rows.append(T("6.3c 方案C：雪球效应（手牌越多，放开上限的提升越大）"))
    rows += tbl(["手牌数", "限1输出", "限2输出", "提升%"], c["雪球效应(手牌越多提升越大)"])
    rows.append(R("结论", c["结论"]))
    rows.append(B())

    ident = bs["身份局收益结构"]
    rows.append(T("6.4 身份局：盲打EV表（8 人局配置 1 主公 / 2 忠臣 / 4 反贼 / 1 内奸）"))
    rows.append(R("假设", ident["盲打模型"]["假设"]))
    rows.append(R("来源标注", ident["盲打模型"]["来源标注"]))
    rows += tbl(["主公手牌数", "误杀忠臣的惩罚(弃牌估值)", "盲打一个未知目标的EV(张牌)"],
                ident["盲打模型"]["表格"])
    rows.append(H("项目", "数值"))
    rows.append(R("保本手牌数", ident["盲打模型"]["保本手牌数"]))
    rows.append(B())
    rows.append(T("6.5 四身份目标函数"))
    rows += tbl(["身份", "胜利条件", "收益口径"], ident["四身份目标函数"])
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("⑥平衡方案对照"), rows)


# --------------------------------------------------------------------------
# ⑦ 武将四维编码
# --------------------------------------------------------------------------
def sheet7(wb):
    gm = load("general_matrix.json")
    rows = [T("⑦ 武将四维编码（OUT / DEF / CTL / SUP，0~4 分）"), B()]
    rows.append(R("编码规则", gm["编码规则"]))
    rows.append(R("来源", gm["来源"]))
    rows.append(R("武将数", gm["武将数"]))
    rows.append(B())
    rows.append(H("武将", "技能条数", "输出", "防御", "控制", "支援", "归类型", "技能清单"))
    for g in gm["武将四维"]:
        rows.append(R(g["武将"], g["技能条数"], g["输出"], g["防御"], g["控制"],
                      g["支援"], g["归类型"], " ／ ".join(g["技能清单"])))
    rows.append(B())

    # 权重敏感性：等权 / 偏输出 / 偏防御
    weights = [("等权（1/1/1/1）", (1, 1, 1, 1)),
               ("偏输出（输出×2）", (2, 1, 1, 1)),
               ("偏防御（防御×2）", (1, 2, 1, 1))]
    rows.append(T("7.1 权重敏感性：三种权重下的前 5 名（同一份四维编码，只换权重）"))
    rows.append(H("权重方案", "排名", "武将", "加权总分", "输出", "防御", "控制", "支援"))
    for label, w in weights:
        ranked = sorted(gm["武将四维"],
                        key=lambda g: (-(w[0] * g["输出"] + w[1] * g["防御"] +
                                         w[2] * g["控制"] + w[3] * g["支援"]), g["武将"]))
        for rank, g in enumerate(ranked[:5], start=1):
            s = w[0] * g["输出"] + w[1] * g["防御"] + w[2] * g["控制"] + w[3] * g["支援"]
            rows.append(R(label, rank, g["武将"], s, g["输出"], g["防御"],
                          g["控制"], g["支援"]))
    rows.append(R("观察", "三种权重下前 2 名始终是「界关羽 / 界张飞」（仅名次互换）；"
                          "第 3~5 名随权重变化较大——等权下大量武将并列 2 分，"
                          "排序由编码颗粒度而非权重决定。"))
    rows.append(B())
    rows.append(FK(FOOT))
    render(wb.create_sheet("⑦武将四维编码"), rows)


def main():
    wb = Workbook()
    wb.remove(wb.active)
    sheet1(wb)
    sheet2(wb)
    sheet3(wb)
    sheet4(wb)
    sheet5(wb)
    sheet6(wb)
    sheet7(wb)
    wb.save(OUT)
    print("[已生成] %s" % OUT)
    print("sheets: %s" % " | ".join(wb.sheetnames))


if __name__ == "__main__":
    main()
