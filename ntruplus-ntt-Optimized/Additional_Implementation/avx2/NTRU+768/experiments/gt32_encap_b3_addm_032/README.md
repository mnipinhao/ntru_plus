# GT32-ENCAP-B3-ADDM-032

This experiment starts from the correctness-qualified four-polynomial Encap
of 031 and tests one bounded seam: add `m_hat` while B3's four finalized output
planes are still live, so the B3 final stores directly materialize
`h_hat*r_hat + m_hat`.

GT Clean is not modified. The selected production B3 source is mechanically
copied and instantiated into a normal/reversed matched-symbol cage.

## Exact work removed

The baseline performs:

```text
B3 final stores
→ poly_add reloads B3 result
→ memory-source add of m_hat
→ poly_add sum stores
```

The candidate performs:

```text
B3 finalizer
→ memory-source add of m_hat
→ B3 final stores of the sum
```

Per polynomial, this removes 48 YMM reloads and 48 YMM stores (3072 bytes of
vector traffic). The 48 `m_hat` reads, 48 `vpaddw`, and 48 final sum stores
remain. The generated B3 uses no stack and no spills. Because 032 starts from
031, both full callers already have the same four-polynomial/6592-byte scratch
shape; the 1536-byte stack reduction belongs to 031, not 032.

## Correctness and range result

`make check` requires:

- 1,000 deterministic exact local and full-Encap differentials;
- raw B3-plus-m words and final Q24 bytes to match the control;
- full ciphertext/shared-secret equality with 031;
- rejection, zero ciphertext, and zero shared secret when each of the 768
  serialized public-key slots is independently set to `q=3457`;
- no stack reference in either generated add-m B3 symbol.

All checks pass. The corpus observed `max |m_coeff|=1` and
`max |B3+m_hat word|=12882`.

That `12882` value is also an important correction: it disproves the stale
`Forward <= 10788` / final `<=12699` documentation for the currently selected
F14-style M Forward. The generated proof now reads the actual selected
frontend/core/B3 constants and conservatively propagates the signed
Montgomery DAG:

| contract | conservative bound |
|---|---:|
| current M Forward terminal | 18424 |
| B3 final degree planes | 1791, 1826, 1861, 1872 |
| B3 + M degree planes | 20215, 20250, 20285, 20296 |

The fused `vpaddw` therefore cannot wrap signed 16-bit. The selected Q24 body
has a full-signed-int16 reducer even though its historical symbol name still
says `highrange12699`.

## SUPERcop-style fixed-ELF result

The final gate uses the host SUPERcop `default-perfevent` core-cycle backend,
pins each fresh process to one CPU, alternates AB/BA, and collects 96 adjacent
cycle observations per variant per launch. Normal and reversed symbol order
each use 32 fresh launches in one unchanged ELF. The local endpoint includes
`B3 + add(m) + H1/Q24`; the full endpoint is deterministic Encap.

| placement | region | paired median | favorable | MAD | bootstrap 95% CI |
|---|---|---:|---:|---:|---:|
| normal | local B3+add+H1 | -29.375 cyc | 32/32 | 3.938 | [-32.667, -27.833] |
| reversed | local B3+add+H1 | -9.167 cyc | 30/32 | 4.167 | [-13.000, -6.250] |
| normal | full Encap | +1.875 cyc | 16/32 | 96.167 | [-60.042, +49.917] |
| reversed | full Encap | -5.771 cyc | 17/32 | 47.458 | [-35.833, +24.167] |

The local mechanism is real, but it fails the predeclared requirement of at
least 20 core cycles in both placements. More importantly, full Encap is
neutral and both confidence intervals cross zero; the local saving is not
delivered through the full caller.

## Decision

032 is correctness-qualified and locally positive, but production promotion
is stopped. This is another algorithmic-win/delivery-loss result: removing
3072 bytes of vector traffic does not produce a stable full-Encap improvement
on this image. Do not tune B3 arithmetic or scheduling based on this result.

Reopen only if a future production image/code-shape change naturally alters
this seam, at which point this exact generated candidate can be re-gated.

Reproduce with:

```sh
make check
make benchmark
```

Machine-readable evidence is in `generated/proof.json`,
`generated/static_audit.json`, and `generated/benchmark.json`.
