# D1-P3B22 pair-local ToBytes hypothesis

Hypothesis: an input q-vector can finish both adjacent serialized q-vectors,
allowing immediate `normalize + pack16 + ST3` without retaining a partner.

Fixed constraints: exact composed map, one load per FR0 input q-vector, no
coefficient/byte scratch, no spill, fixed public flow and exact protocol bytes.
The hypothesis is falsified if all adjacent output-pair input neighborhoods are
disjoint.
