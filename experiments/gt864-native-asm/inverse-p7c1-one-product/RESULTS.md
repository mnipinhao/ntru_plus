# P7-C1 — one-product inverse NTT9 (promoted)

## Result

Fixed baseline: P7-B1 production at parent `7d2ea7d7`.
Only inverse9 changes; terminal constants, lazy I16/tail, centered output,
public wrapper, BaseMul and all KEM/bytes code remain unchanged.

| Same-boundary Pi 5 metric | P7-B1 | P7-C1 | Paired median delta |
|---|---:|---:|---:|
| Complete Inverse cycles | 6995.484 | 5728.891 | -1266.281 |
| Complete Inverse instructions | 10511.125 | 9311.125 | -1200 |
| Decaps cycles | 43386.675 | 42104.900 | -1284.675 |
| Keygen cycles | 46397.125 | 46397.000 | -1.250 |
| Encaps cycles | 45775.625 | 45752.400 | -14.400 |

Inverse improves about 18.1%; Decaps about 3.0%. Keygen/Encaps instruction
counts are identical and their paired-cycle interquartile intervals include
zero, so no improvement is claimed for them. Branch counts do not change.
Raw data: `evidence/run0.csv` through `run5.csv`; `results.json` includes paired
quartiles. Harness labels `p3a`/`p3b` mean P7-B1/P7-C1, not old P3 sources.

## Exact DAG and layout

For every B3, replace four fixed multiplications by one:

```
d = b-c; t = Algorithm10(d,722)
y0 = (a+b)+c
y1 = (a-c)+t
y2 = (a-b)-t
```

First-level triples: (0,3,6), (1,4,7), (8,2,5). Preserve four eta
multiplications. Second-level triples: (0,1,8), (3,4,2), (6,7,5).
Terminal logical order remains [0,3,7,1,4,5,8,2,6], with the same nine
terminal pair loads/mulmods and the same P8 main/tail addresses.

The six nodes save 18 mulmods/block: 37→19. Core arithmetic saves 48
instructions/block; shorter constant/temporary lifetimes save another 52
non-arithmetic instructions. Total 284→184 body instructions, with one RET
outside the scheduled region. Twelve calls yield -1200 instructions/Inverse.
Object text is 1140→740 bytes. Nine coefficient Q loads, eighteen terminal
constant Q loads, sixteen main D stores and eight tail H stores are retained.
No new memory boundary or spills. No secret-dependent branches/addresses.

`candidate.sym.S` is the readable source of truth; `generate.py` describes
each value, and `candidate.clean.S` is the tested physical schedule. GPR
arguments x0..x3 have the contract meanings; Slothy can allocate scratch
x4..x17 and v0..v31. Public callee-save preservation remains in the wrapper.

## Proof and correctness

- P7-C0 exact one-product model remains authoritative. Physical scheduled
  arithmetic matches all 288 terminal linear maps AND interval endpoints.
- Closed chain: I9 internal 22473 → output 2617 → I16 peak 21397 → raw
  output 4577 → centered 1728. Scale stays R^-1 through I9, then existing
  inverse terminal normalization restores R0. Last I16 identity reset stays.
- Existing representatives need not match inside I9; final centered output
  is exact. Local native tests cover 256 inputs and 256 BaseMul R^-1 chains,
  alias, canaries, AAPCS and 1792-byte scratch wipe.
- Regression: BaseInv 808 cases; 64 KEM round trips/tampered rejection; Mac
  and Pi5 100-case KAT digest:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Each of six PMU processes independently checks 24 byte-exact KEM cases,
  24 tampered ciphertexts, 256 exact centered inverses and 256 aliases.
- No new full malformed-ciphertext exhaustive campaign: decoder/rejection
  code is unchanged; this round runs the above differential rejection gates.
- Mac full-package fixture needs a test-only alias for the pre-existing
  `binv_num_pair` symbol omission. That shim is not in Linux or production.
- P7-C0 physical arithmetic reader now tolerates scheduled early stores;
  native exact-output tests, not that arithmetic reader, validate routing.

## Slothy and benchmark provenance

Slothy `/Users/chenpinhao/slothy`; Python
`/Users/chenpinhao/slothy_and_ra/.venv/bin/python`. RA only then timing with
fixed allocation, eight-way small windows, 30-second timeout, no spills.
RA 4.36 s, timing 14.68 s; selfcheck passes. Unicorn selftest is disabled;
real Apple/Pi native execution is the correctness gate. Header expected cycles
71→46 are model metadata, not measured full-kernel latency; whole-region
performance estimation is disabled in the split pass.

Pi5 `pi@100.99.191.9`, isolated directory
`/home/pi/ntruplus-p7c1-20260912-7d2ea7d7`; GCC 14.2.0, core3, ondemand,
post-run 58.2 C, throttled=0x0. Six processes alternate AB/BA, 366 paired
Inverse samples and 186 per KEM. User-space perf cycles/instructions/branches;
same wrapper, warmup and boundary; no empty correction. Official not run.
Selected Official remains SUPERCOP 20260831 aarch64, not independently
verified as latest upstream. Do not compare this run as if it were paired
with the historical Official 4118-cycle inverse checkpoint.

Source SHA256 (baseline/candidate):
`29be0511f5908964bb79720385c092c54bebefcbb82a08961599735e9c46180a` /
`785b5cadc139a25e029e7b1ddfeafc20ee51b70b95c4d42b8fe7075ca29eeea9`.
Linux inverse9 object SHA256:
`b88e0408e3144cba29031e2e06a25fd51b89ea15bc5fc8f344c8beeab201373f` /
`38dc199781a3c2714515755c3cd5296bfd1770b5e6e580529036746efd0a5841`.

## Reproduce and next gate

Run generate.py, optimize.py, optimize.py --timing, prepare.py, verify.py;
Slothy commands require PYTHONPATH=/Users/chenpinhao/slothy and its venv.
Freeze baseline from parent revision, not the now-promoted production tree.
`prepare.py` pins it to `7d2ea7d7`. Re-run the full historical algebra gate
with `python3 ../inverse-p7c0-range/audit.py --source-dir build/baseline`.
Build both source packages on Pi using `make -j4 all test kat`, compile the
paired harness with `gcc -O3 -rdynamic -Icandidate bench.c -ldl -o bench`,
then `taskset -c 3 ./bench baseline/libgt864.so candidate/libgt864.so 0`
and reversed order 1. `summarize.py` reads build/pi5/run*.csv.

Next P8: raw-Inverse-to-ternary. Start from the new proven raw bound 4577,
prove exact equivalence to center864 + crepmod3 before removing either pass.
P9 ToBytes routing search and P10 BaseInv redesign remain queued.
