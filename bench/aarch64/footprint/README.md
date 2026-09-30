# Code size, executed code and cold start

This tool produces the package READMEs' "Code size" paragraph.  It compares GT
with the official `NO_CE` build (GitHub main's, from `../../official/`) on the
Raspberry Pi 5 with gcc.

## What it measures

- **Linked KEM text.**  A program calls the three entry points and is linked
  with gc-sections.  Subtract the text of the same program against empty entry
  points (`size_main.c`).
- **Executed code per operation.**  Count the distinct instruction addresses
  of the measured program that callgrind sees inside the entry point
  (`footprint.c`, `footprint.py`), times 4 bytes.  The C library's code
  (`memcpy`, `memset`, `malloc`, `free`) is counted apart: 0.2-0.7 KB an
  operation, except 3.0 KB for NTRU+1152's GT key generation, whose retries
  hash through the SHAKE API that allocates its state.  The dynamic loader's
  code, which binds the library calls on their first use, is left out.
- **Fully cold operations.**  Before every operation, read 32 MiB and execute
  96 KiB of distinct instructions (`icache_thrash.S`).  Reseed the RNG so every
  run sees the same inputs, and count cycles with the PMU (`perf_counter.c`).
  - Each process prints the medians of 61 runs per operation.
  - Twelve process pairs per set run on one core, alternating which side goes
    first.
  - A figure is the median over the processes.

In steady state every operation of every set fits the 64 KB L1I, so size costs
nothing there.  The cold figures bound what it costs when nothing is cached.
They move by 1-2% between runs of the pairs, so compare GT and the official
build only within a run.  Pooling two runs of pairs gives firmer figures.

## Run

On the Pi 5, with valgrind and user-space access to the cycle counter:

```sh
../../official/setup.sh /tmp/official ~/supercop-20260831
./build.sh /tmp/official /tmp/footprint
./run.sh /tmp/footprint > footprint_pi.txt
./summary.py footprint_pi.txt
```

`run.sh BIN PAIRS CORE` changes the twelve pairs and core 3.
`summary.py` pools several outputs; give it more than one to pool runs.

## Results

On the Pi 5: the code size on 2026-09-30, the cold start on 2026-09-28 (two
runs of the twelve pairs pooled); the package READMEs carry these figures.
Between the two dates, clearing the SHAKE state added 56 B of linked text to
NTRU+864 and NTRU+1152, and removing an unused function took 128 B from
NTRU+864.

| | linked text | executed: keygen / encaps / decaps | cold: GT against official (GT faster in, of 24) |
|---|---:|---|---|
| NTRU+768 | 88,682 B (official 19,174) | 44.6 / 22.4 / 25.0 KB | +8.2 / -3.8 / -0.2% (0 / 23 / 13) |
| NTRU+864 | 48,185 B (official 22,806) | 25.1 / 21.6 / 31.3 KB | -7.5 / -15.8 / -5.8% (24 / 24 / 24) |
| NTRU+1152 | 49,693 B (official 20,854) | 27.8 / 23.1 / 29.0 KB | -1.6 / -12.3 / -2.1% (20 / 24 / 18) |
