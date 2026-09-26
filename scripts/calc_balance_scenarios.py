# -*- coding: utf-8 -*-
"""
三国杀 · 设计决策实验（P0-1）＋ 身份局收益结构（P1-5）

运行：python scripts/calc_balance_scenarios.py
输出：data/balance_scenarios.json

定位
----
这不是"再拆一遍"，而是**改动实验**：
把"如果由我来调"的 3 个方案代入同一套模型，算出【预测值 + 副作用】，
并明确识别出"影响面太小、不值得动"的项。
数值策划的日常是"发现问题 → 提方案 → 建模验证 → 评估副作用"，本脚本补的就是后三步。

口径（与前序脚本一致）
----------------------
* 牌堆 = 标准版 108（含4EX）＋军争篇 52 ＝ 160 张
* 基线手牌 = 4 张（民间规则整理的起手张数）
* 期望命中 = 1 − P(对手 m 张手牌含【闪】)，m=4
* 【杀】的使用上限 = 每回合 1 张；一回合只打一个目标（简化假设，显式声明）
* 不含技能、装备、治疗；桃的回复按"全部用满"的上限计入（因此是上界）
"""

import json
import os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

N = 160
BASE_SHA = 44      # 杀系：普通30 + 火杀5 + 雷杀9
BASE_SHAN = 24
BASE_TAO = 12
BASE_WEAPON = 12   # 诸葛连弩×2 + 其余10把各1
BASE_EQUIP = 25
HAND = 4           # 基线手牌数
PLAYERS = 8
BLOOD_POOL = 5 + 4 * 7   # 主公 5 体力 + 其余 7 人各 4 体力 = 33
DRAW_PER_ROUND = PLAYERS * 2   # 每轮全场摸牌 16 张

KEY_LIMIT = "每回合【杀】上限"
KEY_EUSEFUL = "E[min(手牌杀,上限)]"


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def p_at_least_one(K, n, N=N):
    if K <= 0 or n <= 0:
        return 0.0
    if N - K < n:
        return 1.0
    return 1.0 - comb(N - K, n) / comb(N, n)


def p_none(K, n, N=N):
    return 1.0 - p_at_least_one(K, n, N)


def p_ge(K, n, k, N=N):
    """P(X >= k)，X ~ 超几何(N, K, n)。"""
    if k <= 0:
        return 1.0
    if k > min(n, K):
        return 0.0
    tot = comb(N, n)
    s = 0
    for i in range(k, min(n, K) + 1):
        s += comb(K, i) * comb(N - K, n - i)
    return s / tot


def e_min(K, n, limit, N=N):
    """E[min(X, limit)] = Σ_{i=1..limit} P(X >= i)。"""
    return sum(p_ge(K, n, i, N) for i in range(1, limit + 1))


def e_count(K, n, N=N):
    return n * K / N


def hit_rate(shan=BASE_SHAN, hand=HAND):
    """对手 hand 张手牌时的命中率（对手没有【闪】的概率）。"""
    return 1.0 - p_at_least_one(shan, hand)


def damage_per_round(sha_cnt=BASE_SHA, shan_cnt=BASE_SHAN, limit=1, hand=HAND):
    """单人单回合期望输出 = E[min(手牌中的杀, limit)] × 命中率。"""
    return e_min(sha_cnt, hand, limit) * hit_rate(shan_cnt, hand)


def round_budget(d, tao_cnt=BASE_TAO):
    """对局时长代理：
    每轮全场输出 = PLAYERS × d；每轮【桃】潜在回复上限 = 16 × 桃/160
    净输出/轮 = max(0, 输出 − 回复)；打空血量池所需轮数 = 33 / 净输出
    声明：消耗战代理，不含技能与装备；桃按"全部用满"计，故为下界轮数。
    """
    out_round = PLAYERS * d
    heal_round = DRAW_PER_ROUND * tao_cnt / N
    net = max(out_round - heal_round, 1e-9)
    return {
        "每轮全场输出": round(out_round, 3),
        "每轮桃回复上限": round(heal_round, 3),
        "每轮净输出": round(net, 3),
        "打空血量池轮数": round(BLOOD_POOL / net, 1),
    }


