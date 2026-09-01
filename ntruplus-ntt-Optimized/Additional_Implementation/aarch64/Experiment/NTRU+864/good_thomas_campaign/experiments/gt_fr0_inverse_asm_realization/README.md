# M5E: FR-0 inverse assembly realization

This default-off experiment replaces M5D's two intrinsic functions with
handwritten Armv8-A Neon while preserving every algebra, layout, scale, bound,
and memory-pass boundary. It does not modify or link NTRU+864 Production.

The fixed hypothesis is that the M5D map fits in caller-saved vector registers
without coefficient spills. The primary falsifiers are an exact differential
mismatch, a padding write, a stack or `v8-v15` reference inside an arithmetic
block, a branch inside an unrolled block, or a third full-buffer pass.

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
