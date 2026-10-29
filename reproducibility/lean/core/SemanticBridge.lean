import HenonPub15.Primitivity
import Mathlib.Dynamics.PeriodicPts.Lemmas
import Mathlib.Data.Set.Finite.Basic
import Mathlib.Tactic.NormNum

namespace SemanticBridge
open HenonPub15 Function

theorem period3_iff {α : Type*} (f : α → α) (p : α) :
    minimalPeriod f p = 3 ↔ IsPeriodicPt f 3 p ∧ ¬ IsFixedPt f p := by
  haveI : Fact (Nat.Prime 3) := ⟨by decide⟩
  exact minimalPeriod_eq_prime_iff

theorem universal_minimal (b : ℚ) (hb : b ≠ -1) :
    minimalPeriod (genHenonMap (universalC b) b) (universalP0 b) = 3 :=
  (period3_iff _ _).mpr (universal_period3 b hb)

theorem minus_one_minimal :
    minimalPeriod (genHenonMap (-1) (-1)) (0,-1) = 3 := by
  apply (period3_iff _ _).mpr
  constructor
  · show genHenonMap (-1) (-1) (genHenonMap (-1) (-1)
      (genHenonMap (-1) (-1) (0,-1))) = (0,-1)
    norm_num [genHenonMap]
  · norm_num [IsFixedPt, genHenonMap]

theorem family_collapses :
    universalC (-1) = -5/4 ∧ universalP0 (-1) = (-1/2,-1/2) ∧
    minimalPeriod (genHenonMap (universalC (-1)) (-1)) (universalP0 (-1)) = 1 := by
  constructor
  · norm_num [universalC]
  constructor
  · norm_num [universalP0, universalX0, universalX1]
  · apply minimalPeriod_eq_one_iff_isFixedPt.mpr
    norm_num [IsFixedPt, genHenonMap, universalC, universalP0, universalX0, universalX1]

theorem all_parameters (b : ℚ) :
    ∃ c : ℚ, ∃ p : ℚ × ℚ, minimalPeriod (genHenonMap c b) p = 3 := by
  by_cases hb : b = -1
  · subst b
    exact ⟨-1, (0,-1), minus_one_minimal⟩
  · exact ⟨universalC b, universalP0 b, universal_minimal b hb⟩

def exceptional : Set ℚ :=
  {b | ∃ c : ℚ, ∃ p : ℚ × ℚ, 2 < minimalPeriod (genHenonMap c b) p}

theorem exceptional_all : exceptional = Set.univ := by
  ext b
  simp only [Set.mem_univ, iff_true]
  obtain ⟨c,p,h⟩ := all_parameters b
  exact ⟨c,p,by rw [h]; decide⟩

theorem exceptional_automorphic :
    exceptional ∩ {b : ℚ | b ≠ 0} = {b : ℚ | b ≠ 0} := by
  rw [exceptional_all, Set.univ_inter]

theorem outside_finite (B : Set ℚ) (hB : B.Finite) :
    ∃ b : ℚ, b ∉ B ∧ b ≠ 0 ∧ b ≠ -1 ∧
      ∃ c : ℚ, ∃ p : ℚ × ℚ, minimalPeriod (genHenonMap c b) p = 3 := by
  haveI : Infinite ℚ := Infinite.of_injective (fun n : ℕ => (n : ℚ)) Nat.cast_injective
  obtain ⟨b,hb⟩ := (hB.union (Set.finite_singleton (0 : ℚ) |>.union (Set.finite_singleton (-1 : ℚ)))).exists_notMem
  have h : b ∉ B ∧ b ≠ 0 ∧ b ≠ -1 := by simpa only [Set.mem_union, Set.mem_singleton_iff, not_or] using hb
  exact ⟨b,h.1,h.2.1,h.2.2,all_parameters b⟩

-- Periodic always requires a positive return; n=0 alone is insufficient.
def periodic (f : ℚ × ℚ → ℚ × ℚ) (p : ℚ × ℚ) : Prop :=
  ∃ n : ℕ, 0 < n ∧ IsPeriodicPt f n p

def finiteExceptionAssertion : Prop :=
  ∃ B : Set ℚ, B.Finite ∧ ∀ b : ℚ, b ∉ B → ∀ c : ℚ, ∀ p : ℚ × ℚ,
    periodic (genHenonMap c b) p → IsPeriodicPt (genHenonMap c b) 2 p

def finiteExceptionAutomorphic : Prop :=
  ∃ B : Set ℚ, B.Finite ∧ ∀ b : ℚ, b ∉ B → b ≠ 0 → ∀ c : ℚ, ∀ p : ℚ × ℚ,
    periodic (genHenonMap c b) p → IsPeriodicPt (genHenonMap c b) 2 p

theorem minimum3_not_return2 (f : ℚ × ℚ → ℚ × ℚ) (p : ℚ × ℚ)
    (h : minimalPeriod f p = 3) : ¬ IsPeriodicPt f 2 p := by
  intro hr
  have hd := hr.minimalPeriod_dvd
  rw [h] at hd
  norm_num at hd

theorem no_finite_exception_automorphic : ¬ finiteExceptionAutomorphic := by
  rintro ⟨B,hB,h⟩
  obtain ⟨b,hout,hzero,_,c,p,hm⟩ := outside_finite B hB
  have hp : periodic (genHenonMap c b) p := ⟨3,by decide,((period3_iff _ _).mp hm).1⟩
  exact minimum3_not_return2 _ _ hm (h b hout hzero c p hp)

theorem no_finite_exception : ¬ finiteExceptionAssertion := by
  rintro ⟨B,hB,h⟩
  exact no_finite_exception_automorphic ⟨B,hB,fun b hb _ c p hp => h b hb c p hp⟩

end SemanticBridge

#print SemanticBridge.periodic
#print SemanticBridge.exceptional
#print SemanticBridge.finiteExceptionAssertion
#print SemanticBridge.finiteExceptionAutomorphic
