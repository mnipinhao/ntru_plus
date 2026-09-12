# P13-B — fused terminal scale + top CRT (promoted)

## Decision

P13-B is promoted for the six main `lazy_i16` calls.  The existing packed lane
shape is `[top0 row0..3 | top1 row0..3]`.  Instead of first scaling both halves
and then applying two CRT multiplications, the candidate directly evaluates the
two rows of the scaled CRT matrix.

For pre-terminal values `A,B`, scale constants `sa,sb`, `c=-1634` and
`d=-722`, the old equations are `h=c(sb B-sa A)` and `l=sa A-dh`.  The new
public table stores the four composite coefficients

```
low  = ((1+dc)sa) A + (-dc sb) B
high = (-c sa) A  + ( c sb) B.
```

One Algorithm-10 vector product supplies both A/B contributions in different
halves; `EXT #8` plus `ADD` combines them.  Thus each column uses two general
mulmods rather than three.  To preserve P8's existing raw-output contract, a
two-instruction `b=1` reset is retained for low columns 0/12 and high columns
0/2/8/10.  Conservative interval closure gives 5278 before those resets and
4454 after them, below the existing 4577 boundary.  Scale remains I9 R^-1 to
natural R0; output order and memory stores are unchanged.

## Static and Slothy result

| Per main call | Baseline | P13-B | Delta |
|---|---:|---:|---:|
| Instructions | 733 | 667 | -66 |
| MUL | 65 | 49 | -16 |
| SQRDMULH / MLS | 66 / 66 | 56 / 56 | -10 / -10 |
| LDR | 54 | 86 | +32 |
| MOV / DUP | 33 / 33 | 2 / 2 | -31 / -31 |
| Expected cycles | 184 | 166 | -18 |

The six calls therefore remove 396 retired instructions.  Slothy root is
`/Users/chenpinhao/slothy`; the local external venv interpreter is recorded in
`slothy-result.json`.  Functional RA completed OPTIMAL in 73.077 seconds with
no spill and DFG self-check OK.  Fixed-allocation small-window timing also
self-checks and produces the 166-cycle model.  The generic log parser falsely
labels configured timeout text as failure; the audited solver/output record is
kept separately and no failed artifact was tested.

## Correctness and Pi 5 timing

- 144 exact row/column range contexts and 8,909 P8 raw inputs are exhausted.
- Symbolic baseline/candidate comparison passes 544 main/tail cases with the
  same store addresses and exact residues modulo 3457.
- Pi candidate passes `test_kem`, 100-case KAT digest
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`,
  the 417,216-byte malformed transcript digest
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`,
  and 4,096 exact/alias/AAPCS/scratch-wipe inverse cases.

| Pi 5 boundary | P13-A | P13-B | Independent median delta |
|---|---:|---:|---:|
| Inverse-to-ternary | 5392.734 | 4966.508 | -426.227 cycles |
| Complete Decaps | 40889.425 | 40453.625 | -435.800 cycles |

Paired medians are -428.938 cycles for Inverse-to-ternary, IQR
[-430.266,-426.937] over 366 pairs, and -434.350 cycles for Decaps, IQR
[-443.125,-426.150] over 186 pairs.  Both boundaries retire exactly 396 fewer
instructions and the same branches.  Keygen/Encaps instructions are unchanged;
their cycle IQRs include zero, so no benefit is claimed there.  Pi 5 Cortex-A76
core3, GCC14.2, ondemand governor, 64.2 C, `throttled=0x0`.

The production payload is the tested candidate: the composite table is
byte-identical, the assembly body is the allocated/scheduled output with only
its public label/header adapted, and `gt864_native.c` selects that table for
both Inverse entry points.  The selected Official root remains
`/home/pi/supercop-20260831`; this was a paired P13-A/P13-B experiment, not a
fresh Official run.

## Next

P13-C should separately test the already-proved three-row tail variant; it is
only one call and must earn its own Pi result.  P14 remains the larger queued
target: reduce the aggregate full+small ToBytes routing/normalization boundary.
