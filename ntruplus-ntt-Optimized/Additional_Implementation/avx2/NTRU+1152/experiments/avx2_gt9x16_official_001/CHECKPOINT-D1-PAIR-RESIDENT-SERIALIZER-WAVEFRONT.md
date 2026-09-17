# D1 pair-resident serializer wavefront search

## Outcome

The complete-pass gate passes for one narrowly defined candidate:

```text
paired D1 terminals
  ├─ store the unchanged 72-vector scale-1 state for later MA2
  └─ feed one two-tile Serializer V2 packet from live registers
```

This removes all 72 serializer reloads.  Unlike the rejected asymmetric
stride-8 ABI, MA2 continues to receive its frozen coefficient-plane layout and
pays no recovery routes.

The checkpoint authorizes one namespaced ASM prototype.  It does not authorize
timing, caller integration, Native SUPERCOP, or production.

## Caller-order constraint

At the end of the `r` Forward, only the serializer can consume the result:

```text
available:      r transform state, hash output buffer
not available:  SOTP-derived m, streamed decoded h
```

Therefore D1 cannot flow directly into MA2 in the real Encap order.  The MA2
stores must remain.  The removable complete pass is the serializer's later
read of all 72 state vectors.

## Exact packet order

Serializer V2 partitions the 18 D1 tiles into nine 128-coefficient packets:

```text
packet 0: b0r5, b0r4
packet 1: b0r3, b0r0
packet 2: b0r2, b0r1
packet 3: b0r7, b0r6
packet 4: b0r8, b1r1  (only cross-branch packet)
packet 5: b1r0, b1r2
packet 6: b1r8, b1r7
packet 7: b1r6, b1r5
packet 8: b1r4, b1r3
```

The executable order is:

```text
branch-0 NTT9
packets 0..3
branch-1 NTT9
packets 4..8
```

Branch-0 row 8 remains in the existing materialized NTT9/NTT16 boundary until
branch-1 row 1 is available.  No new transform-state store or reload is
introduced.

## Pair-resident register schedule

The first D1 tile writes its required MA2 state and retains four final vectors.
The second tile keeps the same arithmetic DAG and instruction count, but
serializes its two D2 products and two D1 products so only two Montgomery
temporaries are live at once.

| phase | live YMM |
|---|---:|
| first tile final | 5 |
| first retained + second input | 9 |
| second D8/D4 | 11 |
| second D2 | 11 |
| second D1 unpack | 13 |
| second terminal transpose | 12 |
| both wire-plane quartets | 8 |
| serializer input formation | 9 |
| Serializer V2 body | **14** |

After both MA2-state stores, each packet uses its generated terminal-source
map to destructively form the eight Serializer V2 inputs.  The allocation is
packet-specific because the frozen D1 output-source identities vary by tile;
there is no single fixed `ymm4..ymm7` coefficient ordering.  The generated
contract records all nine exact register maps.  Every map uses eight data,
six temporary, and two read-only constant registers without a seventeenth
YMM, stack scratch, spill, register-copy boundary, or intermediate array.

## Boundary ledger

```text
                               state stores   serializer loads   later MA2 loads
control                              72              72                72
half-resident fallback               72              36                72
pair-resident candidate              72               0                72
```

The pair-resident candidate therefore deletes one complete 2304-byte read
pass.  Relative to `Forward + standalone Serializer V2`, the pre-link dynamic
budget is:

```text
vmovdqa state loads       -72
separate Forward ret       -1
standalone vzeroupper      -1
routing                     0
Montgomery / Barrett        0
serializer byte stores      0
MA2 state stores            0
D2/D1 instruction count     0
```

## Why this is not automatically a win

The earlier per-tile live-terminal dual-output implementation also removed 72
loads but lost by `+421.5694` cycles in all 9 launches.  Hot L1 reloads were
cheaper than extending every D1 terminal with a large dependent serializer
body.

This candidate is materially different but remains speculative:

- nine two-tile V2 hooks replace eighteen tile hooks;
- the selected V2 serializer is 133 linked instructions smaller than the old
  standalone serializer;
- only the second D1 tile in each packet pays the low-temporary schedule;
- the complete reload pass is still removed.

The remaining danger is loss of D2/D1 instruction-level parallelism and the
same producer/consumer decoupling that defeated the older candidate.

## Decision

Proceed with exactly one namespaced pair-packet ASM prototype.  Before any
timing it must prove:

