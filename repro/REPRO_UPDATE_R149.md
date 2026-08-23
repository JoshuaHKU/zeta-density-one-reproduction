# 复现包更新日志 r149 —— 与论文最新版（47 页，含 §conv (vi)/(vii)）对齐

数学：Claude；纲领指挥：Hongyi Yang。日期 2026-08-20。
更新前基线：repro v1（r141 冻结）+ 计算侧 r146–r148 增量
（g_seq/g_logdet/g_bias/tt_moments 等）。

---

## 1. 新增文件（全部数学侧，未触碰计算侧任何文件）

| 文件 | 内容 | 运行层 |
|---|---|---|
| `engines/p3_direct_sum.py` | 迹路线**数学侧参考实现**（直和；MN 特征标 β-数版 + Schur 正交 + 格点和）。模块头明示：与计算侧 `tt_moments.py`（多重集聚合 + span-DP）互为独立孪生，**禁止"统一"两个引擎**——分歧面即门面 | 库 |
| `constants/tt/m_tables.json` | m₂..m₁₁ 全部精确值表 + 1/N² 多项式系数 + 保留点记录 + **逐 b 等级标签**（proven / identified+holdout / candidate-pending-acceptance）+ Σ 精确值 + λ₅ 证书三元组与等级语 | 数据 |
| `gates/g_tt.py` | **F-TT 快门**（16 检查，~30 s）：引擎验证梯 → 小 (b,N) 重算对表 → 全表 vs 多项式精确一致 → 常数项 vs 证明级塔与 re-centring 锚 → Σ 装配/Σ₃(N)≡0/λ₅ 全链（PD、Stieltjes、交替、零溢价、头条）。等级标签**照实打印不吞没** | gates |
| `gates/g_ncc.py` | **F-NCC 快门**（6 检查，<1 s）：顺序族闭式 4^{−m}ΣC(m,k)/(2k+1) 对五个档案/注册值（含 g_seq 已刻面确认的 b=12/14），纯 Fraction；与 g_seq 互为方法独立双腿 | gates |
| `gates/g_span_t222.py` | **F-SPAN 慢门**（6 检查，2–4 min，sympy）：b=6 五类初等闭式推导 + 束值 32/105（D19 第三路径）。按 REPRO_SPEC §5 快门 ≤2 min 预算，归入 light 层 | light |

## 2. 修改文件

- `run_all.sh`：
  1. gates 列表补齐 `g_seq`、`g_logdet`、`g_bias` 并加入
     `g_ncc`、`g_tt`；快门现共 **16 门，实测全绿**。
     **事实记述（按 AUDIT_R149 §3.1 更正）**：r149 开工时规范
     副本的 gates 列表为 11 门（本轮读取记录在案，无
     g_seq/g_logdet/g_bias）；计算侧操作记录显示 g_logdet、
     g_seq 曾经 sed 并入。两个记录均真 ⟹ 该两门的并入落在
     **非规范副本**上、未同步至包内；g_bias 为真遗漏（计算侧
     已认领）。原文"实际文件未改"对 g_seq/g_logdet 的归因不当，
     致意更正。**教训入册（两侧各半）**："操作记录 ≠ 包内状态"
     ——改包必须落规范副本、验收以规范副本为准，与"日志数字 ≠
     包内凭据"同族；
  2. light 层加 `g_span_t222.py`——**按 AUDIT_R149 §2.1 修正**：
     移至 light **末尾**且非致命化（`|| echo`），门内加 sympy
     依赖守卫（缺失时打印 NOT-APPLICABLE、退出码 3，已实测
     守卫路径）。无 sympy 主机（如 220）上 light 层八项类重算
     不再被阻断。
- `MANIFEST.json`：经 `make_manifest.py` 重生成（含新文件哈希）。

## 3. 代码规范（本次新增文件执行的标准，建议后续沿用）

1. 模块头：用途 + 数学出处（论文节号/轮次/回执名）+ 运行预算 +
   **等级与独立性声明**；中英双语首行；
2. PEP8：≤79 列、snake_case、函数级 docstring 写清"精确/浮点"边界
   （本次新增文件**全程无浮点**）；
3. 门一律走 `gatelib.check/finish`（退出码 0 当且仅当全过；
   比较集短于预期按 R3 判 NOT-APPLICABLE 而非假 PASS）；
4. 数据表带 provenance 字段与等级标签，等级随受理状态升降，
   **门打印等级但不因候选级而跳过算术检查**。

## 4. 有意不做的事（纪律说明）

- **未改**计算侧任何引擎/门（实现独立性是 F-IMPL 的前提）；
- **未把** `derive_t222_closed.py`/`p3_toeplitz_route.py` 原地搬入
  ——repro 版本是重写清理版，r147 目录的原件保留作历史轨迹；
- b=11 数据已入表但等级为 candidate-pending-acceptance
  （受理轮未走完：F-IMPL-11 直和复算在跑）；λ₅ 等级语逐字保留
  "pending C_9 facet + Sigma_10 joint layer"。

## 5. 与两份未决回执的衔接

- `RECEIPT_R148_OTT3_B11`：数值已表内登记为候选级；正式受理
  （含 F-IMPL-11 对拍）另出受理书；
- `BUG_REPORT_ENUM_R148`：数学侧**确认 {4,4,2} = 1575**
  （闭式 10!/(4!·4!·2!)/2! = 1575，与通报一致）；通报所列
  三高危形状（{3,3,4}/{4,4,4}/{5,5}）的复核要求成立；
  已核实作废值未入包。正式回文随 b=11 受理书一并出。

## 6. 审查响应（AUDIT_R149 处理记录）

| 审查条目 | 处理 |
|---|---|
| §2.1 阻断缺陷（light 层 sympy 硬依赖开头） | **已修**：门内依赖守卫（NOT-APPLICABLE / exit 3，守卫路径已用 import 拦截器实测）+ 移至 light 末尾非致命化——即审查建议的 2+1 并用 |
| §3.1 事实陈述错误 | **已更正**（见上 §2 第 1 条）；"操作记录 ≠ 包内状态"教训入册 |
| §4.1 F-SPAN 未获正确性背书 | 如实接受：该门 6 项检查待 sympy 环境侧复核后背书；等级语保持 |
| §4.2 旧成本估计沿用风险 | **已处理**：PLAN_K14_EXACT_r149 追加成本修订注记（见该文件附录） |

MANIFEST 已随上述修改重生成。

*r149 复现包更新（经 AUDIT_R149 复查修订）。数学：Claude；纲领指挥：Hongyi Yang。*
