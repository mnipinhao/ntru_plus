# P11 — joint terminal Inverse-to-ternary DAG

P11 is complete and rejected. Production remains the P10 revision
`dd8c3146`, whose Decaps path uses P7-C1 Inverse and the promoted P8
raw-to-ternary consumer.

## Goal and frozen contract

The experiment asked whether the terminal six main NTT16 calls and tail could
stop scattering 864 halfwords to natural order, then rereading the output for
P8 conversion. The public contract remained unchanged:

- input: FR0 R-inverse leaves within the closed `abs <= 2497` KEM contract;
- output: 864 natural-order signed int16 values in `{-1,0,1}`;
- exact `out == in` alias support;
- 1,792-byte private scratch and complete scratch/vector cleanup;
- no secret-dependent branch/address, no new coefficient pass, no lane ST3.

The exact coordinate remains
`natural_index = 27*k + 3*row + component`. The P8 conversion remains
`x -> x + (-[x>1728]) - (-[x<-1728]) -> centered mod 3`; all 9,155 raw
values in `[-4577,4577]` were exhaustively checked.

## Candidate sequence

| Candidate | Change | Slothy / construction | Pi 5 component delta | Pi 5 Decaps delta | Instructions |
|---|---|---|---:|---:|---:|
| A0 | Six contiguous D streams; `LDR D + LDR X + INS`; full ST3; three tail ST1 lanes | 38 instructions, 36 modeled cycles, no spill | +339.843 | +352.150 | -1,161 |
| A1 | k-major six-D records; three LDR Q; reverse in-place route | 35 instructions, 35 modeled cycles, no spill | +123.992 | +120.475 | -1,259 |
| A2 | A1 plus `EXT` and full STR D for row 7 component 2 plus row 8, eliminating tail lane stores | 35 instructions, 31 modeled cycles, no spill | **+13.687** | +25.700 | -1,260 |
| A3 | Two-record joint Slothy schedule | 70 instructions, 47 modeled cycles, no spill | +45.594 | +56.900 | -1,292 |
| A4 | Pure-unfold two unchanged A2 physical bodies; one branch per two records | exact A2 physical schedule duplicated | +20.774 | **+13.175** | -1,292 |

All deltas are candidate minus the paired P10 baseline. A2 is the best exact
component candidate. Its paired-sample component delta is +17.485 cycles with
IQR `[+15.961,+18.422]`; its Decaps paired delta is +33.600 with IQR
`[+22.450,+41.137]`. The rejection is therefore not a summary-median accident.
A4's component paired delta is likewise positive: +19.265 cycles, IQR
`[+18.547,+20.657]`.

## Register and memory findings

The first A1 attempt exposed an important private-ABI rule. `lazy_i16` still
reads its 256-byte input bank through `x1`; repurposing `x1` as a k-major
output pointer corrupts the transform input. Keeping `x1` and writing records
through the now-free `x0` is necessary.

Writing k-major records into the 1,536-byte transform scratch also corrupts
future NTT16 banks. The correct no-extra-scratch construction uses the public
output buffer only after all original input coefficients have been consumed,
then routes from `k=31` down to zero. For every k, natural output bytes
`[54k,54k+53]` are disjoint from every lower unread record
`[48j,48j+47]`, `j<k`; the tail remains at private scratch offset 1,536.

A2 avoids lane-store economics without out-of-bounds writes. After ternary
conversion, `EXT #14` forms the low D lanes
`[component2.row7, tail.component0, tail.component1, tail.component2]`.
A full STR D at output offset 46 overlaps the final two ST3 bytes with the same
value and writes the six tail bytes exactly. No byte outside the polynomial is
touched.

## Why P11 loses despite fewer instructions

The old scalar `UMOV + STRH` scatters are interleaved with six large NTT16
kernels, so much of their apparent instruction cost is hidden by existing
arithmetic and store issue opportunities. P11 removes them, but then creates a
serial post-transform routing boundary containing four loads, conversion,
full ST3/STR D, and pointer work. The 1,260-instruction retirement saving does
not compensate for this new critical memory/store boundary on Cortex-A76.

A3 is also a target-model warning: joint Slothy scheduling predicted 23.5
cycles per record, yet Pi 5 was slower than the sequential A2 schedule. The
A76 model is useful for allocation and local ordering, but cross-record memory
overlap in this region must be accepted only through physical timing.

The initial A0 needed a run-local `vins_d` A76 timing entry because the primary
Slothy checkout parses GPR-to-D INS but does not model it, and it does not parse
the desired D-lane LD1 form. A1 and later remove both instructions entirely;
the final rejection is therefore not caused by that temporary model extension.

## Validation and decision

Mac A0 and Pi candidates passed exact output/alias, AAPCS and scratch wipe.
Both baseline and each timed candidate passed 64 KEM round trips, tampered
ciphertext rejection, 100-case KAT, and an identical 417,216-byte malformed
ciphertext transcript. KAT SHA-256 is
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`;
malformed transcript SHA-256 is
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

Measurements used Pi 5 core 3, six alternating AB/BA processes, GCC 14.2,
ondemand governor, no throttling, and the selected SUPERCOP root
`/home/pi/supercop-20260831`. Official was not rerun in this campaign and its
independent upstream-latest status remains unverified. Against the prior
consistent Official `Inverse + Crepmod3` checkpoint near 4,620 cycles, even A2
remains roughly 814 cycles slower.

P11 is not promoted. Reopen only with a terminal producer that naturally emits
full natural-order vectors, or a new same-boundary DAG with enough modeled and
microbenchmarked margin to overcome the measured routing boundary. Instruction
count reduction, lane-store replacement, or unrolling alone is insufficient.
