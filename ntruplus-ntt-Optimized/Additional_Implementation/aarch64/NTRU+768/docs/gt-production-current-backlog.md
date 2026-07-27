# GT production current backlog

Updated: 2026-07-23

This is the only active backlog for the NTRU+768 AArch64 GT production line.
Completed July plans are summarized in `gt-production-development-timeline-2026-07.md`.

## Fixed baseline

- Full-KEM source closure: minimal, symbol-gated, and default production.
- External key, secret-key, and ciphertext bytes: KPQC canonical compatible.
- Forward NTT: production Good-Thomas/G1R123+S2 lineage with frontend DCE and
  fixed-register scheduling.
- Keygen: mainline direct-CQ profile with explicit `3F+1`/`3G`, a dual-entry
  production NTT, CQ hierarchical K=8 + fqinv15 baseinv, CQ x CQ basemul,
  and CQ canonical pack.
- Historical mixed keygen remains an explicit compatibility and benchmark
  profile; it is no longer the default.
- Encapsulation: canonical U1 unpack and direct-Q31 basemul-add byte endpoint.
- Decapsulation: public `poly_basemul -> poly_invntt` paired rminus1 contract
  and compact F1 canonical verification pointwise endpoint.

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
shared NTT -> BPQ boundary -> baseinv -> matching basemul -> canonical pack
```

For the direct-CQ profile, compare the complete matching contract instead:

```text
direct-CQ NTT -> CQ baseinv -> CQ x CQ basemul -> CQ pack
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

## Priority 3: serialization selected

The compact generic canonical pack and CQ keygen shared-core pack were promoted
on 2026-07-24. Together they remove 6,400 linked text bytes, pass canonical
KAT/ABI/full-KEM gates, and do not regress any warm KEM mode. U1 remains the
selected canonical unpack.

P2/P3, broad cross-chunk scheduling, and a shared whole-unpack endpoint remain
rejected. Reopen serialization only for a concrete boundary fusion that
removes additional work from a real KEM path.

## Priority 4: forward NTT maintenance

The AArch64 forward kernel is already the strongest standalone GT component.
Further local scheduling has a small expected budget. Keep work bounded to a
measured critical region and require same-binary paired PMU. Do not reopen the
rejected all-row rowspec/direct-tuple families without new evidence.

The separate AVX2 GT prototype is not part of this backlog. It continues on
`avx2-gt-ntt-prototype` with its own layout, basemul, and inverse requirements.

## Active order: A76 kernel and code-size work

The shared-NTT keygen change removed the duplicate direct-BPQ transform from
the selected binary and reduced the measured GT text from about 127.9 KB to
107.3 KB. The work is intentionally gated in this order:

1. remove the unused standalone NTT32 object from the selected full-KEM
   closure: complete, `-3712` text bytes;
2. test a two-iteration schedule for `poly_basemul_rminus1`: complete and
   promoted, `-5.35%` direct kernel cycles and about `-81..-115` full
   decapsulation cycles for `+320` text bytes;
3. investigate proof-backed instruction removal in the inverse final
   branchfold/reduction path: complete, no safe deletion in any of 192 chains;
4. only then run larger I-cache and link-order experiments: complete. Section
   GC is now the default production build policy because it removes about
   14.1 KB of text with cycle-neutral balanced results; mode-hot ordering is
   rejected.

The first item changes only source closure. The NTT32 source remains available
for legacy/sample wrappers and experiments.

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
- V3 cross-group gather pipeline plus Slothy-scheduled shared helper:
  production default.
- F1 source-order compact decapsulation verification endpoint: retained as the
  `compact` comparison profile.
- F2 fully unrolled decapsulation verification endpoint: retained as the
  opt-in `speed` profile.
- Q31 two-iteration scheduling: promoted.
- Stage123 pair scheduling without boundary removal: rejected.
- Full-KEM generic/reference source closure: complete.
- Standalone NTT32 removed from the selected full-KEM closure; retained as a
  legacy/experiment dependency.
- Rminus1 two-iteration basemul schedule: promoted. Differential, ABI,
  transform-contract, full-KEM, symbol-closure, and deterministic KAT gates
  pass. The old leaf remains only as the experiment baseline.
- Inverse final V0 arithmetic: closed without an ASM candidate. The exhaustive
  reachable-set model found no safe final-Barrett deletion or two-instruction
  quotient replacement.
- I-cache/link-order wave: current ordering remains selected. Section GC saves
  about 14.1 KB of text and is enabled by default; balanced GC-minus-non-GC p50
  was keygen `+16`, encap `-9`, and decap `+3` cycles, so no speedup is
  claimed. `GT_PRODUCTION_USE_SECTION_GC=0` reproduces the old binary.
- G1R123+S2 promotion evidence: historical and complete.
- Direct-CQ keygen: promoted from experiment to the mainline production
  profile. Current audit result is 36,773 keygen cycles, 906 cycles faster
  than mixed. Text grows by about 2.8 KB and the current unique replacement
  has a roughly 13-cycle encap/decap placement regression.
