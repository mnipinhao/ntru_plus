# Register-flow and memory audit

## Pass 1: one inverse NTT9 block

**Entry.** `x0` points to eight contiguous P8 column vectors, `x1` to one
component's first tail scalar, `x2` to FR-0 row zero, and `x3` to nine public
inverse-twist vectors. `v0-v7,v16` load rows 0 through 8; every lane is one of
eight adjacent GT columns for a fixed `(top, component, block)`.

**Inverse NTT9.** `B3INV` performs two oriented radix-3 layers. The first layer
acts on row triples; public `eta` corrections regroup the three branches; the
second layer produces logical `s` order. Public constants occupy `v17-v22`,
`v23-v29` are radix-3/quotient/transpose scratch, and `v30` holds q. Constants
are normal R0 values paired with rounded reciprocals, so Algorithm 10 maps R0
to R0 directly. Two weighted B3 products or three twists are issued together.

**Inverse twist and layout.** Logical `s=0..8` receives one public inverse
twist per vector. After public register renaming, `v0-v7` hold `s=0..7` and
`v16` holds `s=8`. Three levels of `trn1/trn2` transpose the 8x8 main square:
`v22-v29` leave as eight column vectors whose lanes are `s=0..7`. The tail
lanes in `v16` are stored at public 16-byte strides. The padding lanes 6 and 7
of each tail vector are never addressed.

**Exit.** The arithmetic block touches no stack and no `v8-v15`. Its only
cross-lane work is the required 8x8 transpose and fixed public lane movement.
The next consumer sees the exact M5D P8+tail ABI.

## Pass 2 main: packed alpha/beta inverse NTT16

**Entry.** `x0` is one natural-output component/half base; `x1/x2` point to the
alpha/beta P8 banks; `x3/x4` point to public stage and scale tables. For each
column, `ldr dN` loads four alpha lanes and `ldr d30` plus `ins` places four
beta lanes in the high half. Public bit-reversed register placement maps NTT16
states 0..15 onto `v24,v1-v7,v16-v23`.

**Inverse NTT16.** Each `B2X4` loads four adjacent `(b,b')` pairs into `v0`,
issues four `sqrdmulh`, four `mul`, and four `mls`, then performs public
butterfly updates. `v25-v28` are quotient/saved scratch, `v29` is destructive
scratch, and `v31` is q. Using `v0` is an encoding constraint: halfword
vector-by-element operands must use the low vector bank. Lanes 0..3 remain
alpha and lanes 4..7 remain beta.

**Finish/store.** A public scale is applied per completed state. `ext #8`
exposes beta lanes, then fixed Algorithm-10 Barrett multiplications implement
top recombination. Each completed vector is destroyed and emitted with `umov` plus
`strh` to eight public, component-strided natural positions. This avoids a
third buffer pass, but costs 128 static scalar stores per main block and makes
the block large.

## Pass 2 tail

The same 16-state register bank loads 16 tail vectors. Only lanes 0..5 are
meaningful; public lane extraction writes the six cubic components at each
natural tail position. The dummy third pointer argument exists only so stage
and scale table pointers use the same `x3/x4` convention as the main block.

## ABI and size result

The three arithmetic blocks have zero stack references, zero `v8-v15`
references, zero branches, and zero coefficient spills. The C wrappers still
have a 48-byte GPR-only call frame for public loop counters and saved link/GPR
state; therefore only the arithmetic blocks—not the complete wrapper—are
described as stackless. M5E-r1 totals 7,292 code bytes, down from 10,744 for the
initial widening-Montgomery realization.
