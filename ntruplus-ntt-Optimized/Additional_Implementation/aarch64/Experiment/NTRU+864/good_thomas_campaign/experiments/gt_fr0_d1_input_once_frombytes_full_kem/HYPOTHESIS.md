# D1-P3B12 full-caller FromBytes hypothesis

Observation: P3B11 input-once FromBytes is byte-correct and saves 245.373
cycles per isolated call versus P3B4 C1.  The exact KEM ledger calls FromBytes
zero times in Keypair, once in Encaps, and three times in Decaps.

Primary bottleneck category: layout/permutation boundary integration.

Hypothesis: replacing only C1 FromBytes with P3B11 preserves all KEM bytes and
failure behavior, leaves Keypair unchanged within noise, and saves approximately
245 cycles in Encaps and 736 cycles in Decaps.

Exact proposed change: build Official, frozen P3B4 selected bytes, and P3B4 plus
P3B11 FromBytes in one binary.  Both GT variants retain the same M5R-D Forward,
D1 BaseMul, M5E Inverse and R9 ToBytes objects.

Expected static effect: candidate Encaps retires 1458 fewer instructions and
24 fewer branches; candidate Decaps retires 4374 fewer instructions and 72
fewer branches.  Keypair objects and call graph are identical.

Expected performance effect: candidate beats P3B4 in Encaps and Decaps in all
repetitions, with measured savings close to the exact call ledger.

Expected register-pressure effect: no interprocedural change; P3B11 remains a
separate no-spill boundary call.

Correctness or range impact: none.  Valid and tampered KEM cases must be byte-
identical across all three variants.

Falsifying measurement: any correctness mismatch, wrong linked symbol, Keypair
instruction-count change, Encaps/Decaps instruction delta not equal to the call
ledger, or a non-winning cycle repetition.
