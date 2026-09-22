# NTRU+768 GT vector mapping / Encap co-design

Date: 2026-09-22. Branch: `avx2-gt-ntt`.

Follow-up: [逐函式研究與 eager BaseMul](ntruplus768-encap-function-research.md)
keeps the materialized M ABI and implements one function-internal same-DAG
prototype. Its three-process complete polynomial-island delta is −47.57 cycles.
This supersedes the priority recommendation below, not its historical model
evidence. W aggregate-λ remains unpriced; no Native or clean promotion occurred.

## Result and evidence boundary

This checkpoint performed **source inspection, executable word/ownership models,
range replay and source-level register allocation audits only**. No new optimized
ASM, benchmark, Native candidate or clean change was made. The prefixed-buffer
hash experiment is parked; every path here retains the original hash staging.

The main result is not a new GT decomposition winner:

1. Hwang's whole-vector GT mapping is real, but applies to a particular
   `3 × 2` transformation with an untouched inner `I16`. Its subsequent
   transpose is explicit, not free.
2. Current GT already uses interleaved degree planes for arithmetic, integrated
   twist/frontend work, direct terminal deposition and private caller layouts.
   The missing opportunity cannot simply be described as “use Hwang layout”.
3. Three stage-order families have exact modular models. **No new C2 machine
   schedule is selected**: restoring the row gauges makes the reordered maps
   correct, but does not establish a new eliminated conversion/pass relative
   to the existing N32-first research.
4. C1 W aggregated-λ remains the one bounded next-ASM proposal. Its full ledger
   is less flattering than a codec-only ledger: routing is **+48**, not −480,
   versus current M. It trades fewer data accesses against more constant
   operands, arithmetic and loop/control work. It is not a predicted winner.

The executable report is `generated/tile4_gt_vector_mapping.json` in
`NTRU+768/experiments/avx2_gt32_tile4_official_001`. `C2: null` means unknown,
not zero-cost and not a proof that GT32-first is impossible.

## 1. Sources and mathematical portability

The [public artifact](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/tree/3eb881fb4aa83a9c424a121acefb1b8d35cf6f93)
is pinned to `3eb881fb4aa83a9c424a121acefb1b8d35cf6f93`. Exact archive, inspected
source and paper hashes are in `ref/hwang-vector-mapping-sources.json`.

