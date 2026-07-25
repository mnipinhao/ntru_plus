# NTRU+768 AVX2 KEM Forward-NTT consumer contract

Status: AVX2 native pack completed; full-KEM benchmark-only and default-off

Source revision: `1c4d072ae096a3ab49682934010570b16f941bc5`

This document fixes the representation obligations at all six Forward-NTT call
sites in the NTRU+768 KEM before any production integration is attempted.  It
selects a KEM-wide internal layout and a small set of range/domain formats; it
does not change the production ABI, public-key format, secret-key format,
ciphertext format, or KAT output.

## Sourced ring and wire facts

- Ring: `Z_3457[X]/(X^768-X^384+1)`.
- Coefficients are stored in signed 16-bit lanes internally.
- The existing wire format contains 768 canonical 12-bit residues in the
  production/KPQC quartic-slot order: 1152 bytes per polynomial.
- `poly_frombytes` accepts every 12-bit word, so an untrusted input coefficient
  can be in `[0,4095]`; a valid generated encoding is in `[0,3456]`.
- The existing `poly_tobytes` reduction/correction expression maps every
  signed-int16 input to its canonical representative in `[0,3456]`.  This was
  exhaustively checked over all 65536 signed-int16 inputs.
- All six Forward inputs are secret-derived.  Their control flow, addresses,
  table indices, final-reduction selection, and serialization must therefore
  be independent of coefficient values.  A call-site-constant centered/lazy
  mode is public and permitted.

## Representation vocabulary

The design uses layout, residue domain, and representative range as separate
properties.  A plain `int16_t[768]` must not be treated as sufficient type
information at an optimized boundary.

### `COEFF16`

Natural polynomial coefficient order, used before Forward and after inverse.

### `GTN16`

The selected internal transform-domain layout.  It is the existing fused
Stage345 native layout, with 12 batches, four coefficient vectors per batch,
and 16 lanes per vector:

```text
word = 64*batch + 16*c + lane
c    = 0..3

row 0/1:
  batch = 2*floor(Q/8) + branch
  lane  = (Q mod 8) + 8*k3
  k3    = 0,1

row 2:
  batch = 8 + 2*floor((Q mod 16)/8) + branch
  lane  = (Q mod 8) + 8*floor(Q/16)
  k3    = 2
```

This layout is selected because the current Forward emits it without the 48
cross-128-bit `vperm2i128` operations required by the SoA store, the scheduled
native basemul already consumes it without a 768-word transpose, add/sub are
layout-neutral, and base inversion also consists of 192 independent quartic
operations whose lambda table can be generated in this order.

### `WIRE12`

The unchanged 1152-byte production representation.  It is canonical and uses
the existing production quartic-slot order.  It is an external format, not the
selected in-memory arithmetic layout.

For production batch `pb=2*g+s`, coefficient `c`, and lane `pl`:

```text
wordP   = 64*pb + 16*c + pl
lambdaP = (-1)^s * zetas[624 + 32*g + 16 + pl]  (mod 3457)
g       = 0..5
s       = 0,1
pl      = 0..15
```

The array index is in `int16_t` elements; byte offset 1248 is element 624.
The byte stream does not traverse the production `int16_t` array linearly.
`pack.s` handles two signed-lambda batches together, so the exact public order
is:

```text
for group=0..5:
  for production_lane=0..15:
    for sign=0..1:
      serialize c=0,1,2,3 as four consecutive 12-bit words
```

The native pack must fuse both the lambda-derived slot permutation and this
wire interleave.  A batch-major scalar serializer is byte-incompatible even
when every coefficient is mathematically correct.

### `GTN16` format identifiers

| Format | Residue domain | Representative contract | Legal role |
| --- | --- | --- | --- |
| `GTN-C` | normal | `[-3456,3456]`; centered Forward producer image is the tighter `[-3080,3079]` | General centered/bounded arithmetic value; accepted by the centered baseinv entry |
| `GTN-L3` | normal | generic envelope `abs(x)<=3*(q-1)=10368`; actual lazy Forward image is `10172` in vector slots 0--31 and `9992` in slots 32--47 | Selected producer-specific lazy Forward output; legal for direct baseinv |
| `GTN-L8` | normal | `abs(x) <= 8*(q-1) = 27648` | Conservative lazy superset retained for consumer proofs and center-on-load fallback; not the tight Forward producer format |
| `GTN-U12` | normal | `[0,4095]`; valid generated subset `[0,3456]` | Direct decode of external 12-bit input |
| `GTN-WDEC` | normal | `[-27648,31743]` | Decapsulation-only result of `WIRE12-decoded c - GTN-L8 m2` |
| `GTN-RM1-C0L` | product times `R^-1` | `c0: [-6912,6912]`; `c1..c3: [-2359,2359]` | Basemul output consumed immediately by the matching inverse |

