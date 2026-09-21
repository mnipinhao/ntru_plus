# NTRU+768 Official AVX2 optimization

Branch: `avx2-official-opt`, forked from `84da0b5`. This branch asks how much
Keygen, Encap and Decap improve while retaining the Official 20260831 AVX2
decomposition, stage order, physical layout and Montgomery scale. The pinned
Official `crypto_kem/ntruplus768/avx2` implementation is the performance
baseline. Frozen `avx2-gt32-clean` is a third comparator, not candidate source.

## Research workflow

1. Verify the pinned SUPERCOP snapshot and import Official into the experiment's
   immutable `upstream/supercop-avx2` directory. Record archive and tree hashes.
2. Audit reachable Forward, BaseMul, BaseInv, inverse, codec and caller paths.
   Record each caller's real input ranges, operand order, scratch, retry count,
   vector arithmetic/routing, constant traffic, liveness and code footprint.
3. First prototype: Official BaseMul plus the Encap message add in one AVX2
   loop. Preserve arithmetic, reduction, layout, scale and alias contracts.
4. Second prototype: inspect Forward's proven reduction/constant opportunities
   across Keygen/Encap/Decap. Use a separate small-input entry only if the
   general-input proof fails. If no arithmetic opportunity qualifies, test a
   same-DAG schedule/constant-lifetime variant instead. Do not fill the slot
   without a concrete mechanism.
5. Run independent differential, bounds, ABI, alignment, sanitizer and linked
   audits. Price component, then complete caller with same-residency inputs.
   Only a complete caller win proceeds to serious and disposable Native KEM.

Report Keygen, Encap and Decap separately. Preserve source/ELF hashes,
compiler, CPU controls, raw observations and StQ1/2/3. Formal Native timing
uses unmodified SUPERCOP measure. Fixed-ELF placement/ASLR controls follow a
Native gain. An isolated component win is a research result, not promotion.

## Evidence status

The branch-specific baseline, candidate ledger, test and benchmark results
will be appended here as each gate closes. Do not import historical GT cycle
deltas into an Official optimization claim.
