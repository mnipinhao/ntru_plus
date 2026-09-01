# Slothy region and expansion plan

The repository probe found no local Slothy checkout or venv. Repository policy
requires actual Slothy execution on the configured remote host, so this commit
does not claim a Slothy schedule or expected-cycle result.

Assembler macros already expand to real instructions. The relevant choice is
how many independent operations one macro exposes before a scheduling boundary:

- inverse NTT9: two products per B3 weighted branch and three inverse twists;
- inverse NTT16: four butterflies per `B2X4`;
- scale: four independent states;
- top recombination and scalar stores: two states.

Four-way is the main NTT16 choice because it supplies four independent
`mul/sqrdmulh` chains while consuming four quotient registers. Eight-way would
need eight quotients or split the three instruction classes manually, leaving
too little scratch beside 16 live states. One-way is the measured dependency
chain that this revision removes.

The future Slothy workflow is macro-RA/unfold/window-opt. Do not submit the
entire 811-instruction main block as one region. Use these windows:

1. inverse16 layers 0-1;
2. inverse16 layers 2-3;
3. one `SCALE4` plus two `FINISH_MAIN2` groups;
4. inverse9 B3 arithmetic, twist, and transpose as separate regions.

The reserved policy is `x0-x4` concrete ABI pointers, `x8-x9` public scalar
scratch, `v8-v15` forbidden, `v31=q`, and no spills. A symbolic candidate must
first add exact region labels, baseline extraction, kernel contract,
instruction DAG, and pass the canonical Slothy static gates. Until a remote
Slothy log and full-path benchmark exist, candidate status is `investigate`.
