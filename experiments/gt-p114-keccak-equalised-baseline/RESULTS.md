# P114 — the strictest M2 baseline: Official's sponge on GT's permutation

P113 found GT's `keccakf1600_v84a.S` 7.3% faster than upstream's `CE/f1600.S`,
so even the Official + CE table credited GT with a Keccak advantage.  This
removes it: upstream's `CE/fips202.c` sponge, unchanged, linked against GT's
permutation renamed to `f1600` -- both are `(state, rc)`, so it is a pure symbol
substitution.  Four builds per set in one session, median of three sessions,
min of 401 x 300 under the clock gate.

**GT wins all nine cells with the symmetric primitive held byte-identical.**

| set | | keygen | encap | decap |
|---|---|---:|---:|---:|
| 768 | Official, SUPERCOP as shipped | 4,488 | 5,160 | 3,868 |
| | | **-15.4%** | **-20.9%** | **-18.8%** |
| | Official + upstream CE | 4,167 | 4,756 | 3,710 |
| | | **-8.9%** | **-14.2%** | **-15.4%** |
| | **Official + GT's permutation** | 4,025 | 4,520 | 3,580 |
| | | **-5.7%** | **-9.7%** | **-12.3%** |
| | **GT** | 3,796 | 4,080 | 3,139 |
| 864 | Official, SUPERCOP as shipped | 4,905 | 5,991 | 4,608 |
| | | **-15.4%** | **-22.0%** | **-16.1%** |
| | Official + upstream CE | 4,553 | 5,270 | 4,155 |
| | | **-8.9%** | **-11.3%** | **-7.0%** |
| | **Official + GT's permutation** | 4,399 | 4,997 | 4,004 |
| | | **-5.7%** | **-6.4%** | **-3.4%** |
| | **GT** | 4,148 | 4,675 | 3,866 |
| 1152 | Official, SUPERCOP as shipped | 7,679 | 7,841 | 6,027 |
| | | **-15.2%** | **-21.7%** | **-17.2%** |
| | Official + upstream CE | 7,126 | 6,948 | 5,487 |
| | | **-8.6%** | **-11.6%** | **-9.0%** |
| | **Official + GT's permutation** | 6,887 | 6,591 | 5,276 |
| | | **-5.4%** | **-6.8%** | **-5.4%** |
| | **GT** | 6,514 | 6,140 | 4,991 |

The `noce` and `ce` rows reproduce P108 to within 0.3%, and P113's claim that
upstream's current `CE/f1600.S` times the same as the March copy P108 used is
confirmed at whole-operation scale: 768 encap 4,756 here against 4,751 there.

## What the total margin is actually made of

Splitting each cell's gap from SUPERCOP's Official into the three steps:

| | total | SHA3 instructions | our Keccak kernel | the arithmetic |
|---|---:|---:|---:|---:|
| 768 keygen | 692 | 321 (46%) | 142 (21%) | **229 (33%)** |
| 768 encap | 1,080 | 404 (37%) | 236 (22%) | **440 (41%)** |
| 768 decap | 729 | 158 (22%) | 130 (18%) | **441 (60%)** |
| 864 keygen | 757 | 352 (46%) | 154 (20%) | **251 (33%)** |
| 864 encap | 1,316 | 721 (55%) | 273 (21%) | **322 (24%)** |
| 864 decap | 742 | 453 (61%) | 151 (20%) | **138 (19%)** |
| 1152 keygen | 1,165 | 553 (47%) | 239 (21%) | **373 (32%)** |
| 1152 encap | 1,701 | 893 (52%) | 357 (21%) | **451 (27%)** |
| 1152 decap | 1,036 | 540 (52%) | 211 (20%) | **285 (28%)** |

**Roughly a fifth of every margin is our Keccak kernel** -- strikingly uniform,
20-22% in all nine cells, because it is a fixed 10.7 ns per permutation and the
permutation counts scale with the operations.

**SHA3 instructions are the largest single term**, 22-61%.  That one is not ours
at all: upstream builds it by default and SUPERCOP declined to carry it.

**The arithmetic -- what this campaign is about -- is 19% to 60%.**  Its best
showing is 768 decapsulation at 60%, and its worst is 864 decapsulation at 19%,
which is the same cell the inverse study (P111) identified as the outlier.

## Which table to quote

This one, for a claim about Good-Thomas.  The Official + CE table for a claim
about the implementation against upstream's default build.  The SUPERCOP table
only as the figure a reviewer downloading the tarball would reproduce.