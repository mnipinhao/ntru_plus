# P59 result — the fused region cannot be re-allocated, but it can be inserted

P59 changes no production code.  It answers the question P58 left open: what
windowing and precedence strategy makes a fused producer+route region
schedulable, and is the plan from P29's closing note actually executable?

The answer is that the plan as stated — fuse symbolically, re-allocate, schedule
— **is not executable**, and a different flow is.  Four settings turned out to be
necessary, each established by a measured failure rather than chosen up front.

## 1. `variable_size` is decisive, and P58's probe did not use it

Same 131-instruction fused window, one knob changed:

| configuration | wall time | scheduled cycles | IPC |
|---|---:|---:|---:|
| as used in P58 (`variable_size=False`) | 1,195.5s | 535 | 0.24 |
| **`variable_size=True`** | **128.4s** | **104** | **1.26** |
| `functional_only` (allocation only) | 5.3s | — | — |

With `variable_size=False` Slothy runs an external binary search over stall
counts; every step hit the solver cap and it settled on a bad schedule.  P58
therefore concluded "Slothy scalability is the obstacle" from a configuration
error.  That conclusion is withdrawn.

The third row matters independently: allocation on its own is cheap, so the cost
is in scheduling, not in fitting the registers.

## 2. `ST3` writeback blocks the split heuristic outright

Every configuration using `split_heuristic` with naive interleaving produced a
schedule and then died:

```
split 8 + zip              13.1s   SlothyException: Address fixup failure
split 8 + zip + seam 8     13.0s   SlothyException: Address fixup failure
split 12 + zip + seam 8    13.7s   SlothyException: Address fixup failure
split 8 + zip + seam 8 x2  13.3s   SlothyException: Address fixup failure
```

All 64 `ST3` in P29's route share one post-incremented pointer, and Slothy cannot
repair the offsets after reordering them.  Rewriting delivery as a fixed base
plus a renameable pointer, with no writeback anywhere, removes the failure.

P58 had already found the four-pointer rewrite to be performance-neutral on both
hosts and filed it as incidental.  It is not incidental: it is a precondition for
the split heuristic to run at all.

## 3. Allocation cannot be split, and its practical limit is about 450 instructions

`split_heuristic` cannot be used during allocation, because sub-region boundaries
carrying `V<name>` values cannot be typed:

```
Source line <output:b_r20> can be parsed in multiple ways:
* <output:b_r20:GPR>  * <output:b_r20:NEON>  * <output:b_r20:STACK_NEON> ...
```

So allocation is necessarily one-shot, and it is the binding constraint:

| region | instructions | wall time | verdict |
|---|---:|---:|---|
| `win-04.S` | 136 | 5.0s | OPTIMAL |
| `win-08.S` | 244 | 13.3s | OPTIMAL |
| `win-16.S` | 452 | 45.9s | OPTIMAL |
| `win-32.S` | 892 | >600s | **UNKNOWN (cap)** |

Growth is worse than quadratic, and 892 is the size of one complete fused P0
region.  Symbolic re-allocation of a fused region is therefore off the table.

## 4. The flow that does work: insert into already-allocated code

P28's shipped producer is already allocated.  Recomputing its liveness properly —
per def to the last use before the next def of the same physical register, not
first-def to last-use, which counts every reused register as live throughout —
gives:

| P28 allocated producer, 841 instructions | |
|---|---|
| free physical vector registers | median **11**, p25 4 |
| slots with at least 4 free | **654 / 841 (77.8%)** |
| route to place | 32 bursts x 12 = **384** instructions, working set 4 |

654 eligible slots against 384 needed, consistent with P58's symbolic figure of
62.8% of slots having ten or more free.  The route can be given physical
registers directly, with no symbolic allocation anywhere:

```
P28 allocated producer (841 physical instructions)
   -> insert 384 route instructions into the free slots
   -> phase 2: split_heuristic + naive interleaving + variable_size
```

Only phase 2 remains, and phase 2 operates on physical code, where the split
heuristic works.

## 5. Incidental: the producer is already windowed

`candidate-main.timing.S` carries an inner label `p28_main_terminal_start:` at
line 736, splitting it into a main body and a terminal region.  Slothy will not
parse a label inside an optimisation region, so it has to be stripped or used as
a boundary — which is what P28 itself did.  A fused design should reuse that same
cut rather than inventing one.
## 6. Phase 2 does converge on a full-size physical region — with the right window size

Two further blockers surfaced, both in Slothy rather than in the kernel.

**The Cortex-A76 timing model has no entry for `vins_d`.**  P28's producer parks
six Q states in GPRs with `ins v5.d[1], x6` and friends.  `aarch64_neon.py`
defines `vins_d` with exactly that pattern, but `cortex_a76.py` never references
it, so phase 2 aborts with `UnknownInstruction`.  `slothy-vins_d.patch` adds it
in the six places `vins_h_lane` already appears — same V pipe, same issue slot,
same two-cycle latency.  The patch is applied to a private copy under the
session scratchpad; the checkout at `/Users/chenpinhao/slothy` is untouched.

This also explains P28's region boundary.  All six `ins` sit at instruction 648
and beyond, and `p28_main_terminal_start:` is instruction 356 — so P28's Slothy
region stops before the parking.  The cut was not arbitrary; it routed around
the model gap.

Conveniently, that same boundary is where the route has to go:

| window | instructions | contents |
|---|---|---|
| main | 0–355 | no stores, no unmodelled instructions |
| terminal | 356–840 | **all 32 stores and all 6 `ins`** |

**The per-solve cap has to match the sub-window size.**  With the patch applied,
on the full 843-instruction physical producer:

| configuration | wall time | result |
|---|---:|---|
| `inputs_are_outputs`, split 8 + zip | 533.9s | No solution found |
| `outputs=[]`, split 8 + zip | 757.8s | No solution found |
| **`outputs=[]`, split 16 + zip** | **567.3s** | **OK, 672 cycles** |

Split 8 gives windows of about 105 instructions, and the diagnostic in section 1
already showed that a 131-instruction window needs 128s — more than the 60s cap.
Split 16 gives about 53 instructions per window and converges.  The live-out
declaration made no difference; window size against solver cap was the whole
story.

**Schedule quality at these settings is not yet production grade.**  Slothy
reports 672 cycles for 843 instructions, IPC 1.25, against P28's own 89 cycles
for its 356-instruction main window at IPC 4.00.  Note also that the model's
IPC 4.00 is an issue-slot count: the same kernels measure about 1.7 on hardware,
so the model runs roughly 2.3x optimistic and its absolute cycles must not be
compared with PMU figures.  A production run needs a larger per-solve budget, a
factor tuned between 8 and 16, and most likely the two P28 windows scheduled
separately rather than as one region.

## 7. Verdict

The flow named at the end of P29 — fuse symbolically, re-allocate, schedule — is
not executable.  The flow that is:

```
P28's allocated producer (841 physical instructions)
  -> insert the 384 route instructions into its free slots
     (654 eligible slots, median 11 free registers)
  -> phase 2: split_heuristic factor ~16, naive interleaving,
     variable_size, outputs declared, no ST3 writeback,
     Cortex-A76 model patched for vins_d
```

Every step of this is measured, and no step requires symbolic re-allocation.
What remains before authoring a kernel is tuning the phase-2 budget until the
schedule is at least as good as P28's, and deciding whether to schedule the two
P28 windows jointly or separately.
