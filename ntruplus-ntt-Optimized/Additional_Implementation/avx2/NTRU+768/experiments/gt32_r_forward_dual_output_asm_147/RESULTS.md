# Results

## Correctness and ABI

The candidate passes:

- all 768 coefficient impulses;
- 1,000 deterministic random CBD-range inputs;
- word-exact private-M comparison;
- byte-exact 1,152-byte WIRE12 comparison.

The final V2 assembly has no calls, stack references, pushes, or pops.  Its
symbol is 6,474 bytes and contains 1,441 static instructions.  It uses all
16 YMM registers but does not spill.

## ASLR-off paired benchmark

Control and candidate are in one ELF.  Values below are per complete
`Forward(r) + WIRE12` operation.

| Backend | Control median | Candidate median | Paired delta | 95% bootstrap CI | Favorable launches |
|---|---:|---:|---:|---:|---:|
| RDTSCP | 4999.49 | 5353.85 | **+356.13 TSC** | `[+353.63,+358.24]` | 0/16 |
| libcpucycles `default-perfevent` | 666.93 | 713.85 | **+46.98** | `[+46.57,+47.27]` | 0/16 |

V1 was already a decisive loss:

| Schedule | RDTSCP delta | default-perfevent delta | Favorable |
|---|---:|---:|---:|
| V1 single temporary | +332.84 | +43.62 | 0/16 |
| V2 four-chain scheduling | +356.13 | +46.98 | 0/16 |

V2 therefore does not rescue V1; it is slightly slower.

## Interpretation

Gate 146's work deletion is real at the semantic/dynamic-routing ledger:
96 routes and 48 M reloads disappear.  It is nevertheless not a cycle win.

The executable constraint is the simultaneous dual-output live set.  The
terminal transform values must remain live for M formation while four Q-only
packet values are reduced and packed.  V1 exposes too little packet ILP.  V2
uses the only obvious zero-spill mutation—releasing terminal constants to
obtain four temporaries—but must reload constants and the NTT modulus for
each tile; it also grows the hot symbol from 5,794 to 6,474 bytes.  The
measured loss increases rather than decreases.

This result does **not** say that fewer instructions or loads cannot win in
general.  It says that, for the exact current M ABI and immediate WIRE12
packing boundary, the deleted memory/routing work is dominated by the
dual-output register/scheduling and executable-shape cost.

## Decision

```yaml
GT32-R-FORWARD-DUAL-OUTPUT-ASM-147:
  correctness: PASS
  m_output: WORD_EXACT
  wire12_output: BYTE_EXACT
  zero_spill: PASS
  v1_rdtscp_delta: +332.84
  v2_rdtscp_delta: +356.13
  v2_favorable_launches: 0/16
  full_encap: NOT_RUN_LOCAL_GATE_LOST
  decision: CLOSED_FOR_SCOPE
  production_modified: false
```

Reopen only with a new premise that changes this live-set boundary—for
example, eliminating M materialization as well, sharing actual Q24
reduction/packing arithmetic with the Forward terminal, or a consumer that
accepts the packet-side state.  Another register allocation or constant
reload schedule is not enough evidence to reopen it.

