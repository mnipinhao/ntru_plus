# GT production current backlog

Updated: 2026-07-22

This is the only active backlog for the NTRU+768 AArch64 GT production line.
Completed July plans are summarized in `gt-production-development-timeline-2026-07.md`.

## Fixed baseline

- Full-KEM source closure: minimal, symbol-gated, and default production.
- External key, secret-key, and ciphertext bytes: KPQC canonical compatible.
- Forward NTT: production Good-Thomas/G1R123+S2 lineage with frontend DCE and
  fixed-register scheduling.
- Keygen: private BPQ/CQ NTT, hierarchical K=8 + fqinv15, mixed BPQ x CQ
  basemul, and specialized canonical pack.
- Encapsulation: canonical U1 unpack and direct-Q31 basemul-add byte endpoint.
- Decapsulation: rminus1 basemul/inverse pair and canonical verification
  pointwise endpoint.

Any candidate must remain default-off until differential/KAT, ABI, full KEM,
and Pi 5 PMU gates pass.

## Priority 1: baseinv endpoint and prepare schedule

Production already has hierarchical K=8 base inversion. The open work is not
"add batch inversion"; it is whether a newer prepare/tree schedule should
replace the active BPQ/CQ keygen implementation.

Current experiment evidence includes:

- prepare2 Slothy: faster than the earlier block-major prepare;
- paper-k8 C/Neon: shorter denominator dependency graph;
- paper-full ASM: positive same-binary keygen result;
- remaining gap: the BPQ/block-major prepare layout and its `ld4/st4` cost.

Before promotion, compare the best candidate against the current private
`asm/gt/keygen_bpq_cq/baseinv_{prepare,tree,finish}.S` path, not against the
legacy generic API. Measure the complete keygen contract:

```text
specialized NTT -> baseinv -> matching basemul -> canonical pack
```

## Priority 2: inverse scratch-boundary removal

The source-order two-group Stage123 schedule passed correctness but was flat.
Do not repeat that experiment. The next candidate must remove real memory
traffic or change the producer/consumer contract:

```text
Stage123 output
  -> selected live-register or consumption-order handoff
  -> Stage45/post consumer
```

Required evidence:

- exact or mod-q differential at each changed boundary;
- representative contract required by `poly_crepmod3`;
- ABI sentinel;
- rminus1 decapsulation pair and full decapsulation PMU;
- code-size and stack-frame delta.

## Priority 3: serialization only at full-KEM boundaries

P1 keygen pack and U1 unpack are already selected. P2/P3 and broad
cross-chunk schedules did not justify global replacement. Reopen this line only
for a concrete boundary fusion that removes work from a real KEM path, such as
pointwise-to-canonical-bytes or specialized keygen pack.

Do not optimize generic `poly_tobytes`/`poly_frombytes` based only on isolated
cycles. Promotion requires canonical byte equality, KAT/cross-decap, and a
non-regressing unique replacement binary.

## Priority 4: forward NTT maintenance

The AArch64 forward kernel is already the strongest standalone GT component.
Further local scheduling has a small expected budget. Keep work bounded to a
measured critical region and require same-binary paired PMU. Do not reopen the
rejected all-row rowspec/direct-tuple families without new evidence.

The separate AVX2 GT prototype is not part of this backlog. It continues on
`avx2-gt-ntt-prototype` with its own layout, basemul, and inverse requirements.

## Benchmark and promotion gates

For every production candidate:

1. Confirm the exact linked source/object closure.
2. Run kernel differential and ABI sentinel tests.
3. Run deterministic full KEM and KPQC cross-vector/KAT checks when bytes can
   change.
4. Run same-binary paired A/B where possible.
5. Rebuild a unique replacement binary to remove duplicate-wrapper and code
   placement effects.
6. Report cycles, instructions, text size, alignment, and correctness status.
7. Rerun GT production versus unmodified KPQC final with portable `NO_CE`
   SHAKE on both sides.

## Closed work

- Canonical P1/U1 selection: complete.
- F2 decapsulation verification endpoint: promoted.
- Q31 two-iteration scheduling: promoted.
- Stage123 pair scheduling without boundary removal: rejected.
- Full-KEM generic/reference source closure: complete.
- G1R123+S2 promotion evidence: historical and complete.
