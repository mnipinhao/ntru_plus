# NTRU+864 Good-Thomas campaign

This is the default-off development front door for the NTRU+864 Good-Thomas
campaign. Production remains in `../../NTRU+864/` and does not include this
directory.

Reading order:

1. `PLAN.md` — campaign phases and promotion gates.
2. `LEARNING_PROTOCOL.md` — evidence labels and explanation standard.
3. `ring-profile.yml` — scheme and representation facts.
4. `REFERENCE.md` — authoritative GT C reference and oracle hierarchy.
5. `experiments/README.md` — active experiment registry.
6. `experiments/optimization_scoreboard.md` — decisions and next actions.
7. The selected experiment's contracts, checker, results, and decision.

Run all currently implemented static/correctness gates:

```sh
make check
```

This target does not build or link Production and does not run benchmarks.

Authoritative current range chain (G0):

```text
M5R-D Algorithm-10 NTT16 (9342)
  -> one-product NTT9 / FR-0 (25569 symmetric consumer bound)
  -> M5C BaseMul / BaseMulAdd (2148 / 2205)
  -> M5D reference inverse (19845 maximum lazy halfword)
  -> M5E assembly inverse (17220 maximum lazy halfword, 6888 final bound)
```

`experiments/gt_m5rd_fr0_range_chain_closure` is the machine-checkable source
of this contract. Earlier `8874 -> 24438 -> 2168` figures below describe the
historical M5B/M5C/M5D checkpoints and are not valid premises for new M5R-D
experiments.

Current checkpoint: M5A `experiments/gt_fr0_kernel_realization` is the frozen
first handwritten FR-0 assembly baseline. It passes exact differential,
stack/register, formal-range, and leaf-map gates. Its producer bound is
`|P8+tail| <= 15752`. M5B `experiments/gt_ntt16_producer_range` now proves the
historical twisted radix-2 producer reaches at most 8874 with no extra Barrett
reduction. Its intrinsics spill, so assembly memory scheduling remains open;
M5C `experiments/gt_fr0_basemul_arithmetic` now consumes the generated zetas
in working BaseMul/BaseMulAdd tile arithmetic with proved int32/R0 bounds. M5D
`experiments/gt_fr0_inverse_consumer` closes the matching inverse arithmetic:
inverse NTT9 returns FR-0 to P8+tail, while packed alpha/beta inverse NTT16 and
top recombination finish in the second pass without a top-branch scratch.
M5E `experiments/gt_fr0_inverse_asm_realization` realizes that exact two-pass
map modulo q in handwritten Neon. M5E-r1 uses paired Algorithm-10 fixed Barrett
constants and grouped independent operations. Its arithmetic blocks have no
stack, coefficient spill, callee-saved vector use, or branches; code size is
7,292 bytes and the local combined diagnostic is 545.354 ns versus 1065.938 ns
for M5D intrinsics. Target attribution remains mandatory. Handwritten
M5F `experiments/gt_forward_composition_barrett` now proves the forward
NTT16-to-NTT9 schedule can consume every meaningful P8 coefficient once and
write every FR-0 coefficient once without an intermediate NTT16 boundary. Its
M5F-r2 `experiments/gt_forward_barrett_reduction_search` records the historical
four-product reduction search. M5G `experiments/gt_forward_symbolic_dag`
changes B3 to two products and supplies the current correlation-aware proof:
NTT16 reaches 9342 and the exact full-Forward DAG reaches 28568 with zero
unsafe halfword nodes. Its 15-instruction B3 is written entirely with Slothy
symbolic registers. The remote Slothy gate is OPTIMAL at 24 N1-proxy cycles
and allocates exactly `v0,v24-v31`, with no spill, stack, memory, GPR, or
forbidden-vector instruction. The whole schedule still peaks at 24
caller-saved vector registers. M5H
`experiments/gt_forward_ntt9_level1_slothy` expands this to all three
level-1 B3s while nine registers preserve the other column block. Its remote
OPTIMAL schedule is 48 N1-proxy cycles and uses exactly all fifteen available
registers `v0-v7,v25-v31`, again without spill or reserved-register use.
M5I `experiments/gt_forward_ntt9_core_slothy` adds the four eta products and
all three level-2 B3s. Its 102-instruction RA-first gate is OPTIMAL, and the
corrected physical-live-out split-window pass ends in
`split_heuristic_full:OK!` at 25 N1-proxy cycles. Both artifacts use exactly
`v0-v7,v25-v31` with no spill or reserved-register use. NTT16-to-NTT9 physical
handoff is now closed by M5J
`experiments/gt_forward_ntt16_ntt9_handoff_slothy`: two exact 8x8 transposes,
eight lane twists, and one complete NTT9 form a 190-instruction region. Remote
RA is OPTIMAL and split-window scheduling completes at 47 N1-proxy cycles.
The returned artifacts use exactly `v0-v7,v17-v31`; forbidden `v8-v15` and
fixed held-tail `v16` remain untouched, with sixteen public table loads and no
coefficient traffic or spills. M5K
`experiments/gt_forward_two_ntt9_blocks_slothy` then consumes the held block
while all nine first-block outputs stay live. Its deterministic 333-instruction
region is RA OPTIMAL and split-window full OK at 83 N1-proxy cycles. Both
artifacts use all 24 caller-saved vectors `v0-v7,v16-v31`, with 32 public loads
and no coefficient traffic, store, stack, branch, or spill. M5L
`experiments/gt_forward_tail_ntt16_slothy` now realizes the non-contiguous tail
half of the producer: sixteen exact x4-stride halfword loads and a packed
two-vector NTT16 form a 65-instruction region. Remote RA is OPTIMAL and
split-window full OK at 16 N1-proxy cycles; both artifacts assemble without
over-read, `v8-v15`, stack, store, branch, or spill. M5M
`experiments/gt_forward_one_bank_slothy` adds the exact sixteen-vector main
producer and enters both M5K blocks with the tails live. Its 633-instruction
region reads all 144 meaningful bank coefficients once, performs no
coefficient store, and passes remote no-spill RA plus real split-window
scheduling at 158 N1-proxy cycles. Repeated-bank Forward integration, exact
FR-0 stores. M5N `experiments/gt_forward_six_bank_pass2_asm` now provides that
complete second pass: one shared M5M helper, six public bank calls, and 108
direct FR-0 stores form a 4928-byte linked object. Actual assembly passes 1122
exact-representative oracle cases, covers all 864 meaningful inputs and
outputs, ignores 32 padding positions, and uses no stack or scratch coefficient
traffic. Top-split/full `poly_ntt`, KEM, Pi 5 PMU, and SUPERCOP remain future
gates.

