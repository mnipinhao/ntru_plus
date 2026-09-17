# Results

## Mapping and contracts

The 64 impulse mapping tests and 1,000 random values pass for both outputs.
The candidate retains:

- M output: existing private M presentation, `e=0`, bound `<=10788`;
- WIRE12 output: existing canonical packet semantics for `hash_g`;
- existing B3 input contract;
- no extra center or reduction checkpoint.

QL2 is only the transient branch point already present at the Forward
terminal. It is not stored as a new persistent polynomial.

## Exact executed-work ledger

For each of twelve four-vector groups:

| Path | M branch | WIRE12 branch | Total routes |
|---|---:|---:|---:|
| Current | QL2→M: 12 | M→packet: 12 | 24 |
| Candidate | QL2→M: 12 | QL2→packet: 4 | 16 |

Therefore the candidate deletes:

```text
96 dynamically executed routing instructions / Encap
48 YMM reloads of the materialized r_M / Encap
```

The 48 M stores remain because later B3 still consumes M. WIRE12 stores and
all canonical reduction/packing arithmetic remain; they are moved into the
Forward terminal schedule, not counted as deleted work.

This satisfies the continuation rule: it is not a complete Forward followed
by an extra complete serializer under another symbol name.

## Packet order and code shape

The selected Q24 body consumes Forward tiles in this order:

```text
0, 4, 2, 5, 3, 1
```

Each 256-byte tile corresponds to two adjacent packet groups and 192 bytes of
WIRE12 output. Some tiles emit their high 128-byte half first; S4/S5 makes the
two halves independent, so the candidate can follow the exact `(tile,half)`
packet schedule, scatter each M result to its original M offset, and emit
packets monotonically. This preserves the current overlapping packet stores
and requires only the existing safe final packet; no packet repair buffer is
needed.

The executable candidate must be a bounded six-tile loop with an offset table,
not six fully duplicated tile bodies.

## Register proof

One constructive schedule peaks at 15 YMM registers:

```text
other S4/S5 half       4
current QL2 half       4
Q-only packet outputs  4
q and v constants      2
encode temporary       1
                       --
                       15
```

After packet emission, those output registers die. The existing M formation
then peaks at 14 registers. Reloading the pshufb constant between the two
branches is cheaper than preserving another live register and does not create
a spill or a new arithmetic checkpoint.

## Decision

```yaml
GT32-R-FORWARD-DUAL-OUTPUT-AUDIT-146:
  mapping: PASS
  range_scale_contract: UNCHANGED
  route_deletion: 96_per_Encap
  M_reload_deletion: 48_per_Encap
  M_materialization: RETAINED_FOR_B3
  new_persistent_representation: NONE
  peak_ymm: 15
  zero_spill: PLAUSIBLE_CONSTRUCTIVE_SCHEDULE
  decision: PASS_TO_ZERO_SPILL_ASM_GATE
  production_modified: false
```

The next gate should implement only the local `Forward(r)+WIRE12` candidate
and compare it with `Forward(r)+pack(r)` in one fixed ELF. It must charge the
six-entry tile-order table and hash-input stores. Full Encap is not eligible
until this local gate wins.
