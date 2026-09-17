# P27 — The first SLOTHY gate: `basemul_rinv`

Branch `neon-1152`, parent `8adfb154`.  Pi 5 core 3, GCC 14.2.0.
SLOTHY 0.2.0, `Arm_AArch64` / `Arm_Cortex_A76`, OR-Tools CP-SAT 9.15.6755.

M2-2, and the first time a solver has been run for NTRU+1152.  Everything the
campaign shipped until now either carried NTRU+864's schedule with remapped
immediates, was hand-written and never scheduled, or was intrinsics C.

**2,744 cycles against the intrinsics C's 3,054.  `poly_basemul_rinv` went from
+634 to +232, decaps from -0.86% to -1.68%, and the KEM from -1.55% to -1.79%.**

## 1. Why this kernel, and why a solver was the right tool

P24 established that the gap was not the arithmetic: the official's
`poly_basemul_scale` issues an **identical** multiply multiset — 19 `smlal`,
19 `smlal2`, 7 `smull`, 7 `smull2`, 7 `mul`, 7 `uzp1`, 7 `uzp2` — and reaches
2,551 where our C reached 3,054 against a 2,376 floor.  78% of floor with the
instruction count already minimal is a scheduling problem by elimination, and
the official's number proves the schedule exists.

That is the opposite of what measurement said about every other kernel: `ntt9`
at 93% of floor (P16), the codec at 90% and ~100% (P19).  This campaign has
rejected scheduling four times on measurement; this is the first time it was
the answer.

## 2. The pipeline

`dev/ntruplus1152_clean/generate.py` authors the kernel as a data-flow DAG in
symbolic registers; `dev/ntruplus1152_opt/optimize.py` runs SLOTHY twice.

| stage | seconds | what it does |
|---|---:|---|
| `ra` | 2.1 | allocate the symbolic registers, no reordering |
| `timing` | 372.7 | schedule, software pipelining, split heuristic factor 8 |

The `ra` output is assemblable, so it doubles as the testable clean tier — the
symbolic form itself is not.

## 3. Three SLOTHY constraints the kernel had to be shaped around

Each cost a failed run and is now encoded in the generator, so the next kernel
does not rediscover them.

**Symbolic registers cannot be defined outside the optimized region.**  The four
modulus constants are set up before the loop, so they are *physical* `v0-v3` and
reserved.  Recomputing them inside the loop would have cost eight instructions
per group.

**`stp d8, d9, [sp, #-64]!` does not parse** — SLOTHY's AArch64 model has
`stp <Da>, <Db>, [sp, <imm>]` with no pre-index writeback.  Rather than work
around it, the kernel stashes nothing and reserves `v8-v15`, leaving `v4-v7` and
`v16-v31`.  The `basemul-inverse` ABI sentinel confirms the reservation held.

**`t0`...`tN` are SLOTHY hint registers.**  Naming fresh temporaries `tN` makes
every instruction parse and then fail its type check, with an error path that
itself raises.  NTRU+864's generator carries the comment; this one now does too.

## 4. Measured

| | cycles |
|---|---:|
| `ra` only, allocated but unscheduled | 3,155 |
| intrinsics C | 3,054 |
| **SLOTHY, `Arm_Cortex_A76`** | **2,744** |
| official `poly_basemul_scale` | 2,551 |
| issue floor | 2,376 |

The unscheduled `ra` figure is the honest baseline for a symbolic clean tier:
its instruction order is the generator's, not a compiler's, so SLOTHY's win over
it is 411 cycles and its win over GCC is 310.

Still 193 above the official and 368 above the floor, so the schedule is good
but not finished; a longer timeout or a different split factor may close more.

## 5. Correctness

```
4000 trials x 1152 coefficients, inputs on the declared [0,4095] plus the
all-4095 and random-extreme cases, against the shipped C as oracle:
  not congruent                0
  different representative     0     (byte-identical, not merely congruent)
  max |out|                 1728     exactly as normalize_d7 gives
```

Package gates on the Pi, all green, `basemul-inverse` ABI sentinel included:
KAT sha256 `2ddfc810c4...64c3`, 64 round trips with tampered rejection, 13,824
canonical cases, 11/11 sentinel masks zero, 288/288 baseinv, zeroization clean.

## 6. Whole KEM

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,082 | 63,009 | -1.67% | -1.65% |
| encaps | 59,541 | 58,348 | -2.00% | -2.05% |
| **decaps** | 52,512 | **51,629** | **-1.68%** | -0.86% |
| **total** | **176,135** | **172,986** | **-1.79%** | -1.55% |

The assembly is installed behind `NTRUPLUS1152_ASM_BASEMUL_RINV`: without the
define the C is used and every gate still passes, so the kernel is an
optimization rather than a dependency.

## 7. Next

`baseinv`'s numerator (3,711 against a 2,952 floor) and finish (1,095 against
864) are the other two admitted kernels, worth about 990 together.  The
`apple_m1_firestorm` and `neoverse_n1` schedules of this same kernel are
generated for the record; only `cortex_a76` can be measured in this repository.
