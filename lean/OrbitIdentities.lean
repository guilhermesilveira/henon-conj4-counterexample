import HenonPub15.Defs

/-!
# PUB-15: Three Orbit Identities

Prove that the universal family forms a 3-cycle:
  f(P₀) = P₁,  f(P₁) = P₂,  f(P₂) = P₀.

Each step reduces to a polynomial identity in b, closed by `field_simp; ring`.

Blueprint: `thm:orbit_eq1`, `thm:orbit_eq2`, `thm:orbit_eq3`, `thm:orbit_period_divides_3`
-/

namespace HenonPub15

/-- First orbit identity: f(P₀) = P₁.
    Blueprint: `thm:orbit_eq1` -/
theorem orbit_eq1 (b : ℚ) :
    genHenonMap (universalC b) b (universalP0 b) = universalP1 b := by
  simp only [genHenonMap, universalC, universalX0, universalX1, universalX2, universalP0, universalP1]
  ext <;> simp <;> ring

/-- Second orbit identity: f(P₁) = P₂.
    Blueprint: `thm:orbit_eq2` -/
theorem orbit_eq2 (b : ℚ) :
    genHenonMap (universalC b) b (universalP1 b) = universalP2 b := by
  simp only [genHenonMap, universalC, universalX0, universalX1, universalX2, universalP1, universalP2]
  ext <;> simp <;> ring

/-- Third orbit identity: f(P₂) = P₀.
    Blueprint: `thm:orbit_eq3` -/
theorem orbit_eq3 (b : ℚ) :
    genHenonMap (universalC b) b (universalP2 b) = universalP0 b := by
  simp only [genHenonMap, universalC, universalX0, universalX1, universalX2, universalP2, universalP0]
  ext <;> simp <;> ring

/-- The orbit has period dividing 3: f³(P₀) = P₀.
    Blueprint: `thm:orbit_period_divides_3` -/
theorem orbit_period_divides_3 (b : ℚ) :
    (genHenonMap (universalC b) b)^[3] (universalP0 b) = universalP0 b := by
  show genHenonMap _ b (genHenonMap _ b (genHenonMap _ b (universalP0 b))) = universalP0 b
  rw [orbit_eq1, orbit_eq2, orbit_eq3]

end HenonPub15