Run only the authoritative GT C reference gate:

```sh
make check-reference
```

A1-S `experiments/gt_t1_slothy_scheduling` closes the scheduling-only follow-up
to the bank-major T1 tail result. Dedicated local Slothy 0.2.0 proves OPTIMAL
functional RA and a spill-free split-window schedule for the exact unified
552-instruction one-bank DAG. Linked one-bank, six-bank and full-Forward
correctness all pass, but Pi 5 complete Forward regresses from 4165.040 to
4208.347 cycles with identical retired instructions. T1 remains the active
architecture while the generated N1-proxy schedule is rejected.

B1 `experiments/gt_fr0_handwritten_basemul` freezes the exact GCC FR0
BaseMul/BaseMulAdd baseline and keeps scheduling and arithmetic changes
separate. K1 finds no complete eight-lane Karatsuba-safe group. In parallel,
D1 replaces only the final R0 Montgomery round-trip with direct signed-int32
Barrett reduction. Its exact residual is `[-2911,2911]`, the M5E inverse range
re-closes at 17220, and paired Pi 5 measurements save 523.933 BaseMul cycles
and 676.660 BaseMulAdd cycles without spills. D1-C1 in
`experiments/gt_fr0_d1_consumer_closure` then passes the executable
`2F + BaseMul + Inverse` boundary and saves 547.594 cycles with exactly 755
fewer instructions. D1 is therefore the experimental arithmetic baseline.
The stock serializer is byte-exact for 34 D1-C2a cases. D1-C2b additionally
passes 24 real Encapsulation-derived h/r/m cases through the generated exact
official-to-FR0 coordinate bridge and back to byte-identical stock
ciphertexts. The experimental consumer closure is complete; Production and
SUPERCOP remain unchanged. Any future handwritten scheduling must start from
the 57-instruction D1 DAG.

D1 also changes the meaning of the later B2 campaign. A scale-only
`R^-1 -> R0` fusion is no longer sufficient because D1 already performs the
direct R0 reduction cheaply. B2 may reopen only as a true
BaseMul-to-inverse9 producer-consumer fusion that removes the FR0 store/load
boundary, reuses live values, and proves any deferred reduction end to end.

D1-P1 `experiments/gt_fr0_d1_production_shaped` now closes the unchanged stock
KEM caller graph with an explicit GT poly API. It discovered that M5R-D output
must be normalized before BaseInv/serialization and M5E output must be
centered before `crepmod3`. With those costs included, D1 saves 1068.625,
664.825 and 1024.750 cycles versus GT-old in Keypair, Encaps and Decaps.
Nevertheless GT-D1 remains 9936.375, 3776.475 and 10396.400 cycles slower than
Official respectively. D1 stays the arithmetic baseline, while the complete
GT implementation stays experimental and proceeds to boundary-cost
decomposition rather than KAT/SUPERCOP promotion.

