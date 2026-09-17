# P28 — The same kernel, two schedules, two machines

Branch `neon-1152`, parent `b484f180`.
Pi 5 Cortex-A76 (perf_event cycles) and Apple M2 Pro (derived cycles, macOS).

The `dev/clean/opt` tree exists to produce a schedule per microarchitecture.
This gate asks whether that is worth anything, by scheduling one kernel for two
targets and running both on two machines.

**It is worth something on the A76 and nothing on the M2 Pro, and the target the
schedule was made for does not matter on either.**

## 1. What was built

`basemul_rinv`, from one symbolic source, scheduled twice:

| target | `ra` | `timing` | instructions |
|---|---:|---:|---:|
| `Arm_Cortex_A76` | 2s | 373s | 355 |
| `Apple_M1_firestorm_experimental` | 3s | 733s | 241 |

The different instruction counts are different software-pipelining depths;
both are the same 115-instruction loop body before scheduling.

The M1 run is only possible because of the seven-class model patch
(`dev/slothy_models/apple_m1_ntruplus.py`), whose numbers come from the model's
own `vumull`/`vumlal` entries and from Dougall Johnson's Firestorm tables.

## 2. On the Pi 5, Cortex-A76

Both schedules are **byte-identical** to the C oracle over 4,000 trials x 1,152
coefficients, `max |out| = 1728`.

| | cycles |
|---|---:|
| intrinsics C | 3,054 |
| SLOTHY, `cortex_a76` | **2,744** |
| SLOTHY, `apple_m1_firestorm` | **2,739** |
| official `poly_basemul_scale` | 2,551 |
| issue floor | 2,376 |

Scheduling is worth about 310 cycles, 10%.  **Which target it was scheduled for
makes no measurable difference** — 2,744 against 2,739 is inside the noise.  The
expectation going in was that the M1 schedule would be *worse* here; it is not.

## 3. On the Apple M2 Pro

Three consecutive runs, candidates measured alternately and each reduced to its
minimum:

| | ns | ns | ns |
|---|---:|---:|---:|
| intrinsics C | 278.8 | 277.0 | 277.9 |
| SLOTHY, `cortex_a76` | 277.4 | 277.2 | 278.5 |
| SLOTHY, `apple_m1_firestorm` | 277.6 | 278.8 | 280.8 |

**All three identical**, spread 1.4%.  Neither schedule buys anything.

Nanoseconds are the measurement; cycles are derived, because macOS exposes no
perf_event and `PMCCNTR_EL0` is not readable from userspace.  The derived clock
settles at 3.26-3.27 GHz across runs, so the cycle figures are about 905 for all
three, but the ns are what was actually observed.

## 4. Why the two machines disagree

The A76 is four-wide with a reorder buffer around 128 entries; the loop body is
115 instructions, so barely one iteration fits in the window and a static
schedule has real work to do.  Apple's P-core is far wider with a reorder buffer
several hundred entries deep: it finds the parallelism at run time, and a static
schedule has nothing left to contribute.

That also explains why the *choice* of target does not matter on the A76.  Both
schedules were solved against the same dependency graph, and what they are
mostly doing is spreading the seven Montgomery reductions' serial chains far
enough apart to fill the multiply pipe.  The two models disagree about the
machine but agree about that structure, so they produce schedules that are
different in detail and equivalent in effect.

## 5. The M1 model is a poor predictor, even patched

SLOTHY's `apple_m1_firestorm_experimental` solved to **81 cycles per group**,
2,916 for 36.  The M2 Pro measures about **25 cycles per group**.  A factor of
three, and in the pessimistic direction.

M2 Pro is Avalanche, not Firestorm, so this is not a like-for-like comparison
and the model is not being accused of being wrong about M1.  But it does mean
the model cannot be used to *predict* Apple performance for this kernel, which
removes most of the reason to schedule for it without M1 hardware to check.

## 6. What this settles

1. **Scheduling is worth ~10% on the A76 and nothing on Apple silicon** for this
   kernel.  The campaign's Slothy work should stay pointed at the Pi 5.
2. **Shipping a second, Apple-targeted implementation is not currently
   justified.**  The schedule is no better than the A76 one on the only Apple
   machine available, and the model that produced it is a three-fold pessimistic
   predictor.  The tree keeps the capability; nothing ships.
3. **The multi-target structure still earned its place** — it is what made this
   measurable at all, and the answer would have been a guess without it.

## Reproduce

```sh
# Pi: correctness and cycles for either schedule
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. check_basemul_rinv.c inverse.c <sched>.S -o chk

# macOS: three-way, interleaved and minimised
cc -O3 -std=c11 -I. -DNTRUPLUS1152_ASM_BASEMUL_RINV -DHAVE_M1=1 \
   bench_macos.c inverse.c cortex_a76/basemul_rinv.S m1_renamed.S -o bench3
```
