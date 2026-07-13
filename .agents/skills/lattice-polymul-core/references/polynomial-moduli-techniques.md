# Polynomial Moduli Techniques

Use this reference to route multiplication techniques by polynomial modulus
shape and operation shape.

## Classify the modulus first

- Binomial cyclic: `x^n - 1`.
- Binomial negacyclic: `x^n + 1`.
- Trinomial or sparse non-binomial: for example `x^p - x - 1`.
- Cyclotomic or composed modulus.
- Auxiliary product modulus: for example a CRT product of easier factors.
- Monomial or truncated factor used for low coefficients.
- General dense modulus with no obvious transform structure.

## Cyclic and negacyclic shapes

- Check native NTT or mixed-radix transforms when roots exist.
- Check twisting requirements for negacyclic products.
- Derive reduction identities explicitly.
- Validate that transform-domain pointwise multiplication matches the quotient.

## Prime-degree and non-power-of-two shapes

- Compare direct recursion, Karatsuba, Toom-Cook, mixed-radix embedding,
  auxiliary polynomial CRT, Rader-style transforms, and coefficient switching.
- Do not choose by degree alone.
- Route to `coefficient-ring-embedding.md` if an auxiliary modulus is used.
- Route to `vectorization-and-permutation-framework.md` if factorization creates
  heavy permutations.

## Cyclotomic and mixed-radix shapes

- Factor the relevant transform length.
- Evaluate Cooley-Tukey, Good-Thomas, Rader, truncated Rader, Bruun, or
  vector-radix methods by root availability and permutation cost.
- Prove the connection between the target modulus and any cyclic transform
  domain.
- Validate coefficient order after inverse transforms.

## Toeplitz and matrix-vector formulations

Use TMVP or transposed formulations when:

- The product naturally becomes structured dot products.
- One operand is reused, fixed, or shaped as a matrix/vector.
- Vector-by-scalar operations are efficient on the target ISA.
- The dot-product accumulation range is manageable.

Do not treat TMVP as a universal NTT replacement.

## Short leaf kernels

For small products inside transforms or recursive algorithms, compare:

- Schoolbook with delayed reduction.
- Batched schoolbook.
- Karatsuba.
- Toom-Cook.
- Small NTTs or 2-NTTs.
- TMVP or dualized leaf kernels.
- Rader, Bruun, or Good-Thomas leaves for awkward factors.

Choose leaves by caller context: parent scaling, coefficient order, reduction
schedule, register pressure, and transform reuse.

## Reduction identity worksheet

For any modulus `g(x)`, derive:

- How terms of degree at least `deg(g)` reduce.
- Whether reduction introduces signs, shifts, or coefficient growth.
- Whether reduction can be fused with inverse transform, CRT reconstruction, or
  stores.
- Whether output is exact in the target quotient or temporarily embedded.

## Validation checklist

- Classify `g(x)` and record why.
- Derive reduction identities.
- Prove transform or embedding correctness.
- Validate all boundary degrees.
- Compare against direct multiplication.
- Include target reduction in performance measurements.

## Do not do this

- Do not organize implementation choices by scheme name.
- Do not infer that every prime-degree ring wants Rader or auxiliary CRT.
- Do not use cyclic algorithms for non-cyclic targets without explicit
  embedding and reconstruction.
- Do not copy leaf cutoff sizes from case studies.
