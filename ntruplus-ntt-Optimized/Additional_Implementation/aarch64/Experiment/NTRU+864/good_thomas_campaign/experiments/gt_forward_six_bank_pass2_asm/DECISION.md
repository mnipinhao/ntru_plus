# M5N decision

Status: passed as the complete six-bank Forward pass-2 Experiment hard gate;
not Production and not a full `poly_ntt` performance claim.

Freeze the one-copy M5M helper, stackless public wrapper, fixed output-register
map, direct FR-0 store formula, top-specific compile-time tables, and disjoint
P8/output ABI.  Reject sixfold body duplication because it adds code footprint
without changing arithmetic or eliminating memory traffic.

Next hard gate: implement and validate the complete top-split producer that
writes the exact 896-halfword P8 contract, compose it with M5N behind a
callable experimental `poly_ntt`, and compare the complete transform against
the official Forward output modulo q before Pi 5 and SUPERCOP timing.
