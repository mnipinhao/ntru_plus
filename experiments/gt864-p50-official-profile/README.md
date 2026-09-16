# GT864 P50 selected-Official profiler

P50 is a measurement-only checkpoint. It compares exact committed P48
production (P49 changed only experiment documentation) with the user-selected
SUPERCOP 20260831 `ntruplus864/aarch64` implementation on Pi 5.

Unlike the earlier profiler, this campaign attributes the P47 Decaps
Full-to-compare boundary and the P48 Encaps Full-to-`hash_g` boundary as
separate groups. This permits matched-boundary comparison after serialization
was fused with its consumers. The selected Official's inline `verify` is also
instrumented so P47 is compared against `Full ToBytes + verify`, not against
serialization alone.

Run with:

```sh
python3 experiments/gt864-p50-official-profile/run_pi5.py
```

Generated build trees and raw logs remain excluded; summarized evidence is
committed after all correctness and measurement gates pass.
