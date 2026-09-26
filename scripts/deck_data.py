# -*- coding: utf-8 -*-
"""
三国杀 牌堆数据（数据层基准：标准版 + EX + 军争篇 = 160 张）

【数据来源】
- 标准包（108张，含4张EX）逐张表：三国杀WIKI_BWIKI（bilibili）
  https://wiki.biligame.com/sgs/标准包卡牌
- 军争篇（52张）逐张表：三国杀WIKI_BWIKI（bilibili）
  https://wiki.biligame.com/sgs/军争篇卡牌
- 分类张数交叉验证：zh.wikipedia《三国杀标准版》（基本牌53/锦囊36/装备19）、
  blog.shengbin.me《三国杀卡牌数量》（标准104+EX4=108，军争52，合计160）

【说明】
本文件把上述两个公开逐张表"逐条转录"为结构化数据，再由本脚本自行统计张数。
所以底表里的每一个张数都可以用 `python scripts/deck_data.py` 重跑复现，
而不是抄别人的汇总数字。
"""

# ---------------------------------------------------------------------------
# 标准版（逐张，按 花色→点数→[牌叠1, 牌叠2]，EX 牌单列）
# 转录自 https://wiki.biligame.com/sgs/标准包卡牌
# ---------------------------------------------------------------------------
STANDARD_DECK = {
    "红桃": {
        "A": ["桃园结义", "万箭齐发"],
        "2": ["闪", "闪"],
        "3": ["桃", "五谷丰登"],
        "4": ["桃", "五谷丰登"],
        "5": ["麒麟弓", "赤兔"],
        "6": ["桃", "乐不思蜀"],
        "7": ["桃", "无中生有"],
        "8": ["桃", "无中生有"],
        "9": ["桃", "无中生有"],
        "10": ["杀", "杀"],
        "J": ["杀", "无中生有"],
        "Q": ["桃", "过河拆桥"],
        "K": ["闪", "爪黄飞电"],
    },
    "黑桃": {
        "A": ["决斗", "闪电"],
        "2": ["雌雄双股剑", "八卦阵"],
        "3": ["过河拆桥", "顺手牵羊"],
        "4": ["过河拆桥", "顺手牵羊"],
        "5": ["青龙偃月刀", "绝影"],
        "6": ["乐不思蜀", "青釭剑"],
        "7": ["杀", "南蛮入侵"],
        "8": ["杀", "杀"],
        "9": ["杀", "杀"],
        "10": ["杀", "杀"],
        "J": ["顺手牵羊", "无懈可击"],
        "Q": ["过河拆桥", "丈八蛇矛"],
        "K": ["南蛮入侵", "大宛"],
    },
    "方块": {
        "A": ["诸葛连弩", "决斗"],
        "2": ["闪", "闪"],
        "3": ["闪", "顺手牵羊"],
        "4": ["闪", "顺手牵羊"],
        "5": ["闪", "贯石斧"],
        "6": ["杀", "闪"],
        "7": ["杀", "闪"],
        "8": ["杀", "闪"],
        "9": ["杀", "闪"],
        "10": ["杀", "闪"],
        "J": ["闪", "闪"],
        "Q": ["桃", "方天画戟"],
        "K": ["杀", "紫骍"],
    },
    "梅花": {
        "A": ["决斗", "诸葛连弩"],
        "2": ["杀", "八卦阵"],
        "3": ["杀", "过河拆桥"],
        "4": ["杀", "过河拆桥"],
        "5": ["杀", "的卢"],
        "6": ["杀", "乐不思蜀"],
        "7": ["杀", "南蛮入侵"],
        "8": ["杀", "杀"],
        "9": ["杀", "杀"],
        "10": ["杀", "杀"],
        "J": ["杀", "杀"],
        "Q": ["借刀杀人", "无懈可击"],
        "K": ["借刀杀人", "无懈可击"],
    },
}
# 4 张 EX 牌（同标准版一同销售，通常直接混入标准包使用）
# 转录自同一张表：♥Q / ♦Q / ♠2 / ♣2 各 1 张
STANDARD_EX = ["闪电", "无懈可击", "寒冰剑", "仁王盾"]

