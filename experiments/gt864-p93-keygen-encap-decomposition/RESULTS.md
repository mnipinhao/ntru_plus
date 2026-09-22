# P93 — NTRU+864's key generation and encapsulation, kernel by kernel

P92 did decapsulation.  This finishes 864 by the same method: both
implementations linked into one binary, the official kernels renamed, each timed
directly under the gated harness.

## Key generation

The two sequences are identical except that GT packs with `tobytes_small` twice
and `tobytes` once where Official uses `tobytes` three times.

| kernel | GT | Official | ratio | calls | GT total | Official total |
|---|---:|---:|---:|---:|---:|---:|
| cbd1 | 43.0 | 40.2 | 1.07 | 2 | 86 | 80 |
| triple | 23.5 | 19.6 | 1.20 | 2 | 47 | 39 |
| ntt | 243.1 | 259.6 | **0.94** | 2 | 486 | 519 |
| baseinv | 380.4 | 385.7 | 0.99 | 2 | 761 | 771 |
| basemul | 128.9 | 151.4 | **0.85** | 2 | 258 | 303 |
| tobytes_small / tobytes | 69.8 | 78.2 | **0.89** | 2 | 140 | 156 |
| tobytes, full, both sides | 97.1 | 78.2 | 1.24 | 1 | 97 | 78 |
| **sum** | | | | | **1874** | **1948** |

**GT's key-generation kernels are 74 ns ahead.**

## Encapsulation

GT packs **once** where Official packs twice: `hash_g_fr0` hashes straight out of
the GT representation, so the serialization Official needs before `hash_g` never
happens.

| kernel | GT | Official | ratio | GT calls | Official calls | GT total | Official total |
|---|---:|---:|---:|---:|---:|---:|---:|
| frombytes | 81.6 | 78.4 | 1.04 | 1 | 1 | 82 | 78 |
| cbd1 | 43.1 | 40.2 | 1.07 | 1 | 1 | 43 | 40 |
| ntt | 243.2 | 259.6 | **0.94** | 2 | 2 | 486 | 519 |
| sotp_encode | 43.7 | 43.4 | 1.01 | 1 | 1 | 44 | 43 |
| basemul_add | 147.5 | 178.3 | **0.83** | 1 | 1 | 148 | 178 |
| pack | 69.7 | 78.2 | 0.89 | **1** | **2** | 70 | 156 |
| **sum** | | | | | | **872** | **1016** |

**GT's encapsulation kernels are 144 ns ahead**, 86 of it from not packing twice.

## 864 complete

| operation | GT kernels | Official kernels | kernels | non-kernel | P91 remainder |
|---|---:|---:|---:|---:|---:|
| keygen | 1874 | 1948 | **-74** | -154 | -228 |
| encap | 872 | 1016 | **-144** | -125 | -269 |
| decap | 1705 | 1637 | **+69** | -115 | -47 |

All three reconcile with P91's independently measured remainders.  **Only
decapsulation's kernels lose, and P92 showed it is entirely the inverse at +87.**

## The packer's full path, and why its store count cannot drop

`tobytes` with the reduction is 97.1 against Official's 78.2, and it is called
once in key generation and once in decapsulation, so it is +38 ns across the two.
Note the same kernel without the reduction, `tobytes_small`, *beats* Official at
69.8.

The cost is structural.  Per 48 coefficients Official issues about 69
instructions -- 18 `trn`, 6 `tbl`, 6 stores.  P87's kernel issues 24 `trn` for a
transpose in which only five of the eight rows carry anything, and **16 stores
where Official issues 6**, because each of its eight nine-byte runs needs an
eight-byte store and a one-byte store.

Halving that by storing ten bytes and letting the next run overwrite the
overlap -- the trick P87 records -- **is not available**.  The 144 runs tile the
output at stride nine, but no two adjacent runs belong to the same six-vector
group: 0 of 143.  Writing run `o` before run `o+9` therefore constrains the
order of the groups, and that constraint graph has a cycle, so no group ordering
satisfies it.  Checked exhaustively, 41 edges over 18 groups.

What remains is the transpose: five streams gathered through an eight-row
network.  Worth perhaps 10-18 ns.

## What is left for 864

| item | ns | note |
|---|---:|---|
| decap inverse | ~43 of +87 | P89; 36 of it risks the Slothy schedule |
| packer transpose, 5 of 8 rows | 10-18 | keygen and decap |
| triple | +8 | keygen |
| cbd1 | +6 | every operation |

Closing all of it would take decapsulation's kernels from +69 to near parity,
which moves the operation from **-1.1% to about -2.8%**.  The permutation is 53%
of 864's decapsulation and identical on both sides, so that is the whole prize.
Key generation and encapsulation have nothing left worth taking.
