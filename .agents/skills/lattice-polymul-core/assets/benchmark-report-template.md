# Benchmark Report Template

Use this template to report full-operation measurements. Do not compare isolated
subkernels unless the report clearly says so.

## Target and build

- Ring/operation:
- Platform:
- CPU/core:
- Compiler:
- Flags:
- Clock/cycle measurement method:
- Table location: RAM / flash / generated
- Input distribution:

## Implementations compared

| Implementation | Representation | Precomputation | Scratch/stack | Tables | Notes |
| --- | --- | --- | --- | --- | --- |
| A | | | | | |
| B | | | | | |

## Included work

- Input conversion:
- Forward transform/decomposition:
- Pointwise/base multiplication:
- Inverse transform/interpolation:
- Coefficient reconstruction:
- Target polynomial reduction:
- Output normalization:
- Caller matrix/vector work:

## Excluded or amortized work

- Excluded work:
- Amortized precomputation:
- Reason:

## Results

| Implementation | Cycles/time | Code size | Stack | Scratch RAM | Notes |
| --- | --- | --- | --- | --- | --- |
| A | | | | | |
| B | | | | | |

## Correctness and range status

- Reference implementation:
- Boundary tests:
- Randomized tests:
- Range proof:
- Constant-time review:

## Conclusion

- Selected implementation:
- Why:
- Preconditions:
- Risks:
