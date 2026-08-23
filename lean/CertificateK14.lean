/- CertificateK14.lean -- the k=10/12/14 headline identities.

   Exact rational certificate layer for the Toeplitz-trace rungs
   (paper v0.91, sec s:tt, Theorem t:k14).  Grade at time of
   writing: exact-candidate (per-constant pedigrees in the paper's
   verification section); the identities below are exact rational
   arithmetic regardless of grade.

   Pattern follows Certificate84.lean (grind on Rat identities).
   To be compiled on the program director's toolchain. -/

namespace RhGateK14

/-- Sigma anchors, 11..14 (pre-registered re-centring forms). -/
theorem sigma11_recentre :
    (852071287/2721600 : Rat) - 94560551/302400 = 128291/340200 := by
  grind

theorem sigma12_recentre :
    (1033020076559/1556755200 : Rat) - 199083751/302400
      - 12*(128291/340200) = 1092211019/1556755200 := by grind

theorem sigma13_recentre :
    (240004263497/167650560 : Rat) - 11694191/8400
      - 78*(128291/340200) - 13*(1092211019/1556755200)
      = 45789263/52390800 := by grind

theorem sigma14_recentre :
    (85585542088667/27243216000 : Rat) - 1264331/432
      - 364*(128291/340200) - 91*(1092211019/1556755200)
      - 14*(45789263/52390800) = 27183066233/18162144000 := by grind

/-- k=10 headlines. -/
theorem headline_k10_simple :
    (1 : Rat) - 2*(46970100247159/764967228211380)
      = 335513513858531/382483614105690 := by grind

theorem headline_k10_distinct :
    (1 : Rat) - 46970100247159/764967228211380
      = 717997127964221/764967228211380 := by grind

theorem k10_beats_simple :
    (8771/10000 : Rat) < 335513513858531/382483614105690 := by grind

theorem k10_beats_distinct :
    (9385/10000 : Rat) < 717997127964221/764967228211380 := by grind

/-- k=12 headlines. -/
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

theorem k12_beats_simple :
    (8964/10000 : Rat)
      < 113930863438235495956989609/127097763759076605274248854 := by
  grind

theorem k12_beats_distinct :
    (9482/10000 : Rat)
      < 241028627197312101231238463/254195527518153210548497708 := by
  grind

/-- k=14 headlines: the main theorem's arithmetic layer. -/
theorem headline_k14_simple :
    (1 : Rat)
      - 2*(352633869846878511557783511830740995191/
           7876602339133293193971616991853147607579)
      = 7171334599439536170856049968191665617197/
        7876602339133293193971616991853147607579 := by grind

theorem headline_k14_distinct :
    (1 : Rat)
      - 352633869846878511557783511830740995191/
        7876602339133293193971616991853147607579
      = 7523968469286414682413833480022406612388/
        7876602339133293193971616991853147607579 := by grind

theorem k14_beats_09104 :
    (9104/10000 : Rat)
      < 7171334599439536170856049968191665617197/
        7876602339133293193971616991853147607579 := by grind

theorem k14_beats_09552 :
    (9552/10000 : Rat)
      < 7523968469286414682413833480022406612388/
        7876602339133293193971616991853147607579 := by grind

/-- Monotone pricing chain instance: 7*lambda_7 > 6*lambda_6. -/
theorem mono_7_gt_6 :
    6*(13166900320841109317259245/254195527518153210548497708 : Rat)
      < 7*(352633869846878511557783511830740995191/
           7876602339133293193971616991853147607579) := by grind

end RhGateK14