# ---------------------------------------------------------------------------
# 军争篇（逐张，52 张：每种花色 13 张、每点数 1 张）
# 转录自 https://wiki.biligame.com/sgs/军争篇卡牌
# ---------------------------------------------------------------------------
JUNZHENG_DECK = {
    "红桃": {
        "A": ["无懈可击"], "2": ["火攻"], "3": ["火攻"], "4": ["火杀"],
        "5": ["桃"], "6": ["桃"], "7": ["火杀"], "8": ["闪"], "9": ["闪"],
        "10": ["火杀"], "J": ["闪"], "Q": ["闪"], "K": ["无懈可击"],
    },
    "梅花": {
        "A": ["白银狮子"], "2": ["藤甲"], "3": ["酒"], "4": ["兵粮寸断"],
        "5": ["雷杀"], "6": ["雷杀"], "7": ["雷杀"], "8": ["雷杀"], "9": ["酒"],
        "10": ["铁索连环"], "J": ["铁索连环"], "Q": ["铁索连环"], "K": ["铁索连环"],
    },
    "黑桃": {
        "A": ["古锭刀"], "2": ["藤甲"], "3": ["酒"], "4": ["雷杀"], "5": ["雷杀"],
        "6": ["雷杀"], "7": ["雷杀"], "8": ["雷杀"], "9": ["酒"], "10": ["兵粮寸断"],
        "J": ["铁索连环"], "Q": ["铁索连环"], "K": ["无懈可击"],
    },
    "方块": {
        "A": ["朱雀羽扇"], "2": ["桃"], "3": ["桃"], "4": ["火杀"], "5": ["火杀"],
        "6": ["闪"], "7": ["闪"], "8": ["闪"], "9": ["酒"], "10": ["闪"],
        "J": ["闪"], "Q": ["火攻"], "K": ["骅骝"],
    },
}

# ---------------------------------------------------------------------------
# 分类归属（基本牌 / 锦囊牌 / 装备牌）
# ---------------------------------------------------------------------------
BASIC = {"杀", "火杀", "雷杀", "闪", "桃", "酒"}

TRICK = {
    "过河拆桥", "顺手牵羊", "无中生有", "无懈可击", "南蛮入侵", "决斗",
    "借刀杀人", "五谷丰登", "万箭齐发", "桃园结义", "乐不思蜀", "闪电",
    "铁索连环", "火攻", "兵粮寸断",
}

EQUIP = {
    # 武器
    "诸葛连弩", "雌雄双股剑", "青釭剑", "寒冰剑", "古锭刀", "丈八蛇矛",
    "青龙偃月刀", "贯石斧", "朱雀羽扇", "方天画戟", "麒麟弓",
    # 防具
    "八卦阵", "仁王盾", "藤甲", "白银狮子",
    # 坐骑（+1马 / -1马）
    "赤兔", "大宛", "紫骍",            # -1 坐骑（进攻）
    "的卢", "绝影", "爪黄飞电", "骅骝",  # +1 坐骑（防御）
}

# 延时类锦囊（放在武将牌判定区，需判定）
DELAYED_TRICK = {"乐不思蜀", "闪电", "兵粮寸断"}

# 武器攻击范围（转录自 三国杀攻略Wiki《卡牌列表》点数/花色总表标注 ➹）
# https://sanguoshagonglue.fandom.com/zh/wiki/卡牌列表
WEAPON_RANGE = {
    "诸葛连弩": 1, "雌雄双股剑": 2, "青釭剑": 2, "寒冰剑": 2, "古锭刀": 2,
    "丈八蛇矛": 3, "青龙偃月刀": 3, "贯石斧": 3,
    "朱雀羽扇": 4, "方天画戟": 4, "麒麟弓": 5,
}

# +1 坐骑（防御向，别人算与你的距离 +1）；-1 坐骑（进攻向，你算与别人的距离 -1）
PLUS1_MOUNT = {"的卢", "绝影", "爪黄飞电", "骅骝"}
MINUS1_MOUNT = {"赤兔", "大宛", "紫骍"}


def _iter_cards(flat_deck, ex=()):
    """展开为逐张牌名列表。"""
    cards = []
    for suit, ranks in flat_deck.items():
        for rank, names in ranks.items():
            cards.extend(names)
    cards.extend(ex)
    return cards


def _categorize(name):
    if name in BASIC:
        return "基本牌"
    if name in TRICK:
        return "锦囊牌"
    if name in EQUIP:
        return "装备牌"
    raise KeyError(f"未分类的牌名：{name}")


def build_deck():
    """返回 (全部牌名列表, 张数统计 dict)。"""
    cards = _iter_cards(STANDARD_DECK, STANDARD_EX) + _iter_cards(JUNZHENG_DECK)
    counts = {}
    for c in cards:
        counts[c] = counts.get(c, 0) + 1
    return cards, counts


