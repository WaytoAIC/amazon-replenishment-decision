## 🚀 Way to AIC | 通往 AI 电商之路
---
### 🌐 官网 Website
- https://waytoaic.com
- https://www.waytoaic.com
---

### 👥 社群招募 Community
`Way to AIC 社群招募 | WaytoAIC.com`

<p align="center">
  <img src="https://github.com/user-attachments/assets/d9f8bbf4-2056-4780-975d-86c885b52bab" width="70%">
</p>

---

### 📣 公众号 WeChat Official Account
`维正 WaytoAIC`

<p align="center">
  <img src="https://github.com/user-attachments/assets/71c71a5c-e68a-4f30-9afb-f2b056619991" width="300">
</p>

---

### 🧠 知识星球 Xiaozhixing
`AI电商之路 WaytoAIC`

<p align="center">
  <img src="https://github.com/user-attachments/assets/9eccef07-0e84-45a7-a415-affcb18c928d" width="200">
  <img src="https://github.com/user-attachments/assets/4e99fbc3-1981-4fee-b113-c9821141102d" width="400">
</p>

---

### 🧩 About Way to AIC

**AIC = AI Commerce**

在 AI 重塑商业的时代，我们希望和每一个拥抱 AI 的卖家：

- 找到场景
- 定义问题
- 积累能力
- 设计系统

共同通往 AI 电商之路。

> Way to AIC 不是教学，不是工具，
> 而是一条所有电商人共同走的进化之路。

### WaytoAIC 理念 | Principles

| 中文 | English |
|---|---|
| 场景先于方法 | Context before method |
| AI 的价值来自真实业务场景，而不是技术本身。 | AI creates value through real business contexts, not through technology alone. |
| 问题先于答案 | Problem before answer |
| 定义问题，比拥有工具更重要。 | Defining the problem matters more than collecting tools. |
| 系统胜过技巧 | System over tricks |
| 技巧是术，系统才是道，决定卖家的上限。 | Tricks are tactical; systems define long-term leverage and ceiling. |
| 共创优于独行 | Co-creation over solo progress |
| 我们相信，真正的进化发生在共同探索的过程中。 | Real evolution happens through shared exploration. |

---

# 补货决策 Skill / Replenishment Decision Skill

先查清内外部证据，再判断补不补、何时补、补多少、供应赶不上怎么办。仅项目内使用，人工决策；不含工作台或自动化。

## 安装 / Install

需要 Python 3.9+。从仓库根运行（将项目路径换成你的业务项目）：

```sh
bash install.sh --target codex --project /path/to/business-project
bash install.sh --target openclaw --project /path/to/agent-workspace
```

可指定 `--dest`（必须在项目内）；`--repo WaytoAIC/amazon-replenishment-decision --ref main` 从指定仓库版本安装。默认不覆盖已有Skill，不安装全局配置，不写入MCP密钥。

## 第一次使用

把这句话发给Agent：

> 使用 $project-replenishment-decision。先做数据接入体检：检查已有内部ERP/API、文件和卖家精灵MCP；没有接入的给具体补充步骤和文件替代。确认本项目授权范围及业务规则，再分析一个匿名商品。能自己查的先查，不要全部变成部门待办。

- [首次使用与接入引导](references/onboarding.md)：已接入就复用；缺MCP/权限时给补充步骤；没有API可以先导表。
- [自主查数流程](references/evidence-investigation.md)：销量、流量、广告/促销、采购计划、订单、发货及接收关联。
- [市场数据补充](references/market-evidence.md)：卖家精灵MCP的价格、BSR、关键词需求及竞品，明确采样/估算与实际覆盖。
- [业务规则](references/business-rules.md)：每个使用者自己确认；原公司的规则和数据不在包内。

市场数据不替代内部销量，未下单计划不当确定供应，预计到仓不当可售承诺。输出包含解释、计算和运营/供应链/物流/老板的必要动作。

## English

A project-scoped decision Skill for whether, when and how much to replenish, with options when supply cannot meet demand. It investigates internal records first, uses SellerSprite MCP for external market evidence, explains assumptions, and leaves only genuinely human information or commitments for follow-up.

First use discovers existing tools, validates one authorized read, and offers export-based alternatives when an API/MCP is unavailable. No vendor credentials or live company cases are included. Market estimates never replace actual sales. No automatic orders, shipments, ERP changes or dashboards.

Install locally with the commands above. Configure your own project scope and confirmed business rules. All included tests are synthetic; passing tests does not validate real procurement or business outcomes.

## 验证 / Validation

```sh
python3 -m unittest discover -s tests -v
```

合成演示（非实际商品、承诺或报价）：

```sh
python3 scripts/risk_timeline.py assets/example-synthetic.json --output /tmp/replenishment-demo.json
```

20项合成行为测试覆盖库存时间轴、缺失流量、同星期对照、外部序列排序、负值哨兵与对象层级。首次引导的缺工具/缺权限/文件降级应按接入说明实际验收。

## 权利 / Rights

见 [LICENSE.md](LICENSE.md)。权利保留；不声称OSI开源授权。/ Rights reserved; no general redistribution or commercial-use license is granted.
