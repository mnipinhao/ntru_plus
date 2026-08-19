# GT32-ENCAP-LIFETIME-031

This gate implements the four-polynomial Encap scratch schedule without
modifying GT Clean.  It is a spec-gated implementation refinement, not an
arithmetic or representation change.

The control uses a separate `c` frontend scratch for both Forwards.  The
candidate deposits frontend output into `r` or `m` and invokes the already
alias-qualified M Forward in place.  After the second Forward, `work` is dead
and becomes the unchanged B3/add/Q24 output buffer.  One 1536-byte polynomial
object is removed.

In the current qualification ELF, the control/candidate compiler frames are
8128 and 6592 bytes.  Their absolute sizes include compiler alignment and
protection overhead; the exact 1536-byte difference is the relevant result.

Before benchmarking, `make check` requires:

- 1,000 deterministic exact checkpoint differentials;
- exact `r_hat`, pre-`G` Encodeq bytes, `m_hat`, ciphertext and shared secret;
- equality with the current production deterministic Encap;
- rejection when each of the 768 serialized public-key slots is independently
  set to `q=3457`;
- zero ciphertext and shared secret on every rejected input.

The separate 032 B3-final-store add-m candidate is deliberately not included.
Its obligations are recorded in [SPEC_INVARIANTS.md](SPEC_INVARIANTS.md).

Reproduce with:

```sh
make check
make benchmark
```

Machine-readable evidence is in `generated/spec_gate.json` and
`generated/stack_audit.json`.

## SUPERcop-style architecture gate

The benchmark uses the host SUPERcop `default-perfevent` cpucycles library,
pins every fresh process to CPU 0, and collects the same 33 consecutive
timestamps / 32 adjacent differences used by `crypto_kem/measure.c`.  Each
variant contributes 96 observations per launch; the report uses SUPERcop's
stabilized second quartile.  Control and candidate are in one fixed ELF and
their order alternates AB/BA across 16 fresh launches.

Result:

| metric | result |
|---|---:|
| control median Q2 | 28276.542 core cycles |
| candidate median Q2 | 28043.417 core cycles |
| paired launch median | -78.271 core cycles (-0.277%) |
| favorable launches | 13 / 16 |
| paired MAD | 158.125 core cycles |
| bootstrap median 95% CI | [-288.250, -12.708] core cycles |
| AB / BA median deltas | -161.292 / -78.271 core cycles |

The candidate is directionally positive, but its delivery is not stable enough
for production promotion: launch deltas range from -526.667 to +373.750 core
cycles and only 81.25% of launches are favorable.  The exact one-polynomial
stack reduction remains valid; this gate shows that it does not yet translate
into a placement/runtime-stable caller win.

Full raw launch evidence and addresses are in `generated/benchmark.json`.
