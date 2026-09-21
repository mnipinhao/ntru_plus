# NTRU+768 Official AVX2 optimization

Branch: `avx2-official-opt`, forked from `84da0b5`. This branch asks how much
Keygen, Encap and Decap improve while retaining the Official 20260831 AVX2
decomposition, stage order, physical layout and Montgomery scale. The pinned
Official `crypto_kem/ntruplus768/avx2` implementation is the performance
baseline. Frozen `avx2-gt32-clean` is a third comparator, not candidate source.

## Research workflow

1. Verify the pinned SUPERCOP snapshot and import Official into the experiment's
   immutable `upstream/supercop-avx2` directory. Record archive and tree hashes.
2. Audit reachable Forward, BaseMul, BaseInv, inverse, codec and caller paths.
   Record each caller's real input ranges, operand order, scratch, retry count,
   vector arithmetic/routing, constant traffic, liveness and code footprint.
3. First prototype: Official BaseMul plus the Encap message add in one AVX2
   loop. Preserve arithmetic, reduction, layout, scale and alias contracts.
4. Second prototype: inspect Forward's proven reduction/constant opportunities
   across Keygen/Encap/Decap. Use a separate small-input entry only if the
   general-input proof fails. If no arithmetic opportunity qualifies, test a
   same-DAG schedule/constant-lifetime variant instead. Do not fill the slot
   without a concrete mechanism.
5. Run independent differential, bounds, ABI, alignment, sanitizer and linked
   audits. Price component, then complete caller with same-residency inputs.
   Only a complete caller win proceeds to serious and disposable Native KEM.

Report Keygen, Encap and Decap separately. Preserve source/ELF hashes,
compiler, CPU controls, raw observations and StQ1/2/3. Formal Native timing
uses unmodified SUPERCOP measure. Fixed-ELF placement/ASLR controls follow a
Native gain. An isolated component win is a research result, not promotion.

## Frozen inputs and scope

The new worktree is `/home/nuc/src/ntru_plus-official-opt`; the GT worktree was
not changed. The imported Official source is SUPERCOP `20260831`, archive SHA-256
`9a258febbfbbf6de0c09cee73f343d4014597c259415e78a598b7af4b1787208`,
NTRU+768 AVX2 tree SHA-256
`8db00172e705b67e231b63708295781d65681fef2c7422d717fe91ab48d576e7`.
The importer records the source in the experiment's `upstream/UPSTREAM.json`;
that copy remains unmodified. The frozen GT comparator is the clean
`avx2-gt32-clean` tree at branch base `84da0b5`. All SUPERCOP installations
were made into `/tmp/ntruplus768-official-opt-campaign-20260921`, never the
pristine snapshot.

This first round keeps the Official Forward, BaseInv, BaseMul formula, inverse,
physical layout, Montgomery scale, codec, public API, and wire format. The only
arithmetic-path change is where Encap adds the message polynomial.

## Reachable caller and candidate ledger

| Caller | Official path and relevant cost | First-round candidate |
|---|---|---|
| Keygen | sample/retry `f,g`; Forward; batch BaseInv with tree/scale correction; BaseMul products; key serialization/hash | unchanged; used as regression control |
| Encap | validate/decode PK; sample `r`; Forward and hash fanout; form/Forward `m`; BaseMul `h*r`; separate `poly_add(c,c,m)`; ciphertext packing | combine only BaseMul's existing R² finalizer with add-`m` before its final stores |
| Decap | CT/SK decode; BaseMulScale/inverse; message recovery; recovered-`r` hash; reencryption/equality | unchanged; used as regression control |

The prototype preserves the Official multiplication and reduction instruction
sequence. It retains the same output representation and performs `+m` only
after the original finalizer. Each of the 12 finalizer blocks reads four 32-byte
`m` vectors, adds them to live output registers, then performs the original
stores. Compared with the separate `poly_add` pass, its expected dynamic
movement credit is 48 output reloads plus 48 output re-stores; the 48 `m` loads
remain. The linked candidate has no stack/vector spill, call or internal
`vzeroupper`; its symbol is 32-byte aligned. This is caller-boundary reuse,
not a GT-decomposition benefit, and GT's historical −54-cycle add fusion was
*not* used as a prediction.

