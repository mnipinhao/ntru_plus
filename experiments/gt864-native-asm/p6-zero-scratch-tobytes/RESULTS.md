# P6-A — zero-scratch ToBytes register frontier

P6-A screens the storage-only rewrite before generating a complete ToBytes
kernel. It asks whether the current third-pair route can remain unchanged while
the first two packed pairs are retained entirely in registers.

## Exact storage lower bound

One top has two retained pair results, or 432 arbitrary bytes. With `x18`
reserved for cross-platform AAPCS use and two GPRs required for input/output
pointers, the densest register-only representation is:

```
13 Q registers = 208 bytes
28 X registers = 224 bytes
                         432 bytes
```

The current third-pair route simultaneously carries 18 Q values. Current row 0
then needs a non-destructive row copy and a separate TBL index:

```
13 retained + 18 current route + 1 row copy + 1 index = 33 vectors
```

Only 32 architectural vector registers exist. `proof.py` also checks all 1,296
wire-byte tags and the GPR/vector capacity.

## Pi 5 bridge timing

The storage bridge itself remains interesting after a route redesign. On
Cortex-A76, after empty-loop subtraction:

| Bridge per top | Cycles | Instructions |
|---|---:|---:|
| current 18 full-ST3 plus 36 LDR | 58.999 | 56.001 |
| optimistic 28 UMOV plus 14 FMOV plus 14 INS | 42.000 | 56.007 |

The proxy is about 17 cycles/top faster, or about 34 cycles/full call before
integration. It excludes route, normalization and merge transients.

## Slothy allocation frontier

The local run used the repository requested by the user:

```
PYTHONPATH=/Users/chenpinhao/slothy \
/Users/chenpinhao/slothy_and_ra/.venv/bin/python \
experiments/gt864-native-asm/p6-zero-scratch-tobytes/frontier/run_variants.py
```

Spills were disabled. Synthetic loads/stores only seed and preserve exact live
values; they are not proposed production memory operations.

| Frontier | Slothy result | Meaning |
|---|---|---|
| 31 live + row copy + index | `INFEASIBLE` | current route cannot use a storage-only zero-scratch bridge |
| 30 live + row copy + index | `OPTIMAL` | freeing one vector is sufficient |
| 31 live + row copy, no index | `OPTIMAL` | eliminating/fusing lane repair is sufficient |

The controls show that the exact failure is register capacity, not parser,
model or solver failure. Allocated controls use `v0-v31` and contain no stack
spill. `parse-slothy-log.py` currently mistakes the informational text
`Setting timeout` for a timeout result; the retained raw logs contain `OPTIMAL`
and `selfcheck:OK`.

## Decision

Reject only the **current-route storage-only** P6-A candidate. Do not reject
the zero-scratch objective: the Pi bridge measurement still shows headroom.

P6-B must change the common DAG so that at least one vector lifetime disappears:

1. Produce a consumer-oriented row that may be destroyed after use, avoiding
   the non-destructive row copy; or
2. absorb row TBL repair into the preceding transpose/orientation so there is
   no separately live index; or
3. reduce retained state by one full vector without coefficient reload, byte
   scratch, lane ST3 or output read/modify/write.

Only after that frontier allocates should a complete full/small candidate be
generated, timed and integrated.