`GTN-C`, `GTN-L3`, `GTN-L8`, `GTN-U12`, and `GTN-WDEC` have the same memory layout and
normal residue domain.  They are separate semantic formats because their legal
consumers differ.  `GTN-RM1-C0L` must never be serialized, added to a normal
residue, or passed to normal-domain baseinv/basemul.

## GT-native to production-slot relation

The production and GT transforms factor the ring into the same 192 quartics.
For a GT-native `(batch,lane)`, define its production slot as the unique
`(pb,pl)` satisfying:

```text
gt_native_lambda[batch][lane] == lambdaP(pb,pl)  (mod 3457)
```

Coefficient number `c` is preserved.  The 192-entry lambda multisets are
byte-for-byte equal after centering, and every lambda is unique.  A differential
check over all 768 basis vectors plus 256 deterministic random vectors verified:

```text
GTN16[batch,c,lane] == production_ntt[pb,c,pl]  (mod 3457)
```

Therefore the representation bridge is a pure public permutation plus optional
canonical reduction.  It requires no modular multiplication, DFT, or matrix
conversion.  The lazy Forward has the same mapping modulo q.

The mapping must be generated from `zetas` and `gt_native_lambda`; it must not
be copied by hand.  Generated forward and inverse maps must be checked for
bijectivity and stale output during every test build.

## Six Forward call-site contracts

| ID | Forward value and source | Required Forward format | Immediate and retained consumers | Wire/KAT obligation | Decision |
| --- | --- | --- | --- | --- | --- |
| `KG-F` | `f`: CBD1, triple, then `f[0]+=1`; secret | `GTN-L3` | direct native baseinv; native basemul operand for `hinv`; direct native-to-`WIRE12` pack into `sk` | Secret-key `f` bytes must exactly match production | Lazy selected for the experimental design; all 48 baseinv vectors are square-safe without normalization |
| `KG-G` | `g`: CBD1 then triple; secret | `GTN-L3` | direct native baseinv; native basemul operand for `h` | `g` is not directly serialized, but derived `h` must match | Lazy selected for the experimental design; same zero-normalization baseinv contract |
| `ENC-R` | `r`: CBD1 from encapsulation coins; secret | `GTN-L3` | direct native-to-`WIRE12` pack for `hash_g`; native basemul with decoded public key `h` | Hash input must be byte-exact; malformed public-key words may be `[0,4095]` | Lazy selected; the existing GTN-L8 consumer proof already covers this tighter subset |
| `ENC-M` | `m`: SOTP encode; secret | `GTN-L3` | native add to `h*r`; direct pack of the sum as ciphertext | Ciphertext bytes must exactly match production | Lazy selected; the existing GTN-L8 addition proof already covers this tighter subset |
| `DEC-M2` | `m2`: inverse result reduced by `crepmod3`, then Forward; secret | `GTN-L3` | native subtraction `c-m2`; native basemul of that wide result with `hinv` | Affects recovered `r2`, decode result, failure bit, and shared secret | Lazy selected; the existing GTN-L8 decapsulation proof already covers this tighter subset |
| `DEC-R1` | `r1`: CBD1 regenerated during decapsulation; secret | `GTN-L3` | direct native-to-`WIRE12` pack; constant-time byte verification against `r2` | Verification bytes must exactly match production | Lazy selected; pack canonicalizes before comparison |

Key generation invokes `KG-F` and `KG-G` at least once each and repeats an
individual site when base inversion reports non-invertibility.  Encapsulation
and decapsulation invoke their two listed sites exactly once.

## Consumer-specific range obligations

| Boundary | Input bound | Derived bound or precondition | Required result |
| --- | --- | --- | --- |
| `GTN-L3 r * decoded pk` | actual `abs(r)<=10172`, `pk in [0,4095]` | `10172*4095 = 41654340 < q*2^15`; the older GTN-L8 superset proof also holds | Packed Montgomery unknown-product precondition holds even for an untrusted 12-bit public key |
| `basemul(h,r) + GTN-L3 m` | normal basemul output `[-3456,3456]`, actual `abs(m)<=10172` | sum in `[-13628,13628]` | No signed-int16 wrap; direct pack canonicalizes it |
| decoded `c - GTN-L3 m2` | `c in [0,4095]`, actual `abs(m2)<=10172` | result in `[-10172,14267]`, a subset of `GTN-WDEC` | No signed-int16 wrap |
| decoded-minus-lazy result `* valid hinv` | `abs(c-m2)<=14267`, `abs(hinv)<=3456` | `14267*3456 = 49306752 < q*2^15`; the older GTN-WDEC superset proof also holds | Packed Montgomery unknown-product precondition holds |
| any normal value to direct pack | any signed int16 | exhaustive canonicalizer image `[0,3456]` | Exact production `WIRE12` bytes after slot permutation |

