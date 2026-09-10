# P1 — BaseInv exponent-3455 addition chain

P1 replaces only `binv_inverse3`.  Its ABI, three input loads, three output
stores, Montgomery R1 representation, failure precondition, and public wrapper
are unchanged from P0.

## Arithmetic change

The P0 core starts from Montgomery one and performs 12 squarings plus 10
conditional multiplications.  P1 starts from the already available `xyz` and
uses the 15-multiplication shortest addition chain used by the selected
SUPERCOP source:

`1, 2, 4, 8, 16, 17, 32, 64, 128, 145, 273, 546, 691, 1382, 2764, 3455`.

Including `xy`, `xyz`, and four recovery multiplications, the whole region
drops from 28 to 21 widening Montgomery multiplications.  Static assembly is
`208 -> 157` instructions.  The removed `oneR=-147` materialization is the only
constant-contract change.

## Slothy and correctness

Local Slothy used `/Users/chenpinhao/slothy` with the existing venv interpreter
and the Cortex-A76 model.  It produced a 157-instruction, zero-spill schedule
with an expected 283 cycles.  The exact exponent/scale oracle checked 4,096
vectors (32,768 independent lanes).

Mac and Pi 5 package tests passed the 100-case KAT.  The linked Pi 5 BaseInv
test passed 808 cases (517 success, 291 failure), all 288 injected zero-leaf
positions, exact aliasing, canaries, AAPCS preservation, and wrapper scratch
wipe.  The complete malformed transcript is 417,216 bytes with SHA-256
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`,
identical to P0.

## Pi 5 paired PMU result

Six balanced repetitions on core 3:

| Boundary | P0 cycles | P1 cycles | Delta |
|---|---:|---:|---:|
| BaseInv success | 5561.656 | 5469.860 | -91.797 (-1.65%) |
| Keygen | 47172.250 | 46995.250 | -177.000 (-0.375%) |
| Encaps | 45992.875 | 45997.475 | +0.010% |
| Decaps | 44170.825 | 44178.125 | +0.017% |

BaseInv instructions fall by exactly 51.  Keygen instructions fall by exactly
102, proving that the full-path saving is the two BaseInv calls and not an
unrelated integration change.  Encaps, Decaps, BaseInv failure, and ToBytes are
unchanged within noise.  P1 is promoted.
