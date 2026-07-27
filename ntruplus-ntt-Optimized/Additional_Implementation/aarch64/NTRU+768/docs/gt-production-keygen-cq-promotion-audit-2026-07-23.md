# GT production direct-CQ keygen promotion audit

Updated: 2026-07-23

Mainline note, 2026-07-27: the evidence below records the original
default-off decision. After the standalone Direct-CQ release passed source
closure, KAT, ABI, and full-KEM gates, Direct-CQ became the mainline default.
The measured mixed profile remains available for reproduction.

## Decision

The direct-CQ keygen path is now a formal, default-off GT production profile:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=cq
```

It no longer depends on `asm/gt/experiment/` or `experiments/`. Its source
closure, tests, symbol audit, KAT path, and benchmark target are owned by the
production build.

The balanced release default remains:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=mixed
```

Direct-CQ is the preferred keygen-throughput profile, but it does not replace
mixed as the default in this audit. It saves about 906 keygen cycles while
adding about 2.8 KB of text and causing a repeatable 12-instruction,
approximately 13-cycle code-placement regression in encapsulation and
decapsulation. The latter is only about 0.04%, but the current promotion rule
does not call a larger binary with non-keygen regressions an unconditional
balanced replacement.

## Profile contracts

### Mixed default

```text
coefficient polynomial
  -> generic GT poly_ntt
  -> block-major memory
  -> block-major-to-BPQ conversion
  -> BPQ baseinv prepare
  -> CQ hierarchical inversion
  -> BPQ x CQ basemul
  -> specialized BPQ/CQ canonical pack
```

### Direct-CQ production profile

```text
coefficient polynomial
  -> gt_keygen_poly_ntt_to_cq
  -> CQ memory directly
  -> CQ baseinv prepare
  -> CQ hierarchical inversion
  -> CQ x CQ basemul
  -> specialized CQ canonical pack
```

The production NTT source is dual-entry:

```text
poly_ntt
  -> generic block-major endpoint for encapsulation/decapsulation

gt_keygen_poly_ntt_to_cq
  -> direct CQ endpoint for keygen
```

Both entries share the Good-Thomas frontend and Stage12/Stage345 arithmetic.
Only the public endpoint selector and terminal layout path differ. This keeps
the generic transform contract available without linking a second independent
forward-NTT implementation.

## Production source closure

The direct-CQ-specific production files are:

```text
asm/gt/ntt/poly_ntt_keygen_cq.n1.opt.S
gt/keygen_cq.c
gt/keygen_cq.h
gt/keygen_lambda.c
```

It reuses the following audited keygen sources:

```text
asm/gt/keygen_bpq_cq/baseinv_tree.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
asm/gt/keygen_bpq_cq/pack_cq.S
asm/gt/baseinv/poly_baseinv_fqinv15.S
```

The production layout checker reported:

```text
production_layout_keygen=cq
production_layout_files=43
production_layout_experiment_dependencies=0
production_layout_pass=1
```

The linked symbol closure requires:

```text
gt_keygen_poly_ntt_to_cq
gt_keygen_baseinv_cq_to_cq_scaled_r
gt_keygen_basemul_cq_cq_to_cq_scaled_r
gt_keygen_tobytes_cq
```

and rejects the mixed-only conversion, BPQ baseinv/basemul, and BPQ P1 pack
symbols.

## Correctness and ABI gates

All current gates passed on AArch64:

```text
direct-CQ NTT differential mismatches       0
generic NTT differential mismatches         0
direct-CQ NTT ABI sentinel mask             0x0
generic NTT ABI sentinel mask               0x0
CQ keygen backend differential mismatches   0
CQ keygen backend ABI sentinel mask         0x0
full KEM failure count                      0
production symbol closure                   pass
production source-layout closure            pass
```

The generated KAT response file has:

