# P74 — the same clear technique in production 768 and 864

P73 adopted mlkem-native's single clear technique in the 1152 experiment tree.
This carries it into production, where it turned out to matter far more than
the 1152 measurement suggested.

## NTRU+768 on macOS was using the slowest possible clear

```c
#elif defined(__STDC_LIB_EXT1__)
    (void)memset_s(address, length, 0, length);
#elif defined(__GLIBC__)
    explicit_bzero(address, length);
#else
    volatile uint8_t *cursor = address;   /* <- macOS landed here */
```

macOS provides `memset_s` but does not define `__STDC_LIB_EXT1__`, and it is
not glibc, so **every one of the 35 clears per KEM flow ran a volatile byte
loop** — 26,928 bytes, one byte at a time, unvectorizable by construction.

| M2, NTRU+768 | before | after | |
|---|---:|---:|---:|
| keygen | 11,460 | 6,700 | **-41%** |
| encaps | 9,410 | 6,450 | **-31%** |
| decaps | 6,880 | 3,880 | **-44%** |
| total | 27,750 | 17,030 | **-39%** |

NTRU+864 guarded the same branch on `__APPLE__` instead, so it already reached
`memset_s` and is unchanged on M2: 16,740 -> 16,730.  The bug was one missing
platform test in one of three near-identical copies of the same header, which
is the argument for having one technique rather than three.

## A76

Both trees reached `explicit_bzero` there, so this is barrier-vs-libc:

| A76 total | before | after | |
|---|---:|---:|---:|
| NTRU+768 | 108,095 / 108,310 / 108,003 | 107,703 / 107,830 / 107,701 | -0.32% |
| NTRU+864 | 108,562 / 108,604 / 108,444 | 108,407 / 108,485 / 108,509 | flat |

768 is consistently ahead across three runs; 864 sits inside its own spread.
Neither host regresses on either tree, which with P73's 1152 result covers all
three parameter sets.

## The release gates

Both trees pin this header's contents, and they pinned different things:

- **NTRU+864** required the literal `explicit_bzero`, which this removes, so
  its gate failed and had to change.
- **NTRU+768** required `volatile uint8_t *cursor`, the fallback loop, which
  survives — its gate passed untouched.

I had predicted the opposite in P73, naming 768's gate as the blocker.  Both
now pin the **barrier** instead, because that is the mechanism that makes the
clear survive optimization; pinning one libc's name for the clear was never
testing the property that matters.

`make check` passes on both trees with KAT hashes unchanged
(`22c72039...eaa8` and `0c912274...e61c`), `nonzero_after_clear=0`, and the
same clear_calls/clear_bytes as before.

## Also updated

`NTRU+768/docs/IMPLEMENTATION.md` §10 described the old three-way selection.
