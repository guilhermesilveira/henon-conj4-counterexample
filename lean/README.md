# Lean 4 Formalization

Machine-verified proofs for the main results of this paper.

## What is formalized

| Paper Result | Lean theorem | Tactic |
|---|---|---|
| Theorem 2.1 (universal period-3 family) | `HenonPub15.universal_period3` | `field_simp; ring` + `linarith` |
| Corollary 2.2 (Conjecture 4 is false) | `HenonPub15.conj4_false` | direct from Thm 2.1 |
| Proposition 6.1 (period-7 orbit) | `HenonPub15.period7_closes` | `native_decide` |

## Verification status

- **0 sorry** (no unproved assertions)
- **0 custom axioms** (no trusted assumptions)
- **12/12 blueprint nodes verified**

## Building

```bash
# Install elan (Lean version manager) if needed:
# curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

cd lean/
lake update    # downloads Mathlib (pre-compiled, ~3.5GB)
lake build     # compiles all proofs
```

## File structure

| File | Contents |
|---|---|
| `Defs.lean` | `genHenonMap`, `universalC/X0/X1/X2/P0` |
| `OrbitIdentities.lean` | `orbit_eq1/eq2/eq3`, `orbit_period_divides_3` |
| `Primitivity.lean` | `orbit_primitive`, `universal_period3` |
| `Conjecture4.lean` | `conj4_false` |
| `Period7.lean` | `period7_closes`, `period7_not_fixed`, `period7_all_distinct` |
