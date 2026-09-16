# Integrated GT864 Pi5 validation — 2026-09-08

**Integration gate passes; full behavioral parity with new Official does not.**
No production algorithm changes were made during this test turn. Canonical
input rejection remains an important unresolved compatibility/security gate.

## Exact sources and environment

Isolated remote directory:
`/home/pi/ntruplus-experiments/gt864-integrated-20260908.wD3WXn`.

- `gt`: final production source with ToBytes, BaseInv and first-Decaps paired
  R^-1 BaseMul/Inverse integrated; fresh Linux build, not reused old objects.
- `old`: pre-BaseInv/Inverse package, already containing the same new ToBytes.
- `official`: copied read-only from
  `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64/`.
  Source is SHAKE256 and architecture marker is aarch64. No ref/opt/avx2 or
  archived 20260627 substitution. Upstream-latest provenance is not asserted.

Official sources are unmodified. Standalone harness supplies an identity
crypto_kem.h namespace, randombytes declaration, and cryptoint optblocker
definition; it uses the installed SUPERCOP aarch64 crypto_uint64.h. SUPERCOP
declassification hooks are inactive in this ordinary native timing build.
These are fresh paired PMU measurements of those sources, NOT values extracted
from SUPERCOP's complete benchmark data file or its compiler-selection sweep.

GCC 14.2.0, -O3 -std=c11 -march=armv8-a+simd, CPU3 affinity; identical compiler
policy. Six AB/BA processes x41 samples. Four Keygen or twenty Encaps/Decaps
calls per batch; deterministic matching seeds. User-space cycles/instructions/
branches, no overhead subtraction. Median of six process medians. Governor
ondemand; temperature 64.8 C before/after, throttle flags 0x0. No new Slothy run.

The user's complete SUPERCOP job was no longer running when measured. Its log
ended with `make: *** wait: No child processes`; this is not recorded as a
successful complete SUPERCOP run. No processes were stopped or job files edited.

## Linux correctness

- Fresh `make check` passes for gt and old: manifest, shared-library link,
  64 valid/tampered KEM cases and 100-case KAT generation.
- All 100 KAT cases are byte-identical across old, gt and Official.
  SHA256 .rsp: 0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c.
- Actual Linux production objects pass BaseInv 808 cases (517 success /291
  failure), all 288 injected zero leaves, alias, canaries, AAPCS and wipe.
- Inverse passes 256 inputs +256 BaseMul R^-1 chains, range/identity, alias,
  canaries, AAPCS and 1792-byte scratch wipe.
- Old -> gt: exact deterministic transcript equality for 32 valid, 32 tampered
  and 1024 malformed ciphertext cases. Transcript SHA256:
  2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67.
- Official -> gt: 32 valid/tampered and 32 general malformed cases pass the
  initial harness. This limited result is superseded for overall compatibility
  by the targeted noncanonical counterexample below.

## Noncanonical ciphertext counterexample: existing GT gap

Take a valid Official-generated ciphertext. For a packed 12-bit coefficient
x <=638, replace x with x+3457 (still <=4095). This changes wire bytes but not
the field element. Test seed 864 yielded 79 such candidate coefficients.

All 79 variants:

- Official: return 1 (reject).
- Old GT: return 0 and recover the original valid shared secret.
- Integrated GT: return 0 and recover the original valid shared secret.

The first differing byte offsets were 9,99,105. `check-noncanonical.c` is the
reproducer; run it against ./old.so and ./gt.so in the isolated build directory.

New Official poly_frombytes returns validation status and Decaps rejects invalid
ct/f/hinv encodings. GT's FromBytes currently unpacks 12-bit values without
that validation and the caller has no corresponding rejection path. Random
malformed inputs usually fail later anyway, which is why the general test
did not detect this. This discrepancy predates the native integration, but
must not be dismissed as performance-only or claimed as full API equivalence.
No security reduction or exploit scope beyond this concrete acceptance
counterexample is claimed. Invalid pk/sk paths need their own audit too.

## Valid-input full KEM results

| Old package -> final GT | Old cycles | GT cycles | Change |
| --- | ---: | ---: | ---: |
| Keygen | 53356.625 | 51436.875 | -3.598% |
| Encaps | 45629.800 | 45628.275 | -0.003%, neutral |
| Decaps | 43990.175 | 43144.075 | -1.923% |

All six paired Keygen/Decaps deltas favor integration; Encaps varies in sign.

| New Official -> final GT | Official cycles | GT cycles | GT change |
| --- | ---: | ---: | ---: |
| Keygen | 44295.500 | 51434.000 | +16.116% slower |
| Encaps | 46430.725 | 45642.350 | -1.698% faster |
| Decaps | 40745.375 | 43133.125 | +5.860% slower |

The Official comparison is **valid-input timing only**. Official performs
additional input validation that GT lacks; these are not fully equivalent
validation contracts. Do not advertise the Encaps result as an equivalent-API
win until canonical decoding/rejection behavior is aligned and remeasured.

## Evidence and next gate

`integrated-pi-results.json` preserves counters and per-process deltas;
`integrated-pi-environment.json` preserves all Official source and binary hashes.
Raw logs, disassembly and samples are gitignored under build/integrated, with
the remote copy under experiments/gt864-native-asm/build/integrated.

Binary hashes:

- old.so: 6fcbe41bcd9f94cefc0196759357c89a650306420bfbb8e9e1426d946b30a7e5
- gt.so: ff7c5aaa60906b844f46446b5c26a20bf002f7828c549359028d49359fd0ed4e
- official.so: 8773a7c4ed9b7da34cc7e0e419c79b17edd876e9e7e3e52a0f999611dcd3e6ce

Next gate should align GT FromBytes validity reporting and KEM rejection with
the selected new Official, including invalid pk, ciphertext and secret-key
encodings and output clearing. Preserve the native arithmetic and ToBytes
optimizations, expand differential tests, then rerun the same valid/full-API
comparison. This turn tests/reports the gap; it does not silently implement a
different decoding contract or change the user's SUPERCOP tree.
