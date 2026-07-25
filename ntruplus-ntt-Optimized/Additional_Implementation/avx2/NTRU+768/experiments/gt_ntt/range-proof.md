# Range argument for the AVX2 GT prototype

All statements below assume the explicit prototype precondition
`|a[i]| <= q-1`, where `q=3457`.  Congruences are modulo `q`; `R=2^16`.

1. The top-split Montgomery product is in `[-(q-1),q-1]`.  The two raw
   branch expressions are at most `2(q-1)` and `3(q-1)` respectively, which
   fit signed 16-bit lanes.
2. The branch twist is another Montgomery product.  Its input product obeys
   the scalar reducer precondition, and its output returns to a one-modulus
   residue bound.
3. A DFT3 output is a sum/difference of three one-modulus residues, hence is
   bounded by `3(q-1)=10368`.
4. Each radix-2 stage adds or subtracts one Montgomery-reduced term bounded
   by `q-1`.  With lazy additions, the bounds after stages 1 through 5 are
   `4(q-1)`, `5(q-1)`, `6(q-1)`, `7(q-1)`, and `8(q-1)`.
5. The largest bound is `8(q-1)=27648 < 32768`, so every lazy signed-int16
   add/sub remains representable.

The hand-scheduled frontend/stage1+2 preserves these exact reduction points.
Prepacked CRT byte offsets and twist/qinv vectors change only addressing and
constant construction.  Top split and twist still each perform a fixed-factor
Montgomery reduction before the lazy DFT3 sums.  Stage 1 reduces the distance-16
high operand by Montgomery identity `R`; stage 2 reduces its distance-8 high
operand by either `R` or `omega32^8`.  There is deliberately no Barrett pass at
the frontend, stage-1, or stage-2 boundary: outputs remain within `3(q-1)`,
`4(q-1)`, and `5(q-1)`, respectively, and the existing stage3+4+5 proof reaches
only `8(q-1)` before its packed Barrett checkpoint.

The fused producer's 1536-byte stack allocation is the complete frontend
`row01/row2` semantic scratch.  Standalone frontend and stage1+2 symbols use no
stack, and the fused symbol contains no additional spill slot.  Exact boundary
tests compare all 768 int16 words against the intrinsic producer, including
full-range and in-place inputs.

The direct and half-handoff candidates are only dependency-order changes to
the same arithmetic.  For stripe `q`, they generate pair A=`(q,q+16)` and pair
B=`(q+8,q+24)`.  Direct keeps A's three stage-1 values live until B is ready;
half-handoff temporarily stores and reloads those three values.  Neither path
adds, removes, or moves a Montgomery/Barrett checkpoint, so their bounds remain
`3(q-1)`, `4(q-1)`, and `5(q-1)` at the same semantic points.  Exact stage2
boundary tests cover full-range and random inputs.

The low-level direct and half-handoff entries may begin writing stage2 before
all input coefficients have been loaded, so their 1536-byte output and
768-coefficient input regions must not overlap.  Their public wrappers allocate
a private stage2 scratch, preserving the public `out==in` contract without a
secret-dependent alias check.  The non-overlap requirement is an API
precondition, not a constant-time branch; every direct/half address still
depends only on the public stripe index and generated public offset tables.

The forward argument is followed by separate SoA basemul and inverse arguments
below.  Together they cover the complete prototype polynomial multiplication.

## Signed identity reducer in stage1+2

At the stage1 and one stage2 butterfly, the fixed Montgomery factor is `R`.
The mathematical operation is therefore identity modulo `q`; the canonical
ASM still uses Montgomery multiplication because it also reduces a lazy high
operand.

The benchmark-only identity candidate replaces only those `R` chains with:

```text
t = round(10*a / 2^15)
r = a - 3457*t
```

`vpmulhrsw` implements the rounded quotient.  Exhaustive enumeration gives:

| Input interval | Exact reducer image |
| --- | --- |
| `[-3(q-1),3(q-1)] = [-10368,10368]` | `[-2179,2178]` |
| `[-4(q-1),4(q-1)] = [-13824,13824]` | `[-2359,2359]` |

Thus the stage1 high term is still less than one modulus in magnitude:
`3(q-1)+2179 = 12547 < 4(q-1)`.  At stage2, the conservative bound is
`4(q-1)+2359 = 16183 < 5(q-1)`.  The mixed `omega32^8` and packed-row2 stage2
chains remain Montgomery products, so the original `5(q-1)` stage2 contract
continues to hold.

