# 三国杀数值拆解 · 可复算模型（Sanguosha Numerical Breakdown）

> 对《三国杀》桌游牌堆（标准版 108 张含 4 张 EX ＋ 军争篇 52 张 ＝ **160 张**）的一次系统／数值拆解。
> **📖 配套文章（已发布 · 知乎专栏）**：[《**1 : 1.83 —— 三国杀 160 张牌堆的数值拆解：三条刹车，和三个可验证的改动实验**》](https://zhuanlan.zhihu.com/p/2087293591232295997)
>
> **本仓库的原则：没有一个"没有出处的数字"。** 每个数字要么带公开来源 URL，要么可由本仓库的脚本从零重跑复现。

---

## 一、核心结论（可直接引用）

| 指标 | 值 | 出处 |
|---|---|---|
| 杀 : 闪 | **1.83 : 1**（标准版单独 2.00 : 1） | `scripts/deck_data.py` |
| 起手 4 张无【闪】 | **51.85%**（同时 72.77% 有【杀】） | `scripts/calc_probability.py` |
| 裸模型输出天花板 | **0.5185 点／回合**（手牌 4 张时 0.3773） | `scripts/calc_curves.py` |
| 手牌 4 张时【杀】溢出率 | 33.85%（手牌 12 张升到 70.24%） | `scripts/calc_curves.py` |
| 边际递减 | 第 1 张手牌 +27.50pp → 第 12 张 +0.75pp | `scripts/calc_curves.py` |
| 距离体系 | 攻击范围 1→4，覆盖全场 28.6%→100% | `scripts/calc_probability.py` |
| 身份局主公盲打保本手牌 | **4.25 张**（恰在常规手牌上限 4~5 附近） | `scripts/calc_balance_scenarios.py` |

### 三个可验证的改动实验（本仓库的重点）

| 实验 | 改动 | 模型预测 | 结论 |
|---|---|---|---|
| **A** | 【杀】44 → 38 | 起手无闪率 **51.85% → 51.85%（不变）** | 治观感不治结构；输出 −8.5%、对局时长 +16.6% |
| **A** | 【闪】24 → 30 | 起手无闪率 → **43.20%** | 才真正动到目标指标；输出 −16.7%、时长 +38.7% |
| **B** | 【借刀杀人】门槛放宽 | 单卡 EV −0.773 → −0.583 | **仍为负，且影响面仅 1.06% → 不值得改** |
| **C** | 每回合【杀】上限 1 → 2 | 溢出率 33.85% → **6.25%**，输出 +41.7% | **崩在防御供给**：对局从 14.9 轮压到 7.1 轮（−52%），雪球效应 +84.7% |

---

## 二、文件地图

```
正文_可直接粘贴版.md         配套文章（9 节 + 摘要卡 + 附录，约 6600 中文字）
数据底表.md                  数据底表（12 节，每条数字带来源 URL 或脚本引用）
三国杀数值模型_可下载版.xlsx  可下载模型（7 个 sheet，可直接打开）

scripts/
  deck_data.py               160 张牌堆逐张转录 → 张数统计
  calc_probability.py        起手／累计概率、命中模型、单卡期望、距离覆盖、敏感性
  calc_curves.py             手牌曲线、边际递减、回合曲线、输出期望
  general_matrix.py          武将技能动作四维编码
  calc_balance_scenarios.py  三个改动实验（方案A/B/C）＋ 身份局收益结构
  make_charts.py             生成 fig1~fig5
  make_charts_p0.py          生成 fig6
  export_xlsx.py             导出 xlsx

data/                       5 个 JSON（脚本产物，删掉可重建）
charts/                     6 张图（300 dpi，中文正常）
```

---

## 三、如何复现

```bash
python scripts/deck_data.py            # → data/deck_counts.json
python scripts/calc_probability.py     # → data/probability_results.json
python scripts/calc_curves.py          # → data/curves.json
python scripts/general_matrix.py       # → data/general_matrix.json
python scripts/calc_balance_scenarios.py   # → data/balance_scenarios.json
python scripts/make_charts.py          # → charts/fig1~fig5
python scripts/make_charts_p0.py       # → charts/fig6
python scripts/export_xlsx.py          # → 三国杀数值模型_可下载版.xlsx
```

环境：Python 3.11.9 ／ matplotlib 3.11.2 ／ openpyxl 3.1.5 ／ 中文字体 Microsoft YaHei（脚本内置 `Microsoft YaHei → SimHei → DengXian` 回退链）。

---

## 四、模型边界（重要，请先读这段）

1. **牌堆锁定桌游标准版 ＋ 军争 160 张**；三国杀 OL／移动版的牌堆构成与桌游不同，涉及线上版本的结论在文中单独标注。
2. **起手 4 张**为民间规则整理／社区共识（官方规则集只写"分发起始手牌"，未写张数）。
3. **单卡期望收益**使用作者自建参数模型，唯一自由参数 k ＝ 1 点体力折算的牌数，全部结论以 k ＝ 1／1.5／2 三档给出——**它不是官方数值**。
4. 所有"期望输出／对局时长"都是**裸模型**：不含技能、装备、治疗与团队配合，用途是**比较改动方向**，不是预测真实胜率。
5. **官方不公开武将胜率**，因此本仓库对武将强度只做机制层论证（动作数量与维度覆盖），**不做强度排名**。`charts/fig5_武将强度四维框架.png` 是"技能动作编码示意图"：等权求和是简化假设，权重敏感性检查显示只有前 2 名稳定（第 3~5 名随权重变化），**不能当强度排名使用**。

---

## 五、数据来源

- 牌堆逐张表：三国杀 WIKI（BWIKI）《标准包卡牌》《军争篇卡牌》，逐条转录进 `scripts/deck_data.py`，由脚本自行统计（不抄二手汇总）。
- 规则与技能文本：《三国杀官方规则集》3.0 原文。
- 平衡性调整史：官方公告 7 条，均带 URL（见 `数据底表.md` §6）。
- 交叉验证：维基百科《三国杀标准版》分类张数、第三方统计（blog.shengbin.me）。

---

## 六、许可

- `scripts/`、`data/`、`charts/`、`三国杀数值模型_可下载版.xlsx`：**MIT**
- `正文_可直接粘贴版.md`、`数据底表.md`：作者原创分析，欢迎引用并注明出处，**禁止商用**
- 三国杀及相关素材版权归原厂商（游卡桌游）所有；**本仓库不包含任何游戏原始素材**（全部图表为作者自制）

---

---

## 七、相关链接

- **知乎专栏（本文全文，已发布）**：<https://zhuanlan.zhihu.com/p/2087293591232295997>
- **系列**：数值拆解 · 01《一张牌的定价：逆向拆解杀戮尖塔「腐化」为什么敢把技能牌变成 0 费》／ 02 本篇
- 讨论与勘误：欢迎在知乎文章评论区留言，或在本仓库开 Issue

*作者：王鼎文（@wangdingwen163）· 2026-09-26*
