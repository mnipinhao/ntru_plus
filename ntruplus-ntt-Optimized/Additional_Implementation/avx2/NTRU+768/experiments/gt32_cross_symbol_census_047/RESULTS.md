# GT32 Cross-Symbol Shared-Code Census 047

## Frozen input

- ELF: GT Clean `measure-A` from experiment 046.
- SHA-256: `659ebd7615e639cbc701c0f82a03268091781af9707e803e15f1bf3a9d569329`.
- Full ELF `.text`: 64,432 bytes.
- Selected GT arithmetic/codec symbols inspected: 33,836 bytes.
- GT Clean production sources were not modified.

## Inventory

| Family / symbol | Bytes | Instructions | Existing sharing |
|---|---:|---:|---|
| inverse tail | 5,578 | 1,006 | one Decap consumer |
| M lazy Q24 | 5,120 | 1,350 | shared typed entry body |
| P SP1 lazy Q24 | 4,364 | 738 | Keypair-specific |
| NTT frontend | 3,917 | 685 | shared K/E/D |
| M centered Q24 | 3,815 | 628 | Decap recovered-r |
| M unpack body | 3,470 | 588 | Decode1/Decode3 shared body |
| batch inverse | 1,787 | 347 | BaseInv helper |
| NTT M / P | 1,056 / 1,046 | 194 / 192 | endpoint-specialized |
| inverse core | 948 | 170 | one Decap consumer |
| BaseInv J1 | 923 | 202 | Keypair-specific |
| B3 general / scale / F0-J1 | 684 / 573 / 555 | 141 / 121 / 118 | macro family |

## Duplicate census

### Level 0: byte-identical basic blocks

No cross-symbol cluster was found at the minimum threshold of 16 bytes and
three instructions.

\[
\boxed{\text{direct byte-identical shareable code}=0\text{ B}}
\]

### Level 1: relocation/constant normalized basic blocks

Only two clusters survive:

- 32-byte B3 prologue shared in scale/general/F0-J1: 64 gross duplicate bytes;
- 32-byte NTT M/P prologue: 32 gross duplicate bytes.

Total gross upper bound is 96 bytes before wrappers, jumps, alignment, or ABI
repayment.  This is far below the 1 KiB continuation threshold.

### Larger contiguous normalized matches

These are real code-family similarities, but not direct outlining wins.

| Family | Largest match | Why it is not zero-repayment sharing |
|---|---:|---|
| B3 scale/general | 509 B / 108 instructions | common arithmetic sits inside the 12-block loop while finalizers/contracts differ; sharing needs repeated tail dispatch or a mode branch |
| B3 scale/F0-J1 | 439 B / 95 instructions | same issue plus different scale/output ABI |
| NTT M/P | 381 B and 342 B regions | different physical endpoint schedules split the common stages; sharing needs entry/exit repair or mode-dependent stores |
| centered/lazy M-Q24 | ten 140 B packet patterns | not one common contiguous core; outlining creates a call/dispatch for each packet group and reproduces the 038 compaction trade |
| M-lazy/P-SP1 Q24 | 71 B | too small and different layout routing dominates |

The repeated Q24 matches must not be summed as a free 1.4 KiB saving.  They are
ten dynamic occurrences of a packet pattern.  Turning them into one shared
subroutine changes execution by adding repeated calls/branches and pointer
state; experiment 038 already showed this compact-loop shape is slower.

### Level 2: register-shape heuristic

Register-erased matching adds candidates, including 509-byte B3 and several
inverse/NTT fragments.  None supplies a move-free common register ABI.  These
matches are classified as semantic similarity only and are not counted as
shareable bytes.

## Final accounting

```text
selected GT code                         33,836 B
byte-identical cross-symbol blocks            0 B
relocation-normalized gross duplicates       96 B
large zero-repayment shared core               none
ABI/control-flow repayment candidates     present, rejected
```

The proposed 1–3 KiB unchanged-DAG shared core does not exist in the selected
image under the current ABIs.  GT Clean already shares the important reusable
bodies; the remaining apparent duplication is specialization embedded inside
hot loops or packet schedules.

## Decision

Close cross-symbol outlining for the current image.  Do not write shared-Q24,
shared-B3, or shared-NTT ASM based on this census.  Reopen only if a future ABI
creates a fall-through/tail-entry shared core with no additional dynamic
branch, register move, spill, or endpoint repair and at least 1 KiB net text
saving.