# --------------------------------------------------------------------------
# 方案 A：动手杀还是动手闪？—— 一个"直觉方案"翻车的实验
# --------------------------------------------------------------------------
def scenario_a():
    variants = []

    def row(label, sha_cnt, shan_cnt):
        d = damage_per_round(sha_cnt, shan_cnt)
        variants.append({
            "方案": label,
            "杀系张数": sha_cnt,
            "闪张数": shan_cnt,
            "杀:闪": round(sha_cnt / shan_cnt, 3),
            "起手4张含杀%": round(p_at_least_one(sha_cnt, 4) * 100, 2),
            "起手4张含闪%": round(p_at_least_one(shan_cnt, 4) * 100, 2),
            "起手4张无闪%": round(p_none(shan_cnt, 4) * 100, 2),
            "对手4张手牌命中率%": round(hit_rate(shan_cnt) * 100, 2),
            "单人单回合期望输出": round(d, 4),
            "对局时长代理": round_budget(d)["打空血量池轮数"],
        })

    row("基准（杀44 / 闪24）", BASE_SHA, BASE_SHAN)
    row("A1 减杀：杀44→38", 38, BASE_SHAN)
    row("A2 加闪：闪24→30", BASE_SHA, 30)
    row("A1+A2 同时做：杀38 / 闪30", 38, 30)

    base = variants[0]
    for v in variants[1:]:
        v["期望输出变化%"] = round((v["单人单回合期望输出"] / base["单人单回合期望输出"] - 1) * 100, 2)
        v["对局时长变化%"] = round((v["对局时长代理"] / base["对局时长代理"] - 1) * 100, 2)

    return {
        "假设": "基线手牌4张；对手4张手牌；一回合打一个目标；不含技能装备",
        "关键结论": (
            "A1（减杀）完全没有改善「开局没闪」这个结构指标（起手无闪率 51.85% → 51.85%，纹丝不动），"
            "只是把输出压低、把对局拖长；"
            "A2（加闪）才真正动到「开局能不能防」（无闪率 51.85% → 43.20%），"
            "代价是输出下降、杀:闪 从 1.83 掉到 1.47。"
            "→ 结论：「攻击牌太多」是观感问题，「防御牌供给不足」才是数值问题；"
            "两个方案的副作用方向相同（都让对局变慢），但只有一个解决了目标指标。"
        ),
        "对照表": variants,
    }


# --------------------------------------------------------------------------
# 方案 B：【借刀杀人】—— 一张"负期望、被放弃"的牌，该不该救
# --------------------------------------------------------------------------
def scenario_b():
    k = 1.5
    p_no_sha = p_none(BASE_SHA, HAND)                 # 目标4张手牌无杀系
    p_has_weapon = p_at_least_one(BASE_WEAPON, HAND)  # 目标4张手牌有武器
    p_has_equip = p_at_least_one(BASE_EQUIP, HAND)    # 目标4张手牌有装备
    w_model = 1.0 + 0.5 * k                            # 模型给武器估值
    neihao = 0.5                                       # 逼对手消耗1张杀的价值
    ev_now = p_no_sha * w_model + (1 - p_no_sha) * neihao - 1
    w_breakeven = (1 - (1 - p_no_sha) * neihao) / p_no_sha
    ev_real = p_has_weapon * (p_no_sha * w_model + (1 - p_no_sha) * neihao) - 1
    ev_fix_equip = p_has_equip * (p_no_sha * w_model + (1 - p_no_sha) * neihao) - 1

    per_round_appear = DRAW_PER_ROUND * 2 / N
    table_impact = per_round_appear * ev_now
    impact_pct = abs(table_impact) / (PLAYERS * damage_per_round()) * 100
    b3_impact = (DRAW_PER_ROUND * 4 / N) * ev_now

    conclusion = (
        "【借刀杀人】是「负期望 × 极低配比」的自洽陷阱牌："
        + f"EV = {ev_now:+.3f} 张牌，只有 2 张（1.25%），每轮全场期望见 {per_round_appear:.2f} 张、"
        + f"平均 {1/per_round_appear:.1f} 轮才出现一次；即使把它从牌堆里删掉，"
        + f"对全场每轮输出的影响也只有 {impact_pct:.2f}%。"
        + "→ 结论一：它不值得为了「平衡」而改（影响面比模型误差还小）。"
        + f"→ 结论二：它之所以负期望，不是收益给低了，而是多了一道「目标必须有武器」的门（{p_has_weapon*100:.1f}%）；"
        + f"保本需要武器值 {w_breakeven:.2f} 张牌，模型只给 {w_model:.2f} 张，缺口 {w_breakeven - w_model:.2f} 张。"
        + f"→ 结论三：若要救，改可用性而不是改收益——把「目标必须有武器」放宽为「目标有装备」，"
        + f"单卡 EV 从 {ev_real:+.3f} 升到 {ev_fix_equip:+.3f}，且完全不动牌堆结构。"
        + "→ 结论四：「把数量 2→4」是最差改法——不影响单卡 EV，只是把一张没人用的负期望牌多印两张。"
    )

    return {
        "模型参数": {
            "k": k,
            "P(目标4张无杀系)%": round(p_no_sha * 100, 2),
            "P(目标4张有武器)%": round(p_has_weapon * 100, 2),
            "P(目标4张有装备)%": round(p_has_equip * 100, 2),
            "模型给武器估值(张牌)": round(w_model, 3),
            "逼出对方1张杀的价值(张牌)": neihao,
        },
        "现行公式": "EV = p_no_sha×W_武器 + (1−p_no_sha)×内耗 − 1",
        "现行EV(张牌)": round(ev_now, 3),
        "保本所需武器估值(张牌)": round(w_breakeven, 3),
        "估值缺口(张牌)": round(w_breakeven - w_model, 3),
        "加武器门槛后的EV(张牌)": round(ev_real, 3),
        "改法B1_门槛放宽为任意装备后的EV(张牌)": round(ev_fix_equip, 3),
        "影响面": {
            "每轮全场出现张数": round(per_round_appear, 3),
            "平均几轮见到1张": round(1 / per_round_appear, 1),
            "对全场每轮输出的影响(张牌)": round(table_impact, 4),
            "占每轮总输出的比例%": round(impact_pct, 2),
            "改法B3_只把数量2到4后的影响(张牌)": round(b3_impact, 4),
        },
        "结论": conclusion,
    }


