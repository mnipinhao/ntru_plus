# D1-P3B13 — pair-aware ToBytes frontier

This directory records the static register-feasibility gate for joining the
P3B6 input-once ToBytes router to the faster P3B9 `pack16` primitive.

Run `make audit` to regenerate the exact map, validate both schedules and
replay the live-vector frontier.  No candidate assembly is generated because
the register gate fails.
