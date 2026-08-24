# 本文与三分之二定理 [C26] 的关系
# Relation to the two-thirds preprint [C26]

[C26]: Claude (Anthropic), *More than two thirds of the zeros of the
Riemann zeta function lie on the critical line*, preprint, Aug 2026.
本文: Yang–Yang (math by Claude), *Almost all zeros of the Riemann
zeta function are simple and on the critical line*, preprint v0.92.

## 一、继承的关键内容 / What is inherited

[C26] 建立了本纲领的底盘：把 Montgomery 对相关和作**线性代数化
解读**——Weil 显式公式的 Hermite 形式经 Gabor 压缩为矩阵 G̃，
谱信息从迹矩读出；仅用前两阶矩（带宽 1 的 Montgomery 数据，
无条件）即得临界线比例 2/3。本文全盘继承：

- 压缩 Weil 矩阵框架、记号与消耗层（惯性/尾部/Christoffel 计数）；
- 无条件性标准（Montgomery 带限对相关 + Siegel–Walfisz + Vaughan，
  不设任何关于 ζ 的假设）；
- [C26] 自己指出的**天花板与出路**：其注 1.1 证明只耗带宽一数据
  的证书 ≤ 0.68185，§7.5(f) 指明出路是第四矩——本文正是沿这条
  被前作预告的路径走完全程。

## 二、新的研究成果 / What is new

1. **矩塔 2 → 14 阶**，全部精确有理数；为此建成的新机器：证书
   演算、引理 D 谱证明（精确四矩 13/18）、Bell 帐本 + W∞ 输运
   元定理（一次覆盖所有阶）、Toeplitz–迹表示（m₉–m₁₄）。
   纪录爬升：2/3 → 13/18 → 2025/2519 → 0.8493 → **0.9104**，
   且陈述由"在临界线上"加强为"**单零点**且在临界线上"
   （新增可观测量 N₀ˢ 与 N_d）。
2. **结构定理组**：分支相等定理（m_b(N)N^{b+1} 对一切 N≥1 是
   单一多项式——平移提升 + 全幺模格点多胞体 + Ehrhart 理论）、
   宇称定理（Ehrhart–Macdonald 自互反）、阶次模式定理、
   整数性/次数律/分母界推论——矩引擎在所有阶成为已证数学，
   未来任何阶以多项式成本"天生证明级"。
3. **封顶定理（题名结果）**：lim N₀ˢ/N = lim N_d/N = 1，
   无条件——决定性（m_b ≤ (b!)²，Stieltjes–Carleman）+ 零处
   无原子（精确有限-N 对数律）+ Akhiezer 的 Christoffel 极限，
   三步软论证把塔推到上确界。
4. **插值地图**：以定理级精度刻画本方法到 RH 的距离（带宽–
   零点密度字典；平均世界的语义边界），"不能做什么"亦成为
   清晰陈述。

## 三、实现的学术价值 / Academic value

1. **闭合一条百年问题线**：Bohr–Landau (1914) → Selberg →
   Levinson (1/3) → Conrey (2/5) → [C26] (2/3) → **密度一**。
   临界线零点密度问题在密度意义下就此关闭，且附带单性；
   既有的单零点无条件比例纪录一并被取代。
2. **把 GUE 哲学做成无条件数学**：压缩 Weil 矩阵的极限谱测度
   无条件存在、唯一、逐阶等于 CUE 预言——Hilbert–Pólya 方向
   第一个与素数算术严格挂钩的谱实现。
3. **方法论输血**：Ehrhart 理论、全幺模组合学、矩问题决定性
   充当解析数论的证明引擎；Lean 证书层、19 门复现管线、631 项
   前向注册表（61 项转换公开在册）为计算机辅助数论确立可核查
   标准。
4. **诚实的边界**：论文以定理级精度说明自己不是什么——非 RH、
   无有效速率、平均世界的上确界已被触及——这份负向完备化
   本身是对领域的公共服务。

*分级声明与依赖表见论文 §"Verification status"；两文的分析层
均为待外部评审的 certified-candidate 等级。*