The existing native basemul contract only names centered-by-lazy inputs.  It
must not be silently reused for the two wider KEM cases above: boundary/random
differentials and an updated range proof are required before those wrappers are
callable.

## Selected KEM-wide layout and format design

The selected design is a two-level representation:

1. Keep `GTN16` throughout each in-process NTT-domain arithmetic island.
2. Keep `WIRE12` unchanged at every public-key, secret-key, ciphertext, hash,
   and verification byte boundary.
3. Fuse the fixed `GTN16 <-> production-slot` permutation into native-aware
   pack/unpack.  Do not materialize an intermediate 1536-byte production-layout
   polynomial and do not add a standalone 768-word transpose.
4. Emit `GTN-L3` from the same lazy Forward at all six call sites.  The mode is
   fixed by the wrapper, not by secret coefficient values.
5. Use `GTN-RM1-C0L` only for the closed decapsulation boundary
   `native basemul(c,f) -> matching native inverse`.

This is preferred over making the production 16-bit slot order the universal
internal layout.  A production-layout terminal Forward would force the GT
butterfly-friendly lane arrangement to be globally reassembled after each
Forward.  Conversely, direct native pack/unpack can combine a required wire
conversion with work that already performs canonicalization and 12-bit
bit-packing.  Native add/sub are lane-wise, and native basemul is already the
selected zero-spill arithmetic consumer.

This does not expose lazy output as a public ABI.  `GTN-L3` is an internal typed
boundary owned by these six fixed call sites; every external wire boundary
still canonicalizes to `WIRE12`.  All six consumer chains accept it.  Four
non-baseinv chains were already proved against the larger `GTN-L8` superset,
while the two key-generation chains use the tighter per-vector proof below.

### Baseinv normalization scheduling result

`gt_baseinv_native_center_on_load_asm_avx2` accepts `GTN-L8` without a
standalone normalization pass.  For each of the 48 coefficient vectors, its
first register-resident operation is:

```text
t = vpmulhrsw(a, 10)
a = a - 3457*t
```

Exhaustive evaluation of all 55,297 inputs in `[-27648,27648]` gives
`[-3080,3079]` and preserves the residue modulo q.  The remaining determinant,
adjugate, 12-way batch inversion, output signs, `out==in`, and failure-to-zero
semantics match the centered native baseinv.  Tests cover 19,200 random
invertible quartics, exact lazy endpoints, one-zero and all-zero failures,
Forward-produced operands, and multiplication of every successful inverse
back to the quartic identity.

The first intrinsic schedule added 106.750 cycles to isolated baseinv and made
`forward+baseinv` 53.668 cycles slower.  Moving the production quartic prepare
schedule to native ASM and interleaving the four center chains cut the added
isolated cost to 53.960 cycles.  On Ryzen 7 9700X, CPU 2, seven repetitions of
5,000,000 calls, the final full boundary is nevertheless:

| Key-generation boundary | Cycles | Instructions |
| --- | ---: | ---: |
| centered Forward + centered native baseinv | 1561.595 | 4327.225 |
| lazy Forward + center-on-load native baseinv | 1573.895 | 4339.228 |
| delta | +12.299 (+0.788%) | +12.002 |

The 12-instruction delta is the per-batch reload of the center constant after
the quartic schedule reuses all 16 YMM registers.  A no-broadcast memory-source
variant retired essentially equal instructions across the full boundary but
increased the regression to 17.672 cycles because of extra load uops.  It is
rejected for an arbitrary `GTN-L8` input.

The delayed-center Forward is tighter than `GTN-L8`.  Its fixed terminal vector
slots are:

| Vector slots | Native rows in lanes | Proven absolute bound |
| --- | --- | ---: |
| 0--31 | row0/row1 | 10172 |
| 32--47 | row2 | 9992 |

