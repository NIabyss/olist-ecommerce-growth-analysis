# 电商经营增长诊断与用户复购提升

这是一个基于 Olist 公开电商数据集的端到端分析练习项目：从原始多表数据出发，依次完成 SQL 建模、Python 清洗与统计检验、Tableau 可视化，最终形成一份完整的业务分析报告。项目的核心目标不是展示工具使用，而是练习如何把一个模糊的业务问题拆解成可验证、可复现、边界清晰的分析链条。

`dashboard/data/summary.json` 里的 `data_mode` 目前是 **OLIST_ACTUAL**——报告里的每一个数字都是我用 Kaggle 上的 Olist 真实数据跑出来的,不是编出来的示例。数据截止下单日期为 2018-08-29。

## 我要回答的业务问题

当电商销售增长放缓时,缺口到底来自新客不足、老客不复购、购买频次下降,还是客单价下滑?在这份数据没有营销成本、毛利、流量这些字段的前提下,我又能给出多有把握的优先级建议、哪些结论必须留白?

## 我是怎么做的

第一步我把订单、商品、支付、评价这几张表按订单粒度汇总成一张事实表(`order_fact`)——这是我在这个项目里最在意的一步。如果直接把订单表和一对多的商品表 / 支付表 JOIN 后求和,GMV 会被重复计算,这是我见过很多分析里容易踩的坑,所以我把它当作第一原则写进了项目里。

有了事实表之后,我用"活跃用户数 × 每用户订单数 × 客单价"这个三因子恒等式去定位增长卡在哪个环节,再用 RFM 分层、Cohort 留存和履约体验(是否逾期)做进一步诊断,最后给出可检验的运营优先级,而不是拍脑袋的建议。

整个过程中刻意把"真实观察到的结果"和"用来演示统计方法的模拟实验"分得很清楚。比如营销 A/B 那一节，因为 Olist 数据里没有真实的曝光/分组字段，我用代码模拟了一次分组实验来练习统计检验方法（比例差 z 检验、置信区间、近似 MDE），但报告里会明确标注这是模拟结果，不能当作真实营销效果的证据。我认为"清楚数据的边界在哪里"，比硬凑一个漂亮结论更重要，这也是数据分析的基本素养。

## 快速复现

### 用真实 Olist 数据跑(推荐)

```powershell
cd ecommerce_growth_portfolio
python -m pip install -r requirements.txt
python src/run_olist.py      # 生成 dashboard/data 中的真实分析输出
python src/plotting.py       # 生成报告用的图
```

原始 CSV 从 [Kaggle Olist 数据集](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 下载后放进 `data/raw/`,再执行 `run_olist.py` 即可。我没有把原始大文件放进仓库(体积太大,而且是第三方数据,不适合直接分发),`data/README.md` 里写了每张表该放什么。

### 没有原始数据时,跑模拟演示

```powershell
python src/run_demo.py       # 输出到 dashboard/demo_data,不会覆盖真实结果
```

`run_demo.py` 的输出会标记为 **SIMULATED_DEMO**,我加这一条是为了让别人 clone 仓库后,即使没去 Kaggle 下载数据,也能立刻跑起来看到完整链路。如果要把模拟结果换成真实结果,必须重新跑通真实数据并通过质量检查,**不能只是把"模拟"两个字删掉**。

## 我自己复现时会检查这几件事

1. `python src/run_demo.py` 应该输出 `validation passed`。
2. 打开 `dashboard/data/data_quality.csv`,如果有业务检查失败的行,我会先解释清楚再往下看。
3. 核对 `monthly_kpis.csv` 里的 `identity_gap` 是不是全为 0(这是 GMV 三因子恒等式的自检)。
4. 跑真实数据时确认 `summary.json` 的 `data_mode` 是 `OLIST_ACTUAL`,并核对报告里的数据截止日期有没有跟着更新。

## 项目结构

- `data/` —— 数据来源和清洗约定说明(原始大文件不进仓库)
- `sql/` —— 建表、订单事实表、增长 / RFM / cohort、运营诊断的 SQL
- `notebooks/` —— 清洗、用户分析、模拟 A/B 的可执行入口
- `src/` —— 我复用的 pandas、统计和绘图代码
- `dashboard/` —— 可直接导入 Power BI / Tableau 的 CSV,以及仪表盘搭建说明
- `reports/` —— 业务执行摘要、策略测算、项目讲解提纲
- `docs/` —— 数据字典、指标口径、项目复盘与自我审阅记录

## Tableau 仪表盘

我按 `dashboard/tableau_build_guide.md` 里的设计做了一个三页仪表盘,截图放在 `reports/figures/`:

| 页面 | 内容 | 截图 |
|---|---|---|
| P1 经营总览 | GMV / 订单 / 用户核心指标,月度趋势,地区与品类分布 | `reports/figures/dashboard_p1_overview.png` |
| P2 用户增长 | 新客/复购拆解、三因子表、RFM 矩阵、留存热力图 | `reports/figures/dashboard_p2_user_growth.png` |
| P3 运营诊断 | 履约逾期与评分关系、支付方式、品类机会点 | `reports/figures/dashboard_p3_ops_strategy.png` |

`.twbx` 源文件放在 `dashboard/` 目录下,打开即可看到完整的字段、计算逻辑和三页布局。

## 涉及的分析方法与工具

SQL 多表建模、CTE、窗口函数、日期处理；pandas 数据质量检查与清洗；RFM 用户分层、Cohort 留存分析；scipy 统计显著性检验；Tableau 仪表盘设计；分析结论的业务化表达。

## 我坚持的几条原则

1. 先在订单粒度上把事实表聚合出来,再算 GMV,不做一对多 JOIN 后直接求和。
2. 真实观察结果、假设测算、模拟实验结果三者严格分开标注,不混着说。
3. 没有流量、成本、毛利和真实实验数据的情况下,不对外声称因果关系或 ROI。
