# Hypothesis

For each nonzero FR-ISO2 component, the required output factor is

\[
\tau_{h,r,t}^{c},\qquad c\in\{1,2\}.
\]

CF0 applies all nine row factors after an ordinary M5R-D NTT9.  This costs nine
additional Algorithm-10 multiplications per scaled NTT9 block.  CF1 assigns an
affine scale label

\[
g^{A t+B}
\]

to every node of the exact M5R-D DAG.  At an add/sub boundary, equal scale
labels pass for free; unequal labels are converted to the selected output
label.  At an existing twist, rho, or eta multiplication, the old constant and
the scale ratio become one composite constant.

The hard gate passes only if an exact witness:

1. emits every required FR-ISO2 row factor;
2. needs at most eight extra vector mulmods over M5R-D per scaled block;
3. stays within signed halfwords under the concrete Algorithm-10 constants;
4. adds no coefficient load/store boundary.
