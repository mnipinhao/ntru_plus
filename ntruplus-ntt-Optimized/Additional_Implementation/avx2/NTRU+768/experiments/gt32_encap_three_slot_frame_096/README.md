# 096 — Encap three-slot production frame

Control baseline: production commit `b2a4bea`; destructive B3 alias proof:
`718899c` / gate 095.

Profiles:

- **C4**: current four-slot, 6592-byte frame; distinct B3 product in `c`.
- **A4**: four-slot, 6592-byte alias control; B3 overwrites `r`, while `c`
  remains the Forward frontend buffer.
- **A3**: three-slot candidate, 5056-byte frame; B3 overwrites `r`, and the
  selected frontend plus M Forward use their already-valid exact in-place
  contracts where required.
- **A4I**: attribution-only closure control. It uses the same in-place Forward
  and B3 alias as A3, but forces an unused fourth reservation and retains the
  6592-byte frame without executing extra instructions. Thus A3-A4I isolates
  removal of the reservation and the resulting absolute stack-address shift.

The semantic ownership is:

```text
h          : Decode(pk) -> B3 input -> dead
r/product  : Forward(r) -> pack/hash-facing use -> destructive B3 -> Q24
m          : coefficient message -> in-place frontend/Forward -> Q24
```

The old transformed `r` may be destroyed only after its serialization and
`hash_g`-facing use have completed. Partial overlaps remain unsupported.

The gate is resource-first. Promotion requires a 6592-to-5056-byte frame,
three polynomial slots, unchanged arithmetic kernels/E0V tail, no new spills
or static scratch, exact KEM behavior, and no stable timing regression.

## Decision

Correctness and resource shape pass, but production promotion fails. With
ASLR disabled, A3-A4I Encap is `+402.875` cycles with bootstrap 95% CI
`[+395.5,+417.25]` and 0/16 favorable blocks. A4I-A4 is timing-neutral for
Encap, so in-place Forward is not the loss owner. The current natural
three-slot frame is closed for scope; production remains at `b2a4bea`.
