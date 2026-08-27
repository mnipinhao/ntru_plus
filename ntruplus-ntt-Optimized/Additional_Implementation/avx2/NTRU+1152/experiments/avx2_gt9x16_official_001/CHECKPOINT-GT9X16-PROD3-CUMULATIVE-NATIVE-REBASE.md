# GT9X16-PROD3-CUMULATIVE-NATIVE-REBASE

## Scope

This checkpoint takes a fresh scheme-level coordinate without changing the
selected transform architecture. The measured candidate contains exactly:

```text
persistent-AoS
+ Natural-Q
+ T0-beta
+ Natural-Q MA2
+ Direct H1
```

It is installed under the non-overwriting disposable-SUPERCOP name
`crypto_kem/ntruplus1152/avx2-gt9x16-prod3-cumulative-exp002`. The official
`avx2` implementation and the pristine pinned snapshot remain untouched.

## Integration contract correction

The first cumulative KAT exposed a scope hole in the earlier Q-order pricing
harness. `f0_ma2_planes_{current,natural}_q` already applied `inv4`, while H1
also applies `inv4` before serialization. Current-Q and Natural-Q therefore
remained byte-identical to each other while both missed the production
ciphertext scale contract. The earlier `-160`-cycle Q-order delta remains a
valid relative island price, but that harness was not a KEM-correct ciphertext
oracle.

The cumulative caller uses a namespaced Natural-Q MA2 scale-4 boundary. It
stores the proven signed-i16 pre-`inv4` state (`[-29899, 29901]`) and lets the
unchanged Direct H1 perform the single required `inv4` and packing step. This
is an integration repair, not a new arithmetic optimization: the MA2 formula,
Natural-Q ownership, lambda identity, output bytes, and total `inv4` count are
unchanged.

The linked `crypto_kem_enc_derand` call graph contains two T0-beta forwards,
one scale-4 Natural-Q MA2, and two Natural-Q H1 serializations. It contains no
old recovery bridge and no `f0_ma2_native_full` call.

## Correctness

The installed flat candidate passes all 100 frozen NTRU+1152 KAT vectors
byte-for-byte. The response SHA-256 is
`2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3`.

## Native SUPERCOP result

Both implementations use unmodified SUPERCOP 20260627 `crypto_kem/measure.c`,
CPU 1, performance governor, disabled turbo, ASLR enabled, nine fresh measure
processes, and 96 observations per operation per launch.

| operation | Official StQ2 | cumulative StQ2 | candidate - Official |
| --- | ---: | ---: | ---: |
| keypair | 34236.16 | 34306.01 | +69.86 |
| enc | 42893.51 | 43885.53 | **+992.02** |
| dec | 30297.83 | 30235.99 | -61.85 |

Native SUPERCOP selected gcc 15.2 O2 for Official and gcc 15.2 O3 for the
candidate. The candidate still loses encapsulation by 2.31%, so this is not a
promotion result. Keypair and decapsulation do not exercise the cumulative
Encap path; their small deltas are recorded only as non-regression context.

The previous native campaign reported `+1498.6991` Enc cycles. The new gap is
about 506.68 cycles smaller, but this is a cross-campaign coordinate, not an
additive causal attribution of H1, Natural-Q, or T0-beta.

## Decision

The cumulative implementation is the current correctness-qualified research
baseline, but it is not a native winner. No new ASM is authorized from this
result. The next checkpoint is `ENCAP-CALLER-ATTRIBUTION-V2` on this exact
candidate, separately repricing:

1. the two current producers against Official transforms;
2. the `r -> (MA2 state, hash bytes)` dual-output edge;
3. resident `h` plus MA2 plus ciphertext serialization.

Only the largest measured current debt should select the next architecture.

## Evidence

- `results/gt9x16-prod3-cumulative-native-rebase-intel155h-20260827-001/summary.json`
- `results/gt9x16-prod3-cumulative-native-rebase-intel155h-20260827-001/kat.json`
- `src/kem_cumulative_native.c`
- `asm/gt9x16_prod3_cumulative_ma2.S`
- `scripts/prepare_gt9x16_prod3_cumulative_native.py`
