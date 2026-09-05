# D1-P3A — GT byte/coordinate ABI architecture

This default-off design gate factors the exact 864-entry M5O map and composes
it with the real NTRU+864 `poly_shuffle`/`poly_shuffle2` byte boundary.

Run:

```sh
make audit
```

The important result is that the map is structured, but not as independent
24-coefficient tiles.  For each top branch it is two 9-by-9 bipartite routing
components, each missing exactly one perfect matching.  The same route is
reused for all three cubic components and for both top branches.

No Production source, KAT, SUPERCOP input, or assembly is changed here.
