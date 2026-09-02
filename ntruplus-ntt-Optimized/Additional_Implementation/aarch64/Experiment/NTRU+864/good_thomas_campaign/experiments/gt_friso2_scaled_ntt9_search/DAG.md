# Exact DAG and cost model

The searched block is the complete frozen M5R-D oriented NTT9:

- nine input twist slots (`f0` through `f8`);
- three level-1 one-product B3 nodes (`a`, `b`, `c`);
- four eta correction nodes;
- three level-2 one-product B3 nodes (`g0`, `g1`, `g2`);
- paper-oriented output rows `0,1,2,3,4,5,6,7,8`.

Each one-product B3 uses

\[
y_0=x_0+x_1+x_2,
\quad y_1=x_0-x_2+\rho(x_1-x_2),
\quad y_2=x_0-x_1-\rho(x_1-x_2).
\]

The baseline has eight nonidentity input twists and ten internal fixed
multiplications, hence 18 relevant vector mulmods.  An addition costs zero when
both inputs and output have one scale label, one mulmod when one pair of labels
can be shared, and two when both operands require independent rescaling.
Existing fixed multiplications and input twists cost zero only when their
composite effective constant is one; otherwise they remain one Algorithm-10
mulmod.

The output labels are fixed to the exact FR-ISO2 factor.  Intermediate labels
are MILP variables modulo 3456, represented as `(A,B)`.  Every tracked witness
has cost 26, or eight extra mulmods over M5R-D.  CF0 costs nine extra, so the
witness deletes one mulmod per scaled block.

This is a mathematical operation DAG.  It does not yet specify constant-table
load grouping, physical registers, scheduling, or instruction-cache behavior.
