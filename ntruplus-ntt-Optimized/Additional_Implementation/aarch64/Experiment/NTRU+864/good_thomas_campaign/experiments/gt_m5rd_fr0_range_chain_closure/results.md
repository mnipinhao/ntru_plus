# Results

Status: **PASS — current M5R-D FR-0 range chain is closed.**

- Actual Algorithm-10 NTT16 maximum: `9342`.
- Actual M5R-D one-product Forward maximum and FR-0 operand bound: `25569`;
  output union `[-25569,25566]`; zero unsafe int16 nodes.
- M5C maximum signed-int32 accumulator: `1961321283`, leaving `186162364`
  below `INT32_MAX`.
- M5C R0 output bounds: BaseMul `2148`, BaseMulAdd `2205`.
- M5D reference inverse rerun at `[-2205,2205]`: maximum lazy halfword
  `19845`, final bound `3696`, all checks pass.
- M5E-r1 inverse rerun at `[-2205,2205]`: maximum lazy halfword `17220`,
  final bound `6888`, all checks pass.
- M5E exhaustive fixed-product proof: 270 constants x 65,536 signed inputs =
  17,694,720 checks; maximum output `3444`; zero failures.
- Actual linked M5R-D + M5C + M5E test: 18 complete products and five
  BaseMulAdd products against schoolbook; zero coefficient mismatches.
- M5E new-bound test: 49 boundary/impulse/random cases, zero pass-1/pass-2
  modulo-q mismatches and zero tail-padding writes.

No assembly arithmetic, coefficient-memory boundary, Production source, cycle
measurement, or SUPERCOP package changed.
