import Mathlib.Data.Rat.Lemmas
import Mathlib.Data.Int.ModEq
import Mathlib.RingTheory.Coprime.Lemmas
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! PUB15-N02. All sequence indices are natural numbers; no negative index exists.
The recurrence at n+1 is written using n, n+1, n+2 for arbitrary n : ℕ.
No periodicity or existence of an invariant denominator is asserted. -/

namespace PUB15N02

def parameter (q : ℤ) : ℚ := -(2 * (q : ℚ) + 1) / (q : ℚ)^2

def orbit (q : ℤ) : ℕ → ℚ
  | 0 => -((q : ℚ) + 1) / q
  | 1 => ((q : ℚ) + 1) / q
  | n + 2 => (orbit q (n + 1))^2 + parameter q + orbit q n

def scaled (q : ℤ) (x : ℕ → ℚ) (n : ℕ) : ℚ := q * x n

lemma integer_of_den (q : ℤ) (hq : 0 < q) (x : ℚ)
    (hd : (x.den : ℤ) = q) : (q : ℚ) * x = x.num := by
  have hq0 : (q : ℚ) ≠ 0 := by exact_mod_cast (ne_of_gt hq)
  have h := Rat.num_div_den x
  have hdQ : (x.den : ℚ) = (q : ℚ) := by exact_mod_cast hd
  rw [hdQ] at h
  nth_rw 1 [← h]
  field_simp

lemma coprime_of_square (q k : ℤ) (h : q ∣ k^2 - 1) :
    Nat.Coprime k.natAbs q.natAbs := by
  rw [Nat.coprime_iff_gcd_eq_one, ← Int.gcd_eq_natAbs_gcd_natAbs]
  apply Int.isCoprime_iff_gcd_eq_one.mp
  obtain ⟨d, hd⟩ := h
  exact ⟨k, -d, by nlinarith⟩

lemma den_of_integer_square (q : ℤ) (hq : 0 < q) (x : ℚ) (k : ℤ)
    (ha : (q : ℚ) * x = k) (hs : q ∣ k^2 - 1) :
    (x.den : ℤ) = q := by
  have hq0 : (q : ℚ) ≠ 0 := by exact_mod_cast (ne_of_gt hq)
  have hx : x = (k : ℚ) / q := by apply (eq_div_iff hq0).mpr; simpa [mul_comm] using ha
  rw [hx]
  exact Rat.den_div_eq_of_coprime hq (coprime_of_square q k hs)

lemma scaled_recurrence (q : ℤ) (hq : 0 < q) (x : ℕ → ℚ)
    (hr : ∀ n : ℕ, x (n+2) = x (n+1)^2 + parameter q + x n) :
    ∀ n : ℕ, scaled q x (n+2) =
      (scaled q x (n+1)^2 - 1) / q + scaled q x n - 2 := by
  have hq0 : (q : ℚ) ≠ 0 := by exact_mod_cast (ne_of_gt hq)
  intro n
  simp only [scaled, hr n, parameter]
  field_simp
  ring

/-- General sequence theorem; the first seed covers index zero, and the
recurrence covers every positive central index. The second seed is not needed
for this stronger conditional theorem. -/
theorem criterion (q : ℤ) (hq : 2 ≤ q) (x : ℕ → ℚ)
    (h0 : x 0 = -((q : ℚ) + 1) / q)
    (hr : ∀ n : ℕ, x (n+2) = x (n+1)^2 + parameter q + x n) :
    (∀ n : ℕ, ((x n).den : ℤ) = q) ↔
    (∀ n : ℕ, ∃ k : ℤ, scaled q x n = k ∧ q ∣ k^2 - 1) := by
  have hpos : 0 < q := by omega
  have hq0 : (q : ℚ) ≠ 0 := by exact_mod_cast (ne_of_gt hpos)
  constructor
  · intro hd
    have ha : ∀ n, scaled q x n = ((x n).num : ℚ) :=
      fun n => integer_of_den q hpos (x n) (hd n)
    intro n
    refine ⟨(x n).num, ha n, ?_⟩
    cases n with
    | zero =>
      have hz : (x 0).num = -(q+1) := by
        have hzQ : scaled q x 0 = (-(q+1) : ℤ) := by
          simp only [scaled, h0]
          push_cast
          field_simp
        rw [ha 0] at hzQ
        exact_mod_cast hzQ
      rw [hz]
      exact ⟨q+2, by ring⟩
    | succ n =>
      have hrQ := scaled_recurrence q hpos x hr n
      rw [ha (n+2), ha (n+1), ha n] at hrQ
      have heQ : (((x (n+1)).num : ℚ)^2 - 1) =
          (q : ℚ) * (((x (n+2)).num : ℚ) - (x n).num + 2) := by
        field_simp at hrQ
        nlinarith [hrQ]
      have heZ : (x (n+1)).num^2 - 1 = q * ((x (n+2)).num - (x n).num + 2) := by
        exact_mod_cast heQ
      exact ⟨(x (n+2)).num - (x n).num + 2, heZ⟩
  · intro hs n
    obtain ⟨k, ha, hk⟩ := hs n
    exact den_of_integer_square q hpos (x n) k ha hk