The reachable linked audit (O3GC) provides a first cost map. These are
**static** instruction counts inside one symbol, before multiplying by loop
trip counts: Official `poly_ntt` has 331, `poly_basemul` 283,
`poly_basemul_scale` 247, `poly_invntt_scale` 372, and `poly_frombytes` 96.
The Forward symbol includes 8 `vpmulhrsw`, 46 `vpmulhw`, 34 `vpmullw`, and
63 aligned vector moves; the inverse has 32 routing opcodes and the decoder
24. This does not make any of them a proven bottleneck. In the fused
finalizer, `%r10` holds the public `m` pointer and four live YMM outputs
receive memory-form `vpaddw` immediately before their original stores. The
next consumer remains the unchanged `poly_tobytes`.

The second Forward slot was deliberately not filled. The linked Official
Forward already has the small-input raw top-split multiply; its late
`vpmulhrsw`/`vpmullw` reduction pairs feed both output halves. The current
evidence does not prove any of those reductions redundant across Keygen's
`f/g` domain and Encap's `r/m` domain, nor a same-DAG interleave that shortens
the dependency path without new movement or register pressure. Removing one
would require a separate per-lane, per-operation range proof and consumer
precondition proof. This is an unspent prototype slot, **not** a claim that
Official Forward is fully optimized.

The actual Forward input contracts read from the pinned caller are: Keygen
`f=1+3·CBD1` (the first coefficient can be 4), `g=3·CBD1`; Encap
`r=CBD1` and `m=SOTP` are small coefficients; Decap forwards the recovered
message and a new CBD1 polynomial. These are separate domains. No
preserve-input copy is part of the native destructive `poly_ntt` call. This
round proves the fusion's range behavior by exact equality to the unchanged
Official BaseMul-plus-add instruction semantics over the tested inputs; it
does **not** claim a new per-operation Forward bound. For the fusion, `m` and
the two multiplicands are disjoint caller buffers; output overlap with one of
them is not a supported alias and is not claimed here.

| Future opportunity | Caller coverage | Gate before writing ASM | Status |
|---|---|---|---|
| Late Forward reduction/constant absorption | Keygen, Encap, Decap if general-domain safe | per-lane pre-operation i16 proof and exact scale/residue identity | not yet proven |
| Small-input Forward specialization | Encap `r/m`, Decap CBD1/recovered message only | separate entry, no Keygen substitution, hash/BaseMul input contract | deferred |
| BaseInv tree/scale correction | Keygen | matched retry-controlled component and source-level dependency ledger | diagnostic only |
| Decode→BaseMulScale ingress | Decap | validation/alias/zeroization preservation | later round |
| Serializer/equality reuse | Encap/Decap | wire-byte exactness and full-caller pricing | later round |

## Correctness and machine evidence

- Primitive: 10,003 raw bit-exact differential cases, including input
  immutability, against `poly_basemul` followed by `poly_add`.
- KEM: 100 deterministic vectors compare PK, SK, CT, shared secret and Decap
  bytes; matched keygen randombytes-call count (zero retries in this sample).
  Invalid CT semantics and invalid PK rejection/zeroization also match.
- ASan/UBSan passed the C wrapper and test harness. LeakSanitizer was disabled
  because ptrace is unavailable in this environment. Assembly memory safety
  was additionally checked by canary/immutability tests and linked audit.
- The only new vector arithmetic is four `vpaddw` per finalizer iteration.
  The original BaseMul formula, reduction, R² finalizer, alias direction and
  constant-time branch/index behavior are retained. The O3GC linked image is
  +1,408 B `.text` and +32 B `.rodata`; this is a code-size observation, not
  a performance diagnosis. Static symbol counts are in
  `results/linked-audit-20260921.json` and must not be read as dynamic counts.

## Timing, with evidence levels separated

Host: Intel Core Ultra 7 155H, P-core CPU 1, `performance` governor, turbo
disabled. The SMT sibling is CPUs 1–2. Metadata, source manifests, ELFs,
compiler selection, raw observations and SUPERCOP `data` are in the experiment's
`results/` campaign directories. The Native figures below are each
implementation's pooled StQ2 from nine fresh SUPERCOP processes; independent
pooling is not a paired causal estimate.

