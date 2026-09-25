# P140: two-state Keccak for key generation's two CBD seeds

## Where it can apply

Key generation expands one 32-byte coin into the f seed and one into the g
seed (`shake256(buf, N/4, coins, 32)`: 2 permutations at 768/864, 3 at 1152).
The two are independent; every other hash in the KEM depends on the one
before it, so this is the only pair.  Coins are drawn per f attempt, then per
g attempt, and consumed in stream order: while f is being tried the next draw
is certain to be used (by an f retry or by g), so it can be drawn up front
without changing what randombytes sees.

## What a two-state permutation costs (`kbench.c`, mlkem-native b3ba7b3)

| per call | M2 Pro (ns) | Cortex-A76 (cycles) |
|---|---:|---:|
| GT x1 scalar / mlkem-native x1 scalar | 315.0 / 315.0 | 927.8 / 928.9 |
| GT x1 v84a / mlkem-native x1 v84a | 146.2 / 146.2 | -- |
| **mlkem-native x2 v84a** (two states) | **147.9** | -- |
| mlkem-native x4 v8a + scalar hybrid (four) | 632.1 | 2,479.0 |
| mlkem-native x4 v8a + v84a + scalar hybrid (four) | 632.5 | -- |

On M2 the second state is free.  On the A76 (no FEAT_SHA3) nothing fits: the
x4 hybrid is 620 cycles a state but needs four states, and with two dummy
states (2,479) it is slower than two x1 calls (1,856).  An x2 scalar+NEON
hybrid does not exist and would need a v8a NEON Keccak, which is slow without
SHA3's eor3/rax1/xar/bcax.

## Prototype on NTRU+768 (`patch768.py`, `import_x2.py`)

- `keccakf1600_x2_v84a.S`: mlkem-native's x2 v84a, instructions unchanged,
  C_SYM symbol, empty without `__ARM_FEATURE_SHA3`.
- `fips202.c`: `shake256_x2(out0, out1, outlen, in0, in1, inlen)` for
  inlen < 136; two x1 calls without SHA3.
- `kem.c`: the key pair draws the next 32 coins before trying f and expands
  both seeds at once (see the comment in `patch768.py`).

Checks: KAT byte-identical on M2 (x2 path, the symbol is linked) and Linux
(fallback path); 100 KEM round trips, ABI masks, the runtime zeroization audit
pass.  `check_zeroization.py`'s source gate pins the old `genf_derand` call
text and needs updating in an integration.

| P129 harness, three sessions | keygen | encaps | decaps |
|---|---|---|---|
| M2 (ns) | 3,794 -> **3,485 (-8.1%)** | 4,040 -> 4,040 | 3,108 -> 3,108 |
| A76 (ns) | 13,123-13,136 -> 13,118-13,122 (+-0) | unchanged | unchanged |

The saving (309 ns) exceeds two permutations (292 ns): the sponge work of the
two calls is merged too.  864 and 1152 have the same key-generation shape
(1152's seeds are three permutations each, and its retries fall back to x1),
so a similar M2 gain is expected there.
