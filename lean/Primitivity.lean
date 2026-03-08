import HenonPub15.Defs
import HenonPub15.OrbitIdentities
import Mathlib.Tactic.Linarith

/-!
# PUB-15: Primitivity — Period Exactly 3

Prove that the orbit is primitive (not a fixed point) for b ≠ -1.
Key: x₁(b) - x₀(b) = 3(b+1), which is nonzero when b ≠ -1.
Since 3 is prime, period | 3 and period ≠ 1 implies period = 3.

Blueprint: `thm:orbit_primitive`, `thm:universal_period3`
-/

namespace HenonPub15

/-- x₁(b) ≠ x₀(b) when b ≠ -1.
    Because x₁ - x₀ = 3(b+1).
    Blueprint: `thm:orbit_primitive` -/
theorem orbit_not_fixed (b : ℚ) (hb : b ≠ -1) :
    universalX1 b ≠ universalX0 b := by
  simp only [universalX1, universalX0]
  intro h
  apply hb
  have : (7 * b + 5) / 4 = -(5 * b + 7) / 4 := h
  have : (7 * b + 5) = -(5 * b + 7) := by linarith
  linarith

/-- f(P₀) ≠ P₀ when b ≠ -1 (the orbit is not a fixed point).
    Blueprint: `thm:orbit_primitive` -/
theorem orbit_primitive (b : ℚ) (hb : b ≠ -1) :
    genHenonMap (universalC b) b (universalP0 b) ≠ universalP0 b := by
  rw [orbit_eq1]
  intro h
  have : universalX1 b = universalX0 b := congr_arg Prod.fst h
  exact orbit_not_fixed b hb this

/-- **Main Theorem (Theorem 2.1):** For every b ∈ ℚ \ {-1}, the point P₀(b)
    is a primitive period-3 point of f_{c(b),b}.
    Blueprint: `thm:universal_period3` -/
theorem universal_period3 (b : ℚ) (hb : b ≠ -1) :
    Function.IsPeriodicPt (genHenonMap (universalC b) b) 3 (universalP0 b)
    ∧ ¬ Function.IsFixedPt (genHenonMap (universalC b) b) (universalP0 b) := by
  constructor
  · -- period divides 3
    exact orbit_period_divides_3 b
  · -- not a fixed point
    exact orbit_primitive b hb

end HenonPub15