1. raw scale-1 MA2 state equality;
2. exact 1728-byte serializer and `hash_g` equality;
3. all nine packet ownership intervals;
4. linked `-72` state loads;
5. exact linked def/use peak no greater than 16 YMM;
6. no frame, spill, call, internal `vzeroupper`, or scratch array;
7. unchanged arithmetic, routing, reductions, and stores.

Only after those gates may it receive one short SUPERCOP-derived fanout test.
Given the prior `+421.5694` result, a short non-negative signal closes this
family immediately; it does not proceed to a serious or Native campaign.

The reproducible machine-readable schedule is
`generated/d1-pair-resident-serializer-wavefront.json`, generated by
`tools/generate_d1_pair_resident_serializer_wavefront.py`.

## Namespaced ASM result

The authorized prototype is implemented as
`ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r`.  It emits both the frozen
2304-byte scale-1 MA2 state and the exact 1728-byte wire serialization.

Correctness closes over 1007 zero, positive/negative boundary, alternating,
impulse, and random-CBD1 inputs.  The candidate is raw-state exact against the
current Forward, byte-exact against Serializer V2 and Official `poly_tobytes`,
and `hash_g` exact.  Input immutability, both output canaries, ASan, and UBSan
also pass.

The linked-object audit compares the candidate with the complete split control
(`Forward + standalone Serializer V2`):

```text
dynamic instructions       4033 -> 3959   (-74)
vmovdqa                       100 ->   28   (-72)
ret                             2 ->    1   (-1)
vzeroupper                      1 ->    0   (-1)
all routing                      unchanged
all arithmetic                   unchanged
all state/byte stores            unchanged
.text bytes                 22523 -> 22190 (-333)
.rodata bytes               12224 -> 12224 (0)
```

The candidate has no call, conditional/unconditional branch, stack reference,
spill, frame, scratch array, or internal `vzeroupper`.  Exact backward def/use
replay over the linked instructions reports peak 14 YMM registers and no YMM
live-in.  `.text`, `.rodata`, and the public entry are 32-byte aligned.  This closes the ASM/correctness/static
gate and authorizes only the previously specified short SUPERCOP-derived
fanout diagnostic; Native SUPERCOP and production remain unauthorized.

## Short SUPERCOP-derived fanout result

The one authorized diagnostic is complete.  It starts at the same
coefficient-domain CBD1-compatible `r` and stops after all three exact outputs:

```text
retained scale-1 wire state + hash_g output + SOTP m
```

The control is the frozen wire Forward followed by standalone Serializer V2.
The candidate is the pair-resident Forward/Serializer V2 object.  `hash_g` and
`poly_sotp_encode` are identical downstream calls.  Untimed preflight requires
raw retained-state, hash, and SOTP equality.

Pinned SUPERCOP 20260831, fixed common GCC 15.2 `-O3`, CPU 1, performance
governor, turbo disabled, balanced same-ELF ordering, three fresh processes,
and 576 pooled observations per variant give:

| path | StQ1 | StQ2 | StQ3 |
|---|---:|---:|---:|
| Forward + standalone Serializer V2 | 19742.9236 | 19802.5208 | 20009.8194 |
| pair-resident D1 + Serializer V2 | 20032.8194 | 20079.0625 | 20205.5625 |
| candidate - control | +289.8958 | **+276.5417** | +195.7431 |

Every fresh-process StQ2 delta is positive:

```text
+286.1250, +272.6458, +275.2500 cycles
```

The valid installation is
`crypto_kem/ntruplus1152/avx2-gt9x16-wire-d1-pair-v2-exp016-sc20260831`.
The saved measure ELF SHA-256 is
`0d02c3ba4d109acc4dca4a08a8aabcba8bdd6dff133f649d4a38d24add8cca5f`.
The preliminary `exp015` installation produced no timing data: its wrapper
called the pre-namespace symbol without the `_r` suffix, and SUPERCOP rejected
the link.  It is retained only as a failed-build record.

This result confirms the earlier warning: deleting the 72 hot-L1 reloads does
not compensate for extending the D1 dependency path and removing the
materialized producer/consumer scheduling boundary.  Per the predeclared
decision rule, the pair-resident family is closed immediately.  Do not run a
serious campaign, Native SUPERCOP, or production integration for this
candidate.  The selected baseline remains materialized wire Forward plus
Serializer V2/direct hash-stage work.

Result directory:
`results/20260916-000442/supercop-d1-pair-resident-v2-fanout-short/`.
