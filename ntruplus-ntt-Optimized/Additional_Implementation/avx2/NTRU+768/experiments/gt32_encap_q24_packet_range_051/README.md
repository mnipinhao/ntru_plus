# GT32-ENCAP-Q24-PACKET-RANGE-051

## Question

Can either Encap producer use a cheaper producer-specific Q24 reducer because
some physical packets or lanes have a smaller range?

The audited producers are:

1. `CBD1 -> frontend -> ntruplus768_ntt_m_avx2` (`rhat` serialization), and
2. `B3(h,r) + m` (ciphertext serialization).

This experiment is generator-only. It does not modify GT Clean.

## Important contract correction

The selected symbols whose names contain `lazy10788` and `highrange12699` do
not implement those old bounds. The current selected executable tail-jumps to
the full signed-int16 Q24 reducer. The old names are historical and are not
valid range evidence.

The audit therefore derives bounds from the selected `ntt.s`, `ntt_m.s`,
`basemul.s`, and `pack.s` instruction/data flow and constant tables.

## Method

`tools/audit_packet_ranges.py` conservatively propagates an absolute bound for
every one of the 768 physical 16-bit lanes through:

- the raw top split and per-lane frontend twist;
- DFT3;
- progressive-M S1--S5, including half/qword routing;
- `FR_PACKED_TO_PLANES`;
- the exact M-to-Q24 packet transpose/order;
- for the ciphertext producer, general B3, the R-squared finalizer, and add-m.

The signed Montgomery bound is:

```text
ceil(A * |factor| / 65536) + ceil(q / 2), q = 3457.
```

Packets/lanes are classified as:

- class 1: `|x| < q`, sign correction is sufficient;
- class 2: `|x| < 2q`, one conditional `+/-q` is sufficient;
- class 3: wider, keep the full reducer.

The proof is conservative rather than an observed-value corpus. A class-3
result means the current producer contract cannot safely select a cheaper
reducer from this proof.

## Result

| Producer | Minimum lane bound | Maximum lane bound | Packet classes | Lane classes |
|---|---:|---:|---:|---:|
| Forward `rhat` | 17,445 | 18,348 | 48/48 class 3 | 768/768 class 3 |
| `B3(h,r)+m` ciphertext | 19,235 | 20,220 | 48/48 class 3 | 768/768 class 3 |

There is no physical packet, and not even an individual physical lane, whose
conservative contract falls below `2q = 6914`.

## Decision

The proposed Encap-only packet/lane selective Q24 reducer is a static hard
stop for the selected producer contracts:

```text
producer-specific range specialization: CLOSED
reason: every packet and every lane remains class 3
```

This does not claim that the full-signed-int16 reducer is globally optimal.
It closes only the idea that the existing Encap producers already expose a
non-uniform packet/lane range allowing sign-only or one-q packet variants.

Reopen only if the producer arithmetic/range contract changes, for example if
Forward or B3 emits a newly centered representation as part of work it already
must perform. Do not reopen from the stale symbol names alone.

## Reproduce

From the NTRU+768 GT Clean directory:

```sh
python3 experiments/gt32_encap_q24_packet_range_051/tools/audit_packet_ranges.py \
  --root . \
  --output experiments/gt32_encap_q24_packet_range_051/generated/packet_ranges.json
```
