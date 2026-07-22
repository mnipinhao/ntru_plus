# Canonical serialization cross-chunk scheduling

This default-off experiment combines two complete P1 canonical-pack chunks in
one Slothy DAG. It changes neither arithmetic nor layout. The only intended
gain is issuing chunk 1 fixed-offset gathers while chunk 0 arithmetic and
stores are still in flight.

The exact baseline is the first two chunks of
`asm/gt/support/poly_canonical_pack_p1.S`: 216 instructions, 32 distinct
8-byte source loads, and four ordered 48-byte output stores.

Production remains unchanged until the generated candidate passes contract,
assembly, differential, ABI, Pi 5 PMU, and full-KEM gates.
