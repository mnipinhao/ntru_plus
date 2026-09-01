# M5R-C — one-Algorithm-10 level-1 B3

This isolated Forward experiment keeps M5R-B's memory and transform-domain ABI:

- the same LD3 top split and P8 scratch boundary;
- the same six `(top, component)` banks;
- two independent `ldr q..., [x3], #16` instructions for every NTT9 twist pair;
- the same physical FR-0 slot permutation, R0 scale, output stores, and public wrapper;
- no Production linkage.

Only the six level-1 radix-3 nodes in one bank are changed: three in each of
the two NTT9 blocks.  Since `rho^2 + rho + 1 = 0`, the old two-product B3

```text
y0 = x0 + x1 + x2
y1 = x0 + rho*x1 + rho^2*x2
y2 = x0 + rho^2*x1 + rho*x2
```

is replaced by

```text
d  = x1 - x2
r  = Algorithm10(d, rho)
y0 = x0 + x1 + x2
y1 = x0 - x2 + r
y2 = x0 - x1 - r
```

The B3 body falls from 14 to 10 instructions.  It deletes one complete
`mul/sqrdmulh/mls` triplet and one additional add/sub instruction after the
different output construction is accounted for.

The candidate intentionally does **not** preserve M5R-B's exact signed
representative.  It preserves every residue modulo `q=3457`, the R0 scale, and
the physical output ordering.  The new representatives are carried through
the unchanged eta corrections and level-2 B3 nodes in `prove_one_mul_b3.py`;
their conservative maximum magnitude is 26306, so no ordinary Neon add/sub
wraps signed int16.

Run locally:

```sh
python3 prepare.py
python3 prove_one_mul_b3.py
python3 audit_candidate.py
python3 generate_integration.py
make check-pass2 check-full check-abi
```

Slothy was run on `pinhao@172.25.166.141:51208` with
`/home/pinhao/slothy/venv/bin/python`, using RA-first allocation followed by
the Neoverse-N1 real-instruction scheduler.  Returned assembly and complete
logs are under `slothy-output/`.

The paired Cortex-A76 PMU run is reproduced by `python3 run_pi5.py`.
