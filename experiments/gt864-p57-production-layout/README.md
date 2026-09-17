# P57 — production layout and naming cleanup

This gate changes packaging and identifiers, not arithmetic. It aligns the
NTRU+864 release with the `Additional_Implementation`/`SUPERCOP` split, uses
role-oriented source and symbol names, and removes campaign provenance from
executable-source comments.

The performance control compares committed P55/P56 production against the
renamed P57 source on Raspberry Pi 5 core 3. Both implementations are compiled
as ordered object closures with the original compiler policy. `order0.csv` and
`order1.csv` are the two balanced execution orders from the paired PMU harness.

The checked-in SUPERCOP leaf is also compiled independently from its lowercase
`.s` files and must pass the 64-case KEM/tamper test.
