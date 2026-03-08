import HenonPub15.Primitivity

/-!
# PUB-15: Conjecture 4 is False

Conjecture 4 of Berger et al. (2024) asserts that for all but finitely many
b ∈ ℚ, every ℚ-rational periodic point of f_{c,b} has period dividing 2.

We disprove this: for EVERY b ∈ ℚ \ {-1}, there exists c ∈ ℚ such that
f_{c,b} has a period-3 orbit. The set of "exceptional" b is ℚ \ {-1},
which is infinite.

Blueprint: `cor:conj4_false`
-/

namespace HenonPub15

/-- For every b ≠ -1, there exists c and a point that is periodic of period 3
    but not a fixed point. This contradicts Conjecture 4.
    Blueprint: `cor:conj4_false` -/
theorem conj4_false :
    ∀ b : ℚ, b ≠ -1 →
    ∃ c : ℚ, ∃ p : ℚ × ℚ,
      Function.IsPeriodicPt (genHenonMap c b) 3 p ∧
      ¬ Function.IsFixedPt (genHenonMap c b) p := by
  intro b hb
  exact ⟨universalC b, universalP0 b, universal_period3 b hb⟩

end HenonPub15