# --------------------------------------------------------------------------
# 方案 C：把"每回合限 1 张【杀】"改成"限 2 张" —— 会崩在哪
# --------------------------------------------------------------------------
def scenario_c():
    rows = []
    for limit in (1, 2, 3):
        e_useful = e_min(BASE_SHA, HAND, limit)
        e_have = e_count(BASE_SHA, HAND)
        waste = e_have - e_useful
        rows.append({
            KEY_LIMIT: limit,
            KEY_EUSEFUL: round(e_useful, 4),
            "期望溢出(用不掉的杀)": round(waste, 4),
            "溢出率%": round(waste / e_have * 100, 2),
            "静态期望输出(沿用固定命中率)": round(e_useful * hit_rate(), 4),
        })
    base_static = rows[0]["静态期望输出(沿用固定命中率)"]
    for r in rows:
        r["静态输出变化%"] = round((r["静态期望输出(沿用固定命中率)"] / base_static - 1) * 100, 2)

    shan_supply = DRAW_PER_ROUND * BASE_SHAN / N
    rows_supply = []
    for r in rows:
        demand = PLAYERS * r[KEY_EUSEFUL]
        capped_hit = min(1.0, max(hit_rate(), 1 - shan_supply / demand)) if demand else 0.0
        d_supply = r[KEY_EUSEFUL] * capped_hit
        rows_supply.append({
            KEY_LIMIT: r[KEY_LIMIT],
            "每轮全场可出杀数": round(demand, 2),
            "每轮全场闪供给": round(shan_supply, 2),
            "供给约束下的命中率%": round(capped_hit * 100, 2),
            "供给约束下的期望输出": round(d_supply, 4),
            "对局时长代理(供给约束)": round_budget(d_supply)["打空血量池轮数"],
        })
    base_rounds = rows_supply[0]["对局时长代理(供给约束)"]
    for r in rows_supply:
        r["对局时长变化%"] = round((r["对局时长代理(供给约束)"] / base_rounds - 1) * 100, 2)

    snowball = []
    for m in (4, 6, 8, 10):
        e1 = e_min(BASE_SHA, m, 1)
        e2 = e_min(BASE_SHA, m, 2)
        snowball.append({
            "手牌数": m,
            "限1输出": round(e1 * hit_rate(), 4),
            "限2输出": round(e2 * hit_rate(), 4),
            "提升%": round((e2 / e1 - 1) * 100, 2),
        })

    e1 = rows[0][KEY_EUSEFUL]
    e2 = rows[1][KEY_EUSEFUL]
    spill1 = rows[0]["溢出率%"]
    spill2 = rows[1]["溢出率%"]
    demand1 = rows_supply[0]["每轮全场可出杀数"]
    demand2 = rows_supply[1]["每轮全场可出杀数"]
    rounds2 = rows_supply[1]["对局时长代理(供给约束)"]
    chg2 = rows_supply[1]["对局时长变化%"]
    snow_last = snowball[-1]["提升%"]

    conclusion = (
        "改成「限 2 张」会让【杀】的有效使用量从 "
        + f"{e1:.2f} 张升到 {e2:.2f} 张，溢出率从 {spill1:.1f}% 降到 {spill2:.1f}%"
        + "——从这个角度看，「解溢出」是有效的。"
        + "但它崩在防御牌供给上：每轮全场可出的杀从 "
        + f"{demand1:.1f} 张涨到 {demand2:.1f} 张，而全场的【闪】供给只有 {shan_supply:.1f} 张/轮。"
        + "命中率不再由「对手有没有闪」决定，而由「闪够不够分」决定 → 对局时长代理从 "
        + f"{base_rounds:.0f} 轮压到 {rounds2:.0f} 轮（{chg2:+.0f}%）。"
        + "更糟的是雪球效应：手牌 10 张时限 2 的输出比限 1 高 "
        + f"{snow_last:.0f}%，即领先方受益更大——"
        + "而「体力 = 手牌上限」这条负反馈刹车，恰恰在最需要它的时候（领先方手牌多）失效了。"
    )

    return {
        "静态结果": rows,
        "供给约束结果": rows_supply,
        "雪球效应(手牌越多提升越大)": snowball,
        "结论": conclusion,
    }