No packed multiply can saturate in these intervals.  The largest rounded
quotient magnitude is four, `4*q=13828 < 32768`, and every add/sub result
remains inside the existing signed-int16 lazy bounds.  Therefore Stage345 may
consume identity-candidate scratch without changing any twiddle precondition
or the final `8(q-1)` proof.

## Final reducers

The intrinsic row-bitrev comparison path sign-extends each value to int32 and
uses the reference-compatible rounded Barrett reduction.  Its output is in
`[-1729,1729]`; at an exact half-modulus boundary it may choose either signed
representative.

The canonical Stage345 ASM path instead keeps the checkpoint packed in int16
lanes:

```text
t = (signed_mulhi(a, 19412)) >> 10
r = a - t*3457
```

Here `>>` is an arithmetic right shift.  Every integer input in the proven lazy
interval `[-27648,27648]` was exhaustively checked to satisfy both
`r == a (mod 3457)` and `0 <= r <= 3457`.  The multiply by 3457 and subtraction
remain representable in the int16 operations used by the implementation.  The
different representative convention is intentional; differential tests compare
modulo q.

This `[0,q]` convention matches KPQC Final's AVX2 forward reducer.  Exhaustive
evaluation over all 65,536 signed-int16 inputs shows its exact image is the
complete interval `[0,3457]`; zero and `q` both encode residue zero.  It is an
AVX2 packed representation choice, not the representation used by the scalar
reference.

The benchmark-only centered final candidate uses the same three-instruction
expression as the identity candidate:

```text
t = round(10*a / 2^15)
r = a - 3457*t
```

Over the full proven Stage345 interval `[-27648,27648]`, exhaustive enumeration
gives `r in [-3080,3079]` and `r == a (mod q)`.  The quotient magnitude is at
most eight, so the low-half product satisfies `8*q=27656 < 32768`; neither the
multiply nor the subtraction wraps.  This saves one packed instruction per
lane vector relative to the canonical reducer while deliberately changing the
representative range.

The final 8x8 transpose and SoA store are a pure permutation and therefore do
not change bounds or residues.  For DFT3 row `k3`, NTT32 index `Q`, branch `b`,
and quartic coefficient `c`, the output word is
`64*(4*k3+Q/8) + 16*c + 8*b + Q%8`.  Both directions of this 768-word mapping
are tested against the verified GT row-bitrev reference.

The interleaved, no-copy remapped, resident-constant, and queued-store
Stage345 entries use the same three butterfly layers.  The canonical schedules
use the packed Barrett expression and return `[0,q]`; centered schedules return
`[-3080,3079]`.  Besides reachable forward states, standalone tests fill the
stage2 boundary independently at alternating endpoints and random values in
`[-5(q-1),5(q-1)]`; every candidate is compared modulo q with the intrinsic
Stage345/scatter oracle and checked against its declared range.

The native output keeps the required lane-local 8x8 transpose but removes the
cross-128-bit `vperm2i128` packing.  Its twelve batches are:

```text
row01: batch = 2*floor(Q/8) + branch
       lane  = (Q mod 8) + 8*k3, k3 in {0,1}

row2:  batch = 8 + 2*floor((Q mod 16)/8) + branch
       lane  = (Q mod 8) + 8*floor(Q/16), k3=2
```

This is also a pure permutation.  A test-only mapping converts all 768 words
back to the existing SoA contract and compares byte-exactly with centered
Stage345.  That conversion is not part of any timed or proposed production
path; native basemul and inverse loads must consume the mapping directly.

The U2/U4 single-entry native-forward symbols inline the already-proved
identity-reduced producer and this exact centered-native Stage345 body.  Their
two 1536-byte stack regions only replace the former caller-owned region
boundary; they add no arithmetic operation or representation conversion.
Consequently the stage1/stage2 bounds, Stage345 Montgomery preconditions,
final `[-3080,3079]` range, and native permutation proof are unchanged.

All low-level Stage345 entries load from a 32-byte-aligned 1536-byte scratch
while writing a separate 1536-byte output.  The two regions must not overlap:
an early SoA store can otherwise overwrite a later scratch block.  Public
forward wrappers own a private stage2 scratch and therefore remain safe when
their polynomial output aliases their polynomial input.

