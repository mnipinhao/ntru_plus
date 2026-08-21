# GT32-EXACT-ELF-DYNAMIC-MAP-055 Results

## Decision

The remaining Clean-GT Encap loss is distributed.  It is not one hidden
approximately 100--150 cycle leaf, and it is not ordinary caller glue.

The exact production path contains several medium positive debts, partly
cancelled by the two faster GT Forward producers.  This explains why isolated
kernel wins and cumulative checkpoint movements did not compose into one
component owner.

No production code was changed.

## Inputs and campaign

Frozen 043 ELFs:

| Image | SHA-256 |
|---|---|
| Official | `1b0f1a4353415dd2abfbbe05841be8fbdd3bccf88af036b957f88d476f1f8ad4` |
| Clean GT | `29bf895dbe86c11d32d6e75c75b0bba10e7cb30b1901b246ea1e56a9d0306e9a` |

LBR campaign: CPU 1, ASLR enabled, 64 balanced mirrored launch blocks,
`cpu_core/cycles/u`, period 50,000, `any_call,any_ret`.  The primary unit is
the median of each launch's observed interval values, followed by the median
across launches.  p10/p90 and coverage remain in the JSON.

The same 043 formal benchmark gives Clean GT versus Official Encap:

- paired block median: **+185.63 cycles**;
- 197/256 blocks slower;
- bootstrap 95% CI: **[+162.08, +200.48]**.

## Direct leaf map

Core-cycle LBR intervals in the real Encap path:

| Semantic region | Official | Clean GT | GT - Official |
|---|---:|---:|---:|
| Decode | 177.00 | 207.25 | **+30.25** |
| CBD(r) | 118.00 | 144.75 | **+26.75** |
| r producer: NTT vs frontend+N5 | 728.00 | 679.00 | **-49.00** |
| r-hat serializer | 213.00 | 259.00 | **+46.00** |
| SOTP(m) | 146.00 | 141.50 | **-4.50** |
| m producer: NTT vs frontend+N5 | 720.00 | 683.00 | **-37.00** |
| BaseMul | 526.75 | 562.00 | **+35.25** |
| add(m) | 31.75 | 25.00 | **-6.75** |
| ciphertext serializer | 239.00 | 275.00 | **+36.00** |
| Descriptive mapped-leaf total | 2899.50 | 2976.50 | **+77.00** |

The total excludes Hash/SHAKE, cleanup bodies, and non-leaf intervals.  It is a
descriptive sum of robust leaf medians, not a replacement for whole-operation
timing.  TSC/CPU-cycle scaling, sampling skid, and omitted nested subtrees make
direct subtraction from the +185.63 whole-operation number invalid.

Nevertheless, the shape is decisive:

- the largest mapped positive interval is only +46 core cycles;
- both GT Forward producer regions remain faster (-49 and -37);
- Decode, CBD, both serializers, and exact-path BaseMul each leave medium debt;
- direct caller intervals are normally one cycle, and the entry-to-decode
  interval is comparable (Official 6.75, GT 6.0).

Thus there is no evidence for a large standalone transition/caller interval.

## PMU classification

Separate exact-ELF sampling used 32 process repetitions per image and LBR call
chains to retain only samples whose visible stack contained Encap.  The method
is qualitative: nested call depth can evict the outer Encap frame, and sampled
events have skid.

| Event class | Official visible samples | GT visible samples | Direction |
|---|---:|---:|---|
| cycles | 516 | 608 | GT higher |
| IDQ uops not delivered | 442 | 601 | GT higher |
| L1D pending cycles | 14 | 79 | GT much higher, low absolute coverage |

The GT pending-load samples concentrate in:

- `ntruplus768_ntt_m_avx2`: 33/79;
- `ntruplus768_ntt_frontend_avx2`: 20/79;
- `ntruplus768_unpack_m_body_avx2`: 17/79;
- general B3 and caller/unknown: the remainder.

This supports a mixed frontend plus load-dependency explanation rather than a
single arithmetic hotspot.  It does not justify assigning the sample-count
difference as an exact cycle budget.

## Consequence

The useful optimization targets are now explicit but individually modest:

1. Decode producer work / load dependency;
2. both Q24 serializers (already proven at low tens of TSC in 054);
3. the exact Encap BaseMul execution context;
4. GT frontend/N5 pending-load behavior, only if a structural representation
   change deletes work rather than merely changing code shape.

Hash attribution remains closed.  New prefix checkpoints, padding sweeps, and
attempts to assign the residual to one function are not justified by 055.

