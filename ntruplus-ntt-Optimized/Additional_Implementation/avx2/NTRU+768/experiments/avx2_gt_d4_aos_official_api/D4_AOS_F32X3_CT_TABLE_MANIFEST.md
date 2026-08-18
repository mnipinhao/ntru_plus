# F32X3 CT table manifest

- L0-L2 digest: `03ae270c0656c0e64e74da3538546d3239cf34d8d4fd1343ecb0f968637a9963`
- L3-L4 digest: `323cd674bf9815f19c6980a6d358dd16b73bb47f96f06e5094d042d812291119`
- Generator self-test: known basis values, factor reconstruction, qinv reconstruction,
  and Montgomery result comparison with the scalar field product.
- Regeneration targets: `d4-aos-f32x3-ct-l0-l2-generated-check` and
  `d4-aos-f32x3-ct-l3-l4-generated-check`.

Both families use positive Montgomery factors in `[0,q)` and signed 16-bit
`factor * q^{-1} mod 2^16` qinv lanes. No assembly constant is manually reordered.
