# GT768 Encap compute-island boundary gate

Date: 2026-09-22. Branch: `avx2-gt-ntt`.

## Result and evidence level

The attached Hwang discussion motivates placing specialization inside a
compute island and choosing an output contract for its actual caller. This
checkpoint examines whether NTRU+768 Encap can remove a full intermediate
materialization. The machine-readable source audit is
`generated/tile4_encap_compute_island_gate.json` in the existing 768 experiment.

The first source gate found that the unchanged B3 register schedule could not
retain early outputs. A subsequent, distinct B3→Q24 schedule was implemented
as one namespaced ASM prototype and priced in two short campaigns. It passed
the correctness gates but did **not** produce a repeatable full-island win, so
it was stopped before serious or Native SUPERCOP measurements. This is not a
claim that all direct-terminal designs are slow.

The source manifests are in the JSON. The clean GT implementation and pinned
SUPERCOP baseline are unchanged. The direct prefixed-buffer serializer remains
a separate parked experiment and contributes no credit here.

## What Hwang actually specializes

The pinned Hwang artifact contains `__asm_cyclic_FFT16` and
`__asm_negacyclic_FFT16` kernels whose small-ring transform, multiplication and
reconstruction share one routine. The latter explicitly executes `Bruunx2`,
Karatsuba and `iBruunx2`. Its outer post path still performs inverse
transpose/twist, inverse GT and inverse Rader arithmetic. Thus Hwang does pay
for return to coefficient order; its terminal intermediate is not an external
BaseMul ABI. That source architecture is useful as a *boundary hypothesis*.
Its NTRU Prime ring, number of terminal products and benchmark cycles do not
transfer to NTRU+768.

For this Encap, there is no inverse stage. The actual graph is:

```text
PK bytes → validate/decode → h(M) ───────────────┐
r coeff  → Forward → r(M) ──→ hash bytes          ├→ BaseMul → c
                            └────────────────────┘               ↓
m coeff  → Forward → m(M) ─────────→ add-m → Q24 ciphertext bytes
```

`r` has two consumers and must remain available across hash, SOTP and m
Forward. The early public-key validation is semantically required. `m` has one
arithmetic consumer; `c` has only the ciphertext consumer. These are the two
places where a compute-island boundary could move.

## Measured historical control, then the new source gates

The existing `GT32-ENCAP-Q24-SUM-M-001` already adds m inside the Q24
serializer. It removes 48 c reloads and 48 c stores per Encap, passes 100
byte-exact Encap vectors, and wins locally. Its full caller short test was
approximately −52.25 cycles in normal placement and +14.26 in reversed
placement. The existing `STATUS.yml` rejects production promotion. The new
study treats it as a control, not a fresh candidate.

Current BaseMul uses a 12-block B3 loop. For every block it stores three raw
degree-plane results, reloads them after the fourth result, applies the R²
finalizer, then stores four completed planes. The source-expanded live-register
replay peaks at all 16 YMM. Keeping the first raw result in an additional
register without changing the schedule gives a 17-YMM peak in the next output;
keeping the first two gives 18. This blocks the **unchanged-body** direct
`B3 → add-m → packet pack` link, not every alternative schedule.

The new prototype substitutes 12 memory-form h high-word multiply operands
per B3 block, so `%ymm1..3` can hold the first three raw results. Its R²
finalizer, add-m and Q24 consumer then work from live registers. The linked
function has no stack frame, call or vector spill; it uses the physical
`%ymm0..15` set and a public 12-way packet dispatch. The actual linked symbol
is 5,585 bytes. The static audit does **not** prove a semantic peak-live count;
the raw B3 differential and disassembly are separate evidence.

One non-obvious correction was required. The original Q24 serializer uses
overlapping 16-byte stores for adjacent 24-byte wire packets. B3 visits SoA
blocks in a different order from wire order, so these stores corrupted later
packets when fused. The prototype now writes each packet as exact 16+8+4-byte
segments. This adds 47 store instructions versus the existing serializer's
overlapping store schedule. It is part of the new terminal cost, not a free
implementation detail.

The realized boundary deletes 36 early raw stores and 36 late raw reloads,
then 48 completed-c stores and 48 serializer c reloads per Encap. It also
absorbs the separate add-m pass, but pays the new h memory operands, exact
packet stores, public dispatch and 5.6 KiB code body. Consequently the
removed memory traffic alone cannot predict cycles.

