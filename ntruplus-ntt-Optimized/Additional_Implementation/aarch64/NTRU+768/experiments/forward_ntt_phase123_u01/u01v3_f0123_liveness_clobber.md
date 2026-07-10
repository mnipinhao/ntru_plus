# U01v3 E4 / F0123 Liveness Feasibility

Status: feasibility failed; no E4 physical asm emitted. Production default unchanged.

E4 would extend E3 from F012 to F0123 by keeping block3 Q24..Q31 live in registers while Stage345 block0, block1, and block2 run. Under the current hard rules this is blocked before allocator search: F0123 needs all 32 Stage12 outputs live, while `q0` must remain the modular constant vector used by Stage345 reductions.

Feasibility summary:

```text
feasible_no_spill: False
feasible_no_reload: False
feasible_no_recompute: False
required_simultaneous_outputs_f0123: 32
max_simultaneous_data_outputs_with_q0_reserved: 31
global_output_deficit: 1
available_for_block3_after_e3: ['q2', 'q3', 'q4', 'q14', 'q22', 'q25', 'q27']
required_block3_liveins: 8
block3_deficit_after_e3: 1
```

Blocker:

```text
F0123 needs 32 simultaneously live data vectors, but q0 must remain the modular-constant vector for Stage345, leaving at most 31 data-capable q registers.
```

Block3 first-consume sites were still extracted for future Track G or spill-budget work; see `u01v3_f0123_liveness_clobber.json` for the exact load order, original destination registers, and preclobber sets.

Consequence:

```text
Do not emit u01v3_stage345_semantic_e4_f0123.S under the current rules.
A valid F0123 route needs at least one of: delayed producer, partial shared-prefix, one explicit spill, or a controlled reload/recompute contract.
```
