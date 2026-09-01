# M5E: FR-0 inverse assembly realization

This default-off experiment replaces M5D's two intrinsic functions with
handwritten Armv8-A Neon while preserving algebra, layout, scale, and the
memory-pass boundary. M5E-r1 intentionally changes the noncanonical
representatives by replacing widening Montgomery multiplication with
Algorithm-10 fixed Barrett multiplication; equivalence to M5D is therefore
coefficientwise modulo q. It does not modify or link NTRU+864 Production.

Every fixed constant is stored as `(b, round(b*2^15/q))`; multiplication is the
three-instruction `mul`, `sqrdmulh`, `mls` DAG used by official NTRU+ Neon and
neon-ntt. Four independent inverse16 butterflies are expanded together. This
is not a runtime macro call: assembler macros are expanded, while the larger
macro determines the instruction DAG exposed to later scheduling.

## Run

```sh
make check
make benchmark
```

`make check` is authoritative for this hard gate. `make benchmark` is a local
component diagnostic using `mach_continuous_time`; it is not SUPERCOP and is
not a full-KEM result.

## Two-pass data flow

Pass 1 calls `gt864_fr0_inverse9_block_asm` 12 times: two top branches, three
cubic components, and two eight-column blocks. Each call loads nine FR-0 row
vectors, performs inverse oriented NTT9 plus inverse twist, transposes `s=0..7`
to eight P8 column vectors, and scatters the `s=8` tail lanes. Across all calls,
1728 meaningful input bytes become 1728 meaningful P8+tail bytes.

Pass 2 calls `gt864_inverse16_main_block_asm` six times: three components and
two four-lane halves. Each call packs four alpha lanes into the low 64 bits and
four beta lanes into the high 64 bits of each of 16 state vectors, executes a
shared inverse NTT16, applies per-node public scale, and recombines the two top
branches directly into natural coefficient locations. One tail call processes
the 16 tail vectors with six live lanes. It reads and writes 1728 meaningful
bytes and creates no 2x432 top-branch scratch.

See `REGISTER_FLOW.md` for exact register meanings and the store trade-off.
See `SLOTHY_PLAN.md` for why the chosen scheduling regions stop at two NTT16
layers or four completed output states.
