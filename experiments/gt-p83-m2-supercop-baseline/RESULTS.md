# P83 — the M2 baseline, measured against SUPERCOP's Official and at a certified clock

P82's M2 table is withdrawn.  Two independent faults: it compared against an
Official that is not the one SUPERCOP ships, and its whole timed run fitted
inside the window in which macOS still has the thread on an efficiency core.

## Apple silicon cannot be frequency-locked

There is no `cpufreq` interface on Apple silicon and `taskpolicy` can only
demote, so the clock cannot be pinned the way the Pi5 can.  Two things had to
be measured rather than assumed.

**The thread starts on an E-core.**  `ramp.c` sleeps two seconds, then reads the
clock continuously.  A freshly woken thread runs at 867 MHz, reaches 2420 MHz
within 1.4 ms, and then sits between 2180 and 2425 MHz -- the E-cluster
ceiling -- for the next fifty milliseconds, with only brief excursions to 3200.
Promotion to the P-cluster needs sustained demand.

`pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0)` does not help:
the main thread is already QoS 33, and setting it changes nothing.  Measured
both ways, the first fifty milliseconds look the same.

**The P-core ceiling on this part reads ~3500 MHz.**  Under sustained load the
clock climbs to 3448-3521 and stays, with occasional dips to 3000 when
something else runs.

So the harness does what a frequency lock would have done, in software:

- **witness** -- ten dependent `add`s per iteration.  Each has one-cycle
  latency and the chain is serial, so elapsed time is exactly
  `iterations * 10` core cycles: a direct clock reading, taken immediately
  after every operation batch.
- **gate** -- a batch counts only if its witness came within 2% of the fastest
  witness of the session.  `accepted` in the raw output reports how many
  survived; it runs 25-90%.
- **warm-up** -- time-driven, at least three seconds of load, until five
  consecutive witness readings sit at the ceiling.  A fixed iteration count is
  not enough, which is precisely what P82 got wrong.
- **order** -- the three operations round-robin inside the repeat loop, and the
  nine binaries round-robin across process invocations, so drift is charged
  equally to every candidate.

## Nothing on the timing path is floating point

Upstream's `CE/f1600.S` writes `v8-v15` without saving them, and so does
`poly_tobytes` in `asm/pack.s`; AAPCS64 makes the low 64 bits of that range
callee-saved.  A harness holding a timer there reads back `-inf`, which is what
the first version of this harness did on every `_ce` build.

P82 patched the upstream file to work around it.  This one does not: times and
the witness are `uint64_t` throughout, converted to double only at print, after
the last call.  The official trees are measured exactly as shipped.

## The Official being compared against matters

`ntruplus-ntt-Optimized/Additional_Implementation/aarch64` is not what SUPERCOP
ships.  Fetched from the Pi5 (`~/supercop-20260831/crypto_kem/ntruplus*/aarch64`),
the SUPERCOP revision differs by 203-235 lines in `poly.c` and 463-559 lines in
`ntt.s`; it carries `fqmul_precomp`, which hoists `y * QINV` out of repeated
products, where the vendored copy still has the older `fqmul_neon`/`fqinv_neon`.

Measured under this one harness, the SUPERCOP revision is the faster Official,
almost entirely in keygen:

| set | keygen | encaps | decaps |
|---|---:|---:|---:|
| 768 | -8.3% | -0.9% | -0.6% |
| 864 | -12.1% | -2.0% | -3.5% |
| 1152 | -8.5% | -1.0% | -0.8% |

Both are reported below so the choice is visible rather than buried.

## Shared randombytes

Every binary links the same deterministic xorshift `randombytes` (`rb.c`).  The
shipped one reads `/dev/urandom`, one syscall per call, and its variance swamps
the arithmetic.  `rb_urandom.c` is the control: switching to it adds the *same*
constant to both sides -- NTRU+768 keygen +2014 ns for Official and +2009 ns
for GT, encaps +1024 and +1016, decaps zero (decaps draws no randomness).  It
moves the percentages, because it moves the denominator, but not the ranking
and not the absolute differences.

## M2 Pro, ns per operation, min over gated rounds, 4-10 process invocations

| set | implementation | keygen | encaps | decaps |
|---|---|---:|---:|---:|
| 768 | Official (portable Keccak) | 4,488 | 5,160 | 3,871 |
| 768 | Official + CE (vendored rev) | 4,540 | 4,800 | 3,733 |
| 768 | **Official + CE (SUPERCOP rev)** | **4,162** | **4,757** | **3,706** |
| 768 | **GT** | **3,797** | **4,078** | **3,140** |
| 864 | Official (portable Keccak) | 4,906 | 5,990 | 4,605 |
| 864 | Official + CE (vendored rev) | 5,184 | 5,377 | 4,297 |
| 864 | **Official + CE (SUPERCOP rev)** | **4,550** | **5,267** | **4,145** |
| 864 | **GT** | **4,448** | **5,048** | **4,152** |
| 1152 | Official (portable Keccak) | 7,603 | 7,848 | 6,025 |
| 1152 | Official + CE (vendored rev) | 7,596 | 7,041 | 5,546 |
| 1152 | **Official + CE (SUPERCOP rev)** | **6,947** | **6,973** | **5,502** |
| 1152 | **GT** | **6,865** | **6,656** | **5,373** |

Against Official + CE at the SUPERCOP revision:

| set | keygen | encaps | decaps |
|---|---:|---:|---:|
| **768** | **-365 ns (-8.8%)** | **-679 ns (-14.3%)** | **-566 ns (-15.3%)** |
| **864** | **-102 ns (-2.2%)** | **-219 ns (-4.2%)** | +7 ns (+0.2%) |
| **1152** | **-82 ns (-1.2%)** | **-317 ns (-4.5%)** | **-129 ns (-2.3%)** |

## What this changes

P82 concluded "only NTRU+768 wins on M2", reporting 864 at +2.4/+0.6/+3.0% and
1152 at +4.6/+1.2/+2.0%.  That does not reproduce.  Measured against the same
vendored baseline P82 used, this harness puts GT ahead on all nine numbers; the
sign flip is the harness, not the baseline, because P82's entire timed run --
41 rounds of 300 operations, under a second in total -- happened while the
thread was still on an efficiency core, and each of its nine binaries ran as a
separate process that inherited a different scheduler and thermal state from
whatever ran before it.

The corrected picture is narrower than P82's but points the other way: GT is
ahead of the current Official everywhere except NTRU+864 decapsulation, which
is a tie at +7 ns.  768 keeps a clear margin, 8.8-15.3%; 864 and 1152 hold
1.2-4.5%.  The A76 results are untouched -- neither side has FEAT_SHA3 there,
and that measurement is `taskset`-pinned on a machine whose clock can be fixed.

## Reproducing

```
./build.sh <scratch>        # 9 binaries: {768,864,1152} x {portable, CE, GT}
./run.sh   <scratch> 6      # round-robin, 6 passes
python3 agg.py <scratch>/raw.txt
```

`build.sh` expects the SUPERCOP trees under `<scratch>/supercop/ntruplus*/aarch64`;
fetch them with

```
ssh pi@100.99.191.9 'cd ~/supercop-20260831/crypto_kem && \
  tar cz ntruplus768/aarch64 ntruplus864/aarch64 ntruplus1152/aarch64'
```
