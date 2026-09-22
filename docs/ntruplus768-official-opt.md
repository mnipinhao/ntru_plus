# NTRU+768 Official AVX2 optimization

Latest stage-5 constant-reuse prototype removes 12 linked constant-vector
loads per inverse, passes raw inverse/Decap differential and sanitizer, but
isolated inverse short timing is only about ±2 cycles and complete-Decap
direction reverses under link-order control. It is **not** a confirmed caller
win; no serious, Native or production gate. See
[stage-5 ASM and pricing](ntruplus768-yang-gauge-proof.md#stage-5-constant-residency-asm-and-short-pricing).

Latest pair32 pricing: inverse improves −10.39 cycles versus factored (3/3),
but remains +8.63 versus Official GS (0/3); complete caller-lazy Decap is
+29.36 versus the GS control (0/3). The extra 392 B did not erase all local
gain, but its isolated cost is unmeasured. No serious/Native/production gate.
See [combined short pricing](ntruplus768-yang-gauge-proof.md#combined-pair32-short-pricing).

Latest: the authorized stacked `yang_pair32` ASM passes range, differential,
Decap, guard-page, sanitizer and linked gates: 222 chains / 32 Barrett,
11-YMM tail, `.text` 2692 B (+392 B). Constants unchanged. No timing or
production claim. See [combined ASM](ntruplus768-yang-gauge-proof.md#combined-two-pair--32-barrett-asm).

Latest model follow-up: a 222-chain two-pair tail schedule passes allocation
(11 YMM); a separate reduction-only model safely omits eight radix-3 S0
Barrett vectors (40→32), with final bound ±2547. Neither has new ASM/timing
evidence. See [schedule/reduction audit](ntruplus768-yang-gauge-proof.md#222-chain-scheduling-and-reduction-audit).

Latest Yang machine gate: factored tail ASM is correct and matches its closed
schedule, but short tests lose to Official inverse by +17.80 cycles (0/3) and
caller-lazy complete Decap by +52.25 (0/3). It also loses to wresident inverse
by +11.58 (0/3). Stop this realization; no serious/Native or clean changes.
See [factored ASM and pricing](ntruplus768-yang-gauge-proof.md#factored-asm-and-short-pricing).

Yang follow-up (2026-09-22): [gauge / inverse-tail proof](ntruplus768-yang-gauge-proof.md)
establishes two conditional tail realizations with 238→222 complete inverse
Montgomery chains. Constant costs increase; full caller range and complete
new schedule lowering remain open. No new ASM or timing in this proof gate.

Follow-up closure: actual canonical-input BaseMulScale bounds cover the
7644 prefix contract, and both new tails now pass complete executable
loop/register/range models (tail peak 10 YMM). See the follow-up section in
the Yang report. Candidate linked ASM and performance remain unverified.

Latest (2026-09-22): [Roadmap first gate: serialize-and-compare](ntruplus768-official-opt-serialize-compare.md).
The namespaced Decap helper passes correctness and shows local/serious gains,
but primary placement confirmation is inconclusive and another setting has
an Encap regression: no qualification or clean promotion. Caller-lazy remains
the research control. BaseInv schedule and GS/Yang proof work remain open.

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

## Round 4: Forward lane × stage × caller-domain range closure

The next proof gate is documented in the [Forward lane/consumer report](/home/nuc/src/ntru_plus-official-opt/docs/ntruplus768-official-forward-lane-range.md), with reproducible scripts and machine-readable per-lane bounds in the experiment. It replays the pinned Official Forward's physical routing at eight cutpoints and connects its lazy terminal output to unchanged BaseInv, BaseMul and serializer code. The Decap `crepmod3` output domain was corrected to `[-2,2]` after exhaustive signed-word checking; assuming `[-1,1]` would have understated the Decap Forward input.

All modeled signed-i16 pre-operations and the listed downstream consumer envelopes pass. The proof therefore selects one **research prototype**, a namespaced caller-bounded Official Forward that omits only the 48 terminal Barrett vectors while leaving the general `poly_ntt` intact. It has **not** been implemented or timed. Thus no KEM performance or promotion conclusion changes in this round.

## Round 5: caller-bounded lazy Forward ASM and pricing

The selected prototype is now a complete namespaced ASM/KEM research candidate,
`avx2-officialopt-caller-lazy-exp003`. Its generator asserts the pinned
Official `ntt.s` hash, retains every top-split/radix/route/twiddle instruction
in the same order, removes the single terminal `#reduce2` block and its
constant load, and gives the function independent 32-byte-aligned labels.
The general-input `poly_ntt` is unchanged; the candidate KEM's six call sites
use the caller-bounded entry. The source change removes 48 each of
`vpmulhrsw`, `vpmullw`, and `vpsubw` dynamically per Forward. The linked
candidate symbol is 1,633 B, with 304 disassembly rows, zero stack references,
calls, `vzeroupper`, or remaining terminal Barrett vectors. Its five branches
are the unchanged public loop bounds. The exact linked audit is
[`officialopt-forward-caller-lazy-linked-20260921.json`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-caller-lazy-linked-20260921.json).

Correctness passed 40,012 caller-domain Forward residue/canary cases and 100
deterministic KEM byte-exact vectors for PK, SK, CT and shared secret. Invalid
PK rejection/zeroization and invalid CT output matched Official. ASan/UBSan
passed the C harness with LeakSanitizer disabled for this host's ptrace
restriction. No Keygen inversion retry occurred in those 100 vectors; that
path remains a coverage limitation, although the unchanged retry code and
the preceding BaseInv zero-representative proof constrain the risk. No
general-input safety claim is made for the new entry.

The same-ELF O3GC SUPERCOP-derived campaign used nine fresh processes on
CPU 1 with `performance` governor and turbo disabled. Pooled StQ2 differences
below are candidate minus Official, in cycles; all five regions were faster
in 9/9 launch medians:

| Matched region | Delta |
|---|---:|
| `r` Forward | −105.36 |
| Keygen `f` Forward | −106.63 |
| Full Keygen | −202.78 |
| Full Encap | −149.75 |
| Full Decap | −185.04 |

This is a complete-caller diagnostic, not Native KEM. The raw observations
and ELF/source hashes are in
[`officialopt-forward-caller-lazy-serious-20260921`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-forward-caller-lazy-serious-20260921/summary.json).

A fresh disposable SUPERCOP 20260831 campaign then used unmodified native
`crypto_kem/measure.c` and normal compiler selection (both implementations
selected GCC 15.2.0 O2). Nine independently pooled launches per
implementation gave:

| Native StQ2 cycles | Official | Caller-lazy | Delta |
|---|---:|---:|---:|
| Keypair | 21,609.63 | 21,387.58 | −222.05 |
| Encap | 28,178.59 | 28,009.38 | −169.21 |
| Decap | 19,454.83 | 19,261.25 | −193.58 |

These independently pooled Native numbers are not paired causal estimates.
For placement control, four O3GC fixed ELFs were built in the disposable
campaign. Each of normal/reversed placement × ASLR on/off received 16
ABBA/BAAB blocks, 64 fresh launches. The paired mean deltas were:

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| Normal, ASLR off | −155.74 | −99.84 | −167.92 |
| Normal, ASLR on | −155.30 | −119.22 | −197.77 |
| Reversed, ASLR off | −220.46 | −110.85 | −197.72 |
| Reversed, ASLR on | −188.57 | −105.42 | −223.73 |

All 12 block-bootstrap 95% intervals lie below zero. Encap favorable
blocks were 16/16, 12/16, 16/16, and 14/16 respectively; the full intervals,
ELF hashes, symbol placement and raw observations are preserved in the
[`fixed-ELF paired summary`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/fixed-lazy-paired-20260921/summary.json).

This is a robust **research** win for this machine and these caller domains,
not an automatic clean-production promotion. A separate qualification pass
should explicitly exercise Keygen retry, review the namespaced entry's
consumer contract in a clean implementation, and repeat Native confirmation
from that clean export. The candidate has not been merged with the earlier
BaseMul-add fusion; gains from different campaigns must not be added.

## Round 6: caller-lazy qualification export and independent Native rebase

The missing retry-path coverage is now explicit. A test-only linker wrapper
replaces the second Keygen CBD1 expansion with zero bytes, so `g=0` genuinely
fails the unchanged BaseInv and triggers one retry. Official and caller-lazy
both make exactly three random draws, then produce byte-identical PK/SK. A
subsequent Encap/Decap with those keys is also byte-identical, including the
shared secret. This is controlled *g*-retry coverage, not evidence that an
*f*-retry occurred. The existing 100 deterministic vectors and invalid-PK/CT
checks still pass; ASan/UBSan pass with host-restricted LeakSanitizer disabled.
The injection exists only in the test binary, never in the exported KEM.

The experiment now has a standalone flat qualification export under
`qualification/avx2-officialopt-caller-lazy-qual001/` and a sibling JSON
manifest. Its 26 installed source-file hashes are **identical** to the prior
exp003 Native research candidate. The export consists only of the pinned
Official source tree with `kem.c` and the namespaced Forward ASM overlay; it
contains no diagnostic KEM wrapper or test harness. The exporter refuses to
overwrite, verifies the pinned Official tree, and records every source hash.
The installer verifies the export hash and only copies it into a newly created
disposable SUPERCOP campaign. Neither existing `clean/`, the imported upstream,
nor pristine SUPERCOP was changed.

The new campaign uses unmodified SUPERCOP `crypto_kem/measure.c` and normal
compiler selection. Both implementations selected GCC 15.2.0 O2; CPU 1 met
the performance-governor/turbo-disabled policy. Nine fresh launches per
implementation (864 raw observations per operation) gave independently pooled
StQ2 results:

| Native cycles | Official | Qualification export | Candidate − Official |
|---|---:|---:|---:|
| Keypair | 21,582.01 | 21,407.83 | −174.19 |
| Encap | 28,204.63 | 27,997.69 | −206.95 |
| Decap | 19,497.49 | 19,278.40 | −219.09 |

Raw `data`, `run.out`, compiler identity, host policy and ELF hashes are in
`results/native-lazy-qual-{official,candidate}-20260921/`. These are new
independent Native observations, not a paired estimate; the prior four-setting
fixed-ELF controls remain separate evidence for the **source-identical**
exp003 candidate. No clean-production change or Official/GT combined-candidate
claim follows automatically. The remaining explicit coverage gap is an
actual *f*-inversion retry. Before promotion, a final package review should
also rerun fixed-ELF placement controls on the exact release packaging if its
source layout or link order changes.

## Round 7: inverse radix-2 CT research prototype (2026-09-21)

The Yang NTT paper motivated testing CT on Official's inverse, but its NEON
instruction/range conclusions are not AVX2 performance evidence. Official's
five radix-2 inverse stages (levels 6–2) use GS butterflies
`(a+b, z(a-b))`. This experiment replaces only those stages with twisted CT
butterflies `(A+tB, A-tB)`, while preserving Official's physical routing,
radix-3 stage, level-0 tail, and external scale. For each physical lane the
generator tracks `actual = gauge × stored (mod 3457)`, sets
`t = gauge_b/gauge_a`, and propagates output gauges
`(gauge_a, z×gauge_a)`. It then pays an explicit Montgomery normalization of
all 48 YMM vectors before the unchanged radix-3 stage. This is **not** a
fully gauge-propagated all-CT inverse, and no speed claim follows from the
word “CT” alone.

The namespaced candidate is
[`ntruplus768_officialopt_invntt_ct.s`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/asm/ntruplus768_officialopt_invntt_ct.s).
Pinned-source SHA checks, gauge derivation, range replay, and linked audit
are reproducible with `tools/{generate_inverse_ct,probe_inverse_ct_gauge,prove_inverse_ct_range,audit_inverse_ct}.py`.
The test-only `src/kem_ct.c` changes precisely the Decap inverse call;
Keygen and Encap remain Official. No clean source, frozen package, imported
upstream, or pristine SUPERCOP tree changed.

| Dynamic vector operations per inverse | Official GS | CT prototype |
|---|---:|---:|
| Standalone Barrett reductions, including unchanged radix-3 | 64 | 40 |
| Radix-2 twiddle Montgomery chains | 120 | 78 |
| Gauge-restoration Montgomery chains | 0 | 48 |
| Radix-2 plus gauge Montgomery chains | 120 | 126 |

The CT candidate therefore removes 24 standalone Barrett vectors but adds
6 net Montgomery chains and 10,752 bytes of constant tables. Its linked
function occupies 2,245 bytes, is 32-byte aligned, and contains no stack
reference, call, or `vzeroupper`; these facts do **not** establish cycle
improvement. The new constants and changed dependency pattern could outweigh
the reductions. The 16 radix-3 Barrett vectors and all Montgomery-internal
`#reduce` operations remain.

For the Decap caller, valid CT/SK parsing yields canonical `[0,3456]`
BaseMulScale inputs. A conservative scalar-product bound of 1,911 and at
most four product terms gives the proposed `±7,644` inverse-input contract.
The repaired CT schedule uses 12 vector Barrett reductions before stage 4
and 12 before stage 3; a uniform symmetric interval replay bounds stage
outputs by 15,288, 30,576, 32,476, 21,198, and 23,442, respectively.
After gauge normalization, the bound is 2,336. The unchanged radix-3/level-0
pre-operation upper bounds are 7,008 and 4,008. These are conservative
signed-i16 checks, not an exhaustive bit-vector proof of the complete
BaseMulScale machine object. The full caller-bound proof and independent
machine-level timing remain open.

`make check-inverse-ct` passes 5,003 direct inverse cases (including
impulses and random values within `±7,644`), 1,003 canonical-input
BaseMulScale→inverse/crepmod3 cases, and 100 deterministic KEM Decap
comparisons each for valid ciphertext, tampered ciphertext, and invalid SK.
Residues and final Decap bytes agree with Official. This is a **research
prototype**, not a Native SUPERCOP candidate or clean-production change.
The direct inverse C harness also passed ASan/UBSan with host-restricted
LeakSanitizer disabled; ASan cannot prove the assembly's memory accesses.

## Round 8: CT inverse same-ELF short pricing

This gate priced the Round-7 realization without changing its ASM. The
SUPERCOP-derived diagnostic links Official and namespaced CT into **one
ELF**, uses SUPERCOP `cpucycles()` and the common O3GC recipe, and runs on
P-core CPU 1 with the performance governor and turbo disabled. Normal
placement and ASLR-on were fixed before measurement. Three fresh processes
each produced eight balanced Official/CT blocks, 64 observations per block.
For the inverse cutpoints, each operation begins with a separately reset
BaseMulScale output from canonical inputs; reset is outside timing. Complete
Decap starts from the same deterministic valid CT/SK banks. Untimed preflight
checks inverse residues, crepmod3 bytes and final Decap bytes.

| Same-ELF StQ2 cycles | Official | CT | CT − Official | Favorable launches |
|---|---:|---:|---:|---:|
| Inverse only | 969.66 | 989.20 | +19.53 | 0/3 |
| Inverse + crepmod3 | 1,157.00 | 1,180.79 | +23.79 | 0/3 |
| Complete Decap | 19,394.67 | 19,445.89 | +51.22 | 0/3 |

An independent second three-process campaign, with the exact ELF saved,
confirmed the direction: CT − Official was +18.39 inverse, +22.28
inverse+crepmod3 and +65.93 complete Decap cycles, again 0/3 favorable
launches in every region. Its raw samples, ELF, compiler identity and SMT
siblings are in
[`officialopt-inverse-ct-short-confirm-20260921`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-inverse-ct-short-confirm-20260921/summary.json).

Raw observations, launch deltas, source/ELF hashes, cpucycles identity and
host controls are preserved in
[`officialopt-inverse-ct-short-20260921`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-inverse-ct-short-20260921/summary.json).
The three inverse-only launch deltas are +18.38, +20.58 and +19.45 cycles;
complete Decap deltas are +51.12, +40.82 and +60.62. These observations
do not isolate instruction-cache or code-placement causality, and the caller
delta need not equal the isolated inverse delta. The structural audit shows
the candidate trades 24 Barrett vectors for six net Montgomery chains and
10,752 B of constants; that trade is a plausible explanation, not a measured
per-instruction cost attribution.

**Decision:** stop this partial-CT realization. It failed the short
inverse and full-caller gates, so no nine-launch serious campaign, disposable
Native candidate, or clean promotion follows. The result does not rule out
a different CT design that propagates the gauge through radix-3/level-0 and
avoids the 48-vector normalization, but that would be a new mathematical,
range and schedule candidate requiring its own proof and pricing. It must not
inherit a claimed cycle benefit from this failed prototype. The existing
caller-lazy Forward qualification export remains separate and unchanged.

## Round 9: CT gauge consumed by radix-3 (research candidate)

The next namespaced candidate removes the standalone 48-vector gauge
restoration at the radix-2/radix-3 boundary. For each radix-3 triple, let
`actual (X,Y,Z) = (gx X',gy Y',gz Z')`. It computes
`Yhat = Mont(Y',gy/gx)` and `Zhat = Mont(Z',gz/gx)`; the ordinary radix-3
butterfly then works in the common `gx` gauge. The output-1/2 constants are
changed to `gx·alpha^-1` and `gx·alpha^-2`, so those existing Montgomery
multiplications also remove the gauge. Output zero replaces its old Barrett
with `Mont(X'+Yhat+Zhat,gx)`. Level zero and the external result remain
unchanged. This is consumer-side twiddle fusion, but not full CT-gauge
propagation through level zero.

The linked object has a 2,053-byte, 32-byte-aligned inverse symbol, no stack
reference/call/`vzeroupper`, and a conservative maximum signed-i16
pre-operation bound of 27,893 under the conditional `±7,644` inverse input
contract. It passes 5,003 direct inverse cases, 1,003 BaseMulScale cases,
100 valid Decap vectors, 100 tampered ciphertext cases and 100 invalid-SK
cases; the direct C harness also passes ASan/UBSan. The generator reproduces
the same ASM SHA-256. These checks do not constitute a complete machine-level
constant-time proof.

| Dynamic vector operation | Old CT | CT→radix-3 |
|---|---:|---:|
| Radix-2 CT Montgomery | 78 | 78 |
| Boundary-related Montgomery | 48 restoration | 32 relative inputs + 16 output zero |
| Standalone Barrett | 40 | 24 |
| Added constant tables | 10,752 B | 12,800 B |

Thus this candidate saves the 16 radix-3 Barrett vectors but does not reduce
the 126 total CT-prefix-plus-gauge Montgomery chains. It spends an additional
2,048 B of tables and changes dependencies. In particular, `gx`, `gy`, and
`gz` are generally unequal lane by lane, so simply folding one common
constant into both alpha multiplications cannot remove the two relative-input
operations. The source is in
[`asm/ntruplus768_officialopt_invntt_ct_r3.s`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/asm/ntruplus768_officialopt_invntt_ct_r3.s),
with generator, range proof and linked audit alongside the existing inverse
research tools.

Short SUPERCOP-derived same-ELF diagnostics on CPU 1, performance governor,
turbo disabled, normal placement/ASLR-on, three fresh launches:

| StQ2 delta | CT→radix-3 − Official | CT→radix-3 − old CT |
|---|---:|---:|
| Inverse only | +29.19 cycles (0/3 favorable) | +9.74 (0/3) |
| Inverse + crepmod3 | +32.06 (0/3) | +8.44 (0/3) |
| Complete Decap | −0.73 (2/3; mixed) | +89.86 (0/3) |

The direct CT-vs-CT→radix-3 comparison is the appropriate incremental test;
its complete-Decap difference may also include placement effects and cannot
be assigned to one instruction class. Raw observations, source/ELF hashes,
host controls and saved ELFs are in
[`officialopt-inverse-ct-r3-vs-ct-short-20260921`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-inverse-ct-r3-vs-ct-short-20260921/summary.json)
and the corresponding Official comparison directory. Decision: this
realization is not ready for serious or Native benchmark, and remains a
research result. A further candidate would have to co-design level zero and
its final scale constants, actually reduce the gauge-related Montgomery
count, and prove the resulting range before ASM pricing; merely moving the
same 48 chains into another stage is insufficient.

## Round 10: level-0 shear and final-scale co-design

The next gate corrected an important algebraic assumption before timing.
Official level zero does **not** output the ordinary pair
`(U+V, phi(U−V))`; its actual map is
`(U+V−phi(U−V), phi(U−V))`, followed by separate upper/lower finalizers.
Therefore a direct CT level zero with only gauge-adjusted final constants
was incorrect. The differential test caught it before benchmarking; that
failed generated form is not retained as a candidate.

The working design chooses a common gauge for the two radix-3 triples that
level zero will pair. For the first triple, its X gauge is retained and Y/Z
need two relative Montgomery multiplications. For the corresponding triple
in the other half, X/Y/Z each normalize to that same gauge, costing three.
That is `8 × (2+3) = 40` boundary-related chains instead of the earlier 48.
Radix-3 retains its existing omega/alpha arithmetic and Barrett output-zero
reduction. Level zero retains the exact Official shear and phi multiplication;
its 48 existing finalizer chains use constants multiplied by the propagated
gauge. Thus this candidate **really deletes eight Montgomery chains** rather
than relocating them, while keeping Official output scale and physical ABI.

Two namespaced machine realizations were tested. `full` traverses adjacent
level-0 vector pairs with a per-pair finalizer table. `cohort` traverses the
three coefficient vectors with the same gauge together and reuses finalizer
constants across them. The latter removes 64 dynamic finalizer-constant
vector loads and 2,048 B of repeated table entries relative to `full`, but
changes address order. Neither alters arithmetic or external ownership.

| Structural metric | old CT | full | cohort |
|---|---:|---:|---:|
| Radix-2 CT + additional gauge Montgomery | 126 | 118 | 118 |
| Standalone Barrett vectors | 40 | 40 | 40 |
| Added constant tables | 10,752 B | 13,312 B | 11,264 B |
| Linked inverse symbol `.text` | 2,245 B | 2,408 B | 2,354 B |

Both machine objects are 32-byte aligned and have no stack reference, call
or `vzeroupper`. A conservative physical-vector range replay under the
conditional `±7,644` inverse-input envelope gives maximum signed-i16
pre-operation magnitude 27,900. Each passed 5,003 direct inverse cases,
1,003 BaseMulScale cases, 100 valid Decap vectors, 100 tampered-ciphertext
cases, 100 invalid-SK cases, and the direct C harness under ASan/UBSan.
Generator reruns reproduced the same ASM hashes. Linked evidence is in
[`full audit`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-inverse-ct-full-linked-20260921.json)
and
[`cohort audit`](/home/nuc/src/ntru_plus-official-opt/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-inverse-ct-cohort-linked-20260921.json).

Short SUPERCOP-derived same-ELF StQ2 cycles used CPU 1, performance governor,
turbo disabled, normal placement/ASLR-on, three fresh launches and matched
reset outside timing. Candidate minus comparator:

| Region | full − Official | cohort − Official | cohort − old CT |
|---|---:|---:|---:|
| Inverse only | +44.43 (0/3 favorable) | +26.99 (0/3) | +18.05 (0/3) |
| Inverse + crepmod3 | +49.95 (0/3) | +33.40 (0/3) | +17.20 (0/3) |
| Complete Decap | +78.61 (0/3) | +50.66 (1/3) | +21.47 (0/3) |

The `full` image's old-CT comparison had a different complete-Decap
placement effect despite its slower isolated inverse; the cohort comparison
is the narrower machine arbitration. Raw observations, exact ELFs, source
hashes and host policy are retained under the respective
`results/officialopt-inverse-ct-{full,cohort}*-20260921/` campaigns. These
are diagnostics, not Native SUPERCOP results.

**Decision:** the chain reduction is algebraically and mechanically real, but
neither realization passes the short inverse/caller gate. No serious or Native
campaign and no clean promotion. The remaining cost is not proven to be any
single instruction class. The extra constant traffic, doubled radix-3 loop
body and new dependency pattern are concrete candidate mechanisms; perf or a
separate same-arithmetic schedule control would be needed to assign cause.
The result narrows the next CT question: avoiding eight chains alone is not
enough on this AVX2 machine. Do not infer that CT is globally unsuitable, but
do not keep changing placement to seek a favorable isolated result.

## Round 11: cohort constant-residency and normalization-placement controls

Two namespaced controls now isolate the two proposed mechanisms without
changing the paired-gauge arithmetic or final ABI. `wresident` keeps radix-3
`w` and its QINV companion in two YMM registers; the same 40 relative-gauge
chains use memory-form constants, and one alpha temporary is reassigned to a
dead register. Its constant-load ledger is 80 relative memory operands plus
two hoisted `w` loads, instead of 80 explicit relative loads plus 32 repeated
`w` loads. The predicted retired-load reduction is 30 per inverse; the 80
relative loads have **not** disappeared. `earlynorm` keeps the cohort's
constant strategy but moves exactly the same 40 chains from the radix-3
entrance to the level-2 egress, processing the eight live output vectors of
each physical group. The first group retains the target gauge; the other
five groups use the same per-vector constants in reordered table form. Its
public group-zero branch and address cost are included.

The controls are generated from the SHA-pinned cohort source by
`tools/generate_inverse_ct_controls.py`; rerunning it reproduced both ASM
hashes. Both passed 5,003 raw bit-exact comparisons against cohort, separate
Official-residue/crepmod3 differentials, 100 valid Decap vectors, 100
tampered ciphertext cases, 100 invalid secret-key cases, and C-harness
ASan/UBSan. The conditional `±7,644` input range replay still gives maximum
signed-i16 pre-operation magnitude 27,900: moving a normalization earlier
does not insert a different arithmetic operation between it and its former
location. Linked symbols are 32-byte aligned, with no stack reference, call,
or `vzeroupper`. Both retain 118 radix-2-plus-gauge Montgomery chains,
40 standalone Barrett vectors, and the same 11,264 B added constant tables.

| Linked inverse symbol | cohort | `wresident` | `earlynorm` |
|---|---:|---:|---:|
| `.text` bytes | 2,354 | 2,290 | 2,450 |
| Static instruction rows | 498 | 484 | 523 |

Nine fresh-process, same-ELF, SUPERCOP-derived StQ2 comparisons on CPU 1
(`performance`, turbo disabled, normal placement/ASLR on) gave:

| Candidate minus comparator | Inverse | Inverse+crepmod3 | Full Decap |
|---|---:|---:|---:|
| `wresident` − cohort | −8.50 (9/9 favorable) | −7.55 (9/9) | −5.23 (5/9) |
| `earlynorm` − cohort | +7.94 (0/9) | +7.75 (0/9) | −43.04 (9/9) |
| `wresident` − Official | +16.06 (0/9) | +19.34 (0/9) | +3.72 (1/9) |
| `earlynorm` − Official | +31.92 (0/9) | +36.40 (0/9) | +37.64 (0/9) |

The inverse-only cutpoint is the appropriate mechanism test. `wresident`
recovers about eight cycles, while moving normalization earlier **with the
same chain count** worsens it by about eight cycles. Thus the hypothesized
late-normalization critical path is not established as the principal cost in
this realization; the proposed earlier placement adds a public branch and
changes scheduling, so it is not a pure latency-only test. Full-Decap
directions differ across separately linked images (notably `earlynorm` beats
cohort but loses to Official), so they cannot be assigned to the inverse
instruction change without placement controls.

An isolated `perf stat` diagnostic ran one million inverse calls per process
with identical in-loop reset in the same ELF. Relative to cohort, `wresident`
retired approximately 29 fewer loads and 105 fewer instructions per call;
`earlynorm` changed either by less than one per call. The first result agrees
with the 30-load source ledger and confirms a real constant-load mechanism.
This process-wide PMU test is not a cycle headline; it includes reset and
startup, and small store differences are below useful precision. The machine
counts are in `results/officialopt-inverse-ct-controls-pmu-20260921.json`;
linked audits and raw paired launches are in the correspondingly named
`results/officialopt-inverse-ct-{wresident,earlynorm}*` paths.

**Decision:** neither control beats Official inverse, so neither enters Native
SUPERCOP or clean production. Keep `wresident` as the better CT research
control. This experiment localizes a meaningful part of the cohort regression
to avoidable `w` reloads, but does not establish that the remaining deficit
is solely register pressure or solely CT mathematics.
