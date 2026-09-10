# P5 — KEM temporary reuse

## Decision

`accept` and promote as the GT864 production KEM source.

P5 changes only C object lifetimes.  The transform, FR0 representation, KEM
ordering, rejection policy, hash backend, assembly kernels and public ABI are
unchanged.

## Static result

| Function | P4 frame | P5 frame | Difference |
|---|---:|---:|---:|
| Keygen | 10,720 | 8,992 | -1,728 bytes |
| Encaps helper | 8,704 | 7,392 | -1,312 bytes |
| Decaps | 16,288 | 11,072 | -5,216 bytes |

The small alignment differences around Encaps and Decaps are compiler-selected;
the source-level objects removed are exactly 1,296 and 5,184 bytes respectively.
The linked GCC 14.2 object also shrinks Keygen/Encaps/Decaps from 488/436/756 to
468/404/640 bytes of code.

Cleanup remains explicit for every surviving secret-bearing byte array and
polynomial on both normal and early-rejection paths.  Removed cleanup calls
cover only storage that no longer exists or values fully overwritten by their
new public-output consumer.

## Correctness

- Baseline and candidate passed 64 valid/tampered KEM iterations.
- Both produced the exact 100-case KAT SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- 13,824 non-canonical cases passed across Encaps `pk`, Decaps `ct`, `sk[0]`
  and `sk[1]`, all 864 positions and values 3457/4095.
- Baseline and candidate malformed transcripts are byte-identical with SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

## Raspberry Pi 5 paired PMU

Six balanced runs, core 3, 40 retained samples per implementation per run:

| Operation | P4 cycles | P5 cycles | Delta | Instructions delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen | 46,483.500 | 46,388.000 | -95.500 (-0.205%) | -149 | -36 |
| Encaps | 45,827.850 | 45,778.900 | -48.950 (-0.107%) | -124 | -29 |
| Decaps | 43,526.200 | 43,359.400 | -166.800 (-0.383%) | -455 | -108 |

Every per-run median delta was non-positive.  Encaps is the noisiest boundary
(`-109.35` to `-0.40` cycles), but all six runs retain the expected exact static
instruction/branch reduction and the pooled median is favorable.  The result is
therefore accepted primarily as a memory/cleanup simplification with a small,
consistent full-KEM improvement—not as a new arithmetic optimization.
