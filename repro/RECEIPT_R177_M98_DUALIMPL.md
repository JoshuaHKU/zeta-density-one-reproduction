# 回执 R177：m₉(8) 双实现（O-R176-2）

## 1. 结论

`m₉(8)` 的第二实现已交付，与归档值**逐位一致**。

```
engine         : repro/engines/p3_direct_sum.py  ::  m_b(9, 8)
                 （数学侧参考实现，格点直和 + Schur 正交性 + MN 特征标）
route          : direct lattice summation      （归档值来自计算侧 span-DP 路线）
lattice points : (2N-1)^(b-1) = 15^8 = 2,562,890,625
arithmetic     : fractions.Fraction 全程精确，无浮点

value          : 2365045367/33554432
archived       : 2365045367/33554432     （constants/tt/m_tables_ext.json）
bitwise equal  : TRUE

wall clock     : 2040.3 s  单核单进程
peak RSS       : 83 MB
character cache: 316,995 条（未触及 AUDIT_R177 新设的 400,000 上限）
host           : 审计机（darwin arm64, CPython 3.9）
```

据此，`m_tables_ext.json` 中 `F-BE-EXT-9` 的
`"HIT (holdout) ; dual impl pending addendum"` 之"dual impl pending"部分已清。
等级记录见 `constants/tt/m_tables_grades_v4.json` 的 `redundancy_delivered`。

## 2. 独立性说明

两条路线在**算法层面**独立，不是同一实现跑两遍：

| | 归档值（计算侧） | 本回执（数学侧） |
|---|---|---|
| 引擎 | `tt_moments.py` | `p3_direct_sum.py` |
| 方法 | 多重集聚合 + span-DP | 格点直和，逐点求迹矩 |
| 迹矩来源 | span-DP 递推 | Schur 正交性 + Murnaghan–Nakayama（β-数） |
| 枚举对象 | 多重集 | 全部 15⁸ 个 k-向量 |

`p3_direct_sum.py` 的模块头已声明二者是"独立孪生"，且明确要求不得统一
（"their disagreement surface is the point"）。本次比对正是使用该分歧面。

## 3. 姊妹点的成本判定（同批实测，未开工）

同一成本模型 `(2N-1)^(b-1)`，实测吞吐 0.9–1.1 × 10⁶ 格点/秒：

| 扩展点 | 格点数 | 单核 | 40 worker | 判定 |
|---|---|---|---|---|
| m₉(8) | 2.563e9 | 34 min（实测） | — | **已交付** |
| m₁₁(9) | 2.016e12 | 18–22 天 | ≈13 h | **可行**，见 §4 |
| m₁₃(10) | 2.213e15 | ≈66 年 | ≈604 天 | **不可行**（印证既有降级） |

m₁₁(9) 的 18–22 天不是由小用例外推，而是在**目标参数本身**上做分片探针
（固定前 4 坐标，每片 17⁶ ≈ 2.41e7 点，16 个随机前缀）得到：单片 7.9–51.1 s，
均值 18.95 s × 83,521 片。注意前缀代价差异极大（大 span 前缀被 `weight<=0`
廉价跳过），故总时间须用**分片时间均值**估计，用速率中位数会低估约 20%。

## 4. m₁₁(9) 排产前置条件（内存，非算力）

实测（无界缓存时）：

| 已跑分片 | `trace_moment` 缓存 | `character` 缓存 | 峰值 RSS |
|---|---|---|---|
| 3 / 83,521 | 5,894 | 982,735 | 251 MB |
| 13 / 83,521 | 11,375 | 1,633,393 | 435 MB |

即跑完万分之二的工作量、单进程已占 435 MB 且仍在增长；(μ,ν) 对的上界为
252,116，上表第二行只覆盖 4.5%。按核数开满 worker 会重演 r136 incident 3bis。

AUDIT_R177 已给 `p3_direct_sum.py` 的两处 memo 加上可调上界
（`P3_CHAR_CAP` / `P3_TM_CAP`，默认 400,000 / 200,000，`0` 恢复无界）。
默认值对已发布的一切都是惰性的：门禁规模只用几千条，本回执的 m₉(8) 峰值
316,995 条仍完整命中。

**排产步骤**：
1. 设定上界后先跑 **1/64 探针分片**，实测稳态 RSS 与吞吐——上界会降低命中率，
   吞吐必须重测，不能沿用本回执的数字；
2. worker 数按 `节点内存 / 稳态RSS` 定，**不按核数**；
3. 分片按格点数均分（83,521 片足够多，前缀长尾会被平均掉），逐片检查点落盘
   以保证可续跑。

## 5. 复现方式

```
cd repro/engines
python3 -c "from p3_direct_sum import m_b; print(m_b(9,8))"
# -> 2365045367/33554432   （约 34 分钟单核）
```

比对目标：`constants/tt/m_tables_ext.json` 的 `values["9"]["8"]`。

*计算侧 · r177 · 应数学侧指令 O-R176-2*
