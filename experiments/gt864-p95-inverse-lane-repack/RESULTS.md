# P95 — NTRU+864's inverse, taken apart, and the repacking P89 missed

The question, stripped of the layout argument: with a free hand, how fast can
864's inverse be, and what is it actually spending its time on?

## Where the 404 ns goes

Dynamic instruction counts per coefficient, by class:

| class | GT 864 | GT 1152 | share (864) |
|---|---:|---:|---:|
| multiply (`mul`, `mls`, `sqrdmulh`) | 2.02 | 1.98 | 26% |
| add / subtract / bitwise -- the butterflies | 1.67 | 1.45 | 21% |
| load | 1.08 | 1.08 | 14% |
| **`umov` -- lane to general-purpose register** | **1.00** | **0** | **13%** |
| **`strh` -- two-byte store** | **1.00** | **0** | **13%** |
| permute / move | 0.72 | 0.86 | 9% |
| store | 0.34 | 0.41 | 4% |
| **total** | **7.89** | **5.89** | |

The only structural difference between the two is **2.00 instructions per
coefficient of general-purpose round trip**.

## What that is worth

Calibrated on the measurement itself -- 6,818 instructions in 404.1 ns is
**0.0593 ns per instruction**, about 4.8 IPC, so the code is already scheduled
well:

| | instructions/coefficient | ns |
|---|---:|---:|
| today | 7.89 | 404 |
| **with the `umov`/`strh` replaced by wide stores** | **~6.2** | **~319** |
| Official, for scale | 4.52 | 298 |

**The gap falls from +106 ns to about +21, and none of it requires matching
Official's layout.**  1152 is the proof: 34% more instructions than Official and
only 4% slower, because on M2 extra *vector* instructions are nearly free.  It
is the trip through a general-purpose register that is not.

## Why the round trip is there

`invntt16` writes, per output group, **four halfwords at stride three** --
positions `3j + c` for four consecutive `j` at one fixed `c`.  Four values, none
adjacent, so each needs `umov` then `strh`: eight instructions a group, 32
groups a call, six calls.

The output index is `position = (t + 16h) * 27 + 3j + c`, with
`j` in 0..8 (radix-9), `t` in 0..15 (radix-16), `h` in 0..1 (half),
`c` in 0..2 (the degree-3 base-ring component).  A call fixes `c` and spreads
four `j` across the inner lanes; six calls are 3 components x 2 blocks of four
`j`, and `j = 8` goes to the tail.

## P89 ruled out the wrong repacking

P89 asked whether the inner four lanes could become the **components**, the way
1152's P67/P68 did.  They cannot: 1152 has four components filling four lanes
exactly, 864 has three, so a call would cover one `j` instead of four and eight
calls would be needed where six suffice.  That is correct.

**It is not the only repacking.**  Let the inner four lanes hold four consecutive
*output positions* `p = 3j + c`, mixing the two axes rather than choosing one:

| call | inner lanes hold `p` | which `(j, c)` |
|---|---|---|
| 0 | 0, 1, 2, 3 | (0,0) (0,1) (0,2) (1,0) |
| 1 | 4, 5, 6, 7 | (1,1) (1,2) (2,0) (2,1) |
| 2 | 8, 9, 10, 11 | (2,2) (3,0) (3,1) (3,2) |
| 3 | 12 .. 15 | (4,0) (4,1) (4,2) (5,0) |
| 4 | 16 .. 19 | (5,1) (5,2) (6,0) (6,1) |
| 5 | 20 .. 23 | (6,2) (7,0) (7,1) (7,2) |

Six calls cover `p = 0..23`, which is `j = 0..7` times `c = 0..2` exactly, and
`j = 8` still goes to the tail.  **The call count does not change.**  A group's
four outputs are now `p, p+1, p+2, p+3` -- four contiguous halfwords, one
`str d`.

## And `invntt16` needs no table change

Checked against the generated tables:

| table | rows shaped `[A,A,A,A,B,B,B,B]` |
|---|---|
| `invntt16_main_constants` | **64 of 64** |
| `invntt16_main_scale` | **32 of 32** |
| `invntt16_tail_constants` | 0 of 64 |
| `invntt16_tail_scale` | 0 of 32 |
| `invntt9_constants` | 8 of 72 |

**The main kernel's constants do not depend on the inner four lanes at all** --
they vary only with `half`.  This is the same property that let 1152 swap its
inner lanes with no table change, and it holds at 864 for exactly the same
reason: the transform's twiddles are scalars applied to a whole base-ring
element, so they are blind to which component or which `j` a lane carries.

So the kernel body and its tables are untouched.  Only the arrangement its
caller writes into the scratch changes, and the eight `umov` + `strh` per group
become one `str d`.

## What it costs to build

The work lands in `packed_i9`, which produces the scratch.  It writes `str d`
half-vectors and `st1 {v.D}[1]` high halves at address-computed offsets, and it
carries **no `umov` or `strh` of its own**, so the placement is addressing rather
than extraction.  Its tables *are* lane-dependent (8 of 72), so changing which
problem lands in which lane means regenerating them -- which is precisely what
1152's P68 did with `generate_i9.py`, and that script is on disk.

The tail stays as it is: its constants are not lane-independent, and it already
writes three contiguous halfwords.

## Expected result

Six calls x 32 groups x (8 - 1) instructions, plus about 100 in the tail:

| | |
|---|---|
| instructions removed | ~1,400 |
| inverse | **404 -> ~319 ns** |
| 864 decapsulation kernels | +87 -> **about 0** |
| 864 decapsulation | -1.1% -> **about -3.2%** |

Against Official's 298 the inverse would still be about 7% behind, because the
Good-Thomas decomposition buys 12% fewer multiplies and pays 37% more
instructions.  That trade wins on A76's single multiply pipe and loses on M2's
four, and no repacking changes it.