```text
size    948402 bytes
SHA256  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

This matches the current canonical NTRU+768 response hash used by the
production audit.

## Paired keygen evidence

The same-binary harness links both keygen layouts, uses the same deterministic
inputs and buffers, alternates call order, and checks byte equality after each
pair.

Pi 5 settings:

```text
Cortex-A76, core 3 pinned
portable NO_CE SHAKE
perf cycles/instructions
NTESTS=61
NITERATIONS=2000
NWARMUP=100
32 deterministic input sets
```

| Keygen path | Median cycles | Median instructions | CPI |
|---|---:|---:|---:|
| mixed BPQ/CQ | 37,956 | 86,459 | 0.439 |
| direct-CQ | 36,998 | 81,955 | 0.451 |

Paired result:

```text
median mixed - direct-CQ = 958 cycles
direct-CQ wins            = 61 / 61
correctness mismatches    = 0
```

This establishes that the keygen gain is not caused by linking the candidates
in different binaries.

## Current replacement binaries

These binaries link only the selected production profile. They use portable
`NO_CE` SHAKE on both GT and KPQC final.

| Operation | KPQC final | GT mixed | GT direct-CQ | Direct-CQ vs KPQC | Direct-CQ vs mixed |
|---|---:|---:|---:|---:|---:|
| keygen | 39,962 | 37,679 | 36,773 | -7.98% | -2.40% |
| encapsulation | 39,022 | 37,611 | 37,620 | -3.59% | +0.02% |
| decapsulation | 35,185 | 32,955 | 32,963 | -6.32% | +0.02% |

Retired instructions:

| Operation | KPQC final | GT mixed | GT direct-CQ | Direct-CQ vs mixed |
|---|---:|---:|---:|---:|
| keygen | 80,799 | 86,067 | 81,571 | -4,496 |
| encapsulation | 103,978 | 106,175 | 106,187 | +12 |
| decapsulation | 72,675 | 76,479 | 76,491 | +12 |

A balanced six-run mixed/direct-CQ order check reproduced the replacement
effect:

```text
keygen direct-CQ advantage      about 906 cycles
encapsulation direct-CQ delta   about +14 cycles
decapsulation direct-CQ delta   about +13 cycles
```

## Keygen component attribution

| Component | GT mixed cycles | GT direct-CQ cycles | Delta |
|---|---:|---:|---:|
| sample NTT f | 3,306 | 2,846 | -460 |
| sample NTT g | 3,308 | 2,858 | -450 |
| baseinv actual | 4,044 | 3,942 | -102 |
| basemul actual | 1,668 | 1,762 | +94 |
| baseinv + basemul contract | 5,709 | 5,710 | +1 |
| pack public | 568 | 568 | 0 |
| pack secret f | 605 | 566 | -39 |
| pack secret hinv | 571 | 571 | 0 |

The two direct-CQ NTT calls account for approximately 910 saved cycles.
Baseinv becomes faster and CQ x CQ basemul becomes slower by nearly the same
amount, so the pointwise contract does not hide the NTT saving. The full
keygen result follows the terminal-layout change directly.

## Code size and placement

| Binary | GNU `size` text | ELF `.text` section |
|---|---:|---:|
| KPQC final | 37,397 | not used for the profile decision |
| GT mixed | 98,733 | 90,560 |
| GT direct-CQ | 101,541 | 93,376 |

Direct-CQ adds:

```text
GNU size text   +2,808 bytes (+2.84%)
ELF .text       +2,816 bytes
```

The dual-entry NTT symbols are placed at:

```text
mixed poly_ntt                  address mod32=16, mod64=48
direct-CQ poly_ntt              address mod32=16, mod64=16
direct-CQ keygen CQ entry       address mod32=24, mod64=24
```

The generic encapsulation and decapsulation algorithms are unchanged. Their
small measured delta is consistent with the larger dual-entry text changing
code placement and alignment.

## Frozen source identities

The checked-in assembly is the production source of truth; rebuilding does not
depend on an experiment generator. Current SHA256 values:

```text
b39135f84b72e4cf6e49888fe1b92147476c8c409aaa1a27750d6fa90d73865f  asm/gt/ntt/poly_ntt_keygen_cq.n1.opt.S
b477b37f686fb708513a384d5c09e9ef390b0a4e0c866042329ffcc0e8d1b14f  gt/keygen_cq.c
3f2f537f6a97f1fb76223aa24ac741601f1cff2502a524d2e4f4eeb8e8adbed1  gt/keygen_lambda.c
9cad90bda798981f006033f6c5f6711dcac74b29a3dd9adbc8519411e4d9c6b1  asm/gt/keygen_bpq_cq/baseinv_tree.S
5dd4e2ddb8b7abe3cb00fcbfe73afb29d1010e2f70f31026582ab1d7fdc992d5  asm/gt/keygen_bpq_cq/baseinv_finish.S
bdb52af5bfec5fce0a2b007dd258fd6454c3d5e965ba9559ebb36715b27111e0  asm/gt/keygen_bpq_cq/pack_cq.S
```

The assembly header also records the two source inputs used to form the
dual-entry body:

```text
production input  dcd05579c140e07533f311fa3550bf9e80753bfaf1b7fa342cdafbc48bb21497
direct-CQ input   c8fdb1d61c0c226df0a9493b13c97b3b876284993c3b7ecf9aec1b8d3007ea43
```

## Reopen condition for the default

Direct-CQ may replace mixed as the balanced default after either:

1. the generic entry is laid out so encapsulation/decapsulation no longer
   retire the extra 12 instructions and do not regress in balanced PMU; or
2. the release explicitly chooses keygen throughput over the 2.8 KB text
   increase and approximately 0.04% non-keygen delta.

Until then, both are production-supported profiles, with mixed selected by
default.
