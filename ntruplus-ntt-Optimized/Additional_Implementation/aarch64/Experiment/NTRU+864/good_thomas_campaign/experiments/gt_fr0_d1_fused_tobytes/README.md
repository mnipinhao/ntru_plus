# D1-P3B5 — FR0 fused ToBytes

This experiment keeps the P3B4 byte ABI and the machine-proved FR0-to-Official
map fixed.  It changes only the implementation boundary:

```text
FR0 contiguous q-loads -> R9-A -> full norm -> pack8 -> final bytes
```

Run `make check` on an AArch64 host.  `prepare.py` regenerates the route tables
from the authoritative root-derived map; no generated table is checked in.
The local gate is byte-exact differential correctness plus guarded start/end
buffers.  Pi 5 PMU and full-KEM linkage are later gates.