D1-P2 `experiments/gt_fr0_d1_boundary_cost_decomposition` closes that
decomposition exactly at the retired-instruction and branch levels. Forward
is already 197.835 cycles faster than Official and D1 BaseMul/BaseMulAdd save
701.993/694.741 cycles. The deficits are instead centered in Inverse API
`+2854.900`, ToBytes `+1318.990`, FromBytes `+2222.827`, and the BaseInv bridge
`+3952.375`. Static KEM call counts predict the measured P1 gaps within 126,
7 and 35 cycles for Keypair, Encaps and Decaps. The next gate is therefore a
structured GT byte-boundary architecture shootout; Inverse remains a separate
second-priority campaign, and Slothy is still premature.

D1-P3A `experiments/gt_fr0_d1_byte_abi_architecture` proves the exact routing
unit before implementation. The map is not independent 24-coefficient tiles:
per top it splits into two `K9,9` graphs with one perfect matching removed.
The same 144-leaf route is reused across both top branches and all three cubic
components, giving twelve route9 kernels for the full polynomial. Composition
with the stock shuffle is byte-order exact and bijective, so D1-P3B will
compare route9 and direct pre/post-shuffle byte kernels against the scalar
bridge. The old cross-stage-fusion P3 is deleted from the roadmap; BaseInv and
raw Inverse remain independently attributable campaigns.

D1-P3B0 `experiments/gt_fr0_d1_route9_network_search` closes the exact lane
label question. After public relabeling, `J_i[lane l]` targets logical output
`i+l+1 mod 9`, so the graph is eight cyclic perfect matchings. A plain 8x8
transpose still does not produce Official lane order: it needs final lane
repair. Conservative instruction-selection bounds are 87 instructions for
transpose/repair R9-A and 90 for three-bank-TBL R9-B per route9. Both proceed
as separate benchmark-only candidates; neither is assumed faster before Pi 5.

D1-P3B1 `experiments/gt_fr0_d1_route9_pmu` now proves the machine primitive.
R9-A passes exact bidirectional tagged/random correctness and measures
392.238 cycles FR0-to-Official and 417.285 cycles in reverse, versus
1760.402/1795.766 for the current scalar bridge. R9-B also wins but trails at
595.208/596.192 cycles. The emitted helpers have no vector spill. R9-A is the
coordinate-only champion, but its final Official lane materialization is not
carried blindly into byte code: P3B2 will re-search the composed pre/post-
shuffle targets before Slothy or real ToBytes/FromBytes implementation.

D1-P3B2 `experiments/gt_fr0_d1_composed_byte_routing_search` composes the
authoritative coordinate map directly with stock `poly_shuffle2/poly_shuffle`.
The composed Q-vector graph is not twelve route9 units: each direction is two
top-local 54-by-54 degree-8 components, and every target Q draws one lane from
eight distinct source Qs. Exact bijection/inverse, 864 tags and 128 random
roundtrips pass. C1 direct lane-load gather and C2 two-TBL4 gather form the
machine Pareto set and both remove the full Official intermediate. P3B3 must
now implement complete byte boundaries and time them against both current and
R9-A-plus-stock controls; no static count is treated as a cycle result.

D1-P3B3 now passes local and Pi5 stock-assembly differential and guard-page
checks. Pi5 selects R9-A plus stock for ToBytes at 1849.450 cycles and direct
C1 for FromBytes at 1183.250 cycles; C2 loses both directions. GCC emits no
vector spill. The per-direction choices still require a production-shaped KEM
rerun before promotion. A corrected frontier model gives
input-once routing witnesses with 16/14 partial-output peaks, disproving the
prior asserted 54-vector lower bound. Graph connectivity alone cannot rule
out a factorized route9 or input-once implementation.

D1-P3B4 links the P3B3 winners into the unchanged GT-D1 KEM callers. Eight
valid/tampered cases are byte exact, relocations prove the candidate uses the
selected symbols, and Pi5 shows savings of 1141.500/2666.900/6288.450 cycles
for Keypair/Encaps/Decaps. The isolated call ledger closes within 72 cycles.
Encaps is now only 1174.950 cycles behind Official, while Keypair and Decaps
remain 8791.875/4196.225 cycles behind. Keep this byte ABI experimental and
remeasure BaseInv/Inverse with it fixed before selecting the next target.