# --------------------------------------------------------------------------
# P1-5 身份局收益结构：把"信息博弈"折算成期望值
# --------------------------------------------------------------------------
def identity_payoff():
    roles = {"主公": 1, "忠臣": 2, "反贼": 4, "内奸": 1}
    k = 1.5
    equip_value = 1.0 + 0.5 * k
    reward_kill_rebel = 3.0

    p_rebel = 4 / 7
    p_loyal = 2 / 7
    p_spy = 1 / 7

    rows = []
    for m in (2, 4, 5, 6, 8):
        penalty = m + equip_value
        ev = p_rebel * reward_kill_rebel + p_loyal * (-penalty) + p_spy * 0.0
        rows.append({
            "主公手牌数": m,
            "误杀忠臣的惩罚(弃牌估值)": round(penalty, 2),
            "盲打一个未知目标的EV(张牌)": round(ev, 3),
        })
    breakeven_hand = (p_rebel * reward_kill_rebel / p_loyal) - equip_value

    conclusion = (
        "主公盲打一个未知目标：期望 = 4/7×(+3) + 2/7×(−弃牌估值) + 1/7×0。"
        + f"保本点落在手牌 {breakeven_hand:.2f} 张——而主公的常规手牌上限恰好是 4~5 张（体力值）。"
        + "也就是说：规则用「击杀反贼 +3 张」和「误杀忠臣弃光」两个数字，"
        + "把「瞎打」的期望恰好焊在了 0 附近——手牌少时小赚，手牌多时倒亏。"
        + "这不是巧合，是用数值逼玩家用信息而不是用运气做决策。"
    )

    return {
        "身份配置(8人局)": roles,
        "盲打模型": {
            "假设": "主公面对 7 名未知身份角色（2忠/4反/1内）；击杀反贼 +3 张；主公击杀忠臣 → 弃置所有手牌与装备",
            "来源标注": "击杀奖励与主公误杀惩罚均为民间规则整理/社区共识，非官方规则集原文，正文须标注",
            "表格": rows,
            "保本手牌数": round(breakeven_hand, 2),
            "结论": conclusion,
        },
        "非对称": {
            "反贼/忠臣击杀反贼": "+3 张，且不承担误杀惩罚（忠臣杀忠臣无惩罚）",
            "主公击杀忠臣": "弃置所有手牌与装备（惩罚随主公手牌增长而放大）",
            "结论": "同一个动作（造成击杀）在不同身份手里的期望完全不同——"
                    "这就是「敌我关系不固定」在数值层的体现：身份局没有统一的计分板。",
        },
        "四身份目标函数": [
            {"身份": "主公", "胜利条件": "消灭所有反贼与内奸", "收益口径": "存活优先，误杀代价最高"},
            {"身份": "忠臣", "胜利条件": "保护主公，与主公同胜", "收益口径": "可牺牲自己，敢打敢拼"},
            {"身份": "反贼", "胜利条件": "击杀主公", "收益口径": "击杀主公=直接胜利"},
            {"身份": "内奸", "胜利条件": "自己活到与主公单挑并取胜", "收益口径": "不是输出最大化，而是存活排序，需要控局平衡"},
        ],
    }


