# SUPERCOP 20260831 on the Raspberry Pi 5

This tool produces the package READMEs' SUPERCOP tables: GT's SUPERCOP leaf
against SUPERCOP's own `crypto_kem/ntruplus<set>/aarch64`, measured by
SUPERCOP's unmodified `do-part` / `measure-anything.c` on one core.

## What it does

`run.py setup` stages a small SUPERCOP tree from an installed one.  The tree
holds SUPERCOP's scripts, the ChaCha20 stream and RNG its KEM measurement
draws from, and, for each set, these variants:

| variant | leaf |
|---|---|
| `official` | SUPERCOP's leaf, as shipped |
| `official-nogoals` | the same without its `goal-constbranch` / `goal-constindex` files |
| `gt` | this repository's package, after `make check` on a fresh copy, exported by the package's `scripts/export_supercop.py` |

The default is `official` and `gt`.  Both leaves then declare both goals, so
SUPERCOP builds and measures them in the same security category
(`constbranchindex`).  The category selects only an include path and whether
TIMECOP runs; `official-nogoals` shows that it does not change the cycles.

`run.py measure` runs rounds (six by default).  A round measures every variant
of every set once, in an order that rotates from round to round.  Only the
variant being measured is enabled, because SUPERCOP skips sticky
implementation directories.  Each round's SUPERCOP data file is kept under
`WORK/runs/`.  Throttling and temperature (`vcgencmd`) are recorded before and
after each measurement.

`run.py tables` prints, per set and variant:

- the median over the rounds of SUPERCOP's median;
- the mean over all samples.  Key generation retries rejected candidates (29%
  of them for NTRU+1152), so its distribution is multimodal, and NTRU+1152's
  README reports this mean.
- GT against each official variant, with how many rounds GT was faster.

## Run

On the Pi 5, with a SUPERCOP 20260831 tree already initialised on the host
(`./do-part init` in it once):

```sh
./run.py setup ~/supercop-20260831 /tmp/supercop-work
./run.py measure /tmp/supercop-work
./run.py tables /tmp/supercop-work
```

Setup takes about a minute.  Each measurement (one set, one variant) takes
about nine seconds, so six rounds of the three sets with two variants take
about six minutes.  Keep the machine otherwise idle, and check the recorded
`throttled` values.

## Reproducibility

On 2026-09-28, six rounds of all three sets with the variants `official`,
`official-nogoals` and `gt`:

- The goal files make no difference to the cycles.  `official` and
  `official-nogoals` agree within 0.07% on every median of NTRU+768 and
  NTRU+864, and on NTRU+1152's encapsulation and decapsulation.  NTRU+1152's
  key generation differs by 3.7% in the median and 1.4% in the mean, which is
  its retry noise: SUPERCOP draws fresh candidates in every measurement.
- The NTRU+768 and NTRU+864 figures in the package READMEs were reproduced
  within 0.11%, except GT's NTRU+768 key-generation median, which came out
  0.26% lower.

The NTRU+1152 figures in its README come from this tool's run on 2026-09-30.
