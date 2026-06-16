# Forward v3b Stage345 Live-Out Rewrite

Status: `blocked_current_stage12_boundary`

Gate 8 closed the final-only v3a path: the current rowpack-v2 tail already
matches the 24-permute/block lower bound for an 8x8 16-bit transpose under the
allowed two-input Neon interleave model.

Gate 9 starts v3b.  The purpose is to rewrite stage3/4/5 arithmetic and
register order so rowpack plane vectors are naturally live-out, then store them
with plain vector stores.

Gate 9 step 2 shows that this is not possible under the current stage12 scratch
boundary alone.  The existing stage12 output is k32-major, and the stage345
arithmetic instructions preserve lane indices.  A rowpack plane live-out still
requires a transpose-equivalent 24-permute/block lane-mixing network.

This directory intentionally does not contain a `.S` or `.opt.s` candidate.
Do not author a current-boundary stage345-only candidate unless the contract is
changed.  The next viable scope is stage12+stage345 or a changed stage12
scratch/live-out contract.

Commands:

```sh
make test_gt_rowpack_forward_v3b_stage345_contract
make test_gt_rowpack_forward_v3b_symbolic_candidate
make test_gt_rowpack_forward_v3c_stage12_stage345_layout_search
```

Gate 9 step 2 writes:

```text
docs/gt_soa_layout_experiment/forward_v3b_stage345/feasibility-summary.md
docs/gt_soa_layout_experiment/forward_v3b_stage345/feasibility.yml
```

Gate 10 widens the search boundary to stage12+stage345 and writes YML plus
markdown artifacts under:

```text
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/
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
