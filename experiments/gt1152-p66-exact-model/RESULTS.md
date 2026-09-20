# P66 — there is no 1152 model to find, and none is needed

The plan after P65 was to find or build an exact model of the 1152 inverse, in
the shape of 864's P7-C0, so the per-lane constant tables could be re-indexed to
the (component, half) lane basis.  Neither is the right step.

## 1152's kernels are 864's, remapped

`gt1152-p07-inverse/generate_kernels.py` states it plainly:

> These are immediate remaps: the instruction multiset is preserved exactly, so
> the NTRU+864 A76 schedule stays legal. [...] no solver was run for 1152, so
> Slothy's cycle annotations were stripped rather than carried over.

`inverse9.S` and `inverse16.S` are NTRU+864's files with `[base, #imm]` offsets
scaled.  This works because both parameter sets decompose as `k x 288` with
`288 = 2 (half) x 9 (s) x 16 (t)`; only `k` differs, 3 against 4.  The kernels
are per-component, so only the strides change.

`invntt16_tail_asm` is the exception — its output count grows with the component
count — and it was rewritten rather than remapped.

`inverse_tables.h` is numerically identical between the two trees.

## The target basis is already implemented, in the tail

`gt1152-p22-tail-asm/generate_tail.py` produced 1152's tail from 864's, and it
documents and asserts every part of the change this line needs:

| | 864 | 1152 tail |
|---|---|---|
| scratch packing | `lane = 3*top + branch`, six of eight used | **`lane = 4*top + branch`, all eight** |
| fold over `top` | `ext #6` + `add` | **`ext #8` + `add`** |
| output extraction | `out[27k + branch]`, branch < 3, three `UMOV`/`STRH` | **`out[36k + branch]`, branch < 4, one `STR D`** |
| terminal table row | `[A,A,A,B,B,B,0,0]` | **`[A,A,A,A,B,B,B,B]`** |

That is exactly the (component, half) basis P64 and P65 identified, and it is
correct, shipped and in production use for `s = 8`.

## The main kernel's arithmetic is already compatible

`invntt16_asm` folds with `ext v.16B, vA.16B, vA.16B, #8` plus `add`, thirty-two
times — the same four-halfword rotation the tail uses.  With lanes packed as
`4*top + branch`, that fold lands the four components in lanes 0-3, which is
precisely what `STR D` wants.  The change is in the input packing and the output
extraction, not in the transform.

## What actually has to change

The generator's own note says why the main's table was left alone:

> invntt16_main_constants is unchanged -- invntt16_asm packs its lanes by the
> 16-axis, not by (top, branch), so it needs no repacking

So the main's lanes currently encode the 16-axis, and its terminal table is
shared with 864 because of that.  Moving it to `4*top + branch` means the
terminal constants become per-`s`: eight tables where there is now one, roughly
8KB against 1KB.  The values are a repacking of information the current table
already holds, in the `[A,A,A,A,B,B,B,B]` form the tail generator builds and
asserts row by row.

## Next gate

Extend `generate_tail.py`'s transformation from `s = 8` to `s = 0..7`.  It is a
mechanical, asserted rewrite of a kernel that is already correct, not a new
derivation — which is why no exact model is needed.

Two things to carry in:

- 1152's kernels were never scheduled for 1152.  Any cycle prediction made
  against them inherits 864's schedule, and P36 measured `inverse9` at about
  2,215 cycles against a dependency-relaxed probe of 2,005.  A windowed
  re-solve is a separate, independent opportunity.
- P64's predicted margin on Cortex-A76 is 1.1%.  Every prediction in this
  campaign that survived to assembly came in smaller than its probe.