## SoA quartic basemul

The intrinsic pointwise prototype accepts normal-domain representatives
`|a_i|,|b_i| <= q`.  Define

```text
p_ij = Mont(a_i*b_j)
```

for each of the 16 runtime products.  Since `|a_i*b_j| <= q^2` and
`q^2 < q*2^15`, the scalar Montgomery precondition holds and every `p_ij` is
in `[-(q-1),q-1]` in the `R^-1` domain.

The quartic wrap accumulators are:

| Value | Expression | Bound before lambda |
| --- | --- | ---: |
| `w0` | `p13+p22+p31` | `3(q-1)` |
| `w1` | `p23+p32` | `2(q-1)` |
| `w2` | `p33` | `q-1` |

Each `lambda` is a centered Montgomery-form constant with magnitude at most
1728.  Therefore the largest fixed-factor input product is bounded by
`3(q-1)*1728 < q*2^15`; `Mont(w_i*lambda)` returns to one modulus in the same
`R^-1` domain.  Adding the non-wrapped products gives these conservative
bounds:

| Output accumulator | Bound before finalization |
| --- | ---: |
| `u0` | `2(q-1)` |
| `u1` | `3(q-1)` |
| `u2` | `4(q-1)` |
| `u3` | `4(q-1)` |

The maximum packed addition magnitude is therefore
`4(q-1)=13824 < 32768`, so no `vpaddw` wraps.  Finally, `R^2=867` in centered
Montgomery form and `4(q-1)*867 < q*2^15`; `Mont(u_i*R^2)` returns a normal-
domain representative in `[-(q-1),q-1]`.

All 12 batch iterations and table addresses depend only on public indices.
There are no value-dependent branches, corrections, or memory accesses.  The
three API arrays are required not to overlap; this is an optimization contract,
not a secret-dependent condition.

### Experimental R^-1 basemul/inverse contract

The matching `R^-1` candidates remove all 48 `Mont(u_i,R^2)` finalizers.  A
completely unchecked output is not a valid input to the existing inverse:
starting from the worst `4(q-1)` accumulator, the lazy inverse would reach
`10(q-1)=34560` and wrap signed int16.  The safe candidate instead applies

```text
t = pmulhrsw(u,10)
r = u - t*q
```

to all four coefficients.  This costs three AVX2 instructions rather than the
four-instruction fixed Montgomery product.  Exhaustive evaluation over
`[-4(q-1),4(q-1)] = [-13824,13824]` gives `[-2359,2359]`, so the ordinary
`|a|<=q` inverse proof below applies unchanged while the residue remains in
the `R^-1` domain.

The selected experimental `c0-lazy` candidate exploits the coefficient-
specific accumulator bounds.  It applies the same checkpoint only to
`c1,c2,c3`; `c0` keeps its raw `2(q-1)` representative.  Its inverse NTT32
stream obeys:

| c0 step | Bound |
| --- | ---: |
| basemul/API | `2(q-1)=6912` |
| `len=2` | `4(q-1)=13824` |
| `len=4` | `5(q-1)=17280` |
| `len=8` | `6(q-1)=20736` |
| `len=16` | `7(q-1)=24192` |
| `len=32` | `8(q-1)=27648` |

Thus every addition stays in signed int16, the largest twiddle input still
satisfies `7(q-1)*1728 < q*2^15`, and the existing packed Barrett checkpoint
is already exhaustively valid through `+-27648`.  From that checkpoint onward
all four streams again share the original `[0,q]` contract.

Every inverse multiplication before final normalization uses a factor in
Montgomery form, so a uniform `R^-1` input scale propagates unchanged.  The
matching postprocess changes only the final factors:

```text
low:  (1/192)*R  = -811  -> (1/192)*R^2 = 1679
high: (1/96)*R   = -1622 -> (1/96)*R^2  = -99
```

The corresponding factor-qinv values are 15375 and 30749.  No inverse loop,
twiddle table, permutation, or dynamic instruction is added.  The all-centered
candidate saves 48 retired instructions per basemul; `c0-lazy` saves 84.

## SoA direct-consumer inverse

The inverse accepts normal-domain NTT representatives `|a| <= q`.  Persistent
state remains signed int16; Montgomery products use signed 16-bit high/low
halves, and the packed Barrett checkpoint uses only signed int16 operations.

