# NTRU+ mlkem-native-inspired batch cycle benchmark

The local research default for **new component and caller diagnostic benchmarks**
is the reusable engine in `mlkem_batch.{h,c}`. It adapts the batching method in
[mlkem-native's component benchmark](https://github.com/pq-code-package/mlkem-native/blob/main/test/bench/bench_components_mlkem.c),
as inspected on 2026-09-23:

- prepare the test input outside timing;
- run 50 warm-up operations;
- read a cycle counter once before and once after 300 consecutive operations;
- repeat this for 20 tests;
- sort the 20 batch totals, select element `tests >> 1`, then divide by 300.

The NTRU+ A/B extension alternates arm order AB/BA across tests, uses the
same prepared semantic input for both arms, keeps all 20 raw batch totals,
and repeats the process independently. The counter is supplied by each
architecture harness. The 768 example uses **pinned SUPERCOP `cpucycles()`**,
whose actual backend is printed and saved; this is *not* a byte-for-byte copy
of mlkem-native's `get_cyclecounter()` or its `PERF`/`PMU` selection.

Defaults are in the header and must be explicit in every report. For serious
local diagnostics use nine fresh pinned processes; three are only a short
screen. Before timing, run correctness preflight and verify CPU pinning,
governor, turbo, ASLR and counter backend. Preserve the exact ELF, source
hashes, build command, raw totals and per-process medians. Do not set sysfs
from a runner. For close A/B results, also run a separately built reversed
placement; do not select the most favorable placement as the sole headline.

The operation contract must state whether reset/copy is timed. A destructive
inverse cannot be called 300 times on one already-transformed buffer and
still be called “inverse”. The current 768 example therefore reports
`copy_plus_inverse`: the 1,536-byte reset copy is **inside** the timed
operation. Its complete-Decap region has prepared valid CT/SK inputs and no
per-iteration reset. These are two different cutpoints, not additive costs.

Run the engine self-test:

```sh
make -C bench test-mlkem-batch
```

The current 768 example, from its experiment directory:

```sh
make check-yang-stage5reuse
python3 tools/run_mlkem_batch.py --tag NEW_NORMAL_TAG --processes 9
python3 tools/run_mlkem_batch.py --tag NEW_REVERSED_TAG --processes 9 --reversed-placement
```

The batch number answers warm, repeated-throughput cost under its stated
input/residency contract. It **does not replace** unmodified Native SUPERCOP
`crypto_kem/measure.c` when making Official-compatible KEM claims. Existing
SUPERCOP StQ campaigns and old per-operation diagnostics retain their own
labels; never merge or directly subtract numbers from unlike methods.

For an ASM change smaller than normal link-placement effects, use separate
same-name, same-size ELFs and audit symbol addresses, code outside the edited
function, and constant bytes before comparing their absolute batch medians.
The 768 Yang stage-5 example is `tools/run_yang_fixed_layout.py` in its
experiment. Its ABBA/BAAB blocks use fresh processes, not two arms within a
single process. Per-process `setarch -R` is available for an ASLR-off control
without changing host sysfs. Equal relative layout controls one important
confounder; it does not make process state or frontend behavior identical.
