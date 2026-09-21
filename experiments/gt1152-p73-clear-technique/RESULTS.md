# P73 — one clear technique instead of three

`secure_clear()` branched three ways on platform: `memset_s` on Apple,
`explicit_bzero` on glibc, a volatile byte loop otherwise.  mlkem-native uses
**one** technique everywhere except Windows — a plain clear plus a compiler
barrier — and cites @[FIPS203, Section 3.3, Destruction of intermediate values]
for the requirement.  This adopts that.

```c
#if defined(_WIN32)
    SecureZeroMemory(v, len);
#elif defined(__GNUC__) || defined(__clang__)
    memset(v, 0, len);
    __asm__ volatile("" : : "r"(v) : "memory");
#else
    { volatile uint8_t *p = v; while (len-- > 0) *p++ = 0; }
#endif
```

The barrier is what stops the store being removed as a dead write; the
volatile loop is kept for compilers without GNU inline asm.

## Measured, KEM level, control differing only in this file

| | A76 decaps | A76 encaps | M2 decaps |
|---|---:|---:|---:|
| three-way branch | 43,734 / 43,731 / 43,717 | 46,493 / 46,492 / 46,485 | 5,410 |
| one technique | 43,706 / 43,705 / 43,669 | 46,416 / 46,407 / 46,425 | 5,390 |

Neutral-to-better on both hosts: decaps about -30 cycles and encaps about -70
on A76, decaps -20ns on M2.  keygen is dominated by the rejection loop and its
spread swamps the effect.  All gates pass, KAT byte-identical,
`nonzero_after=0` unchanged.

## What it also removes

`memset_s` is C11 Annex K, optional and unevenly implemented.  macOS provides
it but does not define `__STDC_LIB_EXT1__`, so the header had to declare it by
hand and force `__STDC_WANT_LIB_EXT1__` before `<string.h>` — an include-order
dependency across every translation unit.  That whole hack is gone, along with
the bounds-check semantics we never used.

## Correcting a measurement I reported

I first measured this technique at 454.0ns against 442.0 for `memset_s` and
called it "the worst option".  That was a single noisy sample read as a result.
On a clean re-run of 200 samples both sit at **441.5ns min, 442.0 p5** — they
are indistinguishable, and at KEM level the barrier version is slightly ahead.
The conclusion I drew from the bad number was wrong.

Two other things measured along the way, both refuting suggestions I had made:

- **`dc zva`** (my proposal): 46.5ns on M2 against libc's 38.5ns for the same
  2,304 bytes.  Both hosts report `DCZID_EL0 = 0x4`, 64-byte blocks, DZP=0, so
  it is available — it is simply not the best strategy, because libc already
  picks per microarchitecture.  A76 was the other way, 72.0 against 77.3.
- **Hand-written `stp q` wipe loops** are the slowest of the three everywhere:
  60.0ns on M2 and 144.0 cycles on A76, against libc's 38.5 and 77.3.

## Not applied to production 768/864 yet

They carry their own copy of this header, and NTRU+768's release gate pins its
contents:

```python
require("internal/secure_clear.h",
        ("static inline void gt_secure_clear", "GT_SECURE_CLEAR_AUDIT_HOOK",
         "volatile uint8_t *cursor"))
```

`volatile uint8_t *cursor` is the fallback loop, so adopting this there means
updating `check_zeroization.py` in the same change and re-running both trees'
release gates.  That is a separate piece of work, not a drive-by edit.
