# NTRU+768 Official-opt: BaseInv, Decap ingress, Forward audit

This is a diagnostic round on `avx2-official-opt`, using the pinned SUPERCOP
20260831 `ntruplus768/avx2` source. No optimization ASM, clean source, public
API, or pristine SUPERCOP tree was changed. The phase harness is
**SUPERCOP-derived**, not a Native KEM measurement. Its valid input fixtures
and diagnostic translation unit are reproducible from the experiment.

## Method and evidence boundary

The final campaign used CPU 1, `performance`, turbo disabled, common O3GC,
9 fresh processes, 16 valid input banks, 8 alternating region blocks, and
32 cycle observations per block. Destructive input reset, fixture generation,
preflight, and dispatch selection were outside the timed interval. The linked
ELF SHA-256 is in [metadata.json](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-phase-research-final-20260921/metadata.json); per-launch raw observations and the exact ELF are in that campaign directory. [Summary JSON](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-phase-research-final-20260921/summary.json) reports StQ1/2/3 and each launch's StQ2. This is one Official image, **not** Official-versus-GT paired pricing or a speedup claim.

The Decap diagnostic uses three direct `poly_frombytes` calls on valid CT/SK
inputs. Real Decap short-circuits invalid inputs and declassifies the two SK
decode results. Therefore the decode timings are valid-input mechanism probes,
not the exact Native Decap entry cost. The BaseInv diagnostic wrappers expose
unchanged Official internals; they are not installed into any SUPERCOP candidate.

| Region | StQ2 cycles | What is inside |
|---|---:|---|
| BaseInv denominator | 721.72 | `poly_baseinv_1` plus wrapper |
| BaseInv six-chain batch | 638.58 | `fqinv_batch` plus wrapper |
| BaseInv apply | 306.50 | 12-block `poly_baseinv_2` plus wrapper |
| BaseInv complete | 1249.45 | production `poly_baseinv` on valid input |
| decode three objects | 666.92 | `c`, `f`, `hinv` from bytes |
| decode `c/f` | 531.98 | the first arithmetic operands |
| decode `hinv` | 366.37 | later recovery operand |
| BaseMulScale | 648.44 | predecoded `c/f` |
| inverse | 965.86 | prepared BaseMulScale result |
| crepmod3 | 392.77 | prepared inverse result |
| BaseMulScale→inverse | 1424.62 | one consecutive edge |
| BaseMulScale→inverse→crepmod3 | 1611.53 | one consecutive edge |
| decode→BaseMulScale→inverse→crepmod3 | 2064.02 | one valid-input ingress |

The isolated BaseInv phases sum to 1666.80, far above the complete 1249.45;
isolated Decap stages similarly do not add to 2064.02. Those differences
reflect different cache/residency, wrapper, and scheduling interactions. They
are **not** an optimization credit or proof that a phase can be removed.
Compared with the round-2 caller cutpoints, these absolute timings also have
different input and timing boundaries; do not combine the campaigns.

## 1. BaseInv: actual dependency spine, not an imagined missing batch

Official already performs hierarchical batch inversion. There are 12 SIMD
denominators (16 lanes each), divided into six chains of `chunk=2`.
`poly_baseinv_1` forms all denominators. `fqinv_batch` executes six independent
first products, three pair products, a two-step product of those three, one
R3 scale correction, one vector field inversion using a 15-operation
addition chain for exponent `q−2=3455`, then reverse tree recovery.
`poly_baseinv_2` applies the 12 inverse denominators to four quartic
coefficient vectors each (48 vector applications). The C caller also handles
zero detection/declassification, failure zeroing, and secure clearing.

The likely *serial dependency spine* is:

```text
denominator → one of 6 local products → one of 3 pair products
→ 2 dependent aggregate products → R3 correction → 15-step fqinv
→ reverse aggregate/pair/local products → quartic coefficient application
```

Six lanes of work provide ILP around that spine, but the `fqinv` addition
chain itself is dependent. This is a source-DAG statement, **not** a measured
hardware critical-path latency. The linked census gives 2,821 B for
`fqinv_batch`, 1,153 B for `poly_baseinv_1`, and 162 B for the diagnostic
apply wrapper; the batch symbol contains stack references, while the ASM
denominator routine does not. See [machine census](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-phase-machine-final-20260921.json). Static opcodes and bytes do not assign cycles to individual instructions.

Most defensible next BaseInv experiment: preserve the 15-step inversion and
the six-chain arithmetic, then compare a namespaced same-DAG batch schedule
that shortens one aggregate/reverse handoff or reduces materialization. Its
proof gate must include the zero/retry path, scale `R3` identity, denominator
immutability, and complete Keygen cutpoint; success-path local timing alone
cannot authorize replacement. There is no evidence for a new batch-inversion
algorithm or for deleting the existing secure clears.

## 2. Decap ingress: which values are really live

