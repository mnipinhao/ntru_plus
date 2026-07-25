# Section-GC balanced replacement rerun

Each binary measurement uses 61 samples x 2,000 calls on Pi 5 core 3.
Ten outer rounds alternate AB/BA order. All processes completed their
post-benchmark KEM correctness check.

| Mode | Current median | GC median | Delta p10 | Delta p50 | Delta p90 | GC wins |
|---|---:|---:|---:|---:|---:|---:|
| kem_keygen | 37711.5 | 37716.5 | -3.2 | +16.0 | +26.2 | 2/10 |
| kem_enc | 37601.0 | 37592.0 | -42.3 | -9.0 | +105.4 | 6/10 |
| kem_dec | 32845.5 | 32850.5 | -40.5 | +3.0 | +25.4 | 5/10 |
