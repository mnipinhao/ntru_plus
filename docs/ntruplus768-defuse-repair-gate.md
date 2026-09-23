# NTRU+768 Official-opt: existing-multiply range-repair gate

This is a source-anchored selection gate on `avx2-official-opt`, not a new
linked AVX2 kernel or a cycle comparison. The immutable Official 20260831
source, caller-lazy qualification export, earlier Forward consumer proof,
source-instruction BaseMulScale proof, and exact true-`y=x⁴` factor map are
the inputs. The machine-readable selection record is
[`officialopt-defuse-repair-gate-20260923.json`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/results/officialopt-defuse-repair-gate-20260923.json).

## Corrected Decap entry and CT screen

The earlier true-twist screen reconstructed the first three BaseMulScale
plane bounds from an obsolete two-product zeta estimate. Its worst-degree
bound was valid, but its provenance for the other planes was not. The new
[`research_true_twist_repair_v2.py`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/tools/research_true_twist_repair_v2.py)
refuses stale source hashes, reads all **768 physical cell intervals** from
the closed `yang-closure-schedule-20260923.json`, maps each cell through the
independent `(leaf, degree)` factor table, and screens the six 32-leaf CT
trees. Accepted BaseMulScale operands are canonical `[0,3456]`; the proven
output-plane bounds are `[-3608,3791]`, `[-5285,5651]`, `[-6963,7512]`, and
`[-6912,7644]`. Taking each cell's maximum absolute value is conservative:
the screen uses neither sign nor cross-lane correlation.

The 24 first unproved adds (six cohorts × four degree columns) **all** have
`twiddle=1`. For degree columns 1–3 they first appear at size 8; for degree
0 they appear at size 16. Degree 3 retains the `30576+30576=61152` example.
These are interval-proof failures, not reachable-overflow witnesses. The
current lower input is not multiplied on these paths, so there is no existing
CT twiddle multiplication to move before those adds. Adding Montgomery-by-one
is a possible *new* repair, with a chain and constant cost; reducing one side
with Barrett does not prove the first degree-0 add safe (bounds 33133 or
32984). The five deferred inverse halvings still require exactly one `1/32`
payment in the complete tail. Neither repair placement, final `y³²` untwist,
radix-3/trinomial range, register allocation nor complete Decap cost has been
closed. The old historical range-screen JSON is retained; v2 supersedes its
plane derivation.

## Three caller paths

| Caller | Actual consumer and nearest fixed work | Selection result |
| --- | --- | --- |
| Keygen | f/g Forward reaches BaseInv. Caller-lazy already removes the 48 terminal Barrett vectors per Forward; batch inversion uses runtime products, a literal-zero test, and a fixed R³ correction after those products. | The existing Forward/consumer bounds close. No independent hazardous add with an earlier fixed multiplication has been identified. The R³ correction cannot be moved across zero detection or retry by instruction scheduling alone. |
| Encap | r/m use caller-lazy Forward; r also yields hash bytes. Quartic BaseMul performs Montgomery reduction of runtime products and fixed-zeta terms, then its R² finalizer; message addition follows the finalizer. | BaseMul has no standalone Barrett block to absorb. Reordering the zeta/finalizer relative to sums or add-m changes the arithmetic or scale and needs a new formula and range proof. No current same-DAG candidate qualifies. |
| Decap | Validated c/f enter BaseMulScale. Existing GS inverse multiplies the difference branch after its add/sub, while the untouched sum branch is reduced separately. The true-twist CT input twiddle precedes the merge but is identity at all 24 first unproved paths. Message Forward uses `crepmod3` output `[-2,2]`; reencryption r uses `[-1,1]`. | Moving an existing multiply does not repair the earliest CT nodes for free. Historical `stage5reuse` remains a mechanism control, not a new win. No complete safe allocation and scale schedule qualifies for ASM. |

The source audit asserts these caller call sites, the absence of standalone
Barrett in caller-lazy Forward and BaseMul, and the source order of GS
`update → mul → reduce2`. It records hashes; it does **not** claim linked
instruction-level def/use, exact latency, or exhaustive rejection of other
arithmetic decompositions. Existing Forward lane and consumer proofs cover
Keygen, Encap, Decap message and reencryption domains. BaseInv's literal-zero
status and retry cannot be inferred from residue equality alone.

## Decision and reproduction

No candidate passes the requested semantic, signed-i16, scale, consumer and
allocation gates. The authorized allowance of two ASM prototypes remains
unused. Thus there is no new KAT, linked audit, component short timing, full
caller short timing, or fixed-layout A/B in this round. This is a bounded
selection result: correlated bounds or a jointly redesigned butterfly may
still yield a candidate, but a local instruction move does not yet do so.

From the existing experiment directory, with its pinned proof artifacts:

```sh
python3 tools/research_true_twist_repair_v2.py
python3 tools/audit_defuse_repair_gate.py
```

Both scripts fail if a proof input's recorded source hash is stale. Repeating
the first script writes the same sorted-lane screen JSON; repeating the second
writes the same source-anchored decision JSON.
