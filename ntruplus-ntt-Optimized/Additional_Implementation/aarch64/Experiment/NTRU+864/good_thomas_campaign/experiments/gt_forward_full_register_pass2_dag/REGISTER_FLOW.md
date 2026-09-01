# M5R register and run flow

## Public wrapper

`gt864_forward_poly_ntt_full_register(out,in)` allocates a 96-byte ABI frame.
`x29/x30` occupy bytes 0..15, `x19/x20` bytes 16..31, and the low halves
`d8-d15` bytes 32..95.  It then allocates the unchanged 1792-byte P8 object,
runs the unchanged top split, and calls the M5R-B six-bank Pass-2.  Restoration
is the exact reverse.  The ABI change therefore costs eight dynamic vector
pair instructions; the two stack-adjust instructions already existed and only
their immediate changed from 32 to 96.

## Six-bank entry state

- `x6`: immutable FR-0 output base.
- `x7`: immutable P8 input base.
- `x16`: saved link register across the six helper calls.
- `x4=16`: public byte stride for the sixteen scalar tail loads.
- `v13`: bit-reverse-3 byte indices, loaded once.
- `v14`: eight copies of q=3457, loaded once.
- `v15`: `(rho,rho',rho2,rho2',eta,eta',eta^-1,(eta^-1)')`, loaded once.
- `v16/v17`: fixed per-bank tail outputs; they are overwritten by each bank.

The common block is consumed by one `adr`, one `ldp q14,q15`, and one
`ldr q13`.  `v13-v15` remain bit-identical across all six helper calls.

## Each bank run

For `bank=3*top+component`, the wrapper derives:

- `x0 = P8 + 256*bank`: sixteen main vectors.
- `x1 = P8 + 1536 + 2*bank`: first scalar tail coefficient.
- `x2 = NTT16_table[top]`: 21 vectors; bitrev is no longer present.
- `x3 = NTT9_table[top]`: 32 twist vectors.

The 617-instruction helper performs the same stages and equations documented
by M5Q:

1. gather/twist/tail NTT16 into fixed `v17` and `v16`;
2. main branch twist and four NTT16 layers;
3. two 8x8 transposes;
4. first eight twists and oriented NTT9;
5. second eight twists and oriented NTT9.

The former `a_saved/b_saved/c_saved/g*_saved` symbolic values are not new
values.  Their consumers now read the original source directly, extending its
true lifetime.  The former `hold8` reads fixed `v16` directly.  Thus all
thirteen removed `orr` instructions are identity copies, not arithmetic nodes.

The physical output map returned by pinned Slothy is:

```text
out0..out17 =
v24,v8,v11,v1,v0,v22,v3,v4,v9,
v21,v19,v30,v25,v12,v10,v27,v31,v5
```

All eighteen are stored immediately before the next helper call, so no output
is held across banks and no coefficient spill is introduced.

## Exact dynamic ledger

```text
Pass-2 fixed setup                         4
common adr + ldp(q,roots) + ldr(bitrev)   3
six bank pointer/table setups and calls  36
six helpers = 6 * 617                  3702
six helper returns                         6
FR-0 stores = 6 * 18                    108
outer LR restore and return                2
-------------------------------------------
Pass-2                                  3861
```

The full kernel is `24 wrapper + 849 top split + 3861 Pass-2 = 4734`
instructions.  Relative to M5O, Pass-2 removes 99 instructions and the larger
public ABI wrapper adds eight, for a net full-path reduction of 91.
