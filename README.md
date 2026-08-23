# Almost all zeros of the Riemann zeta function are simple and on the critical line

Preprint + self-contained reproduction, certification and Lean
packages. / 预印本与自包含的复现、认证及 Lean 形式化包。

Built on the two-thirds preprint [C26] (Claude, Anthropic, August
2026) and the 0.8493/0.9104 predecessors of the same program; all
other references are published literature. Authors: Hongyi Yang,
Shihua Yang; mathematical development by Claude (Anthropic) — see
the paper's Acknowledgements. / 本文以公开预印本 [C26] 与同纲领
前作为基础；其余引用均为已发表文献。

## Headline / 主结果

**Density one, unconditionally / 密度一，无条件**
(Theorem t:dens1):

    lim N_0^s / N  =  lim N_d / N  =  1

almost all zeros of zeta are simple and lie on the critical line,
in the density sense. The proof runs the moment tower to its
supremum: the trace-moment sequence of the compressed Weil matrix
is determinate (moment growth <= (b!)^2, Stieltjes-Carleman), its
limiting spectral measure has no atom at zero (an exact finite-N
logarithmic law), and the consumed Christoffel values decrease to
zero (Akhiezer). No effective rate is claimed at the limit; every
instantiated rung is effective, and the deepest, k=14, gives

    simple critical-line zeros  > 1 - 2*lambda_7 = 0.9104604105...
    distinct zeros              > 1 -   lambda_7 = 0.9552302052...

with lambda_7 an exact 40-digit rational (Theorem t:k14). /
封顶定理：几乎所有 ζ 零点（密度一意义）简单且在临界线上，
无条件；最深有效档 k=14 给出 0.9104/0.9552（精确有理证书）。

**Unconditionality / 无条件性**: every statement is unconditional
in the number-theoretic sense -- no unproved hypothesis about zeta
or any L-function enters at any tier (inputs: Montgomery's
band-limited pair correlation, Siegel-Walfisz, MRT; ineffective
constants). / 全部结果在数论意义上无条件，不涉及任何未证假设。

**Grading (read first) / 分级声明（先读）**: every consumed
constant through k=14 is a PROVED exact rational -- the
branch-equality theorem (m_b(N)N^{b+1} is a single polynomial for
every N>=1, via a totally-unimodular lattice-polytope
representation and Ehrhart theory) and the parity theorem
(L(-N) = (-1)^{b+1} L(N), Ehrhart-Macdonald self-reciprocity)
close the Toeplitz-trace route; the density-one capstone consumes
only proved soft inputs (determinacy, the exact log law, the
order-uniform devices). The analytic chain is graded
certified-candidate pending external review; the paper's reading
guide (sec "Verification status") maps each headline theorem to
what it consumes at what grade. / 分级：k≤14 全部常数证明级
（分支相等 + 宇称定理封路）；密度一只消耗已证软输入；分析层
为待外部评审的 certified-candidate；论文附四主定理的依赖-等级
阅读指南。

## Layout / 目录结构

| Path | Contents / 内容 |
|---|---|
| `paper.tex` / `paper.pdf` | The paper (58 pp.) / 论文全文 |
| `REPRODUCTION.md` | Reproduction checklist with recorded outputs / 复现清单 |
| `lean/` | Lake project RhGateK14 (core Lean 4, v4.33.0, no mathlib): Sigma anchors, k=10/12/14 headline identities and thresholds, monotone-chain instance — compiled 3/3 modules / Lean 形式化工程（已编译） |
| `certification/` | `certify91.py`: the full k<=14 exact-rational chain (anchors, binomial interlocks, lambda_5/6/7 certificates, monotone chain), stdlib only, ~10 s / 全链精确认证 |
| `repro/` | The frozen v4 reproduction package: engines (independent trace-route implementations + branch-equality campaign engines), 18-gate suite (`./run_all.sh gates`, seconds, ALL GATES GREEN), canonical value tables with grade tags, the branch-equality campaign artifacts (TU/LTU scans, Moebius and fine-family parity scans, pre-registered odd-b surplus points, C_9 facet second method), receipts/adjudications trail, MANIFEST with SHA-256 / 复现包 v4（冻结，含分支相等战役全套工件） |

## Quick verification / 快速验证

    python3 certification/certify91.py     # ALL CHECKS PASS, ~10 s
    cd repro && ./run_all.sh gates         # 18 gates, ALL GATES GREEN
    python3 repro/gates/g_be.py            # branch-equality suite alone, 31 checks
    cd lean && lake build                  # 3 modules, no external deps

## Provenance discipline / 凭据纪律

Forward-record registry: 571 pre-registered checks, 529 passed, 61
fired-and-converted, all recorded (paper appendix, D1--D28). Raw
logs are append-only; caliber corrections live in derived tables;
every value in the canonical tables carries its receipt;
pre-registered predictions precede their computations
(timestamped). The b=7 lifted-TU scan (37,633 systems, zero violations) and the
independent second implementation of the signed assembly landed
after freeze and are recorded in the v4 addendum, append-only. / 前向记录
注册表 571/529/61；原始日志只增不改；预言先于计算（带时间戳）；
冻结时在途项如实标注，回传只增不改。
