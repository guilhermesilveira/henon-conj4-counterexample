# Universal Period-3 Orbits for Generalized Hénon Maps over ℚ

**A Counterexample to Conjecture 4 of Berger et al. (BIRS 2023)**

## Abstract

The generalized Hénon map f(x,y) = (y, y² + c + bx), with c, b ∈ ℚ, is a polynomial
automorphism whose arithmetic dynamics has been the subject of recent conjectures.
Conjecture 4 of Berger et al. (Arnold Math. J., 2024), from the 2023 BIRS workshop,
asserts that for all but finitely many δ ∈ ℚ, every rational periodic point has
period dividing 2.

We disprove this in the strongest possible way: for **every** b ∈ ℚ \ {-1}, an explicit
algebraic family gives a primitive period-3 orbit, with c = -(29b² + 38b + 29)/16.

Secondary results: sharpness of Conjecture 3 ({1,2,3,4,6,8} all realized), period-7
discovery at b = -1, denominator preservation theorem, and Faltings finiteness analysis.

## Quick Verification (30 seconds)

```bash
# Verify 20 period-3 orbits by exact arithmetic — no dependencies
python3 src/exp002i-odd-delta-family/verify_one_line.py

# Full logical chain: map definition → f³(P₀) = P₀ → period = 3
python3 src/exp002j-unified-parametric/proof_full_chain.py

# SymPy proof that all 3 identities vanish as polynomials in b
python3 src/exp002j-unified-parametric/unified_family_d.py
```

## Repository Structure

- `paper.tex` — Main LaTeX source (9 pages)
- `references.bib` — BibTeX references
- `Makefile` — Build with `make pdf`
- `src/` — All experiment code (self-contained)
  - `exp001-conj3-period-search/` — Conjecture 3 period search
  - `exp001e-period6-cubic/` — Period-6 from Φ₆ cubic factor
  - `exp001f-period8-search/` — Period-8 from denominator pattern
  - `exp001g-parametric-family/` — Denominator preservation theorem
  - `exp002g-conj4-algebraic/` — Algebraic analysis of Conjecture 4
  - `exp002h-wider-delta-confirm/` — Extended search (all integers)
  - `exp002i-odd-delta-family/` — Parametric family for odd δ
  - `exp002j-unified-parametric/` — **Universal family** (main result)
  - `exp004-long-cycles/` — Period-7 discovery
  - `exp005-canonical-heights/` — Canonical height verification
  - `exp006-genus-analysis/` — Genus/Faltings analysis
- `output/` — Experiment outputs (results, logs, data)

## Requirements

- Python 3.x (standard library only for `verify_one_line.py`)
- SymPy (`pip install sympy`) for algebraic proofs
- LaTeX distribution for paper compilation

## Build the Paper

```bash
make pdf
```

## Citation

```bibtex
@article{silveira2026universal,
  title={Universal Period-3 Orbits for Generalized {H}\'enon Maps over $\mathbb{Q}$:
         A Counterexample to {C}onjecture~4 of {B}erger et al.},
  author={Silveira, Guilherme},
  year={2026}
}
```
