# GT(3,16) branch and root search

The special radix-2 gives `y^96=phi` and `y^96=phi^-1`, with `phi=2735` and
`phi^-1=723`.  A standard radix-2 produces four length-48 branches:

| Branch | gamma | beta |
|---:|---:|---:|
| 0 | 2735 | 3209 |
| 1 | 2735 | 248 |
| 2 | 723 | 460 |
| 3 | 723 | 2997 |

Each beta satisfies `beta^2=gamma`.  The generator exhaustively enumerates
all field elements satisfying `F^48=beta^-1`; each branch has exactly 48
solutions.  It then exhausts all `48^4=5,308,416` four-branch combinations
using bitset unions to minimize the combined forward/inverse constant set.
The selected roots are generated data rather than mathematical constants in
this document.

For every selected root and frequency `k`, the component root is
`alpha=F^-1*omega48^k`.  The generator proves `alpha^48=beta` and maps the
resulting 192 exponents bijectively to the frozen Official index tree.
