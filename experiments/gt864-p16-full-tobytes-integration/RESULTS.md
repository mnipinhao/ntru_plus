# P16 result — P15 Full schedule promoted

P16 replaces only production Full ToBytes with the exact retained P15
Cortex-A76 schedule.  Small ToBytes remains P9 and its target object is
byte-identical to the baseline.

## Contract and correctness

- Candidate source SHA-256:
  `2a59fbf9567124f28c009de0c1989e33600be64e795c4a47e634ba4d0a46deb2`.
- Full and Small retain 1,378 and 1,277 instructions per top helper.
- Neither top helper has coefficient-Q stack accesses.
- Small object SHA-256 is unchanged:
  `a9e783d12b21fd639cea17bb831f4232cdeb29dc2e33391efc581499d5aaec21`.
- Baseline and candidate each pass 64 KEM round trips/tampered rejections.
- Six full-KEM compatibility runs each pass 100 exact and 100 tampered cases.
- KAT SHA-256 is unchanged:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed transcript SHA-256 is unchanged:
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

The copied production assembly and both resulting ToBytes objects are
byte-identical to the tested isolated candidate.  The final production tree
also passes its source manifest and `make check` on Pi 5.

## Pi 5 full-KEM PMU

Six processes alternate AB/BA order.  Each operation has 252 paired
observations pinned to Cortex-A76 CPU 3.  The host remained unthrottled.

| Operation | P15 production baseline | P16 candidate | Paired cycle delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen | 43658.875 | 43583.125 | -74.875 | 0 | 0 |
| Encaps | 45313.425 | 45239.225 | -77.775 | 0 | 0 |
| Decaps | 40397.925 | 40327.375 | -71.050 | 0 | 0 |

All three operation gates pass.  The cycle benefit is a scheduling effect;
P16 does not claim reduced work.

## Decision and next work

Promote P16 Full.  Keep Small P9 and reject the P15 Small schedule.  P17 is a
fresh production-versus-selected-Official profiler checkpoint, needed because
P13-B/C and P16 have changed the bottleneck balance since P12.
