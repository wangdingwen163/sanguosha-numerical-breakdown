# -*- coding: utf-8 -*-
"""
三国杀 · 手牌曲线 / 输出期望 / 边际收益递减（纯数学推导，可重跑）

运行：python scripts/calc_curves.py
输出：data/curves.json

模型设定（全部显式写在下面，避免"看起来像结论"）：
* 摸牌引擎：每回合摸牌阶段摸 2 张（官方规则集3.0《游戏流程·阶段》）
* 刹车①：出牌阶段默认只能使用 1 张【杀】（官方规则集3.0《卡牌·基本牌·杀》：出牌阶段限一次）
* 刹车②：弃牌阶段手牌上限 = 当前体力值（官方规则集3.0《用语·数值·手牌上限》）
* 两个模型：
  M1「只看摸牌引擎」：累计摸牌 = 4 + 2t（t为回合数），不设上限
  M2「加上刹车」：手牌数 = min(累计摸牌 − 已使用牌, 体力值)，取体力值 4 的常见情形
"""
import json
import os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
N = 160
SHA = 44       # 杀系（普通30+火5+雷9）
SHAN = 24
TAO = 12
LIMIT_SHA_PER_TURN = 1


def p_at_least_one(K, n, N=N):
    if n <= 0 or K <= 0:
        return 0.0
    if N - K < n:
        return 1.0
    return 1.0 - comb(N - K, n) / comb(N, n)


def hand_curve(max_m=12):
    """手牌 m 张时的关键指标 + 逐张边际增量。"""
    rows = []
    prev = {"杀": 0.0, "闪": 0.0, "桃": 0.0}
    for m in range(1, max_m + 1):
        p_sha = p_at_least_one(SHA, m)
        p_shan = p_at_least_one(SHAN, m)
        p_tao = p_at_least_one(TAO, m)
        e_sha = m * SHA / N
        # 每回合只能出1张杀 → 期望「有效利用的杀」= E[min(X,1)] = 1 - P(X=0)
        e_useful = 1 - (1 - p_sha)
        # 期望溢出（抽到但用不掉）= E[max(X-1, 0)] = E[X] - E[min(X,1)]
        e_waste = e_sha - e_useful
        rows.append({
            "手牌数": m,
            "P(至少1张杀)%": round(p_sha * 100, 2),
            "P(至少1张闪)%": round(p_shan * 100, 2),
            "P(至少1张桃)%": round(p_tao * 100, 2),
            "期望杀数": round(e_sha, 4),
            "期望有效使用的杀": round(e_useful, 4),
            "期望溢出(用不掉的杀)": round(e_waste, 4),
            "溢出率%": round(e_waste / e_sha * 100, 2) if e_sha else 0.0,
            "边际:P(能出杀)增量(百分点)": round((p_sha - prev["杀"]) * 100, 2),
            "边际:P(有闪)增量(百分点)": round((p_shan - prev["闪"]) * 100, 2),
            "边际:P(有桃)增量(百分点)": round((p_tao - prev["桃"]) * 100, 2),
        })
        prev = {"杀": p_sha, "闪": p_shan, "桃": p_tao}
    return rows


def turn_curve(turns=10, hp=4):
    """回合维度的摸牌/手牌曲线：M1 无约束 vs M2 带弃牌刹车。"""
    rows = []
    for t in range(0, turns + 1):
        cum = 4 + 2 * t          # 累计摸到的牌（含起手）
        used = t * 1             # 假设每回合稳定用掉 1 张（一张杀）
        m1 = cum                  # M1：只看摸牌引擎
        m2 = min(max(cum - used, 0), hp)   # M2：出牌+弃牌至体力值
        rows.append({
            "回合t": t,
            "M1_累计摸牌(无约束)": m1,
            "M2_手牌数(含弃牌刹车,体力4)": m2,
            "M2_手牌数(含弃牌刹车,体力3)": min(max(cum - used, 0), 3),
            "M2_手牌数(含弃牌刹车,体力5)": min(max(cum - used, 0), 5),
        })
    return rows


def output_expectation():
    """期望伤害输出：手牌 m 张、对手手牌 4 张为基准。"""
    p_target_shan = p_at_least_one(SHAN, 4)
    rows = []
    for m in range(1, 11):
        p_my_sha = p_at_least_one(SHA, m)
        e_dmg = p_my_sha * (1 - p_target_shan)
        rows.append({
            "我的手牌数": m,
            "P(手中有杀)%": round(p_my_sha * 100, 2),
            "对手4张手牌时的期望伤害": round(e_dmg, 4),
        })
    return {"对手4张手牌时的被闪概率%": round(p_target_shan * 100, 2), "结果": rows}


def main():
    os.makedirs(DATA, exist_ok=True)
    out = {
        "模型设定": {
            "每回合摸牌": 2,
            "每回合【杀】使用上限": LIMIT_SHA_PER_TURN,
            "弃牌阶段手牌上限": "当前体力值（官方规则集3.0《用语·数值·手牌上限》）",
            "牌堆": "160张（标准108含EX + 军争52）",
        },
        "手牌曲线": hand_curve(),
        "回合曲线": turn_curve(),
        "输出期望": output_expectation(),
    }
    path = os.path.join(DATA, "curves.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("=" * 84)
    print("一、手牌曲线与边际增量（牌堆160张，杀系44张，闪24张）")
    print("=" * 84)
    print(f"{'手牌':>4}{'P(有杀)%':>10}{'P(有闪)%':>10}{'P(有桃)%':>10}"
          f"{'期望杀数':>10}{'有效杀':>8}{'溢出率%':>9}{'ΔP杀':>8}{'ΔP闪':>8}")
    for r in out["手牌曲线"]:
        print(f"{r['手牌数']:>4}{r['P(至少1张杀)%']:>10.2f}{r['P(至少1张闪)%']:>10.2f}"
              f"{r['P(至少1张桃)%']:>10.2f}{r['期望杀数']:>10.3f}{r['期望有效使用的杀']:>8.3f}"
              f"{r['溢出率%']:>9.2f}{r['边际:P(能出杀)增量(百分点)']:>8.2f}"
              f"{r['边际:P(有闪)增量(百分点)']:>8.2f}")

    print("\n" + "=" * 84)
    print("二、回合曲线：摸牌引擎 vs 弃牌刹车")
    print("=" * 84)
    print(f"{'回合':>4}{'M1累计摸牌':>12}{'M2手牌(体力4)':>16}{'M2(体力3)':>12}{'M2(体力5)':>12}")
    for r in out["回合曲线"]:
        print(f"{r['回合t']:>4}{r['M1_累计摸牌(无约束)']:>12}{r['M2_手牌数(含弃牌刹车,体力4)']:>16}"
              f"{r['M2_手牌数(含弃牌刹车,体力3)']:>12}{r['M2_手牌数(含弃牌刹车,体力5)']:>12}")

    print("\n" + "=" * 84)
    print("三、期望伤害输出（对手4张手牌）")
    print("=" * 84)
    for r in out["输出期望"]["结果"]:
        print(f"  我的手牌{r['我的手牌数']:>3} 张 → P(有杀) {r['P(手中有杀)%']:>6.2f}%  "
              f"期望伤害 {r['对手4张手牌时的期望伤害']:.4f}")

    print(f"\n[已写出] {os.path.normpath(path)}")


if __name__ == "__main__":
    main()