The real order is `decode/validate c`, `decode/declassify f`,
`decode/declassify hinv`, then `BaseMulScale(c,f)→inverse→crepmod3`.
Only `c` and `f` are needed for the first multiply. `hinv` is retained until
the later recovered-r product. Each decoded polynomial is 768 signed words
(1,536 B); the three resident objects therefore occupy 4,608 B before the
first multiply. The relevant producer-consumer graph is:

```text
CT bytes ──decode c──┐
SK bytes ──decode f──┴→ BaseMulScale → inverse → crepmod3 → message
SK bytes ──decode hinv──────────────────────────────→ recovery BaseMul
```

That graph suggests separate ownership/lifetime studies for `c/f` and
`hinv`, not a single “fuse all three decoders” design. The linked census
contains 1,152 B of BaseMulScale, 1,957 B of inverse, 325 B of crepmod3 and
523 B of decoder entry/body under the audit's ASM boundary rule. This is a
diagnostic linked image, not a dynamic instruction count. The direct
`BaseMulScale→inverse→crepmod3` cutpoint is 1611.53 cycles; the complete
valid-input diagnostic ingress is 2064.02. One cannot subtract isolated
decode cost and label the remainder a pure arithmetic cost.

The next admissible prototype would be a small `c/f` decode-to-BaseMulScale
tile, explicitly retaining validation and a materialized `hinv` path. Before
ASM, prove the exact invalid CT/SK short-circuit, declassification,
zeroization, alias and output scale contracts. A fused valid-input kernel
which changes failure behavior is not a candidate. No Decap ingress
optimization is implemented in this round.

## 3. Forward: fixed constants, reduction and lane proof status

Official's native in-place Forward already uses a raw low-word multiplication
by fixed `−722` for the small-input top split; do not claim that as a new
opportunity. The source-level expanded ledger finds 24 raw top-split
multiply vectors, 168 fixed-twiddle Montgomery vector chains (48 in radix-3,
24 in the first radix-2 stage, 24 in each of D8/D4/D2/D1), and 48 final
Barrett vectors (144 arithmetic instructions). The fixed twiddle chain is
`vpmullw` with `qinv` companion, `vpmulhw` with the twiddle and with `q`, then
`vpsubw`; the final reducer uses `vpmulhrsw` with `v=9`, `vpmullw` by `q`, and
`vpsubw`. See [reduction ledger](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-reduction-audit-20260921.json).

The [physical constant-lane inventory](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-constant-lanes-20260921.json)
resolves all 34 `zetas` twiddle/companion pairs and verifies, in every lane,
`qinv_companion = twiddle × 12929 (mod 2^16)`. It finds 2, 4, 8 and 16
distinct twiddles per 16-lane vector in D8, D4, D2 and D1 respectively.
That progression explains why late-stage constants cannot be treated as a
single broadcast scalar. The table entails 68 executed `zetas` memory-read
instructions per Forward: 8 radix-3 broadcasts, 12 first-radix-2
broadcasts, and 48 later vector loads, in addition to the 5 one-time loads
for `q`, `v`, top-split `−722`, `wqinv` and `w`. These are source-schedule
counts, not cache-miss counts; reducing them requires an actual register-life
or table-reuse schedule, not merely replacing a constant name.

An exhaustive check over all 65,536 signed-word inputs confirms that this
specific `v=9` reducer preserves the residue and produces representatives in
`[-3291,3291]`. This proves the reducer's arithmetic envelope, **not** that
any of the 48 instances is unnecessary. In particular, the experiment has
not proved each physical lane's pre-reduction bound nor that BaseInv,
BaseMul, hash serialization and inverse consumers accept the larger lazy
representatives. The Forward domains also differ: Keygen `f/g` include
coefficients up to 4 in magnitude while Encap `r/m` are small. A removal
proved only for small input needs a distinct entry; it cannot replace
Keygen's shared Forward.

The exact next gate is a lane × stage × caller-domain propagation through
the *linked* shuffle ownership: record every Montgomery input, add/sub
pre-operation, terminal pre-Barrett value and downstream consumer bound.
Classify each terminal vector as required, safely removable, or proof
insufficient. Reuse the existing `qinv`/twiddle table in a constant-lifetime
experiment only after such a range-safe mechanism is identified. This round
implements the census and reducer-domain oracle, **not** a per-lane removal
proof or a new Forward ASM.

## Decision

The three diagnostic questions are now separated, but none has a qualified
optimization candidate. BaseInv has an existing six-chain batch with a
serial exponentiation spine; Decap has a 2,064-cycle valid-input ingress edge
whose decoder and arithmetic phases interact; Forward has 48 terminal
Barrett vectors but no proven removal. Research priority is (1) lane/consumer
range closure for a small Forward change, (2) `c/f` ingress ownership and
failure-semantics-preserving tile, (3) same-DAG BaseInv handoff once its
retry/failure path is modeled. None of these local observations is a new
Native KEM ranking or a clean-promotion claim.
