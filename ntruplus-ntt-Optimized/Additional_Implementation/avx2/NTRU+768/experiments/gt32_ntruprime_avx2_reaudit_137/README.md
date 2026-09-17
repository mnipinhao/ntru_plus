# NTRU Prime AVX2 source re-audit for NTRU+768 (137)

This is a source-level transfer audit of the complete
`NTRU_Prime_truncation/avx2/avx2` directory after NTRU+768 Experiments
129--136.  GT Clean is unchanged.

Primary upstream sources:

- [`__avx2.c`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/__avx2.c)
- [`radix_3x2.S`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/radix_3x2.S)
- [`basemul.S`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/basemul.S)
- [`basemul_core.inc`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/basemul_core.inc)
- [`butterflies.inc`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/butterflies.inc)
- [`permute.inc`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/permute.inc)
- [`rader17.S`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/rader17.S)

The audited source hashes and transfer decisions are recorded in
[`transfer-matrix.json`](transfer-matrix.json).

## What the upstream implementation actually optimizes

The important design is the entire `_mulcore` path, not an isolated assembly
routine:

```text
Rader17
  -> radix 3x2 with address-encoded GT order and pre-twist
  -> twist + 16x16 transpose
  -> cyclic/negacyclic FFT16 multiplication in leaf-instance lanes
  -> inverse 16x16 transpose + post-twist
  -> inverse radix 3x2 and Rader17
  -> one final ring fold + scale
```

Three details matter:

1. `rader17.S` and `radix_3x2.S` encode mathematical permutations in load and
   store offsets.  They do not materialize a canonical permutation first.
2. `twist_transpose_pre/post` performs the diagonal twist on wide source
   vectors at the same boundary as the 16x16 transpose.  BaseMul then operates
   lane-wise; it does not reconstruct quartic coefficients inside qwords.
3. `_mulcore` owns a complete coefficient-to-coefficient multiplication, so
   inverse scale and ring folding have a single final consumer.

## Transfer matrix

| Upstream mechanism | NTRU+768 status | Decision |
|---|---|---|
| GT/Rader permutation in memory offsets | wide frontend/DFT3 deposits already do this | absorbed |
| one persistent leaf-instance SoA island | HWA16 061/062 and Late-SoA 063--067 | persistent form closed; late boundary succeeded |
| twist and transpose at one boundary | M/P/QL2 typed producer stores already use semantic store ownership | substantially absorbed |
| cyclic/negacyclic split before FFT16 BaseMul | normalized D4 072--078 is the quartic analogue | local B3 win; explicit bridge loses |
| fixed-operand `*_precompute` multiplication | prepared P0/fixed-B3 campaign | useful local/prepared primitive; standard caller hard stop |
| tolerate inverse output permutation until post-transform | inverse/merge representation campaigns 026--029 and Late-SoA | covered |
| delayed final ring fold and scale | possible because upstream owns one coefficient endpoint | no matching standard NTRU+ KEM graph; Gate 136 bounds scale credit |
| truncated Rader17 | relies on NTRU Prime's padded/truncated 1536 convolution | not transferable to full NTRU+768 operands/ring |
| large stack-backed FFT16/Karatsuba schedule | upstream uses 0x900--0xb00-byte local workspaces | not a desirable implementation pattern for current zero-spill GT kernels |

## The one remaining source-derived gate

The source does sharpen one still-open premise from Experiment 078:

```text
current rejected bridge:
  Forward(e0/M)
    -> standalone leaf-dependent D(s) normalization
    -> fixed-modulus D4 BaseMul
    -> standalone D(s)^-1
    -> Q24

source-derived candidate:
  conjugated Forward tables/trajectory
    -> directly emit D(s)-normalized leaves
    -> fixed-modulus D4 BaseMul
    -> conjugated Q24 terminal trajectory
```

Here `D(s)=diag(1,s,s^2,s^3)` and every production leaf satisfies
`lambda_i = 2*s_i^4`.  Experiment 076 proved that the normalized fixed-modulus
B3 is executable and wins about 27.7 TSC locally.  Experiment 077 rejected the
explicit 120-Montgomery-chain bridge; Experiment 078 proved that simple
terminal constant relabeling is insufficient, but left a full conjugated
transform trajectory open.

NTRU Prime does **not** prove that this will be free: its pre/post twist still
executes Montgomery multiplications.  The transferable question is whether,
for the NTRU+ NTT32 DAG, each `s^c` diagonal can replace constants on
Montgomery nodes already present rather than introduce new nodes.

### Proposed bounded generator gate

`GT32-D4-CONJUGATED-TWIST-TRANSPOSE-138` should:

1. symbolically conjugate the complete NTT32 Forward by every production
   `D(s_i)`;
2. solve whether the factors can be assigned to existing twist/butterfly
   Montgomery constants, including paths that currently bypass a multiply;
3. do the inverse calculation for the QL2/Q24 terminal map;
4. report added/removed Montgomery nodes, bounds, physical routes and peak
   registers;
5. emit no assembly unless the complete `2F -> normalized B3 -> Q24` path
   deletes a genuine operation class.

The success condition is not merely mathematical equivalence.  It must avoid
the explicit normalization bridge and leave fewer dynamic Montgomery chains
or a shorter measured consumer DAG than the current QL2 path.

## What should not be reopened from this source

- Copying the 16x16 transpose would repeat HWA16; the successful NTRU+ result
  was Late-SoA, not globally persistent planes.
- Copying Bruun/FFT16 does not remove the leaf-dependent lambda normalization;
  076--078 already isolate that exact issue.
- Copying `*_precompute` into the standard SUPERcop API charges preparation on
  every call.  It only makes sense for an explicitly prepared repeated-key API.
- Copying Rader17 truncation changes the algebraic problem and is not a
  scheduling optimization for the NTRU+ ring.
- Moving the final scale without deleting a consumer conversion repeats the
  scale-edge survey and Gate 136; the optimistic free-finalizer ceiling is
  only about 107 TSC against the 218-cycle native-QL2 BaseMul loss.

## Decision

```yaml
direct_kernel_copy: NONE
already_absorbed_or_measured: MOST_MECHANISMS
new_high_value_standard_API_candidate: NONE
bounded_research_candidate:
  name: D4_CONJUGATED_TWIST_TRANSPOSE
  source_premise: pre/post twist at the representation boundary
  prior_local_credit: about_27.7_TSC
  risk: high
  first_step: symbolic_generator_only
production_modified: false
```
