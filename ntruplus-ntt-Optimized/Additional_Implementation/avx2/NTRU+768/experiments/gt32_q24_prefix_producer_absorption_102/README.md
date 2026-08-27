# GT32 Q24-prefix producer absorption (102)

This generator reopens only the final Encap convergence seam:

```text
Forward(m) -> Em --+
                   +-> lane-wise add -> Q24 suffix -> WIRE12
B3(h,r)   -> Ep --+
```

It does not emit assembly and does not modify GT Clean.  The production
baseline remains `b2a4bea`.

## Naming

The layouts in this experiment are Q24-prefix states:

- `M`: current coefficient planes;
- `QL1`: after Q24's four word-unpack routes per group;
- `QL2`: after word plus dword routes;
- `P`: after word, dword, and qword routes.

These names must not be confused with the older Forward-to-B3 transpose-cut
`L1/L2` states already present in the repository.

## Exact result

For twelve four-vector groups, current production executes:

```text
Forward T -> M        12/group
B3 final M             0/group
M-sum -> Q24 packet   12/group
                         total 288 routes
```

The selected shared `QL2` presentation executes:

```text
Forward T -> QL2       0/group
B3 final M -> QL2      8/group
QL2-sum -> packet      4/group
                         total 144 routes
```

The key identity is exact:

```text
QL2(T) = [t0, t2, t1, t3]
```

so Forward changes only register/store ownership.  B3 pays the W+D prefix
after its existing finalizer, while the two-source serializer retains only
the final qword layer.  Both values remain materialized separately; loads,
stores, scale, bounds, and packet-store geometry are unchanged.

Thus `QL2` deletes **144 executed route instructions per Encap**, three full
48-route layers.  It is stronger than `QL1` and packet `P`, which each delete
96 routes.

## Decision

`EPM_QL2_SHARED` passes to an executable experiment.  The next gate should
implement private `Forward_m_QL2`, `B3_output_QL2`, and two-source
`QL2_add_Q24` symbols, first proving raw mapping and WIRE12 equality, then
measuring the complete caller.  Static cost selects the experiment; it is not
a cycle claim.

Run `make check` to regenerate and verify the source contracts and symbolic
lane proofs.
