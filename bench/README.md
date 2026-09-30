# Benchmarks

The tools behind the performance figures in the AArch64 packages' READMEs. They
need only this repository and pinned upstream sources.

| Figures in the package READMEs | Tool | Machines |
|---|---|---|
| Per-operation margins against the official implementation, with and without the same Keccak permutation on both sides, and the hash-layer / arithmetic split | [`aarch64/perop/`](aarch64/perop/README.md) | Apple M2 Pro, Raspberry Pi 5 |
| SUPERCOP 20260831 cycles | [`aarch64/supercop/`](aarch64/supercop/README.md) | Raspberry Pi 5 |
| Code size, executed code, cold start | [`aarch64/footprint/`](aarch64/footprint/README.md) | Raspberry Pi 5 |

`perop/` and `footprint/` compare against the official implementation that
[`official/`](official/README.md) assembles: `github.com/ntruplus/ntruplus`
main 3991b2a, in SUPERCOP 20260831's leaf form. Run its `setup.sh` first.
`supercop/` compares against SUPERCOP's own `crypto_kem/ntruplusN/aarch64`
leaf, as shipped.

The AVX2 packages' figures are SUPERCOP 20260831 Native runs on an Intel Core
Ultra 7 155H; no x86 tool is kept here.
