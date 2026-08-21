# Current GT Clean `vzeroupper` audit — 2026-08-20

## Policy

`vzeroupper` is not a YMM register-preservation operation.  YMM registers are
caller-saved under the relevant ABI.  It is useful only to avoid an
AVX-to-legacy-SSE transition penalty at a boundary that can actually execute
legacy SSE.  Therefore:

- do not insert it merely because a function used YMM registers;
- do not insert it on a proven AVX/VEX-to-AVX/VEX private edge;
- retain or remove it at an outer/unknown boundary only after inspecting that
  boundary and benchmarking the intended target CPU;
- do not create helper boundaries solely to manage upper-lane state.

## Fresh final-ELF inspection

Inspected binaries:

- `gt32_supercop_clean_formal_20260820/build/gt-clean-encap-loop`
- `gt32_supercop_clean_formal_20260820/build/official-encap-loop`

The current GT Clean `ntruplus768_enc_derand_impl` contains no out-of-line
`forward_m` helper.  GCC inlines it as adjacent calls:

```text
ntruplus768_ntt_frontend_avx2
ntruplus768_ntt_m_avx2
```

There is no compiler-generated `vzeroupper` between those calls.  The same is
true of the other inspected C-level polynomial call sequences.  Thus the
current Encap image does **not** exhibit the failure mode "every compiler
helper using YMM gets a compiler-inserted `vzeroupper` at return."

## Compiler-generated outer boundaries

GT Clean has two visible compiler-generated `vzeroupper` instructions in the
Encap caller:

| Address | Preceding work | Next call | Classification |
|---:|---|---|---|
| `0x17bc` | vectorized 96-byte coins copy | `hash_f` | conservative unknown/hash boundary |
| `0x18e2` | vectorized shared-secret copy | `__explicit_bzero_chk@plt` | libc/unknown boundary |

Official has the same two shapes at `0x15c1` and `0x16a2`.  Consequently these
instructions are not a GT-specific helper-boundary tax and cannot explain the
GT-versus-Official Encap gap.

`hash_h` also has a compiler-generated `vzeroupper` immediately before its
SHAKE call in both GT Clean and Official.  The Keccak wrapper exits contain
their own transitions in both images as well.  These shared boundaries are not
selected GT polynomial-island optimization targets.

## Hand-written GT leaf exits

The selected GT polynomial leaves do contain explicit assembly epilogues such
as:

```asm
vzeroupper
ret
```

Examples on the valid Encap path include Decode, both frontend calls, both
NTT-M calls, the lazy Q24 pack, B3 general, and the high-range Q24 pack body.
For AVX2-to-AVX2 adjacency these instructions are not required for register
correctness and do not protect against a demonstrated legacy-SSE transition.

They were nevertheless kept in GT Clean because experiment 039 patched them
out one edge at a time with identical ELF/symbol/address geometry and found no
stable useful cycle return.  Every patch retired exactly one fewer instruction,
but the best observed core-cycle medians were only approximately 1--3 cycles
and launch signs were not robust.  This is evidence that the instructions are
mostly overlapped/low-cost on the tested CPU, not evidence that they are
semantically necessary.

## Decision

The requested rule is confirmed:

> Audit compiler and assembly boundaries; mirror Official's absence of an
> internal transition only where the edge is demonstrably private AVX/VEX.
> Do not add `vzeroupper` without an outer AVX/legacy-SSE boundary and benchmark
> evidence.

For the current image:

- no unwanted compiler helper-return pattern was found;
- the compiler-generated Encap transitions match Official outer boundaries;
- hand-written internal leaf transitions are known but were already
  cycle-adjudicated by 039;
- no blanket insertion or removal is promoted;
- a future fused/private island may omit internal `vzeroupper` by construction,
  but that omission is supporting ABI hygiene, not a standalone speed claim.

