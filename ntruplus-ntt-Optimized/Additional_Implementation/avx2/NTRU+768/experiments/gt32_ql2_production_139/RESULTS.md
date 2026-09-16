# Results

## Qualification

- production `encap.c` directly selects QL2;
- the benchmark GT ELF is compiled exclusively from the production source
  root, not from experiment-generated objects;
- functional KEM test: PASS;
- ASan/UBSan test: PASS;
- canonical KAT SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`;
- 86 pre-existing symbols and rodata are identical between the matched E0V
  and QL2 images;
- both Encap caller slots are 611 bytes;
- `.e0v_tail` and `.ql2_tail` are page-aligned RX; no RWX segment exists.

## Formal SUPERcop comparison

Each ASLR mode used 16 alternating ABBA/BAAB blocks, 32 fresh launches per
implementation, and 3,072 native SUPERcop observations per operation.

| ASLR | Operation | Official | GT QL2 | Delta | Relative | Favorable blocks | 95% CI |
|---|---|---:|---:|---:|---:|---:|---:|
| on | Keypair | 21480.32 | 21262.67 | **-217.65** | -1.013% | 16/16 | [-235.21,-190.73] |
| on | Encap | 28113.76 | 28218.59 | **+104.83** | +0.373% | 1/16 | [+54.02,+109.50] |
| on | Decap | 19314.02 | 19247.86 | **-66.16** | -0.343% | 16/16 | [-88.58,-42.69] |
| off | Keypair | 21443.23 | 21263.68 | **-179.55** | -0.837% | 16/16 | [-198.58,-163.23] |
| off | Encap | 28051.12 | 28207.89 | **+156.76** | +0.559% | 0/16 | [+98.87,+170.52] |
| off | Decap | 19262.85 | 19224.85 | **-38.00** | -0.197% | 16/16 | [-53.58,-24.33] |

## Decision

QL2 is promoted as the GT production Encap architecture at the user's explicit
request. It reduces the previous formal ASLR-on Encap deficit from roughly
252 cycles to roughly 105 cycles while retaining GT wins in Keypair and Decap.
It does not yet make GT Encap faster than Official.
