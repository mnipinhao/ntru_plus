# M5H: complete NTT9 level-1 Slothy pressure gate

This bounded experiment expands M5G from one B3 to the three independent B3s
that consume one complete already-twisted NTT9 block. Nine active data vectors
become real symbolic dataflow; the untouched other column block remains nine
reserved caller-saved registers.

The source has 45 real instructions, nine live outputs, shared `roots` and
`modq`, no memory, and no physical registers. Slothy may allocate only
`v0-v7,v25-v31`; `v8-v15` are ABI-forbidden and `v16-v24` model the preserved
other block. This tests allocation existence, not the preceding NTT16 register
placement or the following eta/level-2 schedule.

Remote Slothy 0.2.2 returns an OPTIMAL 48-cycle N1-proxy schedule with 36
stalls and passes selfcheck. The emitted region uses exactly all fifteen
allowed registers `v0-v7,v25-v31`; it uses none of reserved `v8-v24` and has
no memory, GPR, branch, stack, or spill instruction. The returned source also
assembles as AArch64. This closes level 1 only: its full use of the window is a
warning that level-2 eta products must consume and reuse level-1 lifetimes
rather than assuming spare support registers.