| Native SUPERCOP StQ2 cycles | Official | Official-opt fused | Frozen GT |
|---|---:|---:|---:|
| Keypair | 21,575.25 | 21,626.54 | 21,252.81 |
| Encap | 28,232.12 | 28,095.84 | 28,339.48 |
| Decap | 19,474.44 | 19,375.02 | 19,264.51 |

The same-ELF O3GC component/caller run found a `−24.93`-cycle BaseMul-plus-add
median and a `−39.78`-cycle full Encap median, both 9/9 fresh launches in the
favorable direction. This is a **SUPERCOP-derived diagnostic**, not a Native
SUPERCOP number. The short three-launch Encap result (`−133.83`) was much
larger, so it was not used as the headline.

Native selection used the same compiler class for all three implementations
(SUPERCOP's O2 choice). The common-compiler O3GC fixed ELFs gave nearly tied
normal-placement Encap pooled StQ2 (Official 28,090.20, fused 28,086.12).
We then used independent ABBA/BAAB paired replays: 16 balanced blocks,
64 fresh launches for *each* placement/ASLR setting. Each table entry is the
paired mean `fused − Official`; 95% intervals are block-bootstrap intervals.

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| Normal, ASLR off | +31.15 [20.81, 41.74] | +20.71 [−15.82, 68.04] | +63.39 [36.88, 89.21] |
| Normal, ASLR on | +57.76 [44.92, 72.24] | +38.04 [−37.45, 112.00] | +30.46 [−9.93, 66.16] |
| Reversed, ASLR off | +44.24 [26.84, 61.32] | −1.61 [−40.15, 37.86] | −65.11 [−97.95, −35.30] |
| Reversed, ASLR on | +100.06 [80.77, 121.70] | −25.12 [−90.15, 32.08] | +62.76 [28.88, 94.49] |

Reversed placement renames assembly source files in disposable implementation
copies, changing archive/code ordering without changing their contents. The
Official `poly_ntt` address moved from `0x3f80` to `0x5f00`, confirming a real
placement perturbation. None of the four Encap intervals excludes zero; the
Keypair regression is consistent and significant, despite unchanged Keypair
arithmetic. The independent Native `−136.28` Encap delta therefore cannot be
promoted as a robust win. Decap direction also changes with placement.

Reproduce the non-timing gates from the experiment directory with
`make generate && make check`. Run the sanitized C harness with
`ASAN_OPTIONS=detect_leaks=0 make BUILD=build_san
CFLAGS='-O1 -g -mavx2 -march=native -fsanitize=address,undefined
-fno-omit-frame-pointer -fwrapv' check`. Benchmark commands and compiler
recipes are recorded in each campaign's `metadata.json`; per-launch raw
observations, saved measure ELF, SUPERCOP `data` and the paired manifest are
committed under `results/`. Timing must be rerun only after checking CPU 1,
governor and turbo state. The original GT worktree and clean production were
not modified.

## Decision and next work

The fused BaseMul/add-m is a valid, measurable local optimization, but this
cumulative Official-opt candidate is **not qualified for clean production**.
It is not a demonstrated all-operation winner, nor a defensible stronger
Official baseline for GT work yet. This first round shows a portable
caller-boundary idea from the GT research; it does **not** establish an upper
bound on non-GT AVX2 performance.

Next, isolate the placement regression before adding more source changes:
compare a smaller fused symbol/code organization or explicit source order while
holding arithmetic fixed, and obtain a new independently confirmed Encap
campaign. Forward's arithmetic/reduction opportunity remains open but needs
its own range and dependency proof before a second ASM prototype is justified.

## Round 2: three-caller attribution and compact-code experiment (2026-09-21)

This round compared five separately named implementations in a **single
diagnostic ELF**: O is imported Official; D duplicates the original BaseMul
without fusing `poly_add`; F is the previous duplicated fused function; S has
one multiplication body and two finalizers (plain and `+m`); W is an
independent same-DAG Forward schedule experiment. O/D/F/S/W are diagnostic
labels, not SUPERCOP implementation names. The two *new optimization ASM*
prototypes are S and W; D is a control copy. The third permitted prototype was
not used.

Deterministic test entry points now live only in `tests/kem_*_diag.c`; no test
wrapper is installed into a SUPERCOP candidate. The disposable installer for
D/F/S refuses overwrite and writes hashes of all installed source files to
`SOURCE-MANIFEST.json`. Re-running `make generate` reproduced identical hashes
for the seven new generated ASM/C files. The S and D research installations
in the disposable SUPERCOP campaign were **not** used for Native timing.

### What changed in the machine objects

S retains the Official quartic multiplication loop and makes a public
entry-state choice immediately before the R² finalizer. The plain entry and
the add-`m` entry execute the same multiply body. The choice is once per call,
not once per coefficient or vector. This preserves the original output
layout, Montgomery scale and formula; the add occurs after the original
finalizer. W only moves the two level-6 twiddle loads ahead of independent
lane routing, leaving all arithmetic and stores in the same order. It is a
dependency/scheduling experiment, **not** a reduction removal.

The linked O3GC image's bounded code regions are below. Sizes include
alignment and are not hot-footprint or cache-miss measurements. The W region
is 16 B smaller than O because of padding/encoding, with the same arithmetic
opcode multiset. Every region has zero stack references, calls and
`vzeroupper`. S uses a `%r10` pointer from the public fourth argument; its
branch does not depend on a secret value.

| Code region | bytes | linked static instruction rows |
|---|---:|---:|
| O BaseMul | 1,339 | 283 |
| D duplicate BaseMul | 1,344 | 284 |
| F duplicate fused BaseMul | 1,376 | 290 |
| S shared body, both entries and finalizers | 1,536 | 325 |
| O Forward | 1,792 | 334 |
| W Forward | 1,776 | 332 |

The last instruction-row difference includes two `cs` alignment prefixes in
O, not removed arithmetic. The complete static opcode and address ledger is
in `results/officialopt-matrix-forward-cutpoint-20260921/linked-audit.json`.
This region-level audit establishes no stack spill in these hand-written ASM
regions; it is not a global register-liveness proof for the surrounding C.

### Caller and range contracts

The three caller cutpoints each restart from matching prepared valid inputs.
Keygen's cutpoints use fixed `f/g` coins and price a *successful* inversion
path; randombytes/retry time is excluded there but included in Native KEM.
All nine preflights observed `retry_f=retry_g=0`, so retry cost remains an
unmeasured part of this attribution. Encap starts with PK bytes and coins;
Decap starts with CT/SK bytes. A cutpoint does not consume the previous
cutpoint's warmed output. Each cumulative series uses one estimator family;
incremental figures are differences of cumulative pooled StQ2, not sums of
independently benchmarked primitives. SHAKE/hash work is retained in the
caller, but is not automatically an AVX2 polynomial optimization opportunity.

The immutable input-domain contract read from the reachable Official caller
is: Keygen `f=1+3·CBD1` (coefficient 0 can be 4), `g=3·CBD1`; Encap
`r=CBD1`, `m=SOTP`; Decap's first inverse follows BaseMulScale, then
`crepmod3` produces a message for the message Forward, and reencryption
forwards fresh CBD1 output. The PK decoder rejects noncanonical coefficients;
the ciphertext decoder and failure/zeroization order remain unchanged. No
new Forward reduction is removed, so W inherits Official's exact raw
representatives and S inherits its BaseMul preconditions. These are **caller
domain contracts**, not a new complete per-lane proof of the Official Forward
or BaseInv. Such a proof remains mandatory before any reduction or scale
prototype. The 10,003 raw Forward tests and 100 KEM vectors do not replace it.

Nine fresh processes on CPU 1 gave the following approximate incremental
pooled-StQ2 costs, in cycles. Fused regions are intentionally left fused:

| Caller | Significant cutpoints |
|---|---|
| Keygen | sample `f` 2,794; Forward `f` 753; BaseInv `f` 1,046; sample `g` 2,540; Forward `g` 744; BaseInv `g` 1,035; products+PK/SK packing 755+960; `hash_f` 10,652 |
| Encap | PK decode 366; prehash+CBD `r` 13,329; Forward `r` 752; serialize `r` 208; `hash_g` 11,963; Forward `m` 723; BaseMul+add 567; ciphertext packing 264 |
| Decap | CT/SK decode 667; BaseMulScale 427; inverse+crepmod3 951; message Forward/sub 843; recovery BaseMul 528; recovered-`r` bytes 222; `hash_g` 11,881; reencryption Forward 901; reencryption pack/compare/clear 673 |

Raw launch observations, three StQ estimates for *each cumulative cutpoint*,
ELF/source hashes, host controls and retry preflights are preserved under
`results/officialopt-cutpoints-serious-20260921/`. These costs locate work;
they are not a subtraction against GT, and their sum must not be used as a
Native performance prediction. In particular, BaseInv uses Official's
existing six-chain batch inversion, so there is no “add batching” candidate.

### Matched pricing and decision

The archived nine-launch O/D/F/S diagnostic did not preserve its exact
pre-W harness source, so it is not the final comparison. A new nine-launch
O/D/F/S/W same-ELF campaign (`results/officialopt-matrix-fiveway-serious-20260921/`)
preserved the exact ELF, committed harness source and all raw observations.
It measured the following O-relative StQ2 deltas. Parentheses are favorable
launches out of nine; negative means faster.

| Region | D | F | S | W |
|---|---:|---:|---:|---:|
| In-place Forward `r` | +1.9 (3/9) | +2.5 (0/9) | +2.2 (2/9) | +5.7 (1/9) |
| BaseMul+add | +4.6 (0/9) | −36.9 (9/9) | −46.2 (9/9) | −0.7 (5/9) |
| Keygen | +4.1 (4/9) | +10.6 (2/9) | +4.3 (2/9) | −7.5 (5/9) |
| Encap | +6.0 (5/9) | −44.2 (8/9) | −18.7 (7/9) | +89.5 (0/9) |
| Decap | −14.8 (8/9) | +64.0 (0/9) | −41.8 (9/9) | −20.4 (9/9) |

O→D is a code-body/call-target perturbation, D→F adds fusion arithmetic,
and F→S changes code organization. These deltas cannot be linearly added
across variants. D and S do not establish a causal proof that code placement
alone caused the old Keygen regression. They do show why an isolated fused
BaseMul win is insufficient: S is consistently faster locally, but Encap is
only 7/9 favorable. Notably, S Decap was `+53.5` and 0/9 favorable in the
archived four-way image, but `−41.8` and 9/9 in this five-way image, despite
unchanged Decap arithmetic. This is strong **image/placement sensitivity**,
not a robust Decap algorithmic gain.

The native in-place CBD1 Forward cutpoint resets identical input banks
**outside** timing. In the nine-launch image W's Forward was `+5.7` cycles
and only 1/9 favorable; full Encap was `+89.5` and 0/9 favorable. The W code
is raw bit-exact, but this specific early-load schedule is rejected. This
does *not* reject broader Official Forward reduction or arithmetic work.

Correctness gates: 10,003 raw BaseMul/add cases; 10,003 raw W Forward cases;
100 deterministic O/D/F/S/W KEM vectors, invalid PK/CT, canaries and input
immutability; ASan+UBSan C wrappers (LeakSanitizer disabled for this host).
No observed Keygen retry means the retry-path differential remains limited.
No candidate met the plan's “complete caller signal → Native” gate, so this
round deliberately did **not** start a new Native or fixed-ELF campaign and
did not produce a new Official-vs-GT-vs-Official-opt Native ranking. The
historical Native table above remains historical evidence only.

The third ASM slot remains open. BaseInv is sizable in Keygen but its current
tree already exposes six parallel product chains; the cutpoint alone does not
identify a safe scale identity, movement removal or critical-path shortening.
Likewise, Decap's ingress/inverse and equality edge have measurable cost but
no verified schedule in this round. Next work must start with a concrete
range/scale identity or a same-DAG dependency and liveness mechanism, then
test one change at a time. Neither source-line count nor `.text` size is a
substitute for full-caller pricing.

## Round 3: BaseInv / Decap ingress / Forward diagnostics

The three follow-up research lines were measured in a new valid-input,
SUPERCOP-derived phase campaign and audited against linked Official code.
No new optimization ASM or Native candidate was introduced. The detailed
machine/caller ledger, limits of the measurements, and next proof gates are in
[the round-3 report](/home/nuc/src/ntru_plus-official-opt/docs/ntruplus768-official-opt-round3.md).
