# Experiment log — AVX2-GT-D4-AOS-OFFICIAL-API

## Decision record

This phase builds the requested domain-safe, default-off reference coefficient
multiplication island and API-completeness scaffold.  It does not propose or
measure an AVX2 candidate, and it does not build a shadow KEM.

## AVX2 dataflow follow-up

`gt_d4aos_ntt_avx2_proto`, `gt_d4aos_basemul_avx2_proto`, and
`gt_d4aos_invntt_avx2_proto` are default-off AVX2 intrinsics feasibility
prototypes. They pass 32 deterministic F/I/B differentials against the d4
reference with ASAN/UBSAN. Their direct 96-point algorithm is intentionally
not a candidate: the static 48×96 Forward/Inverse evaluation count blocks
same-binary benchmarking and ASM authorization. Unsanitized inverse audit:
no YMM stack spill; symbols F=0x253, B=0x3cd, I=0x29d bytes. Source hashes:
`d3b72bb83081424140444a30a952865e520a7fd913717df9654c9faa8b5a2de5`
(prototype C), `88c939bde62f67e5a959fa580771ae88090edf34fbfe2908c44f042e1023f5fc`
(header), `c8c0aa7ff774f5fd6375e14b7ba637896eb35d2233a86999752716eba8157da2`
(test), and `73027b9821adde3aafabaa459fc3118a915bde6125245419eeab597d65b851e4`
(sanitized binary).

## Reproduction

Run from this directory:

```sh
make d4-aos-generated-check
make d4-aos-ref-test
make d4-aos-api-coverage
```

The tested compile flags are `-O3 -g -Wall -Wextra -Wpedantic -Wshadow
-Wconversion -mavx2 -fsanitize=address,undefined -fno-omit-frame-pointer`.

The reference test performs 768 natural-basis F/I checks, 768 physical AoS
lane F/I checks, four full representation-boundary F/I vectors, every
coefficient-pair basis product for all 192 terminal roots, 10,000 deterministic
F/I rounds, 1,000 independent natural-schoolbook products, 768 monomial
products, range cases, alias cases, canaries, and ASAN/UBSAN instrumentation.
`ASAN_OPTIONS=detect_leaks=0` is deliberately
set only for the test execution because LeakSanitizer cannot run in the
ptrace-restricted sandbox; ASAN bounds/use-after-free and UBSAN remain enabled.

## Artifact policy

Persistent inputs/evidence are this log, the contract/proof/coverage documents,
the generated table manifest, and the source revisions listed in `STATUS.yml`.
The executable, raw sanitizer output, and object files are ephemeral under
`build/`.  No candidate branch, worktree, source copy, promotion, or commit is
created: this campaign has no assembly candidate.
