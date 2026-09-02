# M5R-D — all level-2 one-multiplication B3

This isolated Forward experiment extends M5R-C's `rho^2=-1-rho` radix-3
identity from the three level-1 B3 nodes to all three level-2 B3 nodes in each
NTT9 block.  It deliberately retains M5R-B's two independent twist `ldr`s,
FR-0 output order, R0 scale, and two-pass coefficient-memory boundary.

The experiment is not linked into Production.  Its reproducible gates are:

```sh
make prepare
make prove
make audit
make linked-check
```

`optimize.py` is the remote Slothy driver.  The checked-in `slothy-output/`
files are the allocation/scheduling evidence returned from
`pinhao@172.25.166.141:51208`; generated binaries and Pi 5 raw rows stay under
ignored `build/`.

The result is an accepted experimental candidate: 569 instructions per bank,
90 Algorithm-10 products per bank, no spill, exact modulo-q Forward output,
and 4229.9409 cycle p50 on Cortex-A76 versus 4457.45735 for M5R-C and
4396.91215 for Official Neon.
