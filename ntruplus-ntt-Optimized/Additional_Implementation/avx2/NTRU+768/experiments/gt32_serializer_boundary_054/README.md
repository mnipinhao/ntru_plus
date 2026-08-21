# GT32-SERIALIZER-BOUNDARY-054

Direct causal measurement of the two serializer boundaries used by Clean GT
Encap.  This experiment does not modify the production implementation.

The single benchmark ELF contains both:

- Official `poly_tobytes`, renamed to `off_poly_tobytes`;
- the selected Clean GT M-domain Q24 serializers.

For each site, setup constructs one real Clean-GT producer output, serializes it,
and uses Official `poly_frombytes` to obtain the corresponding Official physical
representation.  The timed calls therefore have:

- the same mathematical polynomial;
- byte-identical output;
- the same output address;
- fixed function and input addresses in one ELF;
- no Forward, BaseMul, Hash, or caller cleanup in the timed interval.

Sites:

1. `rhat`: N5 M output, comparing `off_poly_tobytes` with
   `ntruplus768_pack_m_lazy10788_avx2`;
2. `ciphertext`: real `B3(h,r)+m` M output, comparing `off_poly_tobytes` with
   `ntruplus768_pack_m_highrange12699_avx2`.

The historical GT symbol suffixes are retained because those are the production
ABI names.  Experiment 051 proved that the selected bodies execute the full
signed-int16 reducer and that the names no longer describe the observed range.

Decision rule:

- about 40--60 TSC or more of stable GT overhead per site: serializer
  architecture remains actionable;
- only low tens of TSC or less: close serializer micro-attribution and do not
  treat the 050 cumulative checkpoint movements as component budgets.

