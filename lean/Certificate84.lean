/- Certificate84.lean — the preprint-0.84 certificate layer.
   Core Lean only (grind + Lean.Grind.OrderedRing.sq_nonneg),
   pattern identical to the compiled RhGate/Certificate.lean.
   Proxy-verified by certification/certify84.py; queued for the
   maintainers' same-machine compile.  代理核验，待同机编译. -/

namespace RhGate84

/-- Corrected pairing bundle (register D19):
    2·(3/70) + 3·(17/420) + 6·(1/90) + 3·(1/180) + 1/70 = 32/105. -/
theorem t222_corrected :
    2*(3/70 : Rat) + 3*(17/420) + 6*(1/90) + 3*(1/180) + 1/70
      = 32/105 := by grind

/-- M6 exact: 119/12 + (32/105 − 23/420 − 1/126) = 640/63. -/
theorem M6_exact :
    (119/12 : Rat) + (32/105 - 23/420 - 1/126) = 640/63 := by grind

/-- Sigma7 = 1/8 − 17/360 = 7/90; m7 = 685/36 + 7/90 = 3439/180. -/
theorem sigma7_exact : (1/8 : Rat) - 17/360 = 7/90 := by grind
theorem M7_exact : (685/36 : Rat) + 7/90 = 3439/180 := by grind

/-- Sigma8 exact assembly (C8 = 157/4032 certified):
    1661/3780 − 127/840 + 23/4536 − 563/11340 = 307/1260;
    307/1260 + 157/4032 = 633/2240;
    m8 = 217/6 + 8·(7/90) + 633/2240 = 747361/20160. -/
theorem sigma8_known :
    (1661/3780 : Rat) - 127/840 + 23/4536 - 563/11340
      = 307/1260 := by grind
theorem sigma8_exact :
    (307/1260 : Rat) + 157/4032 = 633/2240 := by grind
theorem M8_exact :
    (217/6 : Rat) + 8*(7/90) + 633/2240 = 747361/20160 := by
  grind

/-- Degree-6 kernel-polynomial corner: with
    Q3*(x) = 1 − (8232/2519)x + (7368/2519)x² − (1932/2519)x³,
    ∫(Q3*)² dν at the pinned moments equals 247/2519.  Stated as
    the expanded rational identity (moments substituted). -/
theorem lambda3_corner :
    (1 : Rat)*1
    + 2*(1*(-8232/2519))*1
    + (2*(1*(7368/2519)) + (-8232/2519)^2)*(4/3)
    + (2*(1*(-1932/2519)) + 2*((-8232/2519)*(7368/2519)))*2
    + (2*((-8232/2519)*(-1932/2519)) + (7368/2519)^2)*(13/4)
    + (2*((7368/2519)*(-1932/2519)))*(101/18)
    + ((-1932/2519)^2)*(640/63)
    = 247/2519 := by grind

/-- k ≤ 6 exact headlines. -/
theorem headline_k6_simple :
    (1 : Rat) - 2*(247/2519) = 2025/2519 := by grind
theorem headline_k6_distinct :
    (1 : Rat) - 247/2519 = 2272/2519 := by grind
theorem k6_beats_four_fifths : (4/5 : Rat) < 2025/2519 := by grind
theorem k6_beats_nine_tenths : (9/10 : Rat) < 2272/2519 := by grind

/-- Degree-8 headlines at the (M7, M8) corner. -/
theorem headline_k8_simple :
    (1 : Rat) - 2*(12241115/162540559) = 138058329/162540559 := by
  grind
theorem headline_k8_distinct :
    (1 : Rat) - 12241115/162540559 = 150299444/162540559 := by
  grind
theorem k8_beats_08493 :
    (8493/10000 : Rat) < 138058329/162540559 := by grind
theorem k8_beats_09246 :
    (9246/10000 : Rat) < 150299444/162540559 := by grind

end RhGate84
