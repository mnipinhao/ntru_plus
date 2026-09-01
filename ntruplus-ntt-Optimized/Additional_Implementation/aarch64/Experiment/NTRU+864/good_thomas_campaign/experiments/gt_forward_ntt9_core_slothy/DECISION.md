# Decision

Pass the M5I complete-NTT9 register-pressure and Slothy hard gate. Keep the
candidate status `investigate`: this proves allocation and scheduling
existence for a register-only NTT9 core, not integration correctness or target
performance.

Do not relax the nine-register preserved-block model and do not add an
intermediate load/store boundary. The next hard gate is the NTT16-producer to
NTT9-consumer physical ABI: derive the producer's live-out placement, measure
or eliminate any required register permutation, and prove that the combined
boundary still respects the two-load/two-store Forward objective.