/-- The exact canonical sequence in the article, quantified over ALL q≥2 and
ALL n≥0. This is an equivalence, not an assertion of either side. -/
theorem orbit_criterion (q : ℤ) (hq : 2 ≤ q) :
    (∀ n : ℕ, (((orbit q n).den : ℤ)) = q) ↔
    (∀ n : ℕ, ∃ k : ℤ, scaled q (orbit q) n = k ∧ q ∣ k^2 - 1) := by
  apply criterion q hq (orbit q)
  · rfl
  · intro n; rfl

/-- Explicit conversion to the usual integer square congruence. -/
lemma square_congruence (q k : ℤ) :
    q ∣ k^2 - 1 ↔ Int.ModEq q (k^2) 1 := by
  rw [Int.modEq_iff_dvd, dvd_sub_comm]

theorem requested_criterion (q : ℤ) (hq : 2 ≤ q) :
    (∀ n : ℕ, ((orbit q n).den : ℤ) = q) ↔
    (∀ n : ℕ, ∃ k : ℤ, scaled q (orbit q) n = k ∧ Int.ModEq q (k^2) 1) := by
  simpa only [square_congruence] using orbit_criterion q hq

/-- The recurrence with precisely the index convention printed in N02. -/
theorem recurrence_from_one (q : ℤ) (hq : 2 ≤ q) :
    ∀ n : ℕ, 1 ≤ n → scaled q (orbit q) (n+1) =
      (scaled q (orbit q) n ^ 2 - 1) / q + scaled q (orbit q) (n-1) - 2 := by
  intro n hn
  cases n with
  | zero => omega
  | succ m =>
    simpa using scaled_recurrence q (by omega) (orbit q) (fun _ => rfl) m

theorem seeds (q : ℤ) :
    orbit q 0 = -((q : ℚ) + 1) / q ∧ orbit q 1 = ((q : ℚ) + 1) / q := by
  exact ⟨rfl, rfl⟩

/-- Adversarial control: units alone do not imply square-one congruence. -/
theorem coprimality_is_not_enough :
    Nat.Coprime (2 : ℤ).natAbs (7 : ℤ).natAbs ∧
    ¬ Int.ModEq 7 ((2 : ℤ)^2) 1 := by decide

/-- These are the correct two seeds for q=7, followed by an arbitrary tail.
It is NOT the orbit: the recurrence hypothesis has been removed. -/
def withoutRecurrence : ℕ → ℚ
  | 0 => -8/7
  | 1 => 8/7
  | _n + 2 => 2/7

theorem recurrence_cannot_be_dropped :
    withoutRecurrence 0 = -((7 : ℚ)+1)/7 ∧
    withoutRecurrence 1 = ((7 : ℚ)+1)/7 ∧
    (∀ n : ℕ, ((withoutRecurrence n).den : ℤ) = 7) ∧
    ¬ (∀ n : ℕ, ∃ k : ℤ, scaled 7 withoutRecurrence n = k ∧ Int.ModEq 7 (k^2) 1) := by
  refine ⟨by norm_num [withoutRecurrence], by norm_num [withoutRecurrence], ?_, ?_⟩
  · intro n
    cases n with
    | zero => exact Rat.den_div_eq_of_coprime (a := -8) (b := 7) (by norm_num) (by decide)
    | succ n =>
      cases n with
      | zero => exact Rat.den_div_eq_of_coprime (a := 8) (b := 7) (by norm_num) (by decide)
      | succ m => exact Rat.den_div_eq_of_coprime (a := 2) (b := 7) (by norm_num) (by decide)
  · intro h
    obtain ⟨k, hk, hs⟩ := h 2
    change (7 : ℚ) * (2/7) = (k : ℚ) at hk
    have hk2 : k = 2 := by norm_num at hk; exact_mod_cast hk.symm
    subst k
    exact coprimality_is_not_enough.2 hs

end PUB15N02

#print Rat
#check Rat.num_div_den
#check Rat.den_div_eq_of_coprime
#check Int.isCoprime_iff_gcd_eq_one
#check Int.modEq_iff_dvd
#print PUB15N02.parameter
#print PUB15N02.scaled
#check PUB15N02.criterion
#check PUB15N02.orbit_criterion
#check PUB15N02.requested_criterion
#check PUB15N02.recurrence_from_one
#check PUB15N02.seeds
#print axioms PUB15N02.criterion
#print axioms PUB15N02.orbit_criterion
#print axioms PUB15N02.requested_criterion
#print axioms PUB15N02.recurrence_from_one
#print axioms PUB15N02.seeds
#print axioms PUB15N02.coprimality_is_not_enough
#print axioms PUB15N02.recurrence_cannot_be_dropped
