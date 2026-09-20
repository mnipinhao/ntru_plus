# P69 — scheduling the lane-basis inverse kernels, and what the model got wrong

P68 closed by naming the obvious follow-up: neither new kernel had been
scheduled.  `inverse9.S` carried NTRU+864's A76 schedule with 35 instructions
deleted out of it and `inverse16.S` the same with 224 deleted, so both were
schedules for code that no longer existed.  P36 had already found that 1152's
kernels were never scheduled for 1152 at all.

**Taken: A76 5,827 -> 5,774 cycles, -0.91%.  M2 unchanged at 484.5 ns.**
Both hosts hold, so it promotes — but it is a twentieth of what the model
predicted, and that gap is the real result of this gate.

## The measurement

| | A76 cycles | M2 ns |
|---|---:|---:|
| P68 | 5,827 | 484.5 |
| P69, `inverse9` only | 5,825 | 484.5 |
| P69, both kernels | **5,774** | **484.5** |

A76: median of 201 rounds x 200 calls, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`;
three repetitions agreed to the cycle.  M2: median-of-medians over 15 runs of
64x2,000, best min 472.0 against 472.5 — flat to the resolution of the host.

Both variants live in one binary and alternate rounds.  Bit-identical to P68
over 3,000 M2 and 2,000 A76 trials; in the KEM, all gates pass and the KAT is
byte-identical, including the 8/8 ABI sentinels that confirm the
reserved-register policy held.

## What Slothy predicted

| kernel | existing | scheduled | model says |
|---|---:|---:|---:|
| `inverse9` (x16) | 242 | 125 | -48% |
| `inverse16` (x8) | 545 | 325 | -40% |

The "existing" column is Slothy's own timing of the code as it stands, with
`allow_reordering=False` and `allow_renaming=False` — the same model, the same
reservations, measuring instead of optimizing.  Without it the optimized figure
has nothing to be compared against.

Across the call counts that is `16*117 + 8*220 = 3,632` cycles predicted.
**Measured: 53.**  The model over-predicts its own gain by a factor of 69.

## Why

Cortex-A76 is out-of-order.  Slothy models in-order issue with fixed latencies,
so its 242-cycle figure for `inverse9` is what that code would cost on a machine
that could not reorder.  The real A76 has already recovered nearly all of it
dynamically by the time the static scheduler is invited to help.  Two
independent checks agree that there was little to take:

- the instruction multiset is unchanged, 57 mul-class per `inverse9` call, so
  the A76 floor of 114 cycles/call never moved;
- P36 had measured `packed_i9` at **90.5%** of its mix floor and
  `invntt16_asm` at **94.6%** before any of this.

Sanity check against the one Slothy gate that did pay: P27 took `basemul_rinv`
from 3,054 to 2,744, -10%.  That kernel was intrinsics C sitting at **78%** of
its multiply floor.  The distance from the floor, not the model's predicted
delta, is what says whether scheduling is worth running.

## Configurations tried

| kernel | config | solver | model cycles |
|---|---|---:|---:|
| `inverse9` | plain (whole region) | 45.7s | **125** |
| `inverse9` | split 4 + naive interleaving | 28.8s | 127 |
| `inverse9` | split 8 + naive interleaving | 28.9s | 133 |
| `inverse16` | split 8 + naive interleaving | 147.9s | **325** |
| `inverse16` | split 16 + naive interleaving | 125.6s | 336 |

`inverse9` at 149 instructions fits the solver whole, and splitting it only
costs; `inverse16` at 433 needs the split heuristic, and 8 beats 16.
`variable_size=True` throughout, per P59's finding that `False` forces an
external binary search into the solver cap.

Register policy: reserve every GPR the region does not already use, so the
solver cannot introduce a callee-saved register the public wrapper does not
save.  The ABI sentinels confirm it held.

## Not measured under SUPERCOP

53 cycles on a KEM of ~90,600 is 0.06%.  The run-to-run control in P68's
SUPERCOP run was 74 cycles on the official implementation, so this change sits
**below the resolution of that instrument** and a run would report noise.  The
direct `perf_event` A/B above is the honest statement of what it is worth.

## What this closes

The inverse's remaining distance from its multiply floor — 5,774 against 4,970,
16.2% — is now known not to be a scheduling problem.  It is the driver, the
rebase pass, `crepmod3` and genuine dependency.  Any further gate on this
kernel has to remove work, not reorder it.
