/- CertificateK1012.lean -- k=10 and k=12 headline identities.

   Exact rational certificate layer for the Toeplitz-trace rungs
   (paper sec conv (vii); r148/r150 adjudications).  Grades at the
   time of writing: lambda_5 exact-candidate (pending C_9 facet +
   Sigma_10 joint layer), lambda_6 exact-candidate (pending b=11/12
   formal acceptance).  The identities below are exact rational
   arithmetic regardless of grade; grade language lives in the paper.

   Pattern follows Certificate84.lean (grind on Rat identities).
   Compiled with lake (leanprover/lean4:v4.33.0); see lean/BUILD.md. -/

namespace RhGateK1012

/-- Sigma_9 = 52207/302400 from m9 = 495107/6720 + Sigma_9. -/
theorem sigma9_recentre :
    (11166011/151200 : Rat) - 495107/6720 = 52207/302400 := by grind

/-- Sigma_10 from m10 = 199427/1344 + 10*Sigma_9 + Sigma_10. -/
theorem sigma10_recentre :
    (83443081/554400 : Rat) - 199427/1344 - 10*(52207/302400)
      = 1333891/3326400 := by grind

/-- Sigma_11 from the pre-registered anchor. -/
theorem sigma11_recentre :
    (852071287/2721600 : Rat) - 94560551/302400 = 128291/340200 := by
  grind

/-- Sigma_12 from the pre-registered anchor. -/
theorem sigma12_recentre :
    (1033020076559/1556755200 : Rat) - 199083751/302400
      - 12*(128291/340200) = 1092211019/1556755200 := by grind

/-- k=10 headlines at lambda_5 = 46970100247159/764967228211380. -/
theorem headline_k10_simple :
    (1 : Rat) - 2*(46970100247159/764967228211380)
      = 335513513858531/382483614105690 := by grind

theorem headline_k10_distinct :
    (1 : Rat) - 46970100247159/764967228211380
      = 717997127964221/764967228211380 := by grind

theorem k10_beats_08771 :
    (8771/10000 : Rat) < 335513513858531/382483614105690 := by grind

theorem k10_beats_09385 :
    (9385/10000 : Rat) < 717997127964221/764967228211380 := by grind

/-- k=12 headlines at
    lambda_6 = 13166900320841109317259245/254195527518153210548497708. -/
theorem headline_k12_simple :
    (1 : Rat)
      - 2*(13166900320841109317259245/254195527518153210548497708)
      = 113930863438235495956989609/127097763759076605274248854 := by
  grind

theorem headline_k12_distinct :
    (1 : Rat)
      - 13166900320841109317259245/254195527518153210548497708
      = 241028627197312101231238463/254195527518153210548497708 := by
  grind

theorem k12_beats_08964 :
    (8964/10000 : Rat)
      < 113930863438235495956989609/127097763759076605274248854 := by
  grind

theorem k12_beats_09482 :
    (9482/10000 : Rat)
      < 241028627197312101231238463/254195527518153210548497708 := by
  grind

end RhGateK1012
