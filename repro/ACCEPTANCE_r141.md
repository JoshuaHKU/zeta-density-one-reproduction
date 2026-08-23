# 复现包验收记录（r141，数学侧执行）

依据 REPRO_SPEC §8，四项验收在数学侧沙盒（干净环境，无 gmpy2，
RATBACKEND=frac 回退）独立执行：

## (a) 门套件亲跑

`run_all.sh gates`：**9/10 门全绿**（g_ledger 10/10、g_fcyc 7/7、
g_totals 12/12、g_p24 5/5、g_v25 4/4、g_vjoints 4/4、g_o5 12/12、
g_pred_rat 8/8、g_certify84 8/8——头条 0.84937772/0.92468886 逐位
复现）。唯一失败为 g_pure_orbits 的 c8 项（term_orbits.json 未回），
**与 REPRO_LOG §4.1 的如实登记完全一致，且门按规范报
NOT-APPLICABLE + exit 非零而非假过——这正是设计行为**。
frac 回退路径可用性由本次验收顺带确证。

## (b) MANIFEST 抽查

随机 8 个文件 sha256 全部命中（含 O5 原始矩 .npy、双份 RUN.md、
引擎、四个 values.json）；清单共 102 文件。**PASS**。

## (c) 抽样复现

11 个常数的束值全部由逐轨道行独立重建：**11/11 与 total 字段
精确相等**（含 c7 的 685 行、c8 的 6027 行重建 157/4032）。
t222 RUN.md 规范性检查通过（单命令、环境行、jobs 上限、
无隐藏检查点声明、second_path 内嵌）。**PASS**。

## (d) second_path 与论文 verif(d) 对账

| 类 | second_path | 与论文一致 | 备注 |
|---|---|---|---|
| t222/p24/j224/j44/j62/j52 | 实测偏差路径 | ✓ | j52 升级为 ladder-gpu 与论文"两确证"相容且更强 |
| j4222 | cross-host-replication | ✓ | 标签诚实（同码双机 ≠ 独立方法），可选补 GPU 阶梯 |
| c8 | model-side-ABC | ✓ | 论文 pedigree 措辞逐字对应 |
| c7 | model-side-ABC | **建议改标** | C₇ 另有更强的既有第二路径：r121–124 的七档 Romberg 识别（−17/360 机器精度命中，先于符号运行）——建议改为 `identification-ladder`，与论文"exact hit of the registered identification"对齐 |
| p25 | PENDING | **建议补注** | 数学侧已有束级双档阶梯确证（r136 增补，偏 −4.2e-6，F-V-25）；建议记为 `ladder-bundle-mathside`（注明"束级；逐轨道 PENDING"），与论文 Outlook (b) 的"independent bundle ladder"措辞对齐 |
| j225 | PENDING | ✓ | 如实；论文未宣称第二路径 |

## 结论

**有条件通过。**冻结 v1 的两个前置：
1. c8 term_orbits.json 回收（g_pure_orbits 翻绿）；
2. (d) 表中 c7 改标、p25 补注（两处均为元数据修订，不动数值）。

两项完成即冻结为复现包 v1（重生成 MANIFEST），随 certification/
与 lean/ 进 git-pub。p25/j225 的逐轨道第二路径可留 v1.1。

另致意两处工序质量：§3.1 的序号坑被常设门 g_totals 当场抓住
（R1 规则自证其值）；§3.2 拒绝以 3/7 凑 PASS 并重跑取证——
"日志里的数字不等于包里的凭据"应写入纲领工作纪律。

*Round 141。数学：Claude；纲领指挥：Hongyi Yang。*

---

# 数学侧对验收意见的处理（r141 回执）

## 两个冻结前置：**均已闭合**

| 前置 | 处理 | 证据 |
|---|---|---|
| 1. c8 `term_orbits.json` 回收 | 220，32 workers，12293 s，6027 轨道 | `constants/c8/term_orbits.json`；`g_pure_orbits` **5/5** |
| 2a. c7 改标 | → `identification-ladder` | `constants/c7/values.json` |
| 2b. p25 补注 | → **`ladder-gpu`**（超出建议，见下） | `constants/p25/values.json`；`gates/g_v25.py` |

## 三处与验收意见不同的处理，请复核

**(1) p25 没有按建议记为 `ladder-bundle-mathside`，而是做成了完整的
`ladder-gpu`。** 理由是 §3.2 定下的纪律——不引用包里算不出来的数。
给 `ladder_joints_sw.py` 补了 `2p5` 类（10-圈五对，全 size-2 块，无 F-CYC
展开，积分只在 R⁵），V100 上三档 dv 共几秒。结果：

    per orbit  79/79   max|Richardson - exact| = 2.038e-06   (判据 3e-6)
    bundle     0.759808192 vs 10531/13860 = 0.759812410   dev -4.22e-06
    对照       单档 dv=0.05 偏 +8.4e-03

束级 **−4.22e-06** 与数学侧 r136 的 **−4.2e-6** 逐位吻合，且逐轨道同样过判据。
因此建议论文措辞可从 Outlook (b) 的 "independent bundle ladder" 升级为
与 `{2,2,4}`/`{4,4}`/`{6,2}` 同级的逐轨道双路径。**此处请纲领侧确认是否采纳。**

**(2) 验收 (a) 记的 "g_v25 4/4" 查的不是 `{2^5}`，是我的命名错误。**
REPRO_SPEC §3 的 `F-V-25` 指 `{2^5}`；组包时我读成了 `{5,2}`。已更名：
`{5,2}` 的门 → `g_v52.py`（F-V-52，内容不动，仍 4/4），`g_v25.py` 重写为
`{2^5}` 的门。**门总数 10 → 11，`run_all.sh gates` 全绿。**
验收 (a) 的那一行结论仍成立，但它当时确证的是 F-V-52 而非 F-V-25。

**(3) 清单文件数从 102 增至 110、体积 19.9 → 21.3 MB**，增量为：
c8/c7 的 `term_orbits.json`、`{2^5}` 与 `{4,4}`/`{5,2}` 的阶梯检查点、
两份 `{4,4,2}` 跨机日志、`g_v25`/`g_v52`。**MANIFEST 已重生成**，
(b) 的抽查请按新清单重做。

## 仍未闭合（不影响冻结，请确认分级口径）

`{2,2,5}` 的 `second_path` = `PENDING`。它含一个 size-5 块，阶梯需在网格上
展开 C₅：dv=0.1 跑到 6/30 轨道约 10 min，dv=0.05 预计数小时。已在 238 排队，
完成即落盘。**在此之前论文须照 `PENDING` 写。**

## 一条成本事实，供后续排产

C₈ 同一计算：238 上 63.5 core-h，220 上 **109 core-h**（220 单核约慢 1.7×，
且同机另有 90 个 worker 争内存带宽）。**跨机估时不可按核数线性外推**——
这与 r136"把阶梯搬到 238 反而更慢"是同一条教训的两面。

*Round 141 回执。数学：Claude；纲领指挥：Hongyi Yang。*