Both are below the unknown-square safety threshold
`floor(sqrt(q*2^15-1))=10643`.  Therefore the best scheduled normalization for
this producer is none: `gt_baseinv_native_l3_asm_avx2` aliases the centered
wrapper at compile time and executes zero center chains.  The linked benchmark
therefore calls `gt_baseinv_native_centered_asm_avx2`, which in turn calls
`gt_baseinv_native_prepare_centered_asm`; that prepare contains no
`vpmulhrsw`.

The new same-host full-boundary result is:

| Key-generation boundary | Cycles | Ref cycles | Instructions |
| --- | ---: | ---: | ---: |
| centered Forward + centered native baseinv | 1719.121 | 1215.197 | 4327.221 |
| lazy Forward + center-on-load native baseinv | 1742.762 | 1230.917 | 4339.224 |
| lazy Forward + direct GTN-L3 native baseinv | 1662.210 | 1174.715 | 4183.192 |

Direct GTN-L3 saves 56.911 cycles (3.31%), 40.482 reference cycles (3.33%),
and 144.029 instructions relative to centered.  Consequently `KG-F` and
`KG-G` now select lazy Forward in this experimental design.  Production
symbols remain unchanged until full key-generation/KEM integration, KATs, and
full-KEM benchmarks pass.

### Key-generation native-island integration result

The opt-in key-generation island now keeps `f`, `finv`, `g`, `ginv`, `h`, and
`hinv` in GTN16:

```text
CBD/triple
  -> lazy Forward (GTN-L3)
  -> direct GTN-L3 baseinv
  -> native basemul
  -> native-to-WIRE12 pack
```

There is no standalone 768-word GTN16-to-production conversion.  The generated
192-entry map is a bijection, and the direct pack combines that public
permutation, canonicalization, production's two-batch wire interleave, and
12-bit serialization.

Correctness evidence on the Ryzen 7 9700X host includes:

- exhaustive canonicalization of all 65,536 signed-int16 inputs;
- 86 layout tests covering every signed-int16 bit pattern in every quartic
  coefficient position;
- 128 successful deterministic production/GT keypairs with byte-exact `pk`
  and `sk`;
- 16 public-random-stream and full-KEM comparisons;
- the full 100-case NIST KAT, with byte-identical `.req` and `.rsp`;
- KAT response SHA-256
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

The same-binary benchmark uses deterministic in-memory randomness, includes
the real keygen rejection loops, fixes execution to CPU 2, and uses 11
`perf stat` repetitions:

| Operation | Production cycles | GT cycles | Delta | Production instructions | GT instructions | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| keygen, 100,000/rep | 33586.943 | 46620.917 | +38.807% | 86480.524 | 119577.515 | +38.271% |
| keygen+encap+decap, 50,000/rep | 87533.786 | 100853.340 | +15.216% | 215528.032 | 248625.030 | +15.356% |

The regression is localized at the still-scalar native serializer:

| Pack, 1,000,000/rep | Cycles | Ref cycles | Instructions |
| --- | ---: | ---: | ---: |
| production `pack.s` | 226.156 | 158.914 | 815.292 |
| scalar direct GTN16 pack | 4046.129 | 2821.798 | 12152.293 |

Key generation performs three packs, so their instruction excess is about
`3*(12152.293-815.292)=34011.003`, while the complete keygen excess is
`33096.991`.  The GT arithmetic island therefore saves roughly 914
instructions outside packing, but the scalar public permutation/gather costs
more than the arithmetic saving.  Pack cycles also explain about 88% of the
measured keygen cycle regression.

The native island is correct but fails the full-operation performance gate and
remains default-off.  The next bounded experiment is an AVX2
GTN16-to-WIRE12 permutation/pack, compared against the current scalar oracle.
Further Forward tuning is lower priority for keygen until that boundary is
fixed.

### AVX2 native pack result

The scalar blocker is now replaced by a generated AVX2 permutation/pack.
Each public four-lane source chunk uses one dual-sign shuffle, placing sign 0
and sign 1 in the low/high qwords of the same XMM.  Groups 1 and 3 use paired
full-YMM loads because both source halves belong to the same two native
batches.  The serializer retains the production WIRE12 bit-pack network and
does not materialize a production-layout polynomial.

Three public entry contracts avoid unnecessary normalization:

| Entry | Legal input | Cycles | Instructions |
| --- | --- | ---: | ---: |
| general | any signed-int16 | 308.646 | 1056.291 |
| L3 | `abs(x)<=10172` | 287.201 | 960.291 |
| centered | `[-3456,3456]` | 231.480 | 810.289 |
| production control | production slot layout | 225.468 | 815.291 |

