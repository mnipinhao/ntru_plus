# Results

## Decision

The Clean-GT Q24 serializers have a real intrinsic cost relative to Official,
but it is a low-tens-of-cycles cost rather than the 40--100 cycle component
suggested by the old cumulative prefix frontier.

Therefore:

- both serializer sites remain selected production boundaries;
- no new Q24 architecture search is opened from this result;
- the 050 serializer checkpoint movements must not be used as component costs;
- Encap micro-attribution is closed unless a new structural premise deletes an
  operation class rather than merely rescheduling the current Q24 body.

## Correctness and causal controls

One real deterministic Clean-GT Encap fixture was built through the actual
producer paths:

- `rhat`: CBD1 -> M Forward;
- `ciphertext`: unpacked `h`, M Forward `r`, SOTP M Forward `m`, then
  `B3(h,r)+m`.

Each GT output was serialized and decoded by Official `poly_frombytes` to form
the matching Official physical input.  Re-serialization with Official was
byte-identical at both sites.

The timed interval contains only one serializer call.  Official and GT share
the same ELF and output address; Forward, B3, Hash, and cleanup are excluded.

## 256-launch paired TSC gate

CPU 1, 1024 paired observations per launch, 256 independent launches:

| Site | Official median | GT median | GT - Official | 95% bootstrap CI | Direction |
|---|---:|---:|---:|---:|---:|
| rhat | 172 | 192 | **+20 TSC** | [20, 20] | 256/256 GT slower |
| ciphertext | 172 | 192 | **+20 TSC** | [20, 20] | 256/256 GT slower |

The ciphertext symbol is the production five-byte tail jump to the same full
signed-int16 Q24 body, so equal site costs are expected.

## Region PMU corroboration

`perf stat`, CPU-core events, 200,000 calls per run, 11 repetitions per event:

| Site | Delta core cycles | Delta instructions | Delta retired loads | Delta retired stores |
|---|---:|---:|---:|---:|
| rhat GT - Official | +24.54 | +56.27 | +98.23 | +63.78 |
| ciphertext GT - Official | +21.77 | +68.21 | +100.65 | +64.00 |

The event deltas include identical loop/call overhead on both sides.  The load
and store differences are consistent with the current Q24 execution shape:

- memory-source pair-pack and shuffle constants;
- packet-local M-to-wire routing;
- two partial/overlapping stores per 24-byte packet.

The additional retired memory operations do not translate one-for-one into
cycles.  Hot data and out-of-order overlap hide most of the work, leaving about
20 TSC of observable latency per serializer.

## Consequence for Encap accounting

The two serializers together explain only about 40 TSC in this controlled
component experiment.  They do not explain the old approximately +100 movement
across the hash checkpoint, and they do not explain the whole remaining Clean
GT versus Official Encap gap.

Experiments 037/038 already rejected compact-loop rewriting, 041 rejected Q24
constant residency, and 051 rejected a smaller real producer range.  With 054
below the architecture-reopen threshold, another local Q24 scheduling or store
topology probe is not justified without a new operation-class deletion.

