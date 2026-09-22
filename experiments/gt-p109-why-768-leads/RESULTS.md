# P109 — 768 leads on M2 because of its SHAKE wrapper, not its transform

864 and 1152 win 2.5-6.0% on M2 where 768 wins 8.8-15.3%.  This asks why, and
the answer is not the one the whole campaign has been working on.

## Keccak dilution is not the reason

Permutation counts, instrumented at the C entry to the permutation, are
**identical between GT and Official** for every set and operation:

| set | keygen | encap | decap |
|---|---:|---:|---:|
| 768 | 13 | 21 | 12 |
| 864 | 14 | 24 | 14 |
| 1152 | 21.4 | 32 | 19 |

And the permutation itself costs the same on both sides: **upstream's CE
`f1600` 158.33 ns, GT's `keccakf1600_v84a` 158.33 ns**, measured on the same
state.

So Keccak is subtractable, and it is 48-73% of every operation -- **and almost
the same share for all three sets** (768 50/70/51, 864 49/72/53, 1152
48/73/55).  Dilution is not what separates them.

What separates them is the contestable remainder:

| set | keygen | encap | decap |
|---|---:|---:|---:|
| **768** | **-17%** | **-47%** | **-31%** |
| 864 | -9% | -19% | -5% |
| 1152 | -9% | -22% | -10% |

**768 saves two to six times as much of the part that is actually contested.**

## And that remainder is the hash wrapper, not the arithmetic

`hash_f`, `hash_g` and `hash_h` timed directly, both sides linked into one
binary, Official carrying the CE permutation, outputs verified byte-identical
over 64 inputs per set:

| | hash_f | hash_g | hash_h |
|---|---:|---:|---:|
| 768 GT / Official | **0.86** | **0.86** | **0.55** |
| 864 | 0.93 | 0.93 | 0.98 |
| 1152 | 0.92 | 0.92 | 0.89 |

Per-hash permutation counts are identical too (768 9/10/2, 864 10/11/3, 1152
13/15/4), so **the whole difference is the absorb and squeeze around an
identical permutation.**

What GT saves on hashing, against what it saves on the operation:

| set | hashing, encap | operation, encap | hashing, decap | operation, decap |
|---|---:|---:|---:|---:|
| 768 | **732** | 675 | **505** | 565 |
| 864 | **278** | 272 | **150** | 105 |
| 1152 | **456** | 419 | **281** | 259 |

**The hash accounts for the entire operation-level advantage in all six cases**,
and slightly more than it -- because the arithmetic gives some back.  P102 and
P104 measured exactly that: GT's kernels are **slower** than Official's in five
of the six, by +18 to +71 ns.

## What this means

The campaign has spent itself on the transform, which is where GT is **behind**.
Its M2 margin comes from the sponge wrapper, and 768's wrapper advantage is two
to three times 864's and 1152's.

If 864 and 1152 reached 768's ratio -- a 14% hash saving rather than 7-8% --
they would gain roughly **290 ns on encapsulation and 170 on decapsulation**.
For 864's decapsulation that is -2.5% becoming about **-6.7%**, against the
-1.1% to -2.5% that P29, the route and the tail delivered together.

`shake256_prefixed` is character-identical in the three trees, `-fomit-frame-pointer`
makes no difference, and the three Official `fips202.c` are identical, so the
remaining per-set spread is not yet explained and part of it is
process-level layout.  What is not in doubt is the ranking and its size: **the
wrapper is worth two to four times what the entire transform campaign has
delivered on 864's decapsulation.**