### Lazy inverse NTT32

Each `(k3,c)` stream consists of four YMM Q-groups.  `len=2,4,8` operates
inside each 128-bit branch half; `len=16,32` combines Q-groups.  Every stage
after `len=2` has the DIT form `u +/- Mont(v,w)`.  A Montgomery result is
bounded by `q-1` even when its input is lazy, provided its 32-bit product meets
the reducer precondition.

| Step | Input bound | Montgomery term | Output bound |
| --- | ---: | ---: | ---: |
| API | `q` | — | `q` |
| `len=2` | `q` | identity add/sub only | `2q` |
| `len=4` | `2q` | `q-1` | `3q` |
| `len=8` | `3q` | `q-1` | `4q` |
| `len=16` | `4q` | `q-1` | `5q` |
| `len=32` | `5q` | `q-1` | `6q=20742` |

The largest lazy high operand is at most `5q`; every inverse twiddle has
centered magnitude at most 1728, so
`5q*1728 < q*2^15`.  This satisfies the Montgomery reducer precondition.  All
lane additions remain within signed int16 because `6q=20742 < 32768`.

At the NTT32-to-DFT3 boundary, the packed reducer

```text
t = (signed_mulhi(a,19412)) >> 10
r = a - t*3457
```

is used once per vector.  Its already exhaustively checked forward interval
`[-27648,27648]` contains the inverse interval `[-20742,20742]`, so each row
enters inverse DFT3 in `[0,q]`.

### Inverse DFT3, untwist, and merge

For `y0,y1,y2 in [0,q]`, `d=y2-y1` is in `[-q,q]`; the omega3 Montgomery
product returns to one modulus.  The three raw inverse DFT3 outputs obey:

| Output | Expression | Bound before checkpoint |
| --- | --- | ---: |
| `x0` | `y0+y1+y2` | `3q` |
| `x1` | `y0-y1+Mont(d,omega3)` | `2q` |
| `x2` | `y0-y2-Mont(d,omega3)` | `2q` |

All are inside the packed reducer interval and are checkpointed to `[0,q]`.
The unnormalized inverse NTT32 and inverse DFT3 contribute scaling `32*3=96`.

Untwist is a Montgomery multiplication by `F_branch^n*R`; its input product is
at most `q*1728 < q*2^15`, and each branch result is bounded by `q-1`.  For the
top merge:

| Step | Bound |
| --- | ---: |
| branch sum/difference | `2(q-1)=6912` |
| `Mont(branch_difference, ZMINUSZ5INV)` | `q-1` |
| sum minus correction | `3(q-1)=10368` |
| final `Mont(...,1/192)` or `Mont(...,1/96)` | `q-1` |

The largest fixed postprocess factor magnitude is 1665, and
`3(q-1)*1665 < q*2^15`, so both final Montgomery sites meet their preconditions.
The constants fold in the accumulated factor 96, yielding a normal-domain
coefficient in `[-(q-1),q-1]`.

The 4x8 transpose and public CRT block map are pure permutations.  All loop
bounds, table addresses, and stores depend only on `n3`, Q-group, and lane;
there is no secret-dependent control flow or address.  Because every input is
copied into the 1536-byte row scratch before final stores, `out==in` is safe.

## Fused top-split + branch-twist candidate

The benchmark-only fused frontend expands the two branch expressions before
vectorization:

```text
x0 = t0*low + (t0*zeta)*high
x1 = t1*low + (t1*(1-zeta))*high
```

All four fixed factors are generated in Montgomery form.  Each input satisfies
`|low|, |high| <= q-1`; each Montgomery product returns within `q-1`, so the
two raw sums satisfy `|x| <= 2(q-1) = 6912` and cannot wrap signed int16.
Exhaustive evaluation of the exact `vpmulhrsw(a,10); a-q*t` sequence over
`[-6912,6912]` gives `[-1998,1998]`.

After that checkpoint, DFT3 has `|x1-x2| <= 3996`.  Its omega3 Montgomery
term is bounded by `q-1`, giving `|r0| <= 5994` and
`|r1|, |r2| <= 7452`.  This is below the existing `3(q-1)=10368` frontend
contract, so the unchanged Stage12 and Stage345 proofs apply.  The checkpoint
can select a different centered representative from the serial two-Montgomery
schedule, but the output remains modulo-q equivalent, stays in the declared
`[-3080,3079]` final range, is deterministic under `out==in`, and passes the
inverse and polynomial-product tests.

