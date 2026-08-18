# GT32 twiddle-major SIMD gate

Experiment: `GT32-TWIDDLE-MAJOR-SIMD-001`

This directory is an isolated, generator-only study.  It does not modify GT
Clean, its symbols, build files, selector, or production constant tables.

## Question

Can four independent DFT3 instances share one compact QINV/factor YMM by
changing the data layout from

```text
R_i = [qword0 degree0..3 | ... | qword3 degree0..3]
```

to

```text
T_k[4*i+j] = R_i[4*j+k]?
```

For each DFT3 role, four expanded factor vectors then become one compact
vector.  The same compact vector is reused by four register-register
multiplies; no broadcast or runtime factor expansion is required.

## Exact result

The generator parses the selected GT Clean `wide_twist_qinv` and
`wide_twist_factor` tables.  It proves the lane mapping for every active factor
and every data lane, including the inverse mapping back to the current ABI.

Per Forward:

| Item | Current | Four-way compact |
|---|---:|---:|
| Active QINV/factor table bytes | 3072 | 768 |
| QINV/factor memory operands or explicit loads | 96 | 24 |
| Montgomery vector multiplies | unchanged | unchanged |

The table and load reduction is real.  It is not sufficient with the current
producer and consumer, however.

The lowest known constructive mapping for one four-register role uses 16
shuffle instructions:

```text
4 vpshufb
4 vpermd
4 vpunpck{l,h}qdq
4 vperm2i128
```

This is optimistic accounting: `VPERMD` additionally needs an index vector.
Keeping that index resident raises register pressure; reloading it adds more
instructions.  The static stop below therefore does not depend on charging the
index setup cost.

There are twelve role batches per Forward.  Keeping the current producer costs
192 input-transpose instructions.  Returning all three DFT3 output rows to the
current ABI costs another 192.  The 24 explicit compact-constant loads bring
the current-ABI candidate to at least 408 extra retired instructions in this
known schedule.

## Decision

```text
current producer -> compact twist -> current consumer:
    hard stop before assembly

current producer -> persistent twiddle-major consumer:
    hard stop; input formation remains too expensive

producer-native -> persistent twiddle-major consumer:
    open only after a register-liveness and full-consumer proof
```

The proposal is therefore not rejected algebraically.  It is rejected as a
post-hoc transpose.  It may reopen only if the frontend directly produces the
same-role packets, NTT32 and terminal consumers retain them without global
repair, peak live YMM is at most 15 with no spills/materialization, and the
caller-weighted model predicts at least 20 core-cycle saving.

## Reproduce

From the production NTRU+768 directory:

```sh
python3 experiments/gt32_twiddle_major_simd_001/tools/generate_gate.py \
  --ntt ntt.s \
  --output experiments/gt32_twiddle_major_simd_001/generated/twiddle_major_gate.json
```

The generated JSON is the exact table manifest, mapping proof, and static cost
ledger.  No assembly symbol is emitted by this gate.

`make check` regenerates the file independently and requires byte-for-byte
determinism.
