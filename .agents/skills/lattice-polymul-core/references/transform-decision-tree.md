# Transform Decision Tree

Use this reference to choose the high-level multiplication or transform strategy
after completing `new-ring-intake.md`.

## Inputs required

- Coefficient ring and modulus.
- Polynomial modulus `g(x)`.
- Degree and product bounds.
- Required output representation.
- Operation workload: standalone product, module/matrix-vector product,
  recursive matrix/inversion workload, or leaf kernel.
- Platform constraints.

## Decision tree

1. Check whether this is really a standalone product.
2. If the operation is recursive inversion, polynomial matrix-vector, or
   polynomial matrix-matrix multiplication, model the whole operation graph
   before choosing product kernels.
3. Classify the target polynomial modulus.
4. If `g(x)` directly supports cyclic or negacyclic NTT multiplication and the
   coefficient ring has the required roots and inverse scaling, consider native
   NTT.
5. If full NTT layers introduce expensive permutations or unnecessary root
   requirements, consider incomplete NTT with residual base multiplication.
6. If the transform length factors into useful coprime or small factors,
   consider mixed-radix methods such as Cooley-Tukey, Good-Thomas, Rader,
   truncated Rader, or Bruun.
7. If the target modulus is not directly transform-friendly, consider auxiliary
   polynomial embedding or coefficient switching only after proving
   reconstruction.
8. If products are short or appear as leaves inside a larger algorithm, select
   leaf kernels in caller context.
9. If operand shape exposes structured matrix-vector products, evaluate TMVP or
   transposed formulations.
10. If no transform preconditions are favorable, use direct schoolbook,
    Karatsuba, Toom-Cook, or another recursive method with explicit range and
    reduction analysis.

## Native NTT acceptance criteria

- The needed root order exists in the coefficient ring.
- The inverse transform scaling factor is invertible.
- The transform corresponds to the target cyclic or negacyclic quotient, or a
  proven embedding into one.
- Pointwise multiplication implements the intended product.
- Modular multiplication and reduction are efficient enough on the target
  platform.
- Conversion into and out of the transform domain is included in cost.

## Incomplete NTT acceptance criteria

- The residual base ring is explicitly defined.
- Base multiplication is cheaper than additional transform layers in the full
  caller context.
- The transform cutoff preserves the target ring product.
- Residual multiplication range and reduction costs are proven.
- Representation boundaries are clear to callers.

## Mixed-radix acceptance criteria

- Transform length factorization is documented.
- Required roots exist for every radix.
- Index mappings are derived and tested.
- Permutation/shuffle cost is counted.
- Inverse scaling and coefficient ordering are validated.

## Recursive workload guidance

- Draw the recursion tree or operation graph.
- List product sizes at each level.
- Mark which outputs are actually consumed.
- Count transforms that can be reused.
- Prefer kernels that minimize the complete workload, not standalone product
  time.

## Validation checklist

- Compare against a simple reference multiplication or operation-level reference.
- Test boundary coefficient ranges, not only random sampled inputs.
- Verify forward and inverse representation maps.
- Verify root tables and scaling constants.
- Include conversions, precomputations, and final reductions in benchmarks.

## Do not do this

- Do not choose NTT solely because the degree is a power of two.
- Do not choose Rader solely because the degree is prime.
- Do not copy incomplete-NTT cutoffs from case studies.
- Do not use inversion-specific multiplication choices for ordinary products
  without redoing the workload model.