The high-first candidate changes only instruction order.  It uses the same
Montgomery operations, tables, lazy ranges, stores, and final representatives
as the selected serial frontend; its differential contract remains byte-exact.
The generated fixed-displacement variant changes only the encoding of those
same public input addresses and fully unrolls the 16 public pairs.  It has the
same arithmetic, load set, live ranges, output stores, and byte-exact contract;
no range bound or secret-dependent address property changes.

## Q/Q+3 wide loads and delayed centering

The wide-load candidates use the public CRT identity

```text
input_index(n3,Q+3) = input_index(n3,Q) + 3 (mod 96).
```

Each quartic block is eight bytes, so 47 of the 48 `(pair,n3)` rows fit in one
32-byte load beginning at `input_index(n3,Q)`.  `vpermq $0xf0` selects qwords
0 and 3 and duplicates each into its two branch positions.  The only wrap is
`(Q,Q+3)=(30,1), n3=1`, loaded by two public-address broadcasts per polynomial
half.  Every non-wrapped load ends within its 768-byte half, and fixed public-Q
stores restore the canonical frontend scratch layout.  The wide high-first
candidate therefore has exactly the existing high-first arithmetic and
byte-exact output contract.

The wide fused candidate consumes the duplicated qwords directly and omits
the fused frontend checkpoint.  Let `m=q-1=3456`.  Each fixed Montgomery
product is bounded by `m`, giving:

| Boundary | Bound |
| --- | ---: |
| fused split/twist sum | `2m = 6912` |
| DFT3 row 0 | `6m = 20736` |
| DFT3 rows 1/2 | `5m = 17280` |
| NTT32 stage 1 | `7m = 24192` |
| NTT32 stage 2 | `8m = 27648` |
| Stage345 stage 3 | `9m = 31104` |

All pre-checkpoint additions remain in signed int16.  The stage-3 twiddle
inputs also satisfy the Montgomery precondition because
`8m*1728 < q*2^15`.

After stage 3, only the four low operands of the next butterfly layer are
centered.  Exhaustive evaluation of the exact center10 instruction sequence
over `[-31104,31104]` gives `[-3260,3260]`.  The next two layers are then
bounded by

```text
stage 4: 3260 + m = 6716
stage 5: 6716 + m = 10172.
```

The existing final centered reducer consequently retains its
`[-3080,3079]` output range.  This delayed schedule executes 24 vector
reducers (four per Stage345 block) instead of the fused frontend's 48 (three
per pair), while preserving modulo-q equivalence, deterministic `out==in`,
inverse round trip, and polynomial multiplication.

## Lazy-native terminal and asymmetric pointwise consumer

The lazy-native forward retains every checkpoint above through Stage4 and
omits only `GT_NATIVE_CENTER8_REMAPPED_PARALLEL` after Stage5.  The old generic
consumer proof used the conservative signed-int16 envelope

```text
|lazy coefficient| <= 8*(q-1) = 27648.
```

That envelope is valid but loses producer information needed by baseinv.  The
actual delayed-center recurrence distinguishes the DFT3 rows:

| Boundary | row 0 | rows 1/2 |
| --- | ---: | ---: |
| wide fused DFT3 | `6(q-1)=20736` | `5(q-1)=17280` |
| after radix-2 stages 1/2/3 | `9(q-1)=31104` | `8(q-1)=27648` |
| exact center10 image | `[-3260,3260]` | `[-3080,3079]` |
| after stages 4/5 | `abs(x)<=10172` | `abs(x)<=9992` |

After the native transpose, vector slots 0--31 contain row0/row1 lanes and use
the larger `10172` bound.  Slots 32--47 contain row2 lanes and use `9992`.
The generator in `generate_gt_forward_lazy_bounds.py` checks this recurrence,
the exact center10 images, and the mapping for all 48 fixed vector slots.

Both bounds fit the reusable `GTN-L3` envelope
`abs(x)<=3*(q-1)=10368`.  More importantly, every initial unknown product in
baseinv satisfies

```text
10172^2 = 103469584 < q*2^15 = 113278976
 9992^2 =  99840064 < q*2^15 = 113278976.
```

