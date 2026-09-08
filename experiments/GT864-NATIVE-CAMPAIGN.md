# GT864 native consumer campaign

Fixed baseline: production commit 6207939e / benchmark evidence 7c971bd1.
All work below is default-off and separately benchmarked against that baseline.
No production source changes, no combined-speedup claim, no automatic commit.

Caller correction: ordinary BaseMul is called twice by Keygen (kem.c 113–114)
and twice by Decaps (262,268). Encaps uses BaseMul-add (196).
Only the newly introduced BaseMul-for-Inverse is Decaps-only.

1. **FR0-native BaseInv:** implemented conservative and lazy intrinsic variants.
   Lazy passes differential/KEM tests and saves ~914 cycles in Keygen (-1.69%).
   Keep experimental; full compiler CT audit, KAT and promotion review pending.
   Source/proof/results: gt864-fr0-native-baseinv/.
2. **BaseMul–Inverse co-design:** implemented R^-1 boundary prototype and
   regenerated inverse terminal constants. Reuses existing I9/I16 assembly;
   not a rewritten Inverse DAG. Saves ~369 Decaps cycles (-0.83%).
   Keep experimental scale contract for the future new Inverse assembly.
   Source/table checks/results: gt864-decaps-scale/.
3. **ToBytes streaming:** implemented route9-pair normalization/packing with
   final-byte ST3-lane stores. Both loop and unrolled variants are slower and
   spill. Reject; next DAG must consume partial routes sooner, not schedule
   this unchanged all-outputs-live form. Source/results: gt864-stream-tobytes/.

Important remaining work: the user's new Inverse assembly request is NOT
complete. The current step establishes and tests its scale contract; the new
I9-to-I16 producer layout, live-range plan and assembly remain to be built.
There was no Slothy run. Generic polynomial multiplication is outside scope.

Range checks: BaseInv normalization exhaustive on 65536 values, centered REDC
exhaustive enclosing product interval, lazy induction <=4000 operands and
<2000 products. Inverse terminal b/bhat table identity checked, full int16
constant multiplication output maximum 3436; first-Decaps REDC bound 2497.
Unchanged inverse prefix inherits the existing M5E evidence, not a new whole
assembly symbolic proof. KAT/security-cleanup gates remain explicit.

Remote work directories are /home/pi/ntruplus-experiments/ with the same three
experiment names. GCC14.2.0 Linux AArch64, core3; no throttle reported.
