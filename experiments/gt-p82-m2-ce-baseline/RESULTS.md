# P82 — the M2 baseline has to include CryptoExtension, and then 864/1152 lose

The SUPERCOP comparison is A76-only, and the official submission there carries
no SHA3 path at all: `fips202.c` in `crypto_kem/ntruplus{768,864,1152}/aarch64`
has zero references to `__ARM_FEATURE_SHA3`, `eor3` or `f1600`.  Benchmarking
GT against it on Apple silicon therefore credits GT with a Keccak backend the
baseline simply does not have.  Upstream does ship one, in
`ntruplus-ntt-Optimized/.../NTRU+*/CE/`, so the honest M2 baseline is
Official + CE.

## The upstream CE permutation violates AAPCS64

Building that baseline is not straightforward, because `CE/f1600.S` writes
`v8-v15` and neither saves nor restores them:

```asm
f1600:
_f1600:
    mov x2, x0
    ldr d0,  [x0, #0]        /* straight into the callee-saved range */
    ...
    str d24, [x0, #192]
    ret                      /* nothing restored */
```

AAPCS64 makes the low 64 bits of `v8-v15` callee-saved, so any caller holding a
`double` across the call is corrupted.  `f1600check.c` demonstrates both halves:

```
  輸出相同: yes
  upstream       d8-d15 保存: NO
  patched        d8-d15 保存: yes
```

That is also the answer to a symptom seen repeatedly earlier in the day and
worked around rather than diagnosed: timing harnesses linked against official
builds returning `0` or `-inf`.  The timer's own accumulators were living in
`v8-v15`.

`f1600-aapcs.patch` adds the save/restore — four `stp`, four `ldp`, output
bit-identical.  It is applied only to the measurement copy; the vendored
upstream tree is untouched, because patching it would stop it being the
baseline.  NTRU+864's release gate asserts this property for the GT backend
(`test_keccak_v84a: pass (100003 states, d8-d15 preserved)`); upstream has no
equivalent test.

## M2 Pro, ns per operation, min of 41 x 300

| set | implementation | keygen | encaps | decaps |
|---|---|---:|---:|---:|
| 768 | Official (portable Keccak) | 4,570 | 5,353 | 3,860 |
| 768 | **Official + CE** | 4,047 | 4,513 | 3,380 |
| 768 | **GT** | **3,877** | **4,213** | **3,140** |
| 864 | Official (portable Keccak) | 4,987 | 6,143 | 4,603 |
| 864 | **Official + CE** | **4,427** | **5,177** | **4,033** |
| 864 | GT | 4,517 | 5,210 | 4,153 |
| 1152 | Official (portable Keccak) | 7,710 | 8,047 | 6,030 |
| 1152 | **Official + CE** | **6,883** | **6,780** | **5,267** |
| 1152 | GT | 7,253 | 6,863 | 5,373 |

Against the CE baseline:

| set | keygen | encaps | decaps |
|---|---:|---:|---:|
| **768** | **-4.4%** | **-6.7%** | **-7.2%** |
| 864 | +2.4% | +0.6% | +3.0% |
| 1152 | +4.6% | +1.2% | +2.0% |

**Only NTRU+768 wins on M2.**  Against the portable baseline all three appeared
to win by 6-22%; most of that was the backend, not the arithmetic.

## A76, cycles per operation, median of 65 x 60

Unchanged by any of this, because neither side has FEAT_SHA3 there:

| set | implementation | keygen | encaps | decaps |
|---|---|---:|---:|---:|
| 768 | Official | 38,555 | 38,754 | 33,478 |
| 768 | GT | **31,611** | **29,615** | **27,709** |
| 864 | Official | 44,240 | 46,238 | 40,701 |
| 864 | GT | **37,703** | **36,337** | **34,431** |
| 1152 | Official | 67,654 | 59,262 | 52,391 |
| 1152 | GT | **58,018** | **46,894** | **43,559** |

## What this says

768 is the parameter set that has had the encapsulation and unpacking work:
packed16 encap reduction, the compact lazy encap NTT, checked unpack direct
output mapping, the zero decap top-split elimination.  864 and 1152 have none
of them.  On A76 that does not show, because the machine is multiply-port bound
and the extra work hides in the shadow; on M2 there is no shadow.

That is the campaign's central finding arriving at the KEM level: what 864 and
1152 gain in the transform they give back elsewhere, and only A76 conceals it.
