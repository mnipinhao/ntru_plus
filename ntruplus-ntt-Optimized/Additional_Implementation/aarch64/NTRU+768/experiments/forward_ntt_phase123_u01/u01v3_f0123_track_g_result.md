# U01v3 F0123 Track G

Status: Pi5 correctness/ABI pass; PMU matrix completed.  Production default
unchanged.

E4 live-all was not emitted because the hard register contract is infeasible with q0 reserved.  G2_spill1 is also not emitted: one spill removes the global cardinality deficit, but Stage345 block0 would still have only 8 non-future colors while its SSA max-live is 15.

Generated G1 candidate:

```text
symbol: u01v3_f0123_g1_delayed_block3
shape: E3/F012 live handoff + delayed block3 scratch consume
spills: 0
raw q reloads: 0
duplicate Stage12: no
block3 q loads retained: 24
same coverage oracle: u01v3_f0123_production_oracle
scratch baseline: u01v3_f0123_v2_scratch
```

Pi5 correctness:

```text
u01v3_f0123_g1_delayed_block3_abi_mask=0x0
u01v3_f0123_g1_delayed_block3_mismatches=0
mismatches = 0
```

Pi5 PMU matrix, `NTESTS=61`, `NITERATIONS=20000`, `taskset -c 3`:

```text
id,name,status,cycles,instructions,cpi,delta_vs_P,delta_vs_V,text_size,addr_mod32,addr_mod64,mismatches
P,production_source_order_f0123,pass,2707,3835,0.7059,+0,-17,15272,0,32,0
V,u01v2_shared_prefix_scratch_f0123,pass,2724,3875,0.7030,+17,+0,15432,0,0,0
G1,u01v3_g1_delayed_block3,pass,2694,3743,0.7197,-13,-30,14904,0,0,0
```

Interpretation:

```text
G1 vs P: -13 cycles, -92 instructions
G1 vs V: -30 cycles, -132 instructions
```

G1 is a correctness-passing F0123 Track G candidate, but the gain is small.
The result says the E3/F012 semantic-regalloc benefit survives same-coverage
F0123 only partially when block3 is delayed and consumed from scratch.  It is
still better than P/V in this run, but not enough to justify full U01v3 yet.

Next directions:

```text
E3 remains the current best U01 sub-scope candidate.
E4 live-all remains impossible under current hard rules.
G2 one-vector spill live-all is not emitted because allocator feasibility fails.
G1 delayed block3 is viable but small.
G3 controlled recompute/delayed producer is the next model-only direction if
we want to avoid block3 scratch consumption.
```

G3 follow-up:

```text
model: u01v3_f0123_g3_model.py
decision: no physical G3 ASM emitted
G3a delayed block3 producer: hard-gate fail, +201 instructions vs G1, 96 raw q reloads
G3b partial t1/t3 prefix: not plausible, +72 instructions vs G1, extra prefix memory traffic
G3c bounded recompute: hard-gate fail, +201 instructions vs G1, 96 raw q reloads
```

The direct Stage345 block3 handoff is not the blocker: the original block3
destination registers are preclobber-safe.  The blocker is the source contract.
After G1/E3 Stage12 stores out3, raw D is overwritten, so avoiding the block3
scratch q load requires either raw reloads or extra prefix storage.  Neither is
competitive under the current hard gates.
