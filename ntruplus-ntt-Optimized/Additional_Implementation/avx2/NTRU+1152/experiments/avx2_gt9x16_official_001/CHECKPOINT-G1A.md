# Checkpoint G1A: all-shortlist edge oracle closure

G1A prices no edge and adds no assembly. It closes the mathematical and
physical contract needed before G1B--G1E can change a producer tail or consumer
head. F1 and F5 are explicitly orthogonal experiments; G1A does not imply that
terminal-major forward output must feed an inverse-oriented arithmetic tail.

## Portable edge contract

`generated/g1-edge-oracles.json` implements
`gt-representation-edge/v1`. Every edge has:

```text
R_producer -- E=(Pi,B,g,s) --> R_consumer
```

where `Pi` is a complete 1,152-cell component permutation, `B` is the terminal
basis map, `g` is the component gauge relation, and `s` contains transform and
Montgomery scales. The edge also records whether work can be absorbed into:

```text
forward_twiddle      basemul_weight       basemul_finalizer
baseinv_adjugate     baseinv_den          inverse_twiddle
inverse_normalization                    load_address / store_address
```

The architecture-neutral schema is documented in
`../../../common/gt9x16/EDGE-CONTRACT.md`. AVX2 and NEON may attach different
instruction costs to the same edge without changing its component identity.

## Closed edges

| Edge | Closure | Remaining obligation |
| --- | --- | --- |
| F1 D1 store → terminal arithmetic | layout and scale closed | measure fused producer-tail debt and audit YMM pressure |
| F3 D1 → cheap basis family | depth-2 generator family closed | select a concrete matrix by symbolic arithmetic search |
| F4 D1 store → BMAdd/downstream | layout closed | audit the actual encapsulation downstream algebra, scale, and range |
| F5 BMScale store → inverse head | layout and decapsulation scale closed | measure tail debt and inverse-head credit together |
| F5 BaseInv store → inverse head | layout closed | derive direct inverse normalization and preserve `den[18]` semantics |

All five permutations preserve `(branch,p,q,j)` exactly and are proved
bijections over 1,152 active `int16` cells. No edge contains a paid standalone
conversion.

F3's closed family contains signed-permutation generators, adjacent and
even/odd Hadamard maps, and even/odd permutation, with composition depth at
most two. Every listed 4×4 matrix has a generated inverse modulo 3457. The
selected matrix remains null, so this result does not authorize F3 assembly.

## Edge debt and credit

`generated/g1-edge-debt-matrix.json` changes the cost model from layout counts
to producer debt and consumer credit:

```text
net delta = producer debt - consumer credit
```

Only F0 control contains zero cycle deltas, by definition. Every unmeasured F1,
F3, F4, and F5 cycle field remains null. Checkpoint E's 144-instruction F1/F5
figures are retained only as static explicit-schedule estimates.

G1 records edge costs and may reject clearly dominated views. It does not pick
a complete-path winner. That decision is reserved for G2:

```text
F_E + BMAdd + actual downstream
2F_M + BMScale + I_M
F_I + BaseInv + I_I
```

## Next checkpoints

- G1B measures D1 persistent-S/D versus D1 with terminal-major reconstruction
  fused into the real forward tail.
- G1C separately measures BMScale-tail+inverse-head and
  BaseInv-tail+inverse-head prototypes.
- G1D audits and prototypes BMAdd plus its actual encapsulation downstream.
- G1E symbolically searches the closed cheap terminal-basis family before any
  basis-specific assembly.

G1B and G1C may proceed independently. Neither is a prerequisite for the
other, and neither selects a universal representation.
