# P75 — SUPERCOP after P69 through P73

**GT 90,097 against the official's 111,419: −19.14%**, from P68's −18.66%.

The P68 leaf was left in the tree as `aarch64-gt1152.p68`, so both versions were
measured in the same run, same host, same compiler set.

| implementation | cycles | P68 run | P40 | P33 |
|---|---:|---:|---:|---:|
| **`aarch64-gt1152`** | **90,097** | 90,586 | 90,942 | 92,079 |
| `aarch64-gt1152.p68` (control) | 90,539 | 90,586 | — | — |
| `aarch64` (official) | 111,419 | 111,367 | 111,441 | 111,403 |
| `opt` | 193,400 | 193,348 | 193,544 | 193,359 |
| `ref` | 297,742 | 297,675 | 297,636 | 297,704 |

```
current vs official   −21,322 cycles   −19.14%
P68     vs official   −20,880 cycles   −18.74%   (its own run recorded −18.66%)
current vs P68        −   442 cycles   − 0.49%   same run
```

The control reproduces its own earlier figure to within 0.08pp, and the
official moved 52 cycles in 111,367 — 0.05%, the run-to-run floor.

## Per-operation, stabilized quartiles

| operation | q1 | P68 run | delta |
|---|---:|---:|---:|
| keypair | 48,622 | 48,624 | −2 |
| encaps | 46,511 | 46,584 | **−73** |
| decaps | 43,768 | 44,005 | **−237** |
| **q1 sum** | **138,901** | 139,213 | −312 |

That decomposes exactly as the direct measurements predicted: decaps carries
P69+P70+P71's −200 cycles on the inverse plus P73's −30, and encaps carries
P73's −70 alone, since the inverse is not on the encapsulation path.  keypair is
unchanged and its spread is the rejection loop, not measurement noise.

`try` is `ok` for all five implementations against checksum
`2275d10293...a317cb91`, the same one P33, P40 and the P68 run recorded, so the
KEM byte contract is unchanged across the whole sequence.

## What landed between the two runs

| gate | A76 inverse |
|---|---:|
| P68 (measured in the previous run) | 5,827 |
| P69 schedule the lane-basis kernels | 5,774 |
| P70 copy-propagate the vector moves | 5,754 |
| P71 overlay the rebase buffer on the scratch | 5,607 |
| P73 one clear technique | — (KEM-level, not in the inverse) |

`refresh_leaf.py` now also carries `secure_clear.h`, which P73 changed; the leaf
conversion was validated before the run by building the KAT against the leaf's
own `.s` files, hashing to `2ddfc810...64c3`.
