import HenonPub15.Defs

/-!
# PUB-15: Period-7 Orbit at b = -1, c = -9/16

Proposition 6.1: At b = -1, c = -9/16, the generalized Hénon map admits
a primitive period-7 orbit over ℚ. All seven points have denominator 4.

The orbit:
  P₀ = (-3/4, -1/4) → P₁ = (-1/4, 1/4) → P₂ = (1/4, -1/4) →
  P₃ = (-1/4, -3/4) → P₄ = (-3/4, 1/4) → P₅ = (1/4, 1/4) →
  P₆ = (1/4, -3/4) → P₀

Blueprint: `def:period7_params`, `thm:period7_orbit`
-/

namespace HenonPub15

/-- Period-7 parameter b. -/
def p7b : ℚ := -1

/-- Period-7 parameter c. -/
def p7c : ℚ := -9/16

/-- The 7 orbit points. Blueprint: `def:period7_params` -/
def p7pt : Fin 7 → ℚ × ℚ
  | 0 => (-3/4, -1/4)
  | 1 => (-1/4, 1/4)
  | 2 => (1/4, -1/4)
  | 3 => (-1/4, -3/4)
  | 4 => (-3/4, 1/4)
  | 5 => (1/4, 1/4)
  | 6 => (1/4, -3/4)

/-- Each step of the orbit: f(Pᵢ) = Pᵢ₊₁ mod 7. -/
theorem p7_step0 : genHenonMap p7c p7b (p7pt 0) = p7pt 1 := by native_decide
theorem p7_step1 : genHenonMap p7c p7b (p7pt 1) = p7pt 2 := by native_decide
theorem p7_step2 : genHenonMap p7c p7b (p7pt 2) = p7pt 3 := by native_decide
theorem p7_step3 : genHenonMap p7c p7b (p7pt 3) = p7pt 4 := by native_decide
theorem p7_step4 : genHenonMap p7c p7b (p7pt 4) = p7pt 5 := by native_decide
theorem p7_step5 : genHenonMap p7c p7b (p7pt 5) = p7pt 6 := by native_decide
theorem p7_step6 : genHenonMap p7c p7b (p7pt 6) = p7pt 0 := by native_decide

/-- f⁷(P₀) = P₀: the orbit closes after 7 steps.
    Blueprint: `thm:period7_orbit` -/
theorem period7_closes :
    (genHenonMap p7c p7b)^[7] (p7pt 0) = p7pt 0 := by
  show genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _
    (genHenonMap _ _ (genHenonMap _ _ (genHenonMap _ _ (p7pt 0))))))) = p7pt 0
  rw [p7_step0, p7_step1, p7_step2, p7_step3, p7_step4, p7_step5, p7_step6]

/-- The orbit is primitive: f(P₀) ≠ P₀ (not a fixed point). -/
theorem period7_not_fixed :
    genHenonMap p7c p7b (p7pt 0) ≠ p7pt 0 := by native_decide

/-- All 7 orbit points are distinct. -/
theorem period7_all_distinct :
    ∀ i j : Fin 7, i ≠ j → p7pt i ≠ p7pt j := by native_decide

end HenonPub15