def summarize():
    std_cards, std_counts = _iter_cards(STANDARD_DECK, STANDARD_EX), None
    jz_cards = _iter_cards(JUNZHENG_DECK)
    std_counts = {}
    for c in std_cards:
        std_counts[c] = std_counts.get(c, 0) + 1
    jz_counts = {}
    for c in jz_cards:
        jz_counts[c] = jz_counts.get(c, 0) + 1

    def cat_total(cnts):
        out = {"基本牌": 0, "锦囊牌": 0, "装备牌": 0}
        detail = {"基本牌": {}, "锦囊牌": {}, "装备牌": {}}
        for k, v in cnts.items():
            c = _categorize(k)
            out[c] += v
            detail[c][k] = v
        return out, detail

    std_cat, std_detail = cat_total(std_counts)
    jz_cat, jz_detail = cat_total(jz_counts)
    all_counts = {}
    for c in std_cards + jz_cards:
        all_counts[c] = all_counts.get(c, 0) + 1
    all_cat, all_detail = cat_total(all_counts)
    return {
        "标准版(含EX)": {"总数": len(std_cards), "分类": std_cat, "明细": std_detail},
        "军争篇": {"总数": len(jz_cards), "分类": jz_cat, "明细": jz_detail},
        "合计": {"总数": len(std_cards) + len(jz_cards), "分类": all_cat, "明细": all_detail},
    }


if __name__ == "__main__":
    import json
    import os

    s = summarize()
    print("=" * 64)
    print("三国杀 标准版(含EX) + 军争篇 牌堆统计")
    print("=" * 64)
    for scope in ["标准版(含EX)", "军争篇", "合计"]:
        d = s[scope]
        print(f"\n【{scope}】总张数 = {d['总数']}")
        for c, n in d["分类"].items():
            print(f"  {c}: {n} 张")
        print("  -- 明细 --")
        for c, items in d["明细"].items():
            if not items:
                continue
            txt = "，".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(items.items(), key=lambda x: -x[1]))
            print(f"  [{c}] {txt}")

    total = s["合计"]["总数"]
    allcnt = {}
    for scope in ["标准版(含EX)", "军争篇"]:
        for items in s[scope]["明细"].values():
            for k, v in items.items():
                allcnt[k] = allcnt.get(k, 0) + v
    print("\n" + "=" * 64)
    print("关键牌占比（在 160 张牌堆中）")
    print("=" * 64)
    key = ["杀", "火杀", "雷杀", "闪", "桃", "酒", "无懈可击", "借刀杀人",
           "过河拆桥", "顺手牵羊", "无中生有", "决斗", "南蛮入侵",
           "万箭齐发", "桃园结义", "五谷丰登", "乐不思蜀", "闪电",
           "铁索连环", "火攻", "兵粮寸断"]
    for k in key:
        if k in allcnt:
            print(f"  {k:<6} {allcnt[k]:>3} 张   占比 {allcnt[k]/total*100:5.2f}%")

    print("\n派生指标：")
    sha = allcnt.get("杀", 0) + allcnt.get("火杀", 0) + allcnt.get("雷杀", 0)
    shan = allcnt.get("闪", 0)
    print(f"  【杀】系合计 = {sha} 张（普通30 + 火{allcnt.get('火杀',0)} + 雷{allcnt.get('雷杀',0)}）")
    print(f"  【闪】合计   = {shan} 张")
    print(f"  杀 : 闪      = {sha/shan:.3f} : 1")
    print(f"  属性杀占杀系比例 = {(allcnt.get('火杀',0)+allcnt.get('雷杀',0))/sha*100:.1f}%")
    up = sum(allcnt.get(k, 0) for k in PLUS1_MOUNT)
    dn = sum(allcnt.get(k, 0) for k in MINUS1_MOUNT)
    print(f"  +1坐骑 {up} 张 / -1坐骑 {dn} 张")

    # 落盘
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data")
    os.makedirs(out, exist_ok=True)
    payload = {
        "来源": {
            "标准包逐张表": "https://wiki.biligame.com/sgs/标准包卡牌",
            "军争篇逐张表": "https://wiki.biligame.com/sgs/军争篇卡牌",
            "分类张数交叉验证": [
                "https://zh.wikipedia.org/zh-hans/三国杀标准版",
                "https://blog.shengbin.me/posts/number-of-cards-in-sanguosha",
            ],
        },
        "统计": s,
        "关键牌张数": {k: allcnt.get(k, 0) for k in key},
        "派生": {
            "杀系合计": sha, "闪合计": shan, "杀闪比": round(sha / shan, 4),
            "属性杀占杀系比例": round((allcnt.get("火杀", 0) + allcnt.get("雷杀", 0)) / sha, 4),
            "+1坐骑": up, "-1坐骑": dn,
        },
    }
    with open(os.path.join(out, "deck_counts.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n[已写出] {os.path.normpath(os.path.join(out, 'deck_counts.json'))}")
