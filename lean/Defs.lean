import Mathlib.Dynamics.PeriodicPts.Defs
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
# PUB-15: Universal Period-3 Family — Core Definitions

Generalized Hénon map over ℚ and the universal period-3 family.
This is the arithmetic dynamics convention: f_{c,b}(x,y) = (y, y² + c + bx).
-/

namespace HenonPub15

/-- The generalized Hénon map f_{c,b}(x,y) = (y, y² + c + bx).
Blueprint: `def:gen_henon_map` -/
def genHenonMap (c b : ℚ) (p : ℚ × ℚ) : ℚ × ℚ :=
  (p.2, p.2 ^ 2 + c + b * p.1)

/-- n-th iterate of the generalized Hénon map. Re-exports `Function.iterate`.
Blueprint: `def:gen_iterate` -/
abbrev genIterate (c b : ℚ) (n : ℕ) : ℚ × ℚ → ℚ × ℚ :=
  (genHenonMap c b)^[n]

/-- The universal period-3 parameter: c(b) = -(29b² + 38b + 29)/16.
Blueprint: `def:universal_family` -/
def universalC (b : ℚ) : ℚ := -(29 * b ^ 2 + 38 * b + 29) / 16

/-- The universal period-3 orbit: x₀(b) = -(5b+7)/4.
Blueprint: `def:universal_family` -/
def universalX0 (b : ℚ) : ℚ := -(5 * b + 7) / 4

/-- The universal period-3 orbit: x₁(b) = (7b+5)/4.
Blueprint: `def:universal_family` -/
def universalX1 (b : ℚ) : ℚ := (7 * b + 5) / 4

/-- The universal period-3 orbit: x₂(b) = (b-1)/4.
Blueprint: `def:universal_family` -/
def universalX2 (b : ℚ) : ℚ := (b - 1) / 4

/-- The orbit starting point P₀(b) = (x₀(b), x₁(b)).
Blueprint: `def:universal_family` -/
def universalP0 (b : ℚ) : ℚ × ℚ := (universalX0 b, universalX1 b)

/-- P₁(b) = (x₁(b), x₂(b)). -/
def universalP1 (b : ℚ) : ℚ × ℚ := (universalX1 b, universalX2 b)

/-- P₂(b) = (x₂(b), x₀(b)). -/
def universalP2 (b : ℚ) : ℚ × ℚ := (universalX2 b, universalX0 b)

end HenonPub15
