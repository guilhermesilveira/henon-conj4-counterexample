# Rational Cycles of Periods Three and Four for Quadratic Hénon Maps

Guilherme de Azevedo Silveira, Alura.

This repository contains the research manuscript, supplement and selected reproducibility sources.

- [Article PDF](article/paper.pdf) and [LaTeX source](article/paper.tex).
- [Supplement PDF](supplement/supplement.pdf) and [LaTeX source](supplement/supplement.tex).
- [Reproduction instructions and precise certificate coverage](reproducibility/COVERAGE.md).
- [References and consulted versions](REFERENCES.md).
- [Scientific scope and correction note](VERSION-NOTES-v2.txt).
- [SHA-256 file manifest](MANIFEST.sha256).

The article classifies rational marked period-three cycles at every fixed rational coefficient b, treating b=-1 separately and proving infinitude of distinct c. At period four it studies b=1: marked components, normalizations, rational lifts, exceptional fibers and normalized rotation quotients. Classical inputs are credited in the article.

## Build

Obtain the official unmodified [jT.cls](https://jtnb.math.u-bordeaux.fr/jT.cls), verify its SHA-256 against [the recorded class provenance](verification/jtnb-class-source.json), and copy it into both article/ and supplement/. The journal class is third-party material and is not redistributed here. With the required TeX packages installed, run:

```sh
sh scripts/build.sh
```

The article builds first because the supplement uses its cross-reference labels. The supplement identifies article equations, propositions and sections by their printed numbers, which remain readable when the PDFs are saved separately. Internal supplement links and web citations are clickable.

## Verification scope

See reproducibility/COVERAGE.md for the exact-algebra scripts and pinned selected Lean certificates. Four selected exact-algebra checks passed on 28 October 2026; the whole article is not formalized. Included Lean sources retain the declared limited scope and are not a complete proof of both classifications. The manuscript, including its AI-use disclosure, is an unrefereed preprint; this repository is not a journal acceptance record.

The scientific scope and correction note identifies the earlier preprint and the withdrawn assertion. No journal acceptance or journal DOI is claimed.
