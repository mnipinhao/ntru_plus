# Compact DFT3 assembly report

Probe symbol: `gt_d4aos_f32x3_idft3_barrett_probe_asm`, 207 bytes.

Dynamic inventory across sixteen t groups:

- row-state loads: 48; probe stores: 48; constant loads: 4
- `vpmullw`: 64; `vpmulhw`: 80; `vpmulhrsw`: 0
- `vpaddw`: 48; `vpsubw`: 128; `vpsraw`: 48
- `vpshufb`, `vpermq`, `vperm2i128`: zero
- loop branches: 16 executions, 15 taken
- calls, stack bytes, YMM spills: zero

Each t performs one omega relation and forms D0/D1/D2 once. The 48 result stores are
probe-only verification traffic and are not the future terminal-integrated design.
