# P38 result — direct-Forward plus Full-ToBytes co-DAG

## Outcome

**Rejected at the arithmetic gate.** Production is unchanged. No candidate
assembly, Slothy run or Pi 5 benchmark is justified because none of the
examined DAG families removes any net arithmetic.

The exact baseline is commit
`18091661a78d1d9e0911302661335a08a3a01a7f`. The linked symbols are:

- producer: `gt864_forward_poly_ntt_p41_k1_kem_only`;
- Full consumer: `gt864_p18_tobytes_full_asm`;
- Small control: `gt864_p18_tobytes_small_asm`.

The active Full body contains 54 `SQRDMULH` and 54 `MLS` instructions and is
called once per 432-coefficient top. A complete call therefore executes 108
quotient estimates plus 108 corrections: exactly the 216 Full-only vector
instructions identified by P37.

## Exact producer witness gate

The Apple-arm64 executable links the four current production Forward assembly
sources directly. It tests 32,768 inputs in each of two real KEM domains:

1. Encaps/Decaps small producer: every coefficient in `{-1,0,1}`;
2. Keygen `f`: every coefficient in `{-3,0,3}`, followed by the exact
   coefficient-zero `+1`.

The first 1,728 cases are positive and negative impulses; the rest are a
deterministic exhaustive-domain random construction. Every generated vector is
a valid CBD1-image vector because each ternary coefficient has an independent
two-bit preimage.

| Producer | Observed range | Coordinates with an explicit value outside `(-q,q)` | Latest first witness |
|---|---:|---:|---:|
| Small `{-1,0,1}` | `[-16667,15974]` | **864/864** | trial 1758 |
| Keygen `3*CBD1 + 1` | `[-18539,18288]` | **864/864** | trial 1746 |

These are constructive counterexamples, not a statistical range claim: for
each physical output coefficient, the recorded deterministic trial is a valid
input whose exact current Forward representative is at most `-3457` or at
least `3457`. Thus no fixed subset of output coordinates can bypass Full
normalization while retaining the current Forward representatives.

Separately, exhaustive evaluation of all 65,536 signed-int16 inputs proves the
current Full quotient/remainder sequence returns exactly `[0,3456]` with zero
mismatches. Applying only Small's negative correction outside its contract
fails for 58,622 signed-int16 inputs.

## Candidate-family ledger

| Family | Full work removed | Work added | Net | Decision |
|---|---:|---:|---:|---|
| Current Forward, selectively use Small | 0 | 0 | 0 | Rejected: every coordinate has a valid counterexample |
| Canonical post-pass, then Small | 216 | 216 | 0 | Rejected; also adds a coefficient read/write pass |
| Canonicalize before existing Forward stores, then Small | 216 | 216 | 0 | Rejected; changes FR0 representatives with no static saving |
| Reuse existing one-product rho quotient | 0 | 0 | 0 | Rejected: one rho quotient does not determine three output quotients |

For the last row, exact enumeration gives two inputs with the same existing
rho-product quotient but different final-output quotient triples. Keeping the
rho quotient live therefore cannot replace the three independent output
normalizations without another quotient/correction computation.

The P38 hard gate required at least 108 true instruction deletions before
scheduling. Best net deletion is zero, so P38 stops before symbolic assembly.
This also avoids asking Slothy to optimize a DAG that merely relocates work.

## Next gate

P39 returns to the remaining P37 positive boundary: Decaps
Inverse-to-ternary is 147.075 cycles slower than selected Official. The failed
P27--P33 experiments were routing/materialization changes; P39 instead audits
the twelve inverse9 blocks for a new algebraic identity, composite constant or
provably redundant reduction. It must remove at least one complete
Algorithm-10 multiplication per block (36 instructions per Inverse) before
symbolic assembly, while keeping the P35 I16 path and memory ABI frozen.

Machine-readable evidence is in `audit-results.json`. The full deterministic
witness list is regenerated under the gitignored `build/` directory by:

```sh
python3 audit.py
```
