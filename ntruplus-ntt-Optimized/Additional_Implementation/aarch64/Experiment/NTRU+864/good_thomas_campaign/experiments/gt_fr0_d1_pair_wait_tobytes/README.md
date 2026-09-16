# D1-P3B15 — no-scratch pair-wait ToBytes

This experiment implements the P3B13 28-vector witness instead of rejecting it
from the conservative budget alone.  It keeps adjacent output q-vectors until
both complete and calls `pack16` directly, with no coefficient scratch.