The inspected [final paper](https://eprint.iacr.org/2023/604.pdf), sections 4.1.2,
4.2.1 and the comparison discussion, describes a degree-1536 computation ring
over q=4591, truncated Rader, then `(GT3×2 ⊗ I16)`, twisting, interleaving and
small cyclic/negacyclic products. The 768→192 size-8 product comparison concerns
that embedding and the previous NTRU Prime implementation; it is **not** a
fourfold saving available for NTRU+'s 192 terminal quartics.

The supplied early-report mirror returned HTTP 401. Its contents were not
independently re-read in this checkpoint. Historical comparisons below rely
on the final paper's own discussion, not an asserted comparison of two downloaded
paper versions. The final artifact is the source of all instruction-model claims.

NTRU+768 instead computes in q=3457, `x^768−x^384+1`. This checkpoint keeps
all 192 factors `x^4−λ`, their external order, and the wire format. The model
checks that every λ satisfies `λ^192−λ^96+1=0` and that all 192 are distinct.
Changing the computation ring or terminal factors was not authorized here.

### Hwang: one 96-coefficient GT block

Source: `avx2/avx2/radix_3x2.S`, `__asm_3x2_pre` / `post`.

```text
Mathematics: GT3×2 acts across six degree-16 blocks; inner coefficient t stays t.
Input ownership: A_i = [a_(16i+0), ..., a_(16i+7) | a_(16i+8), ..., a_(16i+15)].
Loads: ymm0..5 ← A0, A4, A2, A3, A1, A5 (offsets 0,128,64,96,32,160 bytes).
Pre twist: six table-weight Montgomery products, before the butterflies.
Radix-2: S_i=a_i+a_(i+3), D_i=a_i−a_(i+3), i=0,1,2.
Radix-3 on each S/D triple:
  y0=x0+x1+x2
  y1=x0−x2+ω(x1−x2)
  y2=x0−x1−ω(x1−x2)
Stores: same six block slots, with no lane permutation in this routine.
Next consumer: twist + 16×16 transpose, then homogeneous terminal arithmetic.
```

The pre block has six twist chains and two radix-3 chains; the post block moves
the six table products after the two radix-3 chains. Both still execute eight
chains per block, sixteen blocks. This is not multiplication absorption merely
because twist and transform share one routine. The source expands Montgomery
into `vpmullw`, `vpmulhw`, low-word QINV multiplication, high-word q product and
`vpsubw`. The model uses the actual constants and checks all 1,536 basis inputs
for pre and all 1,536 for post. This is not a full Hwang input-range proof.

### Hwang: transpose really changes what a vector means

Source: `_twist_transpose_pre` in `__avx2.c`.

Before: 16 vectors, each a polynomial's 16 coefficients. Selected source rows
are 0,2,...,30, separating the relevant cyclic/negacyclic group by addresses.
After: output vector j holds **degree j from 16 different polynomials**:

```text
before A0: [p0.c0 ... p0.c7 | p0.c8 ... p0.c15]
after  B0: [p0.c0 ... p7.c0 | p8.c0 ... p15.c0]
after  B1: [p0.c1 ... p7.c1 | p8.c1 ... p15.c1]
```

Replaying the actual unpack and permute immediates gives natural output degree
order 0..15. Per 256-coefficient block it executes 16 twist multiplications,
48 unpack operations and 16 `vperm2i128`, with 16 data loads/stores. Twisting
and transposing share the pass; neither the 16 multiplications nor the 64
routes disappears. The C intrinsic variable count is not a linked YMM allocation
proof. The source deliberately materializes buffers between these routines.

The following cyclic/negacyclic FFT16 paths consume same-degree, different-ring
lanes and use CT/Bruun plus Karatsuba. **That interleaving principle is already
present in our M BaseMul.** The polynomial modulus, constants, small-ring
formula and expansion costs are different; their cycle results do not transfer.

## 2. Current GT: complete frontend → NTT32 → terminal example

Only reachable clean Encap symbols are included. Macro expansion respects
source definition order and `.purgem`/redefinitions; counting the last macro
definition in `pack.s` gives the wrong executable path.

### Frontend / GT coordinate formation

```text
Input: six coefficient YMMs from byte offsets 0,256,...,1280 + packet displacement.
Top split: l−722h and l+723h for independent ternary input coefficients.
Instructions: raw vpmullw plus add/sub; GT_BLEND3; twist Montgomery; DFT3.
Output: one YMM into each of six tiles per iteration, eight iterations.
Meaning: n=(64*n3+33*n32) mod 96; branch weight s^(−n), s=2 or 22.
Scale: e=0; the fixed multiplication table stores weight×R.
Next: NTT32 over each (branch,k3), preserving its current raw representative.
```

For packet 0 and n3=0, the four qword owners are n=`[0,33,66,3]`:

```text
low half:  n0.c0 n0.c1 n0.c2 n0.c3 | n33.c0 n33.c1 n33.c2 n33.c3
high half: n66.c0 n66.c1 n66.c2 n66.c3 | n3.c0 n3.c1 n3.c2 n3.c3
```

These are qwords from three different current source YMMs. **Renaming whole
32-byte loads cannot produce this vector.** `GT_BLEND3` uses six blends per
branch, 96 per Forward. This is a counterexample to one address-only shortcut,
not a global shuffle lower bound: smaller loads or a different intermediate
layout remain possible, with their instruction/address cost included.

### NTT32 tile

Eight YMMs represent 32 q positions × four degrees. D16 pairs vectors
`(0,4),(1,5),(2,6),(3,7)` using raw add/sub. D8 and D4 multiply high arms by
fixed roots using Montgomery companions. D2 moves 128-bit halves and D1 pairs
qwords; the terminal then materializes four M degree planes per half-tile.

```text
register input: ymm0..7, q and terminal mask
operations: D16 → D8 → D4 → half-pair D2 → qword-pair D1 → terminal transpose
register output: same residues, bit-reversed physical q, degree planes
bound: hash-verified refined proof ends at |x|≤15592 for independent ternary input
consumer: lane-wise quartic BaseMul; Q24 codec must recover wire quartic grouping
```

The report stores all six stage states for a representative tile, all 768
semantic owners, and all 48 direct-W deposits with real source registers,
`vpermq` immediates and `vpblendd` masks. W still needs two source D1 vectors per
packet. A semantic AoS vector is not assumed to be a raw D1 register.

Current M plane lanes correspond to physical q
`[0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]`. W instead stores four consecutive
wire quartics, four degrees each; all sixteen lanes remain useful.

## 3. C2 stage-order screen: exact algebra, no new allocation claim

The generator checks DFT3 before all radix-2 stages (cut0), after stage3,
after stage4 and after all five stages. It reuses the existing N32-first oracle.

With current residual weights d_i, a CT butterfly uses
`w' = w*d_high/d_low`, then both outputs inherit `d_low`. Before DFT3, the
screen explicitly multiplies each row/coordinate by its remaining residual.
Only then can the unchanged DFT3 and common remaining NTT32 stages be used.
The mod-96 carry in the twist is retained; naïvely factoring
`s^(−((64i+33j) mod96))` into two independent powers is not assumed valid.

| Cut | 96 basis × two branches | Conservative final bounds, branches 0/1 | Allocation/new mechanism |
|---|---|---|---|
| 0 | pass | 18335 / 18348 | current control, not a new candidate |
| 3 | pass | 9039 / 9101 | not constructed / not established |
| 4 | pass | 7194 / 7279 | not constructed / not established |
| 5 | pass | 5360 / 5467 | existing N32-first family, not a new mechanism |

These bounds belong to the explicitly normalized models. Cut0's conservative
bound does not replace the tighter current exact-marginal 15592 proof. Smaller
bounds at later cuts are **not a free win**: every restoration multiply is
included, including identity multiplications in this screen. All word operations
and a conservative canonical-h MulAdd/serializer consumer envelope are safe.
No hidden repair reduction was inserted.

No C2 is selected because the tested address-only shortcut fails ownership,
while the tested reordered transforms have not removed a pass or established
a new register schedule beyond historical variants. This is a bounded outcome,
not exhaustive search and not rejection of GT32-first/interleaved GT in general.

## 4. C1 complete caller: arithmetic and dataflow ledger

W retains early PK validation and five aligned 1536-byte scratch arrays.
`r(W)` survives hash_g, SOTP and m Forward unchanged. `c` is frontend scratch
until m terminal finishes, then becomes MulAdd output. No sixth polynomial array
or validation-only pass is introduced. Keygen P/J1 and Decap inverse remain
unchanged; using W there would require separate contracts, not a free port.

For each quartic output degree j:

```text
T_i[j] = Mont(h_i, r_((j−i) mod4))         e=−1
S_j    = sum_i T_i[j]
U_j    = sum_(i>j) T_i[j]
C_j    = S_j + Mont(U_j, (λ−1)R)          e=−1
out_j  = Mont(C_j, R²) + m_j              e=0
```

Register flow: load h/r to ymm0/1; form T3,T2,T1 with half-local shuffle masks;
keep cyclic sum in ymm4 and wrap sum in ymm5 using blend masks 0x77/0x33/0x11;
form the single correction; compute T0; combine, finalize and add m. q/zero
remain in ymm15/14 across the packet loop. The physical model peaks at 9 live
YMM, has no stack/spill and does not form the four complete M planes.

Range: product ≤2551, wrap sum ≤7653, cyclic sum ≤10204, correction ≤1930,
corrected value ≤12134, finalizer ≤1889, final add ≤17481. The report includes
every lane's interval for all 48 actual constant packets. Low-word wrap is
intentional; all signed add/sub preconditions are checked before truncation.

### Whole Encap accounting, not codec-only accounting

| Item | Current M | Aggregated W | Difference |
|---|---:|---:|---:|
| MulAdd Montgomery chains | 276 | 288 | +12 |
| Terminal routing, two producers | 288 | 288 | 0 |
| Decode routing | 288 | 192 | −96 |
| Two complete pack routings | 576 | 192 | −384 |
| MulAdd routing | 0 | 528 | +528 |
| Whole polynomial path routing, including shared Forward | 1632 | 1680 | **+48** |
| Data-load instructions | 613 | 529 | −84 |
| Data-store instructions | 566 | 482 | −84 |
| Constant-memory operands | 1157 | 1707 | **+550** |
| Add/sub instructions | 1828 | 1888 | +60 |
| Serializer Barrett vectors | 96 | 96 | 0 |

Source expansion includes all selected loop trips. Data access counts include
XMM and tail accesses: they are instruction counts, not uniformly 32-byte
traffic. Constant operands include memory forms, not assumed cache misses or
one load-uop each. No measured cycles can be inferred from this table.

Memory savings decompose into **48 loads/stores from separate add-m fusion**
and **36 loads/stores from avoiding M's late R² finalizer materialization**.
Neither removes the retained producer boundary. The latter is also potentially
an Official/M scheduling opportunity; portability is not yet experimentally
proved. The m input loads and its addition remain.

Arithmetic implementation matters beyond chain counts: current M precomputes
four runtime operand companions and reuses them; W's four shuffled runtime
products use ordinary five-instruction Montgomery chains. W also spends memory
operands on repeated shuffle masks. The aggregate λ identity removes 96 chains
relative to **old W**, not relative to M.

| Expanded source region | M instructions / peak live YMM | W instructions / peak live YMM |
|---|---:|---:|
| Shared frontend | 685 / 10 | same |
| NTT32 + terminal | 1133 / 14 | 1184 / 13 |
| Decode + validation | 596 / 10 | 489 / 4 |
| Mul, or fused MulAdd | 1614 / 16, plus separate add | 2406 / 9 |
| One pack | 773 / 7 | 865 / 4 |

W pack routes less but executes more instructions because it uses a compact
48-packet loop. M pack is unrolled; its symbol reserves 5120 bytes with `.org`
padding after return. That reserved extent is not hot executed instructions.
The W aggregate correction table is 3072 bytes plus 256 bytes of reused masks.

The source-level GPR/control/call/return totals are 204 versus 936, **excluding**
current C `poly_add` compiler control and the ciphertext highrange alias jump.
They are not presented as an exact full linked-image delta. The JSON preserves
def/use traces and complete opcode distributions; assembler alignment padding,
encoded `.text` and actual hot footprint need the future machine gate.

## 5. Validation and reproducibility

Checks completed in the generator:

- Hwang pre/post: 1536 actual-table basis cases each; source transpose 256 owners.
- GT reordered maps: 96 basis vectors × two branches × four cutpoints.
- Current word Forward: 1536 signed impulses plus 36 zero/alternating/boundary/
  random ternary polynomials, against independent direct factor evaluation.
- Direct-W vs M projection: all 768 owners raw-exact; exact r wire bytes.
- W arithmetic: 1536 basis, 864 uniform boundary, 768 mixed boundary and 10003
  random packets, plus 32 full 48-packet polynomial serialization cases.
- Decoder: q−1/q/4095 at every one of 768 wire positions (2304 cases).
- Serializer: all 65536 signed words, plus 32 full random roundtrips.
- Scratch last-use/overlap and the final 24-byte packet stores 16+8+4 checked.
- Seven regression tests include stale macro-definition lookup, uninitialized
  register rejection, XMM/YMM alias, ownership counterexample and wrong companion.

Ternary tests cover the CBD1/SOTP **alphabet superset**, not a new statistical
sampler test. These checks do not replace future ASM ABI/guard-page/sanitizer,
constant-time, KAT or linked conformance tests. No new whole KEM was implemented.

Reproduce from the experiment directory after downloading/unpacking the pinned
archive to an external cache (SHA-256 is in the source manifest):

```sh
python3 tools/research_gt_vector_mapping.py --artifact-root <unpacked-pinned-artifact>
python3 tests/test_gt_vector_mapping_models.py -v
python3 tools/research_gt_vector_mapping.py --artifact-root <unpacked-pinned-artifact> --check
```

`--check` reruns the checks and compares the generated JSON byte-for-byte. The
generator verifies the pinned artifact sources and the existing refined range
proof's source hashes; no network, ASM generation or timing occurs inside it.

## 6. Decision

**One bounded next-ASM proposal: C1 aggregated-λ W single-packet**, with unchanged
W producer/codec and original hash staging. It is selected for its complete
model/range/allocation and new mechanism relative to old W, not a static-score
prediction that it beats M. Its suffix-sum dependency, constant traffic and
extra control are explicit risks.

The decisive future boundary is PK bytes + r/m coefficients → r hash input
bytes + ciphertext bytes, followed by the full deterministic caller if it has
a signal. Controls must include current M, an M add-fused control and old W;
fix timed dispatch/input-bank asymmetry first. None is run in this checkpoint.

C2 remains open. A next C2 proposal must show where the 96 frontend blends or
another complete conversion/pass actually disappears, including the cost of
restoring gauge and supplying both consumers. A modular stage-order identity
alone is not sufficient to launch another ASM candidate.
