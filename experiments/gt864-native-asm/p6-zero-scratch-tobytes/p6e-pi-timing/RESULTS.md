# P6-E — Pi 5 complete-ToBytes timing

## Decision

**Reject P6-D3 for production.**  The zero-coefficient-scratch architecture is
correct and removes substantial write traffic, but it is slower than the frozen
production serializer at the exact public full and small ToBytes boundaries.
Production remains unchanged and no full-KEM benchmark is warranted for this
candidate.

Before timing, P6-D3 was corrected to match production's public cleanup policy:
all `v0-v31` are cleared before restoring the low halves of `v8-v15`.  The
candidate therefore does not win or lose because cleanup was omitted.

## Method

- Host: Raspberry Pi 5 Cortex-A76, CPU 3, Linux 6.18.33.
- Workspace: `/home/pi/supercop-20260831/bench/pinhao/gt864-p6e-20260910`.
- Toolchain: GCC 14.2.0 `-O3`.
- Governor: `ondemand`; temperature 62 C; `get_throttled=0x0`.
- Boundary: one public 1,296-byte serializer call from an aligned 864-int16
  input to an aligned output buffer.
- 128 calls per PMU sample, 74 samples per implementation and mode, two reverse
  runs, with order alternating inside each run.
- PMU group: cycles, retired instructions, retired branches, A76
  `MEM_ACCESS_RD` (`0x66`) and `MEM_ACCESS_WR` (`0x67`).
- Each of the four benchmark processes first passed 513 differential cases and
  output canaries.  Full uses unrestricted signed int16 inputs; small uses only
  values strictly in `(-3457,3457)`.

The first two remote attempts produced no measurements: the first exposed the
production shared object's caller-provided `randombytes` import; the second
exposed the host's concrete `armv8_cortex_a76` PMU device name.  Both were fixed
in the harness before the recorded run.

## Measured medians

| Mode | Implementation | Cycles | Instructions | Branches | PMU reads | PMU writes | IPC |
|---|---|---:|---:|---:|---:|---:|---:|
| Full | production | 1766.734 | 3245.156 | 66.031 | 552.023 | 200.094 | 1.837 |
| Full | P6-D3 | 2268.457 | 4074.156 | 3.031 | 653.023 | 95.094 | 1.796 |
| Small | production | 1363.399 | 3010.156 | 59.031 | 552.023 | 200.102 | 2.208 |
| Small | P6-D3 | 2268.223 | 4074.156 | 3.031 | 653.023 | 95.094 | 1.796 |

Difference of medians:

| Mode | Cycle delta | Instruction delta | Read delta | Write delta |
|---|---:|---:|---:|---:|
| Full | +501.723 (+28.40%) | +829 (+25.55%) | +101 | -105 |
| Small | +904.825 (+66.37%) | +1064 (+35.35%) | +101 | -105 |

The paired-cycle conclusion is stronger than the difference of independent
medians: all 74 full samples regress, with paired median `+501.660` cycles and
p10--p90 `+501.270..+514.681`; all 74 small samples also regress, with paired
median `+911.192` and p10--p90 `+898.169..+913.171`.

## Interpretation

The experiment falsifies the assumption that removing the 432-byte scratch
boundary is sufficient.  P6-D3 successfully removes about 105 write events and
56--63 branches, but its repeated route/index construction adds about 101 read
events and 829 full-path instructions.  Its lower IPC shows that the larger DAG
also does not hide those extra dependencies on Cortex-A76.

A small-only conditional-add specialization would remove the extra Barrett
work, but it cannot rescue the already-failed full architecture.  Even after
removing that arithmetic, the route/table DAG remains materially larger than
production small.  Do not spend another round specializing P6-D3-small unless a
new route construction first removes the full-path instruction/read deficit.

The ToBytes reopen gate is therefore structural, not another scratch-storage
experiment:

1. Find a smaller `FR0 coordinate -> wire byte` permutation network.
2. Jointly consume normalization, 12-bit packing and routing without forming
   nine complete routed rows.
3. Reduce TBL2/TBL3 and their index loads, rather than merely retaining values
   in registers.
4. Keep separate full/small DAGs; small must contain no full Barrett steps.
5. Beat frozen P5 statically by at least roughly 829 instructions and 101 reads
   before Slothy, then return to the same Pi 5 boundary.

Current priority is `Inverse CT feasibility`, then the existing
`raw-Inverse-to-ternary` gate, then this new ToBytes routing search.

## Reproduction artifacts

- `bench.c`: linked-symbol correctness and in-process grouped-PMU harness.
- `pi_run.py`: isolated production/candidate build and balanced run.
- `p6e-results.json`: medians, deltas, environment and SHA-256 identities.
- `p6e-dispersion.json`: paired delta and MAD/percentile audit.
- `summarize_dispersion.py`: raw-sample summarizer; raw CSV/build files remain
  gitignored.
