# NTRU+768 Official Forward: lane × stage × caller range gate

Branch `avx2-official-opt`; pinned Official SUPERCOP 20260831. This gate asks
whether the 48 terminal Barrett vectors in the unchanged Official `poly_ntt`
can be omitted **for the KEM caller input domains** while preserving layout,
factor/root ownership and Montgomery exponent `e=0`. It does not introduce an
optimized ASM or change the original general-input `poly_ntt`.

## Evidence hierarchy

1. [Lane proof artifact](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-lane-proof-20260921.json): the pinned `ntt.s` SHA is asserted; every physical lane is interval-propagated through top split, radix-3, the first radix-2 stage, and the fused D8/D4/D2/D1 routing. Fixed-constant Montgomery images and the final Barrett image are enumerated over each reachable integer interval. Every signed-word add/sub and Montgomery input is checked before operation. These are conservative proof envelopes, not observed ranges.
2. The scalar replay is compared raw-exact to compiled Official ASM at eight cutpoints: top split, radix-3, first radix-2, D8, D4, D2, pre-Barrett D1 and full output. It passes 1,746 test inputs, including positive and negative impulses at **every one of the 768 coefficient positions**. This checks the model's physical routing; finite differential testing alone is not the range proof.
3. [Consumer proof artifact](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-consumer-proof-20260921.json): a separate conservative Montgomery magnitude envelope, `ceil(A·B/65536)+1729`, is applied to Official BaseInv and quartic BaseMul intermediate formulas. The actual `poly_tobytes` and `poly_crepmod3` ASM are differentially checked for **all 65,536 signed input words**, distributed across all vector/packet positions.
4. [Untimed Official-consumer differential](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-lazy-consumer-differential-20260921.json): modeled pre- and post-Barrett states feed *unchanged* linked Official consumer code. It checks 200 BaseInv cases, 100 Encap MulAdd/hash/ciphertext cases, 100 Decap recovered-r cases, plus a targeted noncanonical `q`-as-zero BaseInv case. All tested status, residues and wire bytes agree. No actual no-Barrett Forward ASM or full KEM KAT exists yet.

## Forward pre-operation and terminal bounds

The model tracks 48 physical YMM vectors × 16 lanes at each stage. Keygen
`f[0]∈{-2,1,4}`, other `f` and `g` coefficients lie in `{-3,0,3}`; Encap
`r/m` and Decap reencryption `r` lie in `[-1,1]`. For Decap's recovered
message, the **full signed-word** Official `crepmod3` instruction sequence
has output `[-2,2]`; this is used instead of assuming `[-1,1]` from valid
samples. At all modeled Forward operations, the signed-word failure list is
empty.

| Input domain | top split | radix-3 | first R2 | D8 | D4 | D2 | D1 pre-Barrett | after Barrett |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keygen f | 2173 | 5688 | 7507 | 9418 | 11306 | 13285 | **15252** | 2372 |
| Keygen g | 2172 | 5687 | 7506 | 9417 | 11305 | 13284 | **15251** | 2372 |
| Encap r/m | 724 | 4221 | 6014 | 7893 | 9761 | 11701 | **13636** | 2372 |
| Decap message from `crepmod3` | 1448 | 4956 | 6761 | 8656 | 10535 | 12492 | **14449** | 2372 |
| Decap reencryption r | 724 | 4221 | 6014 | 7893 | 9761 | 11701 | **13636** | 2372 |

Entries are maximum absolute *independent-interval envelopes* across all
physical lanes, not measured maxima. The machine-readable artifact retains
each lane's `[min,max]`, so no global number is used to silently authorize a
particular lane. No pre-Barrett value reaches the signed
word limit; removing the final reducer does not itself require a repair.

## Consumer connection

The removed Barrett changes representatives, not residues or scale. For
runtime × runtime Montgomery, the low-word multiplication is intentional;
the bound above limits the *returned signed word* and each following add/sub.
Terminal quartic `λ` has `|λ|≤1728`, and Official BaseMul's R² finalizer uses
`867`.

| Caller edge using lazy Forward | Largest relevant proven envelope | Consequence |
|---|---:|---|
| Keygen `f/g → BaseInv` | determinant ≤4472; adjugate ≤5764; applied inverse ≤1892 | All tracked quartic arithmetic remains signed-i16 safe. Existing six-chain batch zero check reads a local product ≤2035 < q, so a zero residue is represented by the actual word zero; retry status is preserved. |
| Keygen Forward × inverse product | See per-operation bounds in consumer JSON | Existing quartic BaseMul/add/finalizer remains within signed-i16. |
| Encap `h × r + m` | runtime product ≤2449; quartic pre-finalizer ≤9796; final `+m` ≤15495 | PK-decoded `h∈[0,3456]`; the additive message is applied after the unchanged R² finalizer. |
| Decap `c − Forward(message) → recovered-r BaseMul` | subtract input ≤17905; BaseMul pre-finalizer ≤10696; finalizer ≤1871 | CT and `hinv` are canonical decoded words. The recovery product and subsequent bytes remain representable. |
| r/recovered-r/key/ciphertext serializer | entire signed-i16 input domain | Linked `poly_tobytes` output is byte-exact to feeding canonical residues for every signed word. |

The BaseInv zero argument is especially important: modulo equality alone
would not protect a machine `vpcmpeqw zero` test. Because each six-chain
local product has magnitude **strictly below q**, a zero residue there can
only be the literal word zero. The proof also retains the existing zero
branch, output clearing and retry semantics; it does not delete them.

## Prototype selection and limits

The proof gate selects exactly one next prototype:

```text
officialopt_poly_ntt_caller_lazy
  = Official Forward, same DAG/layout/twiddles/e=0,
    with only the 48 terminal Barrett vectors omitted.
```

Its theoretical structural change is 48 `vpmulhrsw`, 48 `vpmullw` and 48
`vpsubw` fewer per Forward, plus the now-unneeded `v` constant load. This is
**not** a cycle prediction. The original `poly_ntt` remains available for
general inputs outside these proven KEM domains. A new name avoids silently
changing its contract or code-placement baseline.

Before any timing, the namespaced ASM must pass raw stage differential up to
D1, modulo-q terminal differential, per-caller 100-vector KAT including
Keygen retry/failure and invalid-input semantics, alias/canary/immutability,
linked ABI/alignment/spill/constant-time audit, sanitizer around C wrappers,
and exact serializer bytes. The untimed differential above observed no
random Keygen inversion retry; targeted `q`-as-zero tests do not replace a
full retry-path KAT. Even a local Forward win would not authorize promotion:
complete Keygen, Encap and Decap Native SUPERCOP and placement controls are
separate gates.

## Reproduction

From the AVX2 `NTRU+768/experiments/avx2_official_opt_001` directory, run
these commands in order. Each refuses to overwrite an existing result; the
explicit output paths keep the recorded campaign intact.

```sh
python3 tools/prove_forward_lanes.py --output /tmp/officialopt-lanes-recheck.json
python3 tools/prove_forward_consumers.py --output /tmp/officialopt-consumers-recheck.json
python3 tools/check_forward_lazy_semantics.py --supercop-root /home/nuc/supercop-20260627 --output /tmp/officialopt-differential-recheck.json
```

The second and third scripts consume the recorded first-stage lane artifact,
so a changed lane artifact must be reviewed and promoted deliberately before
those consumer checks are treated as a new campaign.