# --------------------------------------------------------------------------
def main():
    os.makedirs(DATA, exist_ok=True)
    out = {
        "口径与假设": {
            "牌堆": "标准版108(含4EX) + 军争篇52 = 160张",
            "基线手牌": HAND,
            "人数": PLAYERS,
            "血量池": BLOOD_POOL,
            "每轮全场摸牌": DRAW_PER_ROUND,
            "免责": "全部为裸模型（不含技能/装备/治疗交互），用于比较改动方向，而非预测真实胜率",
        },
        "基准单人单回合期望输出": round(damage_per_round(), 4),
        "基准对局时长代理": round_budget(damage_per_round()),
        "方案A_减杀还是加闪": scenario_a(),
        "方案B_借刀杀人": scenario_b(),
        "方案C_杀的使用上限": scenario_c(),
        "身份局收益结构": identity_payoff(),
    }
    path = os.path.join(DATA, "balance_scenarios.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    base_d = out["基准单人单回合期望输出"]
    base_r = out["基准对局时长代理"]["打空血量池轮数"]
    print("=" * 88)
    print(f"基准：单人单回合期望输出 = {base_d}   对局时长代理 = {base_r} 轮")
    print("=" * 88)

    print("\n【方案 A】减杀 vs 加闪")
    print(f"{'方案':<24}{'杀:闪':>7}{'起手无闪%':>10}{'起手含杀%':>10}{'命中率%':>9}{'输出':>9}{'时长变化%':>10}")
    for v in out["方案A_减杀还是加闪"]["对照表"]:
        chg = v.get("对局时长变化%", 0.0)
        print(f"{v['方案']:<24}{v['杀:闪']:>7.2f}{v['起手4张无闪%']:>10.2f}"
              f"{v['起手4张含杀%']:>10.2f}{v['对手4张手牌命中率%']:>9.2f}"
              f"{v['单人单回合期望输出']:>9.4f}{chg:>10.1f}")

    print("\n【方案 B】借刀杀人")
    b = out["方案B_借刀杀人"]
    bp = b["模型参数"]
    print(f"  现行EV = {b['现行EV(张牌)']:+.3f} 张牌；保本需武器值 {b['保本所需武器估值(张牌)']:.2f} 张"
          f"（模型给 {bp['模型给武器估值(张牌)']:.2f} 张，缺口 {b['估值缺口(张牌)']:.2f}）")
    print(f"  加入武器门槛后 EV = {b['加武器门槛后的EV(张牌)']:+.3f}；"
          f"放宽为任意装备 → {b['改法B1_门槛放宽为任意装备后的EV(张牌)']:+.3f}")
    print(f"  每轮全场出现 {b['影响面']['每轮全场出现张数']:.3f} 张；对总输出影响 "
          f"{b['影响面']['占每轮总输出的比例%']:.2f}%")

    print("\n【方案 C】每回合杀上限 1 → 2 → 3")
    print(f"{'上限':>4}{'有效杀':>9}{'溢出率%':>9}{'静态输出':>10}{'变化%':>8}"
          f"{'可出杀数':>10}{'闪供给':>8}{'约束下轮数':>12}")
    for r, s in zip(out["方案C_杀的使用上限"]["静态结果"],
                    out["方案C_杀的使用上限"]["供给约束结果"]):
        lim = r[KEY_LIMIT]
        eu = r[KEY_EUSEFUL]
        print(f"{lim:>4}{eu:>9.3f}{r['溢出率%']:>9.2f}"
              f"{r['静态期望输出(沿用固定命中率)']:>10.4f}{r['静态输出变化%']:>8.1f}"
              f"{s['每轮全场可出杀数']:>10.2f}{s['每轮全场闪供给']:>8.2f}"
              f"{s['对局时长代理(供给约束)']:>12.0f}")

    print("\n【P1-5 身份局】主公盲打一个未知目标的期望")
    ip = out["身份局收益结构"]["盲打模型"]
    for r in ip["表格"]:
        print(f"  主公手牌 {r['主公手牌数']} 张 → 误杀惩罚 {r['误杀忠臣的惩罚(弃牌估值)']:.2f} 张"
              f" → EV = {r['盲打一个未知目标的EV(张牌)']:+.3f} 张牌")
    print(f"  保本手牌数 = {ip['保本手牌数']:.2f} 张")

    print(f"\n[已写出] {os.path.normpath(path)}")


if __name__ == "__main__":
    main()
