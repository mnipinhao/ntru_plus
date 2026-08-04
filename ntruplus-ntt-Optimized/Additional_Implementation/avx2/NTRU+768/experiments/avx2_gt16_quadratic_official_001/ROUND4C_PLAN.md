# Round 4C quadratic terminal plan

## C1: algebra and mapping

- Exhaust all 16 square-root orientations in each fixed `(k3,k16)` vector.
- Record quartic/Official slots, chosen root, factor sign, quadratic modulus,
  representation scale, Montgomery power, range, and pair-local lanes.
- Require all 384 quadratic factors and all Official quartic mappings to be
  deterministic and reproducible.

Root negation only exchanges the two factors.  Because both `s` and `-s`
already occur in the vector, sign search cannot reduce the number of required
field constants; it is retained for deterministic lane order and future
consumer mapping.

## C2: scalar oracle

- Check split/merge inverses on boundaries and random full-field values.
- Check `quartic BM == split -> two quadratic BM -> merge`.
- Check quadratic norm inversion, zero failure, and zero output.
- Run full GT16 forward, quadratic component multiplication, inverse, and
  schoolbook quotient-ring differential.

## C3: static AVX2 schedules

Compare weighted-operand, postmultiply, and expanded asymmetric-right ABIs.
Count weighted preparation, both `vpmaddwd`, exact 32-bit reduction, packing,
loads/stores, registers, and expanded storage.  YMM15 is reserved and no pair
may cross a 128-bit half.

The selected reducer computes `m=low16(x)*q^-1`, forms `m*q` with
`vpmaddwd`, and returns `(x-m*q)>>16`.  Its five-instruction model is valid over
the generated `vpmaddwd` interval and intentionally returns `R^-1` output for
inverse normalization to absorb.

## C4: gates

The arithmetic gate uses the caller multiplicity `2F+B+I`.  A provisional
instruction pass authorizes one benchmark-only intrinsic boundary, not ASM or
integration.  ASM additionally requires:

- a concrete vertical inverse execution trace;
- same-binary C-versus-candidate cycle measurements;
- direct quadratic-to-Official serialization and parsing estimates;
- quadratic baseinv/keygen estimate;
- byte-exact, range, alias, malformed-input, sanitizer, and constant-time gates.
