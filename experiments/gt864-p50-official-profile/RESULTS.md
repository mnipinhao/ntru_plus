# P50 — P48 production versus selected SUPERCOP Official

P50 is a measurement-only checkpoint. Exact committed GT864 production at
`53ba4e2708b544f178ff15cced86c5f910b456ac` was compared on Pi 5 with the
user-selected implementation at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
The selected source is SHAKE256-based. It remains deliberately labelled
`official_upstream_latest_verified: false`: P50 verifies the selected tree and
its hashes, not whether a newer upstream revision exists.

## Provenance and correctness

- Official tree SHA-256:
  `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT tree SHA-256:
  `f0c2e87102a01aac96edf98139b380a0714069543ab4bc1d657733908d2ffb7d`.
- The required Official `kem.c`, `symmetric.c`, and `api.h` hashes matched the
  frozen baseline before compilation.
- Fresh GT manifest/build/KEM/KAT passed. KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Six processes each passed 100 exact cross-implementation transcripts and
  100 tampered-ciphertext rejections.
- Twelve cycle-profiler and 24 event-profiler instrumentation-equivalence
  processes passed.
- Pi 5 CPU 3, GCC 14.2.0, ondemand governor; no `do-part` was active and the
  host stayed unthrottled (`0x0`) from 58.2 to 62.6 C.

## Clean full-KEM PMU

Each entry is the median of 252 clean observations. Negative delta means GT
is faster or retires less work. IPC is retired instructions divided by cycles.

| Operation | Official cycles | GT cycles | Cycle delta | Delta % | Instruction delta | Branch delta | Official IPC | GT IPC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keygen | 44297.125 | 43115.000 | **-1182.125** | -2.669% | +4698.0 | +378.0 | 2.016 | 2.181 |
| Encaps | 46446.025 | 44859.125 | **-1586.900** | -3.417% | +2328.0 | -85.0 | 2.601 | 2.745 |
| Decaps | 40760.950 | 39765.075 | **-995.875** | -2.443% | +7161.0 | -60.0 | 2.126 | 2.359 |

P48 production therefore beats the selected Official in all three complete
KEM operations. Relative to the pre-P46/P47/P48 P43 checkpoint, the Encaps and
Decaps margins have grown by about 176 and 144 cycles respectively; Keygen is
stable. This agrees with the caller-specific promotion history.

## Matched component profile

Call-site medians are diagnostic and do not add exactly to the clean KEM
median. P50 extends the old profiler with two fused groups. Encaps compares GT
`Full_to_hash_g` against one Official Full serializer plus `hash_g`. Decaps
compares GT `Full_compare` against one Official Full serializer plus the
separately instrumented inline `verify`. Official's two identical Full calls
are divided by their measured call count before composing these boundaries.

| Operation / matched boundary | Official cycles | GT cycles | Delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen / Forward x2 | 7523.125 | 6793.000 | -730.125 | +1110 | +22 |
| Keygen / BaseInv x2 | 8356.500 | 8314.000 | -42.500 | +1784 | +394 |
| Keygen / BaseMul R0 x2 | 4869.500 | 4349.000 | -520.500 | -356 | +2 |
| Keygen / all ToBytes | 3336.000 | 3383.000 | **+47.000** | +2119 | -39 |
| Encaps / Forward x2 | 7523.000 | 6790.175 | -732.825 | +1110 | +22 |
| Encaps / BaseMulAdd | 2901.000 | 2170.000 | -731.000 | -100 | +1 |
| Encaps / FromBytes checked | 767.400 | 723.050 | -44.350 | +234 | -13 |
| Encaps / Full-to-hash_g | 15676.975 | 15757.750 | **+80.775** | +449 | -70.5 |
| Encaps / ciphertext serializer | 1107.900 | 981.000 | -126.900 | +669 | -13 |
| Decaps / Forward x2 | 7522.850 | 6797.825 | -725.025 | +1110 | +22 |
| Decaps / BaseMul R0 | 2435.000 | 2175.000 | -260.000 | -178 | +1 |
| Decaps / BaseMul Rinv | 1755.000 | 1755.350 | +0.350 | +770 | +73 |
| Decaps / FromBytes checked x3 | 2265.250 | 2166.500 | -98.750 | +699 | -39 |
| Decaps / Inverse+Crepmod3 to fused ternary | 4608.000 | 4761.725 | **+153.725** | +3666 | +57 |
| Decaps / recovered-f serializer+hash_g | 15656.425 | 15446.825 | -209.600 | +521 | -45.5 |
| Decaps / regenerated-f serializer+verify | 1289.950 | 1466.000 | **+176.050** | +822 | -95 |

The key interpretation is that P47 and P48 did not make the underlying GT
Full route cheaper than Official. They removed materialization/copy work at
the caller boundary. Encaps's two serialization-related paths now win by about
46 cycles in aggregate, and Decaps's two paths win by about 34 cycles in
aggregate, even though each fused Full-only sub-boundary remains slower.

GT Forward, BaseMul R0/BaseMulAdd, checked decode, Small serialization and the
recovered-f-to-hash path are not the next bottlenecks. BaseInv and R-inverse
BaseMul retire many more instructions, but are tied with or faster than
Official in cycles on this run. Their instruction cleanup remains secondary
unless a new arithmetic DAG avoids the earlier IPC regressions.

## Decision: P51 transform-domain re-encryption equality

The largest isolated positive boundary is Decaps re-encryption compare at
about 176 cycles. P51 changes the question instead of further polishing the
P47 byte serializer:

```text
current:
  recovered f -> Small bytes -> hash_g
  regenerated f -> Full route/normalize/pack -> byte compare

P51 candidate:
  recovered f -> Small bytes -> hash_g       (unchanged)
  retain recovered FR0 f
  regenerate candidate into a dead poly slot
  compare the two FR0 polynomials modulo q in constant time
```

At that point `c`, `hinv`, and natural-domain `m` are dead, so the candidate
can use an existing polynomial slot. No new coefficient scratch or memory pass
is inherently required. The gate must prove that both operands have the same
FR0 coordinate/root/Montgomery scale and that invertibility of the complete GT
transform makes component-wise congruence equivalent to the existing
canonical-byte equality. It must close exact producer bounds, prove the chosen
zero-mod-q test has no false accept/reject over those bounds, preserve KEM and
malformed-ciphertext behavior, use secret-independent control/addressing, and
beat P47 at complete Decaps. Only after the algebra/range gate may it enter
assembly, Slothy, and Pi 5 timing.

The fused Inverse-to-ternary deficit, about 154 cycles, remains P52 priority if
P51 fails or after it closes. Generic Keygen/Encaps Full work is lower priority
because aggregate caller-level serialization paths are already near parity or
ahead and P38/P44/P45/P49 closed the obvious families.
