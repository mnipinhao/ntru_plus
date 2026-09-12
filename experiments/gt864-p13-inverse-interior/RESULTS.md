# P13-A — wide Inverse scratch clear (promoted)

## Result

P13-A is accepted and promoted.  It preserves every arithmetic, FR0 scale,
range, layout, alias, scratch-size and public-ABI contract.  Only the fixed
zero-store granularity in `gt864_inverse_ternary_asm` changes.

| Same-boundary Pi 5 metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| Inverse-to-ternary cycles | 5418.609 | 5393.945 | -24.664 |
| Inverse-to-ternary instructions | 9096.125 | 8805.125 | **-291** |
| Inverse-to-ternary branches | 228.188 | 114.188 | **-114** |
| Complete Decaps cycles | 40910.900 | 40899.050 | -11.850 |
| Complete Decaps instructions | 96081.950 | 95790.950 | **-291** |
| Complete Decaps branches | 1230.100 | 1116.100 | **-114** |

Paired-sample deltas are stronger than the difference of independent medians:

- Inverse-to-ternary: median **-23.555 cycles**, IQR
  `[-24.891,-23.172]`, 366 pairs.
- Complete Decaps: median **-20.050 cycles**, IQR
  `[-31.537,-3.200]`, 186 pairs.
- Keygen and Encaps retire exactly the same instructions and branches; their
  cycle variation is noise and no performance claim is made for them.

## Exact change

The old tail-padding initialization used 16 iterations of:

```
stp xzr, xzr, [x9], #16
subs x10, x10, #1
b.ne loop
```

P13-A writes the same 256-byte interval using eight fully unrolled
`stp q0,q0,[x9],#32` after zeroing `v0`.  The old post-operation scratch wipe
used the same three-instruction loop 112 times.  P13-A uses fourteen fixed
iterations, each with four 32-byte full-vector stores followed by one
`subs/b.ne`, still writing exactly 1792 bytes.

The changed regions dynamically fall from 388 to 97 instructions and from 128
to 14 branches.  Store addresses remain sequential and public; no coefficient
is live at either boundary.  `RESTORE_PUBLIC` remains unchanged and still
clears all volatile SIMD state before restoring callee-saved registers.

## Validation and provenance

- Baseline production revision: `dd8c3146`; P12 control revision: `b6d59f3e`.
- Production and tested candidate `gt864_native_public.S` SHA-256 are identical:
  `c49a7454c5ea60a575e6f69794b6a2a548a76f1f85d49e4f4c440eb34d258e71`.
- Both package manifests, fresh Linux builds, `test_kem` and 100-case KAT pass.
  KAT SHA-256 remains
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- The complete 417216-byte malformed-ciphertext transcript is identical;
  SHA-256 remains
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- Candidate passes 4096 inverse-to-ternary exact, in-place alias, AAPCS and
  exact scratch-wipe cases.  Every paired process repeats valid/tampered KEM
  and inverse/alias comparisons before PMU.
- Pi 5 Cortex-A76 core 3, GCC 14.2.0, ondemand governor, 60.9 C after run,
  `throttled=0x0`; six balanced processes.  Selected SUPERCOP root remains
  `/home/pi/supercop-20260831` but was not re-benchmarked in this candidate-only
  gate.
- No Slothy pass was needed: the candidate changes fixed wrapper stores and
  loop control, not a schedulable arithmetic region or register allocation.

The first remote attempt completed build/KAT/malformed checks but its extra
probe path was packaged incorrectly.  The corrected run used a new `pi-run-v2`
directory and completed all gates; no failed-run performance data is used.

## Next gate

P13-B now targets the six-call `lazy_i16` arithmetic interior.  The candidate
must reduce actual mulmod/table/copy work with a closed range/scale proof and a
same-boundary modeled cycle margin.  Terminal routing and scratch clearing are
not reopened.  P14 ToBytes remains next after the Inverse arithmetic decision.
