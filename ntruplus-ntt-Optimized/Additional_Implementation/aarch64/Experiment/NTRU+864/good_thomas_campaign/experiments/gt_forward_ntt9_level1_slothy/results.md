# Results

The M5H hard gate passes:

- 45 real instructions implementing three independent two-product B3s;
- maximum exact level-1 magnitude 16816 and zero unsafe signed-halfword nodes;
- remote Slothy 0.2.2 result OPTIMAL, 48 expected N1-proxy cycles, IPC 0.94,
  and 36 minimum stalls;
- exact emitted register set `v0-v7,v25-v31`, all fifteen allowed registers;
- zero use of reserved `v8-v24`;
- zero memory, GPR, branch, stack, or spill instructions;
- Slothy selfcheck and local AArch64 assembly pass;
- optimized SHA-256
  `191b4053e4efc7f0ccb58827f47e0d3a8f38734f05629f0cb9ae1b00776eb8ff`;
- log SHA-256
  `4afb25d6fcc30547cde57b69239f326849e2b343a49b051a0afa2eaa9796a046`.

For this solver result, the boundary mapping is:

| Role | Register | Role | Register |
| --- | --- | --- | --- |
| input `f0` | `v7` | output `a0` | `v27` |
| input `f1` | `v26` | output `a1` | `v3` |
| input `f2` | `v1` | output `a2` | `v2` |
| input `f3` | `v3` | output `b0` | `v5` |
| input `f4` | `v4` | output `b1` | `v25` |
| input `f5` | `v29` | output `b2` | `v28` |
| input `f6` | `v25` | output `c0` | `v31` |
| input `f7` | `v6` | output `c1` | `v30` |
| input `f8` | `v31` | output `c2` | `v4` |
| input `roots` | `v2` | input `modq` | `v0` |

The mapping is evidence for this returned allocation, not a stable ABI. In
particular, roots and modulus registers are reused after their final reads.
The 48-cycle solver estimate is lower than three isolated 24-cycle M5G
schedules because independent B3 multiplication latency overlaps; it is not a
Pi 5 timing claim.

The Neon feature and secret-independent scanners report zero warnings. The
pattern scanner reports the expected 18 `sqrdmulh` observations across the
symbolic and returned files; their signed fixed-Barrett bounds are discharged
by `prove_level1.py`, not by the scanner.
