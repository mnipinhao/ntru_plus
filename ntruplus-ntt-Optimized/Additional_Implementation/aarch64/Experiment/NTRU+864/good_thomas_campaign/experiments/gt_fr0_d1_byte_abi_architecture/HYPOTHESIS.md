# D1-P3A hypothesis

Observation: D1-P2 measured 1,319 cycles for ToBytes, 2,223 cycles for
FromBytes, and 3,952 cycles for BaseInv above Official.  The current bridge
executes one generated-map assignment per coefficient.

Hypothesis: the 864-entry map is a repeated small routing graph, so a direct
FR0 byte boundary can replace scalar coefficient translation and the separate
Official shuffle pass.

Falsifier: reject direct Neon work if the map is an arbitrary 864-way
permutation, if top/component copies require different routing, or if the byte
shuffle composition cannot be proved bijective and byte-order preserving.

Isolation: this gate emits no assembly and changes no linked implementation.
It selects the unit of work for the next benchmark-only candidate.
