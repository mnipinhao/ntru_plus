# GT32-HASH-CODE-ADDRESS-053

2x2 code-address factorial for the complete Hash/SHAKE path. Production is not
modified.

Relocation-free Hash and SHAKE templates are copied byte-for-byte into an
anonymous executable cage at production-like page offsets:

| Slot | Hash page offset | SHAKE page offset |
|---|---:|---:|
| OO | `0xb20` | `0x2d0` |
| GO | `0x000` | `0x2d0` |
| OG | `0xb20` | `0xf80` |
| GG | `0x000` | `0xf80` |

The Hash template receives the selected SHAKE address as an argument. The
SHAKE template calls the common Keccak primitives through an operation table.
Consequently all Hash clones are byte-identical, all SHAKE clones are
byte-identical, and no clone has a RIP-relative relocation.

`DUP` repeats OO page offsets at different higher virtual-address bits. A large
DUP difference invalidates a simple page-offset interpretation.

All profiles share the same caller, input/output addresses, algorithm, Keccak
implementation, and stack/data geometry. Four untimed calls train each profile
before each timed call. The runner pins every launch to one logical CPU.

The templates intentionally replace production relative calls with indirect
calls to make byte identity possible. Therefore this is a causal geometry gate,
not a byte-exact replay of the production wrapper.

## Decision

The 256-launch factorial is neutral for engineering purposes: all paired effects
are between -2 and +2 TSC, DUP is exactly zero, and the interaction is -1 TSC.
Hash/SHAKE code-address geometry is closed. See `RESULTS.md`.
