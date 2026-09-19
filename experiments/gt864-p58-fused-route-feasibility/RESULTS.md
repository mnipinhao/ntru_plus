# P58 result — register feasibility is proven; the blocker was never the route

P58 changes no production code.

## 1. Register feasibility: the fused region needs no more registers than the producer alone

Symbolic vector-register pressure of the straight-line Slothy sources
(`pressure.py`; live range = first def to last use, so the model is an upper
bound any allocator must meet):

| source | instructions | symbolic values | peak live |
|---|---:|---:|---:|
| `p28_paired_i16` producer | 841 | 319 | **33** |
| `p29_main_route` | 873 | 484 | **10** |
| `p29_tail_direct` | 784 | 295 | 24 |

The allocated producer uses exactly 32 vector registers and 17 GPRs, so the
model is +1 conservative on the producer.  The route's working set is 4–10 with
a mode of 7, of which four are the ternary constants.

The producer's pressure is a spike, not a plateau: it is at 33 for only 3.8% of
its schedule, and **62.8% of its slots have 10 or more free registers**.

Constructive fusion (`fuse.py`, `fuse2.py`) keeps the producer's Slothy order
fixed and inserts the route work wherever the live count allows — a sufficient,
not optimal, schedule, so success is a real feasibility proof:

| variant | constants held live | peak | verdict |
|---|---:|---:|---|
| A  constants live across the region | 4 | 37 | over by 5 |
| B  `sqrdmulh`/`mls` take theirs by element | 3 | 36 | over by 4 |
| C  constants reloaded once per burst | 0 | 33 | = producer's own peak |

`margin.py` then sweeps the budget:

```
  budget   peak  peak attained at   route interleaved
    28      33   producer-only       384/384 (100.0%)
    30      33   producer-only       384/384 (100.0%)
    32      33   producer-only       384/384 (100.0%)
```

**The peak is attained at a producer-only instruction at every budget, and all
384 route instructions interleave even at a budget of 28.**  The route
contributes exactly zero to the register peak.  The only obstacle in variants A
and B is holding the ternary constants live; nothing about the route work
itself.

Reloading those constants per burst is free.  Measured 2026-09-18: substituting
`movi` for the 448 repeated composite-table loads — which frees the load port
while preserving the dependency shape — made **both** hosts slower (M2
421.9 -> 446.6 ns, A76 4,808 -> 4,888 cyc), because the load ports sit idle and
`movi` competes for the vector pipes.  Extra loads cost nothing here.

## 2. Cycle budget on Cortex-A76

Same-harness measurements with the route stage nop'd out:

| | A76 cyc | content |
|---|---:|---|
| production without `crepmod3` | 4,387 | main I16 x6 + tail + i9 |
| P29 without its route pass | 4,436 | paired x3 + P29 tail + i9 |
| production complete | 4,819 | |
| P29 complete | 5,022 | |

Two facts follow.  P29's paired producers are themselves about **49 cycles
slower** than production's six one-bank calls despite retiring far fewer
instructions, so the paired basis is not free.  And the fused route must land
under **4,819 - 4,436 = 383 cycles** to avoid an A76 regression, against
P29's current standalone **586** — a 35% reduction, to be bought entirely by
issuing those instructions in the producer's idle slots rather than serially.

## 3. Slothy convergence: this is the real obstacle

Fused producer+route windows were generated in symbolic form (`genwindow.py`,
variant C) and given to Slothy with the Cortex-A76 model, full timing schedule,
spills disabled, 300s solver cap (`probe.py`).  Environment: Slothy from
`/Users/chenpinhao/slothy` with ortools 9.15.6755 / sympy 1.14.0 / unicorn 2.1.4
in an isolated venv, because the interpreter used by the earlier gates no longer
exists on this machine.

| window | instructions | fused outputs | result |
|---|---:|---:|---|
| `window-02.S` | 81 | 2 | converged, **Expected cycles 70** (~10 min) |
| `window-04.S` | 131 | 4 | **did not return within 25 minutes**; probe stopped |

This reproduces P32's recorded experience ("a whole-region timing solve was
stopped after it failed to return inside the bounded run").  A fused P0 region
is 1,193 instructions.  Scheduling it as one Slothy region is not currently
practical; a windowing strategy with explicit precedence constraints is itself
the next piece of work, not an implementation detail.

## 4. Incidental finding: the ST3 pointer chain constrains Slothy, not the hardware

Slothy emits `Forbid reordering of (... type st3_with_inc ...) to avoid address
fixup issues` for every pair of `ST3`.  All 64 `ST3` in the shipped P29 route
share one post-incremented pointer (`st3 {...}, [x2], #24`, with `add x2, x2, #6`
between groups), so the whole delivery path is pinned to program order.

The route uses only x0, x1 and x2, so x3-x17 are free.  Rewriting the 64 `ST3`
onto four rotating pointers (`p29_route.S`, group `k` uses pointer `k mod 4`,
advanced by `6 + 3*54 = 168` after its pair) keeps the output byte-identical to
production over 20,000 x 864 coefficients and costs three instructions:

| | A76 cyc | M2 ns |
|---|---:|---:|
| P29 | 5,022 | 380.2 |
| P29 with four ST3 pointers | 5,029 | 380.2 |

**No change on either host.**  Out-of-order renaming already handles the `x2`
chain, and the allocated schedule is fixed, so the addressing mode alone buys
nothing.  The constraint is worth removing only as an input to a fresh Slothy
run, where it would widen the search space.

## 5. Verdict

- **Registers are not the obstacle.**  A fused region needs exactly the vector
  budget the producer already needs, provided the ternary constants are reloaded
  per burst rather than held live.  This holds at every budget from 28 up.
- **Slothy scalability is the obstacle.**  131 instructions of fused region did
  not schedule in 25 minutes; a full region is 1,193.
- The A76 cycle budget is tight but not absurd: the fused route must come in
  under 383 cycles against P29's 586, and P29's paired producers already give
  away about 49 cycles against production's one-bank calls.

Recommended next gate: a windowing and precedence strategy for the fused region,
validated on one `(top,t)` group before any full kernel is authored.  Do not
author assembly first.
