# P3B28 — small-input raw top-split closure

Status: **PASS for the frozen KEM's small-input Forward specialization.**
Scope/mode: localized range-contract review. No assembly or production changes;
no cycle measurements and no newly linked raw-top candidate are claimed.

## Contract

- Ring: Z_3457[x]/(x^864-x^432+1).
- Natural input: signed int16, each coefficient in [-3,4].
- Top roots: alpha=-722 and beta=723=1-alpha modulo 3457.
- Output: existing FR0 layout and R0 scale; equality is modulo q, not necessarily
  equality of signed integer representatives.
- Candidate change under proof: remove only top-split SQRDMULH/MLS reductions.
  Keep MUL, all following arithmetic, data routing, memory bounds and constants.
- Baseline: P3B26 original-allocation T1, including bank-major tail preparation.

## All Forward input producers

The frozen `kem_stock.c` has exactly six static Forward call sites:

| Call | Producer | Proven coefficient range |
|---|---|---|
| Keygen f | CBD1, multiply by 3, increment coefficient zero | [-3,4]; coefficient zero actually {-2,1,4} |
| Keygen g | CBD1, multiply by 3 | [-3,3] |
| Encaps r | CBD1 | [-1,1] |
| Encaps m | SOTP XOR followed by CBD arithmetic | [-1,1] |
| Decaps m2 | Inverse, centered normalization, crepmod3 | [-1,1] |
| Decaps r1 | CBD1 | [-1,1] |

Keygen retries repeat the same producer. Received public-key/ciphertext bytes
do not go directly into Forward. Even malformed-input Decaps reaches Forward
through crepmod3 or CBD1. The crepmod3 instruction formula was additionally
exhausted over **all 65,536 signed halfwords**: output is [-2,1], still within
[-3,4], independently of the stronger centered-input premise.

CBD's masked byte digits are 1+a_bit-b_bit in [0,2]; no inter-digit carry or
borrow occurs. Exhausting all 65,536 byte pairs and both extraction parities
gives exactly {-1,0,1}. SOTP XOR preserves the arbitrary-byte input domain.
TRN and sign extension change position/width, not the coefficient set.

These statements cover the selected KEM, not every external call to the general
GT transform. Do not silently narrow the general API's old input contract.

## Top split and connection to the old proof

For a=low, b=high in [-3,4]:

| Step | Exact conservative range | Machine condition |
|---|---|---|
| -722*b | [-2888,2166] | raw MUL result fits signed int16 |
| a+b | [-6,8] | fits signed int16 |
| alpha output: a-722*b | [-2891,2170] | fits signed int16 |
| beta output: a+b-(-722*b) | [-2172,2896] | fits signed int16 |
| Existing NTT16 entry contract | [-3456,3456] | contains both candidate outputs |

The proof exhausts all 64 (a,b) pairs and checks congruence to the actual old
Algorithm-10 formula. Of 128 scalar top outputs, 48 change representative;
all remain congruent. Therefore a future correctness test must not require
raw top-output bit equality. Natural final coefficients/serialized bytes remain
the external comparison boundary.

The central argument is **set containment**, not a claim that the old bound is
tight: every new raw-top input to Pass-2 is already covered by the independent
input intervals of the G0 proof. T1 only permutes the tail. The complete G0
calculation is freshly executed; cached range-chain.json is not consumed.

## Reclosed NTT16 and actual one-product NTT9

| Boundary/node family | Maximum absolute value |
|---|---:|
| NTT16 | 9342 |
| NTT9 input twist products | 2197 |
| First-level one-product B3 | 13563 |
| eta correction products | 1863 |
| One-product difference input | 12604 |
| One-product fixed rho result | 1893 |
| Second-level B3 / largest Forward node | 25569 |

The actual B3 relation checked is:

```
d = x1-x2
r = Algorithm10(rho*d)
y0 = x0+x1+x2
y1 = x0-x2+r
y2 = x0-x1-r
```

All 288 logical leaf intervals are recomputed; components share the bound.
Output union is [-25569,25566], with zero unsafe int16 nodes. Algorithm-10
low-half MUL/MLS intentionally use modular low-half arithmetic; the proof does
not incorrectly require their unreduced mathematical products to fit int16.

## M5C and the actually selected D1 consumer

All leaf intervals are supplied to the M5C cubic accumulator proof, not just a
single guessed global magnitude. Maximum M5C signed-int32 accumulator is
1,961,321,283. BaseMul output magnitude is 2148; BaseMulAdd is 2205.

The current full-KEM uses D1, so the gate additionally recomputes its cubic
accumulator and direct-add union:

```
[-1,961,116,731, 1,961,346,849]
```

The exact 32-bit Barrett quotient-transition proof with reciprocal 621199
returns [-2911,2911]. Quotient products and residuals fit their signed machine
types. Required early cross-term Montgomery reductions remain unchanged;
zeta R1 cancels the intermediate R^-1 scale, and D1 returns R0.

## M5E and normalization

The inverse table is regenerated and compared byte-for-byte to the frozen
header. All 270 fixed constants are rechecked against every signed halfword:
**17,694,720 products**, maximum output magnitude 3444, no failures.

| D1 -> M5E boundary | Maximum absolute value |
|---|---:|
| Entry | 2911 |
| First radix-3 plain sum | 8733 |
| First weighted radix-3 result | 9799 |
| Second radix-3 lazy result | 16687 |
| Inverse16 layers | 3444, 6888, 10332, 13776, 17220 |
| Top difference / final raw output | 6888 |
| Final centered normalization | 1728 |

The M5C -> M5E path at input 2205 also passes. Both paths' maximum halfword
magnitude is 17220. Final centered normalization is exhausted over [-6888,6888]
and gives [-1728,1728], closing the Decaps producer loop through crepmod3.

## Decision and next gate

The mathematical/range gate authorizes trying a **small-input specialized**
raw-top experiment. It does not modify assembly or prove the as-yet-unbuilt
candidate binary. Preserve the general transform or explicitly expose its
new [-3,4] precondition: for example high=46 already makes -722*high=-33212,
outside signed int16, so arbitrary old-range inputs cannot use this shortcut.

There are 4 vector products per iteration and 16 iterations. Removing each
SQRDMULH+MLS pair deletes **128 dynamic arithmetic instructions** per Forward;
64 MULs remain. Constant setup removal is separate and not counted here.

Next: implement only that substitution, verify modular intermediate identity,
complete product/KEM bytes and ABI/guard behavior, audit the actual object,
then measure paired against T1. No layout change or new Slothy schedule should
be mixed into that experiment. No cycle gain is inferred from this proof.

## Reproduction and evidence

Run `python3 prove.py` in this directory. It produces `build/proof.json` and a
regenerated inverse table. The JSON records all leaf/accumulator intervals and
source hashes. T1 Pass-2, D1 and M5E sources are checked against their proof-owner
sources. Assembly kernels are not edited. The scope does not constitute a new
end-to-end security proof or certify arbitrary external transform callers.
