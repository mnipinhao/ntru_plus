# Results

The hard gate passes at the mathematical and symbolic-source levels:

- exact B3 input union `[-16816,16816]`;
- exact NTT16 maximum magnitude 9342;
- complete two-product Forward DAG maximum magnitude 28568 at
  `top0.column13.level2.g0.y2`;
- output union `[-28568,28565]` and zero unsafe signed-halfword nodes;
- two Algorithm-10 fixed products and 15 instructions per B3;
- zero loads, stores, concrete GPRs, or physical vector-register tokens in the
  symbolic region;
- M5F C replay: 55 cases, zero mod-q mismatches, observed output maximum
  13886, 864 meaningful pass-2 loads and stores, and no intermediate NTT16
  traffic.

The rejected `2a -> 3a` DAG reached magnitude 50448 at 176 nodes even though
the same small C differential set passed. This demonstrates why the exact DAG
proof is a correctness gate rather than supporting documentation.

The remote Slothy hard gate now passes:

- repository venv interpreter `/home/pinhao/slothy/venv/bin/python`;
- Slothy checkout `d636d638d06b370d1acc5774ca31c9572d3d2e6f`, version 0.2.2;
- solver result OPTIMAL, expected N1-proxy cost 24 cycles, expected IPC 0.62,
  and 20 minimum stalls;
- emitted register set exactly `v0,v24,v25,v26,v27,v28,v29,v30,v31`;
- zero `v1-v23`, GPR, load/store, branch, stack, or spill instructions;
- Slothy selfcheck passes and the returned source assembles as AArch64;
- optimized source SHA-256
  `751a179d2d81fe6d3f919bc5a8a8aca62167472861763367cb704afb561ec128`;
- log SHA-256
  `06cb62b5e82c95753459e2afbecac3e81add5996073fb54e60150480c3682921`.

For this returned allocation, the boundary mapping is:

| Symbolic role | Physical register |
| --- | --- |
| input `roots` | `v0` |
| input `a` | `v25` |
| input `b` | `v28` |
| input `c` | `v27` |
| input `modq` | `v29` |
| output `y0` | `v28` |
| output `y1` | `v25` |
| output `y2` | `v30` |

Slothy reuses `v0` after the last required root-lane read and reuses scratch
lifetimes across `v24,v26,v31`. This mapping describes this generated result;
it is not a stable ABI or a required assignment for later solver runs.

The first remote attempt is classified as a driver-contract failure, not an
allocation result: it omitted live-outs `a,b,c`, so Slothy rejected the final
unused values before invoking a meaningful solve.

The candidate remains `investigate`, because this isolated B3 result does not
prove that the surrounding NTT9 schedule fits, and the N1 model is only a
proxy. Complete Forward integration, Pi 5 measurement, and SUPERCOP evidence
remain missing.
