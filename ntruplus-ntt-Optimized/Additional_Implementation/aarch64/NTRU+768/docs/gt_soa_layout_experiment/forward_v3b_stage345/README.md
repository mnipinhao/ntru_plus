# Forward v3b Stage345 Live-Out Rewrite

Status: `contract_scaffold_no_candidate`

Gate 8 closed the final-only v3a path: the current rowpack-v2 tail already
matches the 24-permute/block lower bound for an 8x8 16-bit transpose under the
allowed two-input Neon interleave model.

Gate 9 starts v3b.  The purpose is to rewrite stage3/4/5 arithmetic and
register order so rowpack plane vectors are naturally live-out, then store them
with plain vector stores.

This directory intentionally does not contain a `.S` or `.opt.s` candidate.
Candidate assembly is gated on this contract and instruction DAG.

Commands:

```sh
make test_gt_rowpack_forward_v3b_stage345_contract
```

Future commands after candidate assembly exists:

```sh
make bench_gt_rowpack_forward_v3b_stage345_cycles
make bench_gt_rowpack_lazy_asm_v3b_forward_fullchain_compare
```

Store policy:

- allowed: `str qN, [public_offset]`
- allowed: `st1 {vN.8h}, [public_offset]`
- forbidden: `st4`
- forbidden: lane stores
- forbidden: scalar halfword stores/scatter
- forbidden: scalar GT-to-rowpack conversion

Performance gate for the future candidate:

- weak pass: recover at least 100 cycles/NTT versus rowpack Forward v2
- strong pass: recover about 200 cycles/NTT
- reject: forward time at or above rowpack v2, or use of a forbidden store form
