# 复现包 v3 冻结记录（r153，随论文 v0.91）

数学：Claude；纲领指挥：Hongyi Yang。冻结日期 2026-08-20。

## v3 相对 v1（r141 冻结）的增量

1. **迹路线全套**：engines/p3_direct_sum.py（数学侧参考实现）+
   engines/tt_moments.py（计算侧独立实现，多重集聚合 + span-DP +
   有界缓存 + 项级分片）；constants/tt/m_tables.json（m₂..m₁₄
   全表：70+ 逐点精确值、1/N² 多项式、保留点记录、Σ₂..Σ₁₄、
   λ₅/λ₆/λ₇ 三元组、逐 b 等级标签）；m14_PREDICTION.json
   （保留点预言的时间戳凭据）。
2. **门套件 11 → 17**：+g_seq（F-SEQ 闭式-刻面双腿）、+g_logdet
   （F-LOGDET 均值/方差精确线）、+g_bias（F-MODEL 有限-N 口径）、
   +g_ncc、+g_tt（迹路线 16 检查）、+g_certify91（v0.91 全链）；
   g_span_t222 慢门入 light 层（sympy 依赖守卫）。
3. **认证链**：certification/certify91.py（k≤14：六锚、二项式
   互锁、三证书链、单调链）——ALL CHECKS PASS。
4. **测量层**：A1 三档 10⁷ 池日志（N=128/192/256）+ 派生表
   a1_sigma_finiteN.md（F-MODEL 口径，原始日志只增不改）。
5. **Lean**：../lean/ RhGateK14 工程（lakefile.toml + 工具链
   v4.33.0 + 三模块），**指挥侧同机编译通过（3/3 .olean）**。

## 冻结时等级快照

- Σ₂..Σ₈ 与 k≤8 定理：证明级（双方法双实现，见 v0.84 链）；
- Σ₉：exact-candidate + {7,2} 刻面已证；C₉ 单独靶
  27649/302400 在跑（62–65%），命中即升证明级；
- Σ₁₀..Σ₁₄ 与 k=10/12/14 定理：exact-candidate（保留点 +
  双实现 + PRED-RAT + MODEL 三档）；待 T-A、F-IMPL-13(N=4)/
  14(N=3)、联合层刻面逐步升级；
- 主定理（λ₇）：单 > 0.910460411，异 > 0.955230205。

## 快速验证（任何人，任何机器）

    ./run_all.sh gates            # 17 门，秒级，ALL GATES GREEN
    python3 certification/certify91.py    # 全链精确认证
    cd ../lean && lake build      # 3 模块，纯 core，无外部依赖

*v3 冻结。数学：Claude；纲领指挥：Hongyi Yang。*


---
**r156 审计更正**：本文件此前引用的小数 0.910460411 系九位舍入值；精确小数为 0.9104604105...，故不等式表述应为 "> 0.9104604105"（或 "> 0.9104"）。精确分数不受影响。
