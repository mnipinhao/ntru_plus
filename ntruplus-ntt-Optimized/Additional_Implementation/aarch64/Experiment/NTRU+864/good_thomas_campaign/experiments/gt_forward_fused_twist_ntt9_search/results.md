# M5S-A results

The local mathematical gate passes, but the full-path performance gate fails.

## Algebra and static cost

- 352 direct-versus-factored NTT9 cases pass.
- 3,168 `lambda -> lambda*eta^a` row-rotation cases pass.
- all nine independent cyclic B/C orientations were enumerated; the minimum
  remains four non-identity eta corrections.
- no mulmod is removed in this family.
- pairing each block's eight adjacent `(b,bprime)` reads changes 16 `ldr`
  instructions into eight `ldp` instructions.
- historical pre-M5R block: 142 instructions.
- fair copy-free M5R-B block: 136 instructions.
- M5S-A block: 128 instructions.
- one bank: 617 -> 601; complete Forward: 4734 -> 4638.
- coefficient bytes, coefficient load/store boundaries, FR-0 ordering, roots,
  R0 scale, and range DAG are unchanged.

## Slothy and correctness

Remote Slothy 0.2.2 at the configured endpoint reports RA `OPTIMAL`, no spill,
selfcheck `OK`, and `split_heuristic_full:OK` for the 601-instruction region.
The canonical parser reports a false timeout because it matches the benign
configuration line `Setting timeout of 14400 seconds`; the retained raw logs
end in the success markers above.

- Pass-2: 1,122 cases, zero mismatch and zero padding dependency.
- Full Forward: 1,254 cases and 1,083,456 comparisons, zero mismatch.
- seeded `d8-d15` ABI preservation: pass.

## Pi 5 paired PMU

Same binary, Cortex-A76 core 3, three repetitions, `OBCN` and `NCBO` order in
each repetition, 61 samples per order and 20,000 calls per sample:

| Variant | p50 cycles | kernel instructions | IPC |
| --- | ---: | ---: | ---: |
| Official | 4396.946100 | 4028 | 0.917683 |
| M5R-B baseline | 4668.356700 | 4734 | 1.015561 |
| M5S-A paired loads | 4703.579875 | 4638 | 0.987546 |

M5S-A removes 96 instructions but regresses by 35.223175 cycles or 0.754509%.
All three repetitions regress.  Thermal throttling remains `0x0`.

The result shows why paired loads cannot be accepted from static count alone:
`ldp q,q` couples two otherwise independently schedulable table reads and the
lower dynamic instruction count does not recover the lost A76 throughput.
