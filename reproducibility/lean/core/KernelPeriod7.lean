import HenonPub15.Defs
import Mathlib.Tactic.FinCases
import Mathlib.Data.Fintype.Fin
import Mathlib.Tactic.NormNum
import Mathlib.Dynamics.PeriodicPts.Lemmas

/-!
# PUB-15: Period-7 Orbit at b = -1, c = -9/16

Supplement period-7 example: at b = -1, c = -9/16, the generalized Hénon map admits
a primitive period-7 orbit over ℚ. All seven points have denominator 4.

The orbit:
  P₀ = (-3/4, -1/4) → P₁ = (-1/4, 1/4) → P₂ = (1/4, -1/4) →
  P₃ = (-1/4, -3/4) → P₄ = (-3/4, 1/4) → P₅ = (1/4, 1/4) →
  P₆ = (1/4, -3/4) → P₀


-/

namespace AuditKernel
open HenonPub15

/-- Period-7 parameter b. -/
def p7b : ℚ := -1

/-- Period-7 parameter c. -/
def p7c : ℚ := -9/16

/-- The 7 orbit points.  -/
def p7pt : Fin 7 → ℚ × ℚ
  | 0 => (-3/4, -1/4)
  | 1 => (-1/4, 1/4)
  | 2 => (1/4, -1/4)
  | 3 => (-1/4, -3/4)
  | 4 => (-3/4, 1/4)
  | 5 => (1/4, 1/4)
  | 6 => (1/4, -3/4)

/-- Each step of the orbit: f(Pᵢ) = Pᵢ₊₁ mod 7. -/
theorem p7_step0 : genHenonMap p7c p7b (p7pt 0) = p7pt 1 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step1 : genHenonMap p7c p7b (p7pt 1) = p7pt 2 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step2 : genHenonMap p7c p7b (p7pt 2) = p7pt 3 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step3 : genHenonMap p7c p7b (p7pt 3) = p7pt 4 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step4 : genHenonMap p7c p7b (p7pt 4) = p7pt 5 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step5 : genHenonMap p7c p7b (p7pt 5) = p7pt 6 := by norm_num [genHenonMap, p7c, p7b, p7pt]
theorem p7_step6 : genHenonMap p7c p7b (p7pt 6) = p7pt 0 := by norm_num [genHenonMap, p7c, p7b, p7pt]

/-- f⁷(P₀) = P₀: the orbit closes after 7 steps.
     -/
theorem period7_closes :
    (genHenonMap p7c p7b)^[7] (p7pt 0) = p7pt 0 := by
  show genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _
    (genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _ (p7pt 0))))))) = p7pt 0
  rw [p7_step0, p7_step1, p7_step2, p7_step3, p7_step4, p7_step5, p7_step6]

/-- The orbit is primitive: f(P₀) ≠ P₀ (not a fixed point). -/
theorem period7_not_fixed :
    genHenonMap p7c p7b (p7pt 0) ≠ p7pt 0 := by norm_num [genHenonMap, p7c, p7b, p7pt]

/-- All 7 orbit points are distinct. -/
theorem period7_all_distinct :
    ∀ i j : Fin 7, i ≠ j → p7pt i ≠ p7pt j := by
  intro i j
  fin_cases i <;> fin_cases j <;> norm_num [p7pt]

theorem period7_minimal :
    Function.minimalPeriod (genHenonMap p7c p7b) (p7pt 0) = 7 := by
  haveI : Fact (Nat.Prime 7) := ⟨by decide⟩
  exact Function.minimalPeriod_eq_prime period7_closes period7_not_fixed

theorem period7_denominators :
    ∀ i : Fin 7, (p7pt i).1.den = 4 ∧ (p7pt i).2.den = 4 := by
  have d1 : (1 / 4 : ℚ).den = 4 := by
    apply Int.ofNat.inj
    simpa only [Int.cast_ofNat] using (Rat.den_div_eq_of_coprime (a := (1 : ℤ)) (b := (4 : ℤ))
      (by norm_num) (by decide))
  have d3 : (3 / 4 : ℚ).den = 4 := by
    apply Int.ofNat.inj
    simpa only [Int.cast_ofNat] using (Rat.den_div_eq_of_coprime (a := (3 : ℤ)) (b := (4 : ℤ))
      (by norm_num) (by decide))
  intro i
  fin_cases i <;> norm_num [p7pt, d1, d3]

end AuditKernel

#print axioms AuditKernel.period7_closes
#print axioms AuditKernel.period7_not_fixed
#print axioms AuditKernel.period7_all_distinct

#print axioms AuditKernel.period7_minimal
#print axioms AuditKernel.period7_denominators
