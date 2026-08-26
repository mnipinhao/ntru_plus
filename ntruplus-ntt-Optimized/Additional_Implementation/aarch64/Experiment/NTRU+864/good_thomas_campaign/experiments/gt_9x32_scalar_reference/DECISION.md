# Decision

Status: `keep_as_canonical_algebra_oracle`.

The declared correctness gate passes with zero mismatches. Freeze this
implementation as the readable canonical algebra oracle.

Do not add legacy layout, Montgomery, lazy-range, Neon, or benchmark candidates
to this closed experiment. The next bounded experiment must address the mapping
between this row-major GT grid and the current leaf/serialization boundary.

This decision does not promote code or authorize Neon until the legacy
representation and Montgomery boundary contracts are separately fixed.

Production default changed: no.
