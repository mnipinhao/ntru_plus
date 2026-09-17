# Wire-monotone shared MA2 ABI: Gates 1-5

## Scope

This checkpoint asks whether both GT forwards, streamed public-key ingress,
the direct `r` serializer, MA2, and exact ciphertext egress should share one
wire-monotone physical lane ABI. It changes leaf-to-lane ownership only. The
GT arithmetic DAG, scale-1 contract, reductions, MA2 formulas, serializer byte
semantics, and pinned Official oracle remain unchanged.

For tile `t`, coefficient plane `j`, and lane `k`, the candidate ABI owns

```text
wire coefficient = first_wire(t) + 4*k + j
```

The work is namespaced below this experiment. It does not modify the pinned
upstream import, clean production, or the pristine SUPERCOP snapshot.

## Gate 1: exact serializer credit

The generated Natural-Q and wire-monotone serializers were compared against
pinned Official `poly_ntt` plus `poly_tobytes`. Both produce the same 1728
bytes. The wire-monotone input makes the exact wire pairing directly local:

| linked operation | Natural-Q | wire-monotone | delta |
| --- | ---: | ---: | ---: |
| `vpermd` | 72 | 0 | -72 |
| index-vector loads | 30 | 0 | -30 |
| parity/pack routing | unchanged | unchanged | 0 |
| static instructions | 1489 | 1387 | **-102** |
| `.text` bytes | 9133 | 8525 | -608 |

This applies independently to direct `r` serialization and the M3B exact
ciphertext egress.

## Gate 2: D1 terminal absorption

The preliminary post-epilogue adapter required 72 `vpshufb` per forward. It
is retained only as an upper bound and is not the selected implementation.

`generate_d1_wire_monotone_absorption.py` instead starts at the D1 live
registers and enumerates the three-level unpack network, operand/output swaps,
free register/store renames, and all `vpermq` choices. The selected result is:

| result | per forward |
| --- | ---: |
| zero-delta tiles | 4 / 18 |
| tiles requiring four lane-local shuffles | 14 / 18 |
| irreducible new `vpshufb` | **56** |
| explicit mask loads | 0 |
| memory-form mask operands | 56 |
| extra cross-half operations | 0 |
| peak-YMM delta | 0 |

The lower-bound claim is deliberately scoped to the enumerated
unpack/rename/`vpermq` family. The linked namespaced forward is raw bit-exact
to the Natural-Q forward after applying the generated ownership permutation.
Its `.text` changes from 14945 to 15449 bytes and `.rodata` from 11968 to
12192 bytes.

## Gate 3: H3 and MA2 feasibility

The H3 decode/validate-to-MA2 schedule was reindexed to the new physical tile
and lane ownership. MA2 arithmetic is unchanged and lambda constants are
reindexed offline. A generator error that initially indexed lambda vectors by
semantic `(branch,p)` instead of the physical plan tile was caught by the raw
MA2 differential and fixed before timing.

| linked property | Natural-Q | wire-monotone | delta |
| --- | ---: | ---: | ---: |
| consumer-required routes | 360 | 360 | 0 |
| loads/stores | same | same | 0 |
| peak YMM | 16 | 16 | 0 |
| `.text` bytes | 22072 | 22072 | 0 |

Valid inputs match the Natural-Q H3 output under the exact ownership map;
invalid public keys are rejected identically.

## Gate 4: caller-weighted static ledger

All entries below are linked static instructions, never cycle estimates:

| Encap component | delta |
| --- | ---: |
| two forwards | +112 |
| H3 ingress/MA2 | 0 |
| direct `r` serializer | -102 |
| M3B ciphertext egress | -102 |
| MA2 and offline-reindexed constants | 0 |
| **total per caller island** | **-92** |

The corrected negative ledger authorizes serious pricing. The old `+144 -102
-102 = -60` calculation is only the superseded adapter upper bound.

## Correctness and linked gates

- Generated artifacts reproduce with `--check`.
- Forward ownership mapping is raw bit-exact for zero, alternating, and 400
  random-small trials.
- Direct serializers match each other and pinned Official output for 240
  random-small trials.
- H3 valid/invalid decode and raw MA2 differentials pass for 160 trials.
- The complete island matches Natural-Q and pinned Official ciphertext for 120
  trials; invalid public keys are rejected.
- ASan/UBSan pass the complete island.
- Wire forward, H3, direct serializer, and H4 objects have 32-byte-aligned
  entries, no calls, branches, stack references, or `vzeroupper`.

Reproduce these gates with:

```sh
make wire-monotone-shared-generate
make wire-monotone-shared-check
make wire-monotone-shared-sanitize
```

## Gate 5: SUPERCOP-derived serious pricing

Boundary:

```text
two coefficient-domain forwards
+ r exact-wire serialization
+ PK decode/validation and MA2
+ exact ciphertext egress
```

`hash_g`, SOTP, and random generation are outside the timed boundary. This is
therefore `supercop-derived-wire-monotone-shared-abi`, not native SUPERCOP KEM
evidence. The campaign uses the pinned SUPERCOP release, its `cpucycles()` and
StQ2 estimator, fixed common O3GC, CPU 1, 9 fresh processes per setting, and
normal/reversed placement with ASLR off/on.

| placement | ASLR | median delta cycles | bootstrap 95% CI | direction |
| --- | --- | ---: | --- | --- |
| normal | off | -47.98 | [-54.48, -26.47] | 9/9 negative |
| normal | on | **-38.86** | **[-53.26, -26.36]** | **9/9 negative** |
| reversed | off | -64.47 | [-71.94, -53.39] | 9/9 negative |
| reversed | on | -62.96 | [-68.50, -55.51] | 9/9 negative |

Normal/ASLR-on is the headline because the selection rule chooses the fastest
ASLR-on control placement. It measures 5207.89 control versus 5168.26
candidate cycles. All four controls agree, so Gate 5 passes: the shared
wire-monotone ABI is a measured win for this complete representation-fanout
island.

## Decision

The shared ABI is accepted as the next research baseline for this caller
island. The result does not authorize clean production or native KEM
promotion. The next admissible step is integration into a namespaced complete
encapsulation caller, full KAT/alias/constant-time closure, then native
SUPERCOP `enc_cycles` and fixed-ELF promotion evidence.

