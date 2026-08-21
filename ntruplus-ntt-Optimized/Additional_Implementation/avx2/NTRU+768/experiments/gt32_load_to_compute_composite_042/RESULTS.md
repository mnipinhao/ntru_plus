# GT32-LOAD-TO-COMPUTE-COMPOSITE-042 results

## Decision

The two 041 load-to-compute primitives remain locally qualified, but their
composite is **not selected for GT Clean**.  The complete Encap effect is not
stable under exact control/candidate target-position reversal.

No production source was changed.  No clean export or formal SUPERcop gate is
started from this experiment.

## What was compared

The final harness uses one fixed-address common Encap caller.  Its two indirect
targets select the four factorial profiles:

| Profile | Decode | B3 |
|---|---|---|
| A | production | production |
| D | resident `0123` mask | production |
| B | production | preload `qinv` |
| DB | resident `0123` mask | preload `qinv` |

The indirect calls are identical overhead in all profiles.  The target bodies
are equal-sized and live in isolated objects.  Normal and Reversed exchange
their exact virtual addresses:

| Target | Normal control | Normal candidate | Reversed control | Reversed candidate |
|---|---:|---:|---:|---:|
| Decode | `0x402d00` | `0x403ac0` | `0x403ac0` | `0x402d00` |
| B3 | `0x405180` | `0x4058c0` | `0x4058c0` | `0x405180` |

The common caller remains at `0x401d30`.  Decode body/wrapper sizes are
3470/27 bytes in both variants; B3 is 684 bytes in both variants.

## Correctness

Both binaries check all D/B/DB ciphertext and shared-secret results byte for
byte against A before measurement.  Normal and Reversed smoke tests pass.

## Final 48-launch result

The measurement source is SUPERcop `libcpucycles` (`default-perfevent`), pinned
to CPU 0.  A launch contains 32 rotating-order rounds; each profile/round is the
median of 31 calls after warm-up.  The launch median is the statistical unit.

| Placement / effect | Median cycles | Wins | Bootstrap 95% CI |
|---|---:|---:|---:|
| Normal D−A | −30.75 | 45/48 | [−36.25, −22.5] |
| Normal B−A | −5.0 | 33/48 | [−11.75, −1.5] |
| Normal DB−A | **−35.5** | **47/48** | **[−42.5, −29.0]** |
| Normal interaction | −1.25 | 25/48 | [−5.5, +8.0] |
| Reversed D−A | +26.75 | 1/48 | [+21.5, +34.5] |
| Reversed B−A | −34.25 | 48/48 | [−44.5, −28.5] |
| Reversed DB−A | **−4.0** | **27/48** | **[−14.5, +3.0]** |
| Reversed interaction | +9.5 | 19/48 | [−4.5, +15.5] |

## Interpretation

The exact address reversal exposes two strong target-placement effects:

- the Decode candidate is favorable in the later slot and unfavorable in the
  earlier slot;
- the B3 candidate is strongly favorable in the earlier slot and weak in the
  later slot.

DB therefore wins strongly in Normal, where Decode receives its favorable
slot, but is statistically unresolved in Reversed because the Decode loss and
B3 gain nearly cancel.  The interaction is compatible with zero in both
placements, so there is no evidence of a new synergistic composite mechanism.

This does not invalidate 041's matched local results.  It establishes the
narrower production fact:

> Approximately 6--9 cycles of local load-to-compute credit is too small to be
> delivered robustly by this full Encap image.

## Close and reopen conditions

Closed:

- promotion of Decode residency plus B3 preload as the current GT Clean Encap;
- clean export and formal SUPERcop benchmarking for this composite;
- padding/alignment search whose only purpose is to select the favorable slot.

Preserved:

- Decode mask residency as a local-qualified reference;
- B3 `qinv` preload as a local-qualified reference;
- the matched-target factorial harness for future composition checks.

Reopen only when another independently justified Encap change alters the
selected code shape, or when a larger operation-class deletion can make the
expected caller effect materially exceed the observed placement sensitivity.

