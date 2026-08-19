# GT32 unweighted-merge executable adjudication 027

This experiment was opened to benchmark the 026 proposal instead of rejecting
it from instruction count alone.  GT Clean and all production symbols remain
unchanged.

## Requested comparison

The intended candidate was:

```text
current:    48 merge Montgomery chains -> current inverse
candidate:  raw signed difference -> 45 relocated inverse chains
            -> DFT3 -> 48 terminal blends
```

The maximum Montgomery depth calculated for both schedules was six, so chain
count alone was not allowed to veto assembly.  Three matched 32 KiB cages were
emitted for control, heterogeneous, and repaired candidates in normal and
reversed order.

## Correctness result

The native differential failed on the first random trial.  Investigation
found a semantic error in 026, before any meaningful cycle comparison:

```text
current difference representative  = weight[v] * raw_difference
candidate raw representative        = alpha[v] * raw_difference

candidate/current ratio             = alpha[v] / weight[v]
```

026 propagated `weight[v] * alpha[v]`.  That is the inverse relation.  When
the exact candidate/current ratio is propagated through the size-2 and NTT16
butterflies, none of the eight difference lanes belongs to a DFT3 character
class, even after exhaustive free `+/-1` sign choices.  Therefore the DFT3
correction is not a permutation of three output registers and cannot be
implemented by 48 `vpblendw` instructions.

The best sign choice still leaves an eight-nonzero-coefficient 3x3 correction
matrix for every difference-lane class (rather than a three-nonzero monomial
matrix).  This requires real field arithmetic, not lane selection.

The exact lane results are in
`generated/exact_conjugation_gate.json`.  The generated assembly is retained
only as an executable counterexample to the old propagation; its candidate
symbols are explicitly not benchmark-eligible.

## Can the blends be absorbed?

For the claimed 026 graph, no: the 48-blend repair itself is not a correct
repair.  More generally:

- postweight relabeling is diagonal and cannot perform the required
  cross-output linear combination;
- whole-register store relabeling cannot work because one YMM contains both
  sum and difference degree lanes;
- the current branch merge cannot absorb it for free; accepting the exact
  candidate would require a new dense three-input DFT3/terminal operator;
- a typed heterogeneous consumer only helps when the residual scales are DFT3
  characters.  Exact 027 proves they are not.

An exact candidate is still possible only by adding nontrivial field
multiplications/mixes at or before DFT3, which is a different operation graph
and loses the proposed `45 Montgomery + 48 blend` accounting.

## Decision

No timing or PMU number is reported: benchmarking a non-equivalent transform
would be misleading.  This is a correctness-level stop for the specific 026
candidate, not an instruction-count stop and not evidence that more
instructions can never reduce cycles.

Reopen only with a newly proved exact graph, such as a producer representation
whose true candidate/current scales form DFT3 characters, or a consumer that
defines and pays for the required dense mixed basis.

Follow-up gates resolve both immediate branches: 028 proves that direct
conjugated DFT3 needs at least three chains per unit (versus one current), and
029 finds character compatibility for only one of four difference-lane
classes.  Neither is assembly-eligible.

## Reproduction

```sh
make check
```

`make check` regenerates the exact proof, builds normal/reversed diagnostic
objects, verifies the control against 1,000 full inverse trials, and confirms
that the claimed 026 repaired schedules are rejected.
