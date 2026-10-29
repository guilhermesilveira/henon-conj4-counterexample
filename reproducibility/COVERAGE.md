# Reproduction and scope

The article and supplement contain the mathematical arguments. These selected certificates support particular steps; they do not formalize the entire manuscript and do not certify novelty. Numerical examples or failed searches for counterexamples are not general proofs.

## Exact algebra

Use Python 3 with `python3 -m pip install -r reproducibility/requirements.txt`. The ordered-escape checks additionally require the `z3` executable (validated version 4.16.0) on PATH. Run from the repository root:

```sh
python3 reproducibility/period3/verify_exact.py --output /tmp/period3-exact-results.json
python3 reproducibility/period3/verify_second.py --output /tmp/period3-escape-results.json
python3 reproducibility/period3/check_bridges.py
python3 reproducibility/period4/verify.py --output /tmp/period4-results.json
python3 reproducibility/period4/check_supplement.py
```

The ordered-escape check writes SMT queries under reproducibility/period3/queries/, and the supplement check writes reproducibility/period4/supplement-results.json. The published .gitignore excludes those generated files. Other JSON reports are written only to an explicitly requested output path, such as /tmp; JSON files are not ignored globally. Consult each script's output and assertions, not its execution alone. SymPy, Python's exact rational arithmetic and the Z3 implementation form part of the declared trust base.

| Certificate | Correspondence and limits |
|---|---|
| period3/verify_exact.py | Article period-3 parametrization, differences, exceptions and fiber identities; algebra plus the general proof in the article. |
| period3/verify_second.py | Supplement ordered escape and word transport. Universal real formulas are decided by Z3; rational witnesses and infinitude require the explicit mathematical bridges. |
| period3/check_bridges.py | Exact word-transport identities and a control disproving global affine conjugacy. |
| period4/verify.py | Marked components, eliminations, parametrizations and exceptional fibers at b=1. |
| period4/check_supplement.py | Quotient/lifting identities, bounds and controls at b=1, read with the article and supplement. |

The finite-fiber and ordered-escape proofs give two distinct routes to infinitude for each rational b. They share the cycle parametrization/transport assumptions. The finite-fiber argument uses the bound of six parameters in a fiber. The escape argument is independent of that bound. Period 4 is restricted to b=1; the quotients concern normalizations, not the entire singular scheme.

## Lean certificates

Two independent toolchain directories are intentional. With elan/Lake installed, each directory has an exact Lean version and a pinned Mathlib Git revision. Dependency downloads require network access.

In `reproducibility/lean/core`:

```sh
lake update
lake exe cache get
lake build
lake env lean --trust=0 SemanticBridge.lean
lake env lean --trust=0 KernelPeriod7.lean
```

Lean 4.29.0-rc4, Mathlib `3bad2b8ecd5b83c92c411251264c178763cd984c`. Defs and OrbitIdentities define the explicit period-3 section and prove its three transitions and return after three iterates. Primitivity proves nonfixity for b≠-1. SemanticBridge derives minimum period 3, supplies the separate b=-1 witness, verifies the section's collapse at b=-1, and formalizes the finite-exception contradiction, including its restriction to automorphisms. KernelPeriod7 proves the supplement's specific rational period-7 example. It does not classify all rational periods.

In `reproducibility/lean/denominators`:

```sh
lake update
lake exe cache get
lake build
lake env lean --trust=0 N02.lean
```

Lean 4.29.0-rc2, Mathlib `239118b0f8961c721ba33cf81102b387e6a36c0e`. `requested_criterion` formalizes the denominator criterion for the stated b=1 seed sequence, all n≥0 and integer q≥2; its recurrence uses n≥1. It does not prove periodicity or uniform behavior of all seeds.

The complete period-3 and period-4 classifications and their infinitude proofs are not formalized here. Kernel certificates retain the usual Lean/Mathlib trust assumptions. The included proof sources have the limited coverage described above. No complete formal verification of the manuscript is claimed.
