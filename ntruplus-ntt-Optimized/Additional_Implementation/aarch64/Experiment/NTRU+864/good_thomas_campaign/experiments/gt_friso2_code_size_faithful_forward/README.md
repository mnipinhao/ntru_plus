# M5U-CF5-B — code-size-faithful FR-ISO2 Forward

This experiment changes only code placement.  CF5-A proved that the frozen
M5R-D NTT16 producer can feed each scaled CF3 NTT9 consumer with no copies,
spills, or coefficient-memory boundary, but emitted four static copies of the
same producer.

CF5-B emits one producer helper.  Each scaled-bank call returns directly to its
unique inline consumer.  The consumer therefore sees the exact CF5-A physical
register state; there is no handoff instruction at the boundary.

The arithmetic regions are inherited byte-for-byte from the remote Slothy
outputs.  Slothy is not rerun because the instruction DAG and allocation are
unchanged; `audit_cf5b.py` proves exact instruction identity and separately
audits the new control-flow/code-placement layer.
