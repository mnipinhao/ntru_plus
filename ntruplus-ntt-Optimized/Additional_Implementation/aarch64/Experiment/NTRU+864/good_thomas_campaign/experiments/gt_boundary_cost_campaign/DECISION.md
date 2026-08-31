# Decision

Retain fused FR-0 as the primary transform-boundary shape.  It completes the
same P8+tail-to-SoA boundary 62.72% below FC-0 at the stabilized local median,
while avoiding an 864-value intermediate scratch.

Keep FC-0 as a correctness and cost control only.  Its isolated bridge is
cheap, but its within-register radix-3 transform uses only three meaningful
lanes and loses decisively over the complete boundary.

Keep FR-lane-0 conditional.  It reduces the exact constant-bundle classes from
32 to 30, but does not reduce vector mulmods or constant-load occurrences.  Its
compiled code shape is identical to FR-0 and its timing overlaps FR-0.  A
32-byte potential table saving is not enough to change the ABI now.

Do not promote.  Open a separate fused-FR assembly experiment for explicit
register allocation, formal range proof, BaseMul root ordering, inverse map,
forward integration, target-host attribution, and full-KEM SUPERCOP.