Keygen serializes `h` and `hinv` with the centered entry and `f` with the L3
entry.  Exhaustive differential coverage now includes all 65,536 general
values, all 6,913 centered values, and all 20,345 L3 values, in addition to
the existing layout/keypair/KAT tests.  The KAT response hash is unchanged.

Six balanced process-order pairs show keygen at -28.380 cycles (-0.089%) and
-779.014 instructions relative to production.  Full
keygen+encapsulation+decapsulation is still +391.266 cycles (+0.450%), although
it also retires 779.008 fewer instructions.  The format-boundary blocker is
therefore closed, but production promotion still fails the same-binary
full-KEM cycle gate.  The next bounded experiment localizes frontend/I-cache
cost in the first operation after GT keygen.

## Required consumer kernels

The final internal design requires these typed boundaries:

```text
forward_gt_centered(COEFF16) -> GTN-C
forward_gt_lazy(COEFF16) -> GTN-L3

pack_gtn_to_wire12(GTN normal int16) -> WIRE12
unpack_wire12_to_gtn(WIRE12) -> GTN-U12

baseinv_gtn_direct(GTN-L3) -> GTN-C or failure
baseinv_gtn_center_on_load(GTN-L8) -> GTN-C or failure  [fallback/control]
basemul_gtn_normal(valid contracted pair) -> GTN-C
basemul_gtn_rm1_c0lazy(contracted pair) -> GTN-RM1-C0L

add_gtn(GTN-C, GTN-L3) -> GTN normal [-13628,13628]
sub_gtn(WIRE12-decoded GTN, GTN-L3) -> GTN normal [-10172,14267]

inverse_gtn_rm1_c0lazy(GTN-RM1-C0L) -> COEFF16
```

In C-facing code, distinct wrapper names or representation structs must make
illegal mixes visible during review.  The preferred physical container is
still one 32-byte-aligned 1536-byte object; no runtime tag is stored beside
secret data.

## Candidate layouts retained for measurement

| Candidate | Description | Status |
| --- | --- | --- |
| `N`: selected arithmetic design | `GTN16` arithmetic plus direct native-aware wire pack/unpack | AVX2 pack complete; keygen reaches parity, full-KEM cycle gate still fails |
| `P`: integration control | Forward materializes production 16-bit slot order and reuses all production consumers | Benchmark control; useful if direct native pack/unpack is unexpectedly expensive |
| `S`: GT SoA | Existing `batch=4*k3+floor(Q/8)`, `lane=8*branch+Q%8` | Oracle and inverse-development layout; not KEM default |
| standalone `N<->P` pass | Separate 1536-byte permutation before/after a consumer | Forbidden in a proposed production path |

The `P` control and `N` candidate must be compared at complete consumer
boundaries.  An isolated Forward comparison is not sufficient.

## Implementation and validation order

1. Generate the 192-slot `GTN16 <-> production` bijection and add permanent
   lambda-set, basis-vector, random-vector, and stale-map checks.
2. Implement direct `GTN16 <-> WIRE12` pack/unpack and compare byte-exactly with
   production for all declared representative ranges and arbitrary 12-bit
   inputs.
3. Add native add/sub wrappers and the two wider native-basemul range contracts.
4. Build an encapsulation-native island first: it needs pack/unpack, basemul,
   add, and the two lazy Forward sites, but not baseinv or inverse.
5. Implement native baseinv, then build the key-generation-native island.
   Completed: exact KAT and AVX2 native pack pass; keygen reaches parity but
   the same-binary full-KEM cycle gate still rejects promotion.
6. Implement the direct native inverse first-load mapping and the matching
   `R^-1` normalization, then build the decapsulation-native island.
7. Only after all three paths pass KAT and differential tests, compare complete
   keygen, encapsulation, and decapsulation against the unchanged KPQC Final
   binary on the same host.

## Promotion gates

- Production `WIRE12` byte identity for valid key, ciphertext, hash, and verify
  buffers.
- Existing invalid 12-bit decode behavior preserved; no new secret-dependent
  validation branch.
- Every format transition covered by boundary and randomized differential tests.
- Lazy/wide Montgomery inequalities and accumulation bounds checked in the
  synchronized range proof.
- No secret-dependent branch, address, table index, or value-dependent loop.
- No timed or production standalone 768-word layout conversion.
- Correctness, KAT, ABI, AVX2-only linked-object, and full-KEM benchmark gates.
- Promotion only when each touched KEM operation is faster as a whole; isolated
  Forward or pack wins are insufficient.
