# D1-P3B14 — paired-input FromBytes frontier

This directory records the static register-feasibility gate for replacing two
P3B11 12-byte decodes with one adjacent 24-byte `LD3`-style decode.

Run `make audit` to regenerate the exact inverse composed map and replay the
optimistic and atomic-pair frontiers.  No candidate assembly is generated
because the no-spill register contract fails.
