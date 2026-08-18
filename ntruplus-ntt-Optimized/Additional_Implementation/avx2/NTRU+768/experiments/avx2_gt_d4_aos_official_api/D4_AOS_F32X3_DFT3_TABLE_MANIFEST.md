# Compact DFT3 table manifest

- Experiment: `AVX2-GT-D4-AOS-F32X3-COMPACT-DFT3-001`
- Digest: `f1ab09d04fe0ecf14ddf19f60fafb0115171c5e173024f2089abc8423172e0d6`
- Mathematical inverse omega3: 722
- Signed Montgomery omega3: -886
- Signed qinv: 13706
- Packed Barrett reciprocal: 19412
- q: 3457

The generated AoS vectors repeat each factor over `c0..c3` in physical order
`8*b+4*u+c`. Regenerate with `d4-aos-f32x3-dft3-generated-check`.
