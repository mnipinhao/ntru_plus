# GT32-HASH-HANDOFF-052

This experiment isolates the Encap `rhat serializer -> hash_g` handoff found
by experiment 050. It does not time cumulative prefixes and does not modify GT
Clean production.

One ELF contains both producers:

```text
Official NTT -> Official poly_tobytes --\
                                       +-> same buffer -> same hash_g address
GT frontend -> N5 -> Q24 -------------/
```

The producer outputs are checked byte-for-byte before timing. Only `hash_g` is
inside the TSC interval. Three entry-state modes are compared:

- `raw`: hash immediately after the producer;
- `mfence`: drain/order prior stores before timing the hash;
- `common_copy`: both producers write a staging buffer, then the same AVX2 copy
  writes the hash input buffer before timing.

`mfence` and `common_copy` are attribution controls, not production proposals.
The process is pinned to one logical CPU by the runner. Each launch reports
medians from 1024 paired measurements; launch medians are the statistical unit.

## Decision

The 256-launch result is exactly neutral in raw mode: median `GT-Official = 0`
TSC with bootstrap CI `[0,0]`. Neither `mfence` nor common-copy normalization
changes the differential. The approximately 100-cycle cumulative movement in
050 is therefore not a slower `hash_g` body after the GT producer. See
`RESULTS.md`.

Build and run:

```sh
./experiments/gt32_hash_handoff_052/tools/build.sh
python3 experiments/gt32_hash_handoff_052/tools/run.py \
  --binary experiments/gt32_hash_handoff_052/build/hash_handoff_052 \
  --blocks 64 --cpu 1 \
  --output experiments/gt32_hash_handoff_052/results/handoff-64.json
```