Thus all 48 terminal vectors, not merely a subset, are square-safe for the
packed signed Montgomery reducer.  The public normalization mask for a value
produced by this exact Forward is therefore the all-zero mask.

The centered partner stays in `[-3080,3079]`, hence satisfies `|a| <= q`.
For every runtime Montgomery product in the native basemul,

```text
|a*b| <= q * 8*(q-1)
      = 95,579,136
      < q * 2^15
      = 113,278,976.
```

Therefore the signed packed Montgomery reduction has the same `q-1` result
bound as the centered-by-centered path.  Subsequent basemul additions depend
only on reduced products: the largest pre-lambda or final accumulator remains
`4*(q-1)=13824`, so no int16 addition wraps.  The proof is symmetric in the
two multiplicands; either input may be the lazy one, but lazy-by-lazy is not an
approved contract.

The native lambda tables are permutations of the existing SoA table:

```text
row01 batch = 2*floor(Q/8)+branch
      lane  = (Q mod 8)+8*k3,                 k3 in {0,1}

row2  batch = 8+2*floor((Q mod 16)/8)+branch
      lane  = (Q mod 8)+8*floor(Q/16),        k3 = 2
```

The generator and test enumerate all 192 `(k3,Q,branch)` objects and verify
both `lambda` and `lambda*qinv` at their native lanes.  This is a pure public
permutation; it changes neither arithmetic bounds nor constant-time behavior.
The runtime final-center selector is also public call-site state and adds one
input-independent mode branch per Stage345 block.

## Native baseinv center-on-load

The center-on-load control consumes an arbitrary value in the conservative
`GTN-L8` interval:

```text
-27648 <= a <= 27648.
```

Its first operation on each loaded coefficient vector is exactly

```text
t = vpmulhrsw(a, 10)
c = a - 3457*t.
```

Exhaustive enumeration of all 55,297 signed inputs establishes:

```text
-3080 <= c <= 3079
c == a (mod 3457).
```

Consequently every subsequent unknown product in the determinant/adjugate
schedule has the centered-control bound:

```text
|c_i*c_j| <= 3080^2 = 9,486,400
                         < q*2^15 = 113,278,976.
```

Each product is Montgomery-reduced before addition.  At most three reduced
terms form `t0` or `t1`, so their packed additions stay within signed int16;
the next multiplication consumes Montgomery outputs under the production
baseinv schedule's existing bound.  The 12 determinant vectors then use the
unchanged lane-wise batch inversion and final scale.  The input reduction is
fixed-count and address-independent, and no standalone 768-word pass exists.

This proves algebraic legality, not adoption.  The best scheduled ASM result
still pays 156 dynamic instructions (48 three-instruction center chains plus
12 constant broadcasts).  It remains useful only when the producer contract
is no tighter than `GTN-L8`.

For the delayed-center Forward, the preceding per-vector proof gives `GTN-L3`.
`gt_baseinv_native_l3_asm_avx2` is an inline contract alias of the centered
wrapper: the linked path executes no `vpmulhrsw`, no `vpmullw` by `q`, and no
normalization subtraction.  Once each initial `a_i*a_j` product is proved below `q*2^15`,
the Montgomery outputs enter exactly the same bounds as the centered control;
the rest of determinant, adjugate, batch inversion, failure, and final-scaling
proofs are unchanged.

The linked-ASM tests cover exact row01/row2 endpoints, 19,200 random invertible
quartics with independently chosen congruent `GTN-L3` representatives, zero
determinants, `out==in`, input immutability, inverse identities, and actual
Forward output.  On Ryzen 7 9700X, CPU 2, GCC 16.1.1, seven repetitions of
5,000,000 calls:

| Complete boundary | Cycles | Ref cycles | Instructions |
| --- | ---: | ---: | ---: |
| centered Forward + centered baseinv | 1719.121 | 1215.197 | 4327.221 |
| lazy Forward + center-on-load baseinv | 1742.762 | 1230.917 | 4339.224 |
| lazy Forward + direct GTN-L3 baseinv | 1662.210 | 1174.715 | 4183.192 |

The direct boundary saves 56.911 cycles (3.31%), 40.482 reference cycles
(3.33%), and 144.029 retired instructions relative to centered.  This is a
real elimination of terminal normalization rather than a relocation into
baseinv.  It remains benchmark-only until native KEM integration and KAT/full-
KEM measurements pass.
