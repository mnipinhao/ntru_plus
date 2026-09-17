# WIRE-MONOTONE-NATIVE-REBASE3 / SUPERCOP 20260831

## Source identity

The branch lock was explicitly refreshed from the official SUPERCOP index.
The formal harness is now `supercop-20260831`:

```text
archive sha256   9a258febbfbbf6de0c09cee73f343d4014597c259415e78a598b7af4b1787208
NTRU+864 AVX2    13e0d983221e430a3cc5097042aa04dd1197981fb39761b02fbc845253107006
NTRU+1152 AVX2   78daf6b9a6350c02d61cbd9f4dd1e717503b91183fe399005e1369eb5c365010
```

The NTRU+ AVX2 tree hashes are identical to the previous SUPERCOP 20260627
lock.  The source imported from the upstream `ntruplus-20260723` bundle is
therefore byte-identical, after the SUPERCOP integration procedure, to the
implementation shipped in the official 20260831 archive.  This rebase changes
the SUPERCOP release/harness identity, not the Official NTRU+1152 arithmetic.

A read-only pristine tree was extracted from the official archive at
`/home/nuc/src/supercop-pristine-20260831`.  Candidate installation and all
measure substitution occurred only in the disposable campaign
`/home/nuc/src/supercop-campaign-1152-rebase-20260910-002`.

The candidate is the previously frozen exp006 source.  Relative to that
candidate, only `SOURCE-MANIFEST.json` and `SHA256SUMS` changed to record the
new SUPERCOP release.  All compilable source files are byte-identical.

## Method

- CPU 1, Intel Core Ultra 7 155H, sibling list `1-2`.
- `performance` governor and Intel turbo disabled (`no_turbo=1`).
- Kernel `7.0.0-31-generic`.
- Nine fresh measure-ELF processes and 864 observations per operation.
- SUPERCOP 20260831 stabilized quartiles; StQ2 is the headline.
- Unmodified `crypto_kem/measure.c` for the Native KEM result.
- Native compiler selection was not forced.

## Native SUPERCOP KEM result

| operation | Official | exp006 | candidate - Official | percent |
|---|---:|---:|---:|---:|
| keypair | 34930.77 | 34218.07 | -712.70 | -2.04% |
| encapsulation | 43056.29 | 44070.36 | **+1014.07** | **+2.36%** |
| decapsulation | 30541.06 | 30568.92 | +27.87 | +0.09% |

Official selected GCC 15.2 O3.  The candidate selected GCC 15.2 O2.  Keypair
and decapsulation retain the Official source path and remain noise/compiler
controls; their deltas are not candidate credits.  Encapsulation is the
changed caller and loses under this Native selection.

The old 20260627 Native campaign measured `+672.27` encapsulation cycles and
selected O3 for both implementations.  Official encapsulation is effectively
unchanged (`43062.03` to `43056.29`), while the current candidate result uses a
different selected optimization level.  Consequently the change from +672 to
1014 must not be attributed entirely to NTRU+ source or to the SUPERCOP
release.

## SUPERCOP-derived component attribution V3

This diagnostic is not a Native SUPERCOP public number.  It uses the same
SUPERCOP 20260831 `default-perfevent` cpucycles backend, host controls, nine
fresh processes, and an O3 same-ELF balanced ordering.  Values below average
the first/second position StQ2 estimates.

| boundary | Official | exp006 | candidate - Official | launch direction |
|---|---:|---:|---:|---:|
| coefficient input -> forward state | 1486.99 | 1484.17 | -2.82 | 7/9 negative |
| forward + r serialization | 1800.59 | 1988.19 | +187.60 | 9/9 positive |
| forward + serialization + `hash_g` + SOTP | 19793.21 | 20043.24 | +250.03 | 9/9 positive |
| PK bytes + transformed r/m -> ciphertext | 1632.45 | 2071.88 | +439.43 | 9/9 positive |
| complete changed polynomial caller | 22413.31 | 23240.15 | +826.84 | 9/9 positive |

The current forward is statistically near parity at this caller boundary; two
of nine launch deltas are positive and the pooled difference is only about
-2.8 cycles.  The stable debts remain the r serialization/hash fanout and the
PK ingress/MA2/ciphertext tail.  The complete O3 component model is about 187
cycles below the Native gap.  Unlike the earlier campaign it does not close
the Native number directly, because the Native candidate selected O2 while
this same-ELF profiler selected O3, and because the component boundary excludes
some complete KEM entry/exit work.

## Decision

The exp006 candidate remains rejected for production.  The 20260831 Native
headline is +1014.07 encapsulation cycles.  Do not interpret the latest
forward as a demonstrated win over Official: it is effectively parity in the
current component campaign.  Forward work remains useful for NTRU+864 reuse
and for structural improvement, but the largest measured NTRU+1152 caller
debts are still outside the forward leaf.

Artifacts are under:

```text
results/wire-monotone-native-rebase3-sc20260831-intel155h-20260910-001/
```
