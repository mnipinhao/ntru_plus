# P1 NTRU+1152 NTT16-first / blocked gate

## Result

The one permitted NTT16-first challenger stops before ASM. It is not rejected
mathematically; it lacks the exact machine schedule required to justify a
high-risk representation prototype.

The frozen current control is the NTT9-first persistent-AoS C1 path:

| linked/generated item | current value |
|---|---:|
| loads after top split | 144 |
| stores after top split | 144 |
| routing | 576 |
| NTT9-to-NTT16 materialization | 72 stores + 72 reloads |
| peak YMM | 16 |

NTT16-first must form coefficient planes at entry, run the q transform, and
then accumulate nine row values for NTT9. Its only credible credit is removing
some or all of the 72-vector axis materialization. No current schedule proves
that deletion without spilling, recomputing other planes, or creating an
equivalent materialized boundary.

The existing exact early-plane C2 schedule is the closest machine-geometry
control. It needs 792 routes, versus C1's 576 (`+216`). This is a warning, not
a universal lower bound: a future NTT16-first schedule may reopen if it gives
an exact full-branch def/use replay with peak YMM <=16 and shows the complete
load/store/routing/constant delta after entry formation.

Generated gate:

```text
generated/p1-ntt16-first-gate.json
```

Reproduce it with:

```sh
python3 tools/generate_p1_ntt16_first_gate.py \
  --schedule generated/gt9x16-prod3-aos-schedule.json \
  --output generated/p1-ntt16-first-gate.json \
  --check
```

No linked candidate, paired benchmark, P2 work, production selector, or
SUPERCOP implementation is authorized by this checkpoint.

