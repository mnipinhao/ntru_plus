# GT32 Compact Frontend 036

> **Causal correction (036R):** the compact schedule is locally neutral.  A
> fixed-size A/B/C cage subsequently showed that the old whole-image Encap
> improvement is produced by releasing the 1.4-KiB reservation and relocating
> later hot symbols, not by faster frontend execution.  See
> `../gt32_compact_frontend_036r/README.md`.  The historical measurements below
> remain valid for that exact linked image, but `compact_hot_footprint_confirmed`
> must not be read as a portable frontend speedup.

This experiment keeps the production wide frontend arithmetic, layout, range,
twiddles, and eight packet semantics unchanged.  It tests whether reducing the
active static body improves executable delivery enough to pay for loop control.

The shape audit finds the production sequence `0,1,2,0,1,2,0,1`.  Its minimum
period is three, not one, two, or four.  The only exact compact repeating shape
is therefore:

```text
U3 body x 2 + U2 tail
```

The local executable uses a 3,917-byte matched cage for both control and
candidate, so normal/reversed builds preserve following-symbol geometry.  Dead
NOP padding is outside the candidate's executed path.  GT Clean is not edited.

The gate measures frontend-only, full Forward, and two-Forward regions with TSC
and region-scoped core cycles.  A locally slower compact frontend is not an
automatic architecture veto; whole-image testing is warranted if the penalty
is small and active footprint drops materially.

## Results

### Static and correctness

- Production control body: 3,917 bytes.
- Compact active body: 2,472 bytes (`-1,445`, `-36.9%`).
- Matched local cage: 3,917 bytes for both symbols.
- Production-shaped fixed ELF `.text`: 64,343 -> 62,935 bytes (`-1,408`).
- No frontend stack references or spills.
- 1,000 frontend exact differential trials: pass.
- Canonical KAT: 100/100 request and response byte-exact.

The canonical SHA-256 values are:

```text
req 36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
rsp 22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

### Matched-cage local gate

Median candidate-minus-control core cycles across eight launches:

| Placement | Frontend | Forward | 2 x Forward |
|---|---:|---:|---:|
| Normal | -0.431 | +0.267 | +0.647 |
| Reversed | -0.486 | +0.292 | +0.356 |

The loop overhead is therefore effectively neutral.  Shrinking the active body
does not create a meaningful arithmetic penalty, but it also is not a local
Forward acceleration mechanism.

### Fixed-ELF whole-KEM: compact minus GT Clean

| ASLR | Keypair | Encap | Decap |
|---|---:|---:|---:|
| off | +65.469 | **-132.167** | +86.833 |
| on | +82.823 | **-94.948** | +12.979 |

ASLR-off confidence intervals are entirely positive for Keypair/Decap and
entirely negative for Encap.  With ASLR enabled, Keypair remains a clear
regression, Encap remains a clear improvement, and Decap becomes neutral.  The
same frontend is used by all three operations, so this operation-specific split
cannot be attributed to its nearly-neutral arithmetic delta.  It is executable
delivery caused by the 1.4-KiB image contraction.

### Fixed-ELF whole-KEM: compact minus Official

| ASLR | Keypair | Encap | Decap |
|---|---:|---:|---:|
| off | -255.281 (-1.188%) | +26.833 (+0.096%) | -150.240 (-0.777%) |
| on | -267.063 (-1.242%) | +57.219 (+0.204%) | -266.438 (-1.375%) |

Keypair and Decap remain faster than Official.  Encap is brought into a very
narrow parity band, but does not establish a win; the ASLR-on bootstrap
confidence interval crosses zero and the ASLR-off interval is slightly
positive.

## Decision

**Promote 036 as the selected experimental Encap architecture and the baseline
for 037; do not replace the global GT Clean implementation with it yet.**

036 confirms the mechanism proposed by this experiment: compact active hot code
can materially change whole-caller delivery even when local arithmetic is
neutral.  However, the benefit is redistributed between operations rather than
creating a robust aggregate backend win.  The candidate is retained as an
Encap-oriented and footprint-attribution reference.

`GT32-COMPACT-Q24-037` therefore starts from the 036 export rather than plain GT
Clean.  It applies the same shape-class audit to Q24, where the active body is
larger and the packet schedule may offer more total static reduction.  It must
again be judged across all three KEM operations; this result does not authorize
broad alignment or linker-order tuning.