The m Forward loop runs six times and emits two complete four-plane M blocks
per iteration. Its first block becomes available before the second. However,
the existing BaseMul body also reaches 16 live YMM. Merely calling it while
four m planes remain live does not establish a spill-free link. A candidate
must consume m one plane at a time or supply a bounded operand-reload schedule.
It must also avoid overwriting unread frontend input in the reused `c` buffer.
The source gate identifies the exact first/second block output instructions;
it does not prove every alternative schedule impossible.

The asymmetric ingress branch has no independently established new consumer
schedule. Old D01 saves decoder routes but forms the same pairs in the
consumer, and old W-Montgomery loses the complete island by about 346 cycles
for one-packet arithmetic. The later aggregated-λ W model reduces that W
arithmetic debt, but its full modeled path still has routing +48 and constant
operands +550 versus M. It remains unpriced machine research, not evidence
that changing r/h presentation removes a complete pass.

## Range and decision contract

The existing refined small-input proof gives a maximum Forward representative
magnitude of 15,592 and a conservative post-add bound of 17,448. The
serializer's reduction was checked over all 65,536 signed 16-bit inputs. The
present gate preserves arithmetic and raw representatives. Any reordered
output or operand-reload schedule must replay signed pre-operation bounds and
Montgomery low-word behavior before ASM timing; the older `10788/12699`
metadata must not substitute for this proof.

The linked A prototype passed 1,003 primitive differentials including raw B3,
input immutability and canaries, 100 deterministic KEM vectors including
invalid PK/CT behavior, and ASan/UBSan for the C caller. Both short campaigns
used pinned SUPERCOP `cpucycles()`, the common O3GC recipe, CPU 1 with
`performance` and turbo disabled, the same ELF and three fresh launches:

| Campaign | B3+add+pack StQ2 delta | Full polynomial island StQ2 delta | Full-island favorable launches |
| --- | ---: | ---: | ---: |
| `encap-live-b3-q24-short-20260922-a` | +10.67 cycles | −3.15 cycles | 2/3 |
| `encap-live-b3-q24-short-20260922-b` | +8.04 cycles | −0.29 cycles | 1/3 |

Correction (2026-09-22, function-level research): the former runner averaged
disjoint quarter slices, not SUPERCOP stabilized quartiles. The table now uses
the pinned `stq.h` estimator; `summary-corrected-stq.json` supersedes the
retained historical `summary.json` in each campaign. Raw observations are
unchanged and their SHA-256 values are recorded. The Python replacement passes
240 comparisons against the actual pinned C implementation, including odd
sample counts. The counter is `default-perfevent`, not RDPMC. The historical
harness also includes timed region/variant dispatch and a sink; correcting its
estimator does not repair that scope. Do not use these samples for new causal
component attribution.

The full-island cutpoint starts at PK bytes and r/m coefficients and ends at
r hash-input bytes and ciphertext bytes; it does not execute `hash_g` or
sampling. Its mixed deltas are too small to claim a gain. A is therefore a
correct, linked but performance-inconclusive/rejected realization. It does
not proceed to serious pricing or Native.

B (m terminal→MulAdd) still needs an exact schedule that preserves unread
frontend scratch while consuming m planes without the full 48-plane store.
C (asymmetric ingress) still has no distinct full-pass removal beyond prior
D01/W work. Neither has an authorized ASM prototype at this point. No clean
production or pristine SUPERCOP source was changed.

## Reproduce

From the existing 768 experiment directory:

```sh
make encap-compute-islands-check
```

To intentionally regenerate the tracked report after a source change:

```sh
make encap-compute-islands-generate
make encap-compute-islands-check
make encap-live-b3-generate encap-live-b3-check encap-live-b3-kem-check
make encap-live-b3-sanitize
make encap-live-b3-short SUPERCOP_ROOT=/home/nuc/supercop-20260627 \
    BENCH_CPU=1 RESULT_TAG=<new-unique-tag>
```

The first audit reads the reachable clean B3 loop, M Forward loop, Encap
caller, refined range report and historical control status. The live-B3
generator additionally lowers a candidate machine object; only the short
runner calls a cycle counter. The raw runs and linked audit are retained under
`results/encap-live-b3-q24-short-20260922-{a,b}` in the experiment.
