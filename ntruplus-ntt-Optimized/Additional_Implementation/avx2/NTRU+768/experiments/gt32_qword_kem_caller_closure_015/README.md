# GT32-QWORD-KEM-CALLER-CLOSURE-015

Experiment 014 only stops the symmetric
`F013 -> scale-B3 -> current InvNTT` island.  The current Encap and the two
post-inverse Forward callsites in Decap do not have that dataflow.  This
generator-only gate proves their actual consumers separately.

## Existing Q24 reducer

The selected lazy/high-range Q24 pack and native equality both already use:

```text
vpmulhrsw 9
vpmullw   q
vpsubw
```

Exhaustive scalar emulation proves that this unchanged sequence maps the full
signed-int16 domain to a congruent representative with maximum absolute value
`3291`; the existing sign fix then produces canonical `[0,3456]`.  For the
F013 terminal interval `[-14358,14358]`, the residual maximum is `2372`.

Thus `10788` and `12699` are typed producer contracts, not arithmetic limits
of the reducer.

## Encap closure

The exact caller path passes without new instructions:

- `F013(r) -> current lazy Q24`: pass.
- `decoded h x F013(r) -> current general B3`: every product,
  accumulator, lambda, and RSQ edge is signed-int16 safe.
- General-B3 output bounds are `[1783,1815,1847,1856]`.
- Adding `F013(m)` produces bounds `[16141,16173,16205,16214]`; `vpaddw`
  cannot wrap.
- The unchanged high-range Q24 reducer canonicalizes the result exactly.

## Decap closure

The two post-inverse Forward callsites also pass:

- `decoded c - F013(m)` lies in `[-14358,17814]`; `vpsubw` is safe.
- Multiplication by decoded `hinv` through current general B3 is safe.
- Its RSQ output bounds are `[1783,1815,1847,1865]`, satisfying the
  unchanged centered-Q24 input contract.
- Native equality compares that recovered result with `F013(derived r)`.
  The pre-reduction difference lies in `[-16223,16223]`, so its initial
  `vpsubw` is safe and the existing reducer is exact.

## Decision

Both Encap and the relevant Decap Forward callsites have zero-extra-instruction
range closure.  The qword-semantic Forward is therefore eligible for an
independent executable ASM gate.  This does not reopen the current inverse and
does not modify GT Clean.

Run `make check` to regenerate and validate the proof.
