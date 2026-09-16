# BaseInv fixed-scale conversion gate

Status: localized mathematical/model gate passed; default-off. No production
assembly changed, no Slothy allocation, no new cycle or full-KEM claim.

## Contract

NTRU+864, q=3457, R=65536; the existing FR0 cubic leaves and zR table are
unchanged. Input is any signed int16 R0 coefficient. Output remains centered
FR0 R0 in [-1728,1728]. All coefficient inputs are secret; constants are public.
The candidate models contain no secret-dependent branches or addressing.
reference.c is semantic test code, not constant-time production code.

This changes HOW required scale conversions are computed, not WHETHER they occur.

| Site | Old | New fixed multiply | b / bhat | Exact new range |
|---|---|---|---|---|
| numerator input | REDC(a×867): R0→R1 | a×R modulo q | -147 / -1393 | [-3013,3013] |
| finish denominator | REDC(d×1): R1→R0 | d×R^-1 modulo q | -682 / -6464 | [-1824,1824] |

For fixed b, bhat=round(b×32768/q), and the model executes int16 mul,
sqrdmulh and mls including wrapping and signed rounded-high semantics.
Numerator's old output bound was 2162: the new result is NOT covered by that
old bound. Exhaustive checking finds 16384 inputs with a different integer
representative, though every result is congruent. Finish differs at 56 inputs.

## Updated range chain

1. Exhaustively test all 65536 input coefficients: the new conversion has
   magnitude <=3013, below the common subsequent operand limit 4000.
2. With |a|,|b|<=4000, signed Montgomery correction has magnitude <=32768q.
   Product plus correction <=129278976 < 2^31, and REDC magnitude <=1972.
3. Numerator differences and the denominator's intermediate/final sums have
   magnitude <=3944 <4000. Thus every following numerator multiplication still
   satisfies the common precondition, including the z multiplication (|zR|<=1728).
4. Prefix and recovery continue to produce representatives within (-q,q).
   Congruent denominator values yield congruent prefix products. Within this
   interval zero modulo q iff integer zero: the existing failure predicate is
   therefore unchanged for all inputs, not only successful random cases.
5. The unchanged field inversion operates on the same residues and R1 scale.
   Finish converts its recovered denominator: exhaustively verified on [-2000,2000]
   with result bounded by1824. Three final products satisfy the 4000 envelope,
   return within (-q,q), and unchanged canonical correction uniquely centers
   them to [-1728,1728]. Exact final FR0 integers therefore match the baseline.

All memory positions, scratch sizes and public wrapper behavior remain unchanged
at the model level. Physical alias/ABI/wipe gates must be rerun after allocation.

## Instruction ledger

Models share b/bhat across all three input conversions and remove the unused
r2/one constants. Counts include constant materialization, loads/stores and
arithmetic, but exclude ret/public wrappers and any later lowering overhead.

| Kernel | Baseline / tile | Candidate / tile | Saved / BaseInv (36 tiles) |
|---|---:|---:|---:|
| numerator | 124 | 114 | 360 |
| finish | 59 | 57 | 72 |
| Total | | | 432 |

Arithmetic alone saves 576 instructions per BaseInv, but additional fixed
constant materialization reduces the complete model saving to **432**.
For a Keygen with two successful attempts: 864 model instructions saved.
This is not a cycle projection; constant lifetimes/RA and A76 scheduling can
change the physical result. Final normalization remains present and necessary
under the public centered-output contract.

## Evidence

- prove.py: exhaustive conversions; analytic downstream bounds; exact symbolic
  instruction execution of 12 complete 864-coefficient BaseInv cases, all 12
  successful, each checked against the cubic multiplication identity.
- Existing independent regression model also passes 520 BaseMul cases and 272
  inverse differentials. These do not constitute new physical assembly testing.
- reference.c: independent portable C fixed-conversion check, all 69537 cases;
  compiled/executed on Mac with AddressSanitizer and UBSan, passed.
- proof.json retains exact ranges, counts and hashes. candidate-model.json
  records the default-off instruction DAG; generator/baseline identity asserted
  before substitution, preventing an unnoticed stale symbolic source.

Run:

    python3 experiments/gt864-native-asm/baseinv-fixed-scale/prove.py
    cc -O2 -fsanitize=undefined,address experiments/gt864-native-asm/baseinv-fixed-scale/reference.c -o /tmp/gt864-fixed-scale-reference
    /tmp/gt864-fixed-scale-reference

## Next gate

Create separate numerator/finish physical candidates using these proven ranges,
review the extra constant lifetimes, then apply the Slothy skill (local entry
/Users/chenpinhao/slothy per user policy). Require no spill, unchanged coefficient
memory boundaries and passing full-range/zero-leaf/alias/ABI/wipe/KAT tests.
Then compare complete BaseInv and cleanup-aligned Keygen against the frozen
2026-09-09 baseline. Do not promote from model instruction counts alone.
