# NTRU+768 / NTRU+1152 Official AVX2: direct 12-bit codec (NTRU+864 exp002 idea) — analysis and stop decision

Date 2026-09-23, branch `official-opt-lazy-864-1152` (from `01a9895` = `origin/avx2-official-opt`, not pushed).
This note answers one question: does the NTRU+864 exp002 "direct 12-bit codec" also pay off for Official NTRU+768 and NTRU+1152 `poly_tobytes` / `poly_frombytes`?
The work had a decision gate: stop if the estimated saving is below about 50 cycles per call for both functions of a parameter.

**Result: stopped for both parameters.**
The analysis and a scratch measurement both put the saving well below the gate:

| saving per call, same ELF, mean of normal and reversed link order | NTRU+768 | NTRU+1152 |
|---|---:|---:|
| tobytes, best direct design vs the freeze2op baseline | −19.5 | −38.3 |
| frombytes, best direct design vs Official | −11.3 | −18.2 |

No candidate was built. There is no generator, no KEM binding and no Native run.
The scratch kernels, bench and runner are committed so the measurement can be repeated.
Nothing under `NTRU+768/experiments/avx2_official_opt_001/` (another agent's directory) was read for this work or written.
The NTRU+864 generators and outputs are untouched (`--check` passes).

All directories below are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`.
The shared files are in `common/official_opt_lazy/`:
- `bench/scratch_codec8.c`: the scratch kernels (intrinsics);
- `bench/bench_codec8_scratch.c`: the component bench, plus a `check` mode that runs the differential;
- `bench/count_codec8_scratch.c`: the instruction-count helper;
- `codec8_scratch.mk`: build rules, included by both experiment Makefiles;
- `tools/run_codec8_scratch.py`: the timing runner.

Results are in `NTRU+768/experiments/avx2_official_opt_freeze_001/results/` and `NTRU+1152/experiments/avx2_official_opt_001/results/`.

## 1. Internal layout (both parameters)

Official `pack.s` for 768 and for 1152 is the same file except for two loop bounds (`lea 1536/2304`, `lea 1152/1728`).
Both work on 128-coefficient blocks of 8 ymm registers (256 bytes in, 192 wire bytes out), with 6 blocks for 768 and 9 for 1152.

In block b, register r (poly bytes `256b + 32r ..`), 16-bit word l (0..15) holds **wire coefficient 128b + 8l + r**.
This is 8-way SoA per 128 coefficients.
It was confirmed empirically: Official `poly_frombytes` of a wire with c_i = i puts i at `coeffs[128b + 16r + l]`, for both parameters.
The scratch kernels also assume this layout and match Official on the exhaustive sweep in §4.

What follows from this layout:
- Wire group l of a block (12 bytes, coefficients 8l..8l+7) is word l of all eight registers. Lane 0 holds groups 0..7 and lane 1 holds groups 8..15.
- Wire pair (8l+2s, 8l+2s+1) is `(R_2s[l], R_2s+1[l])`: **the pairs are in-lane**, in the same word of two registers, as in NTRU+864.
- Unlike NTRU+864, Official 768/1152 already packs **directly from this layout in one pass**.
  There is no transpose to natural order and no stack round trip.
  NTRU+864's Official `poly_tobytes` did both: `poly_ntt_pack` to a 1728-byte stack buffer, then a second 4-way kernel.
  That second pass is where exp002's large saving came from, and it does not exist here.

## 2. What Official does now

### poly_tobytes (per 128-coefficient iteration)

The steps below follow `pack.s:11-142`:

1. Load 8 ymm registers.
2. Freeze all 8. This is Barrett (`vpmulhrsw v`, `vpmullw q`, `vpsubw`) plus an add of q, done in 3 ops in Official and 2 ops (`vpaddw q; vpminuw`) in the freeze2op candidate.
3. Dense bit-pack: `A0 = R0 ^ R1<<12`, `A1 = R1>>4 ^ R2<<8`, `A2 = R2>>8 ^ R3<<4`, and the same for R4..R7 to give B0..B2. Word l of A0 A1 A2 B0 B1 B2 is then exactly the 12 wire bytes of group l.
4. A 6×8 in-lane word transpose: `vpslld/vpsrlq 16` + `vpblendw`, `vpsllq/vpsrlq 32` + `vpblendd`, `vpunpck{l,h}qdq`. Afterwards each lane is one contiguous 16-byte wire chunk.
5. 6 `vperm2i128` join the lanes.
6. 6 × 32-byte stores.

| tobytes, per iteration | Official | freeze2op (baseline) |
|---|---:|---:|
| loads | 8 | 8 |
| freeze: Barrett / add of q | 24 / 24 | 24 / 16 |
| dense bit-pack (10 shifts, 6 xor) | 16 | 16 |
| in-lane transpose (12 shifts, 6 blendw, 6 blendd, 6 unpckqdq) | 30 | 30 |
| cross-lane `vperm2i128` | 6 | 6 |
| stores (32 B) | 6 | 6 |
| loop | 4 | 4 |
| **total** | **118** | **110** |
| vector uops by port class: p01 (mul/shift) / p015 (add/logic/min/blendd) / in-lane shuffle / cross-lane | 46 / 36 / 12 / 6 = 100 | 38 / 36 / 12 / 6 = 92 |

Per call (plus 2 constant loads, `lea` and `ret`) that is:
- NTRU+768: 712 Official and 664 freeze2op;
- NTRU+1152: 1066 Official and 994 freeze2op.

The linked-ELF `perf stat instructions:u` counts agree: 719 / 671 and 1073 / 1001, with about 7 instructions of harness dispatch per call.

### poly_frombytes (per iteration)

`pack.s:156-251` mirrors tobytes:

1. 6 ymm loads and 6 `vperm2i128`.
2. The same 30-op in-lane transpose, inverted.
3. A 22-op 12-bit extract (8 `vpand`, 10 shifts, 4 `vpxor`).
4. 8 stores.
5. A per-iteration canonical check: 7 `vpmaxuw`, `vpcmpgtw`, `vpmovmskb`, `or`.

| frombytes, per iteration | Official |
|---|---:|
| loads / cross-lane | 6 / 6 |
| in-lane transpose | 30 |
| 12-bit extract | 22 |
| canonical check | 10 |
| stores / loop | 8 / 4 |
| **total** | **86** |
| vector uops: p01 / p015 / in-lane / cross-lane (+ `vpmovmskb`) | 30 / 18 / 12 / 6 (+1) = 67 |

Per call that is 523 (768) and 781 (1152); `perf` measures 533 and 791.

### Calls per KEM operation (pinned `kem.c`, identical for 768 and 1152)

- `poly_tobytes`: keypair 3 (pk, sk f, sk h), encap 2 (ct r_hat, then ct), decap 2 (buf1 f, buf2 f).
- `poly_frombytes`: keypair 0, encap 1 (pk), decap 3 (ct, sk f, sk hinv).

## 3. Direct-pack designs for this layout

**exp002 transcribed literally ("madd"):**
1. Build 8 dword registers `D_s^{lo,hi} = vpmaddwd(vpunpck{l,h}wd(R_2s, R_2s+1), (1,4096))`. In each lane, dword j holds pair (group j or 4+j, s).
2. Collect the 4 pairs of each group with a 4×4 in-lane dword transpose (8 unpacks per half; the NTRU+864 5-op triple trick does not apply, because the groups are 4 pairs wide).
3. One `vpshufb` per register drops the 4th byte.
4. 16 × 16-byte stores at `12·group`, in ascending order (see the NTRU+864 section; the last group is stored as 8 + 4 bytes).

No cross-lane operation is needed. The cost is 16 + 16 + 8 = 40 vector ops after the freeze, 32 of them on the shuffle ports.

**Better for this layout ("pack"):** keep Official's dense shift pack (16 ops, 8 → 6 registers). Then:
1. 3 pairs of `vpunpck{l,h}wd` give dwords `X = (A0,A1)`, `Y = (A2,B0)`, `Z = (B1,B2)` per group. Group l is `[X_l Y_l Z_l]`, 12 bytes already in wire order.
2. A 7-op in-lane interleave per half puts one group in order in each lane:

       XYl = unpckldq(X,Y); XYh = unpckhdq(X,Y); Zs = vpsrldq(Z,4)
       O0 = unpcklqdq(XYl,Z)   = [X0 Y0 Z0 *]
       O1 = vpalignr(Zs,XYl,8) = [X1 Y1 Z1 *]
       O2 = vpblendd(XYh,Z,0x44) = [X2 Y2 Z2 *]
       O3 = unpckhqdq(XYh,Zs)  = [X3 Y3 Z3 0]

   No `vpshufb` is needed.
3. The same 16 stores as above.

That is 16 + 6 + 14 = 36 vector ops after the freeze, 18 of them shuffles. Against the freeze2op baseline it saves per iteration:
- 12 p01 shifts;
- 4 p015 blends;
- 6 cross-lane permutes;
- at a cost of 6 more in-lane shuffles and 10 more store uops (16 × 16 B instead of 6 × 32 B; `vextracti128 m128` is a plain store).

**frombytes ("word route"):**
1. 16-byte loads at `12·group` (`vmovdqu xmm` for groups 0..7, `vinserti128 m128` for 8..15). The last group is loaded from −4 and uses a lane-1 mask shifted by 4, so nothing is read past the end.
2. One `vpshufb` per register to the raw words `[b0b1, b1b2, b3b4, b4b5, …]`.
3. An 8×8 in-lane word transpose (24 unpacks).
4. `vpand 0xfff` on even registers and `vpsrlw 4` on odd ones.
5. `vpmaxuw` into one accumulator, with a single compare at the end.

The exp002 dword route (expand to `[b0 b1 b2 0]`, 4×4 dword transpose, and/shift/`vpackusdw`) costs 48 ops instead of 40.
The mirror of "pack" (inverse 7-op interleave, word de-interleave, Official's 22-op extract) costs 54.

| per iteration | tobytes freeze2op | tobytes pack | tobytes madd | frombytes Official | frombytes word route |
|---|---:|---:|---:|---:|---:|
| vector uops | 92 | **76** | 80 | 67 | **56** (incl. 8 `vinserti128`) |
| p01 / p015 / in-lane / cross-lane | 38 / 36 / 12 / 6 | 26 / 32 / 18 / 0 | 24 / 24 / 32 / 0 | 30 / 18 / 12 / 6 (+1) | 12 / 12 / 32 / 0 |
| loads / stores | 8 / 6 | 8 / 16 | 8 / 16 | 6 / 8 | 16 / 8 |
| instructions | 110 | 104 | 108 | 86 | 76 |

### Estimate before measuring

The freeze2op change removed 48 (768) and 72 (1152) vector uops per call. It measured −17 and −23 cycles, which is about 0.33 cycles per removed vector uop.
At that rate the best designs save:

| per call | NTRU+768 | NTRU+1152 |
|---|---:|---:|
| tobytes pack vs freeze2op (16 uops × iterations) | 96 uops ≈ −32 | 144 uops ≈ −48 |
| frombytes word route vs Official (11 uops × iterations) | 66 uops ≈ −22 | 99 uops ≈ −33 |

Every estimate is below 50 cycles per call; 1152 tobytes is the only one close.
The model also leaves out the 10 extra store uops (tobytes) and 10 extra load uops (frombytes) per iteration.
The gate therefore called for a short scratch measurement.

## 4. Scratch measurement (supercop-derived component timing, not Native)

The kernels are intrinsics compiled with the common O3GC recipe. They are not hand-scheduled asm.

**Correctness first.** `make codec8-scratch-check` runs release and ASan/UBSan/LSan builds. Results are in `results/codec8-scratch-check-20260923.json`.

tobytes covers 216,608 polys, checking freeze2op, pack and madd each against Official, byte for byte:
- every int16 at every position (K = 0, 1, 40503);
- 20,000 random polys;
- 64-byte canaries on both sides of the wire;
- input immutability.

frombytes covers 3,189,824 inputs (768; 511,391 of them rejected by Official) and 4,762,688 (1152; 756,767 rejected):
- every 12-bit value at every position over a valid background;
- all-equal patterns;
- random valid encodings and random byte strings;
- output and return value.

0 failures. No guard-page test, mutation check or KEM test was run, because no candidate was built.

**Timing.** `bench_codec8_scratch` puts every variant in one ELF. The run used:
- CPU 1, ASLR on;
- 31 fresh launches, with 12 rotated blocks × 32 = 384 observations per variant per launch;
- perf-event cpucycles from the disposable campaign;
- one call per observation. The ~220-cycle cpucycles overhead is in every absolute number and cancels in the deltas.

The reversed rows link the same sources in reverse order. All 4 batches ran under `phase_b_batch.py` and were clean on attempt 0 (pre-batch loadavg1 0.25–0.36).

Table cells are pooled StQ2 deltas in cycles, then favourable launches out of 31:

| NTRU+768 | normal | reversed |
|---|---:|---:|
| tobytes Official (absolute) | 428.3 | 426.4 |
| freeze2op − Official | −17.7 (31) | −14.0 (31) |
| **pack − freeze2op** | **−22.8 (31)** | **−16.2 (31)** |
| madd − freeze2op | +7.5 (0) | −2.8 (31) |
| pack − Official | −40.5 (31) | −30.2 (31) |
| frombytes Official (absolute) | 364.8 | 362.3 |
| **word route − Official** | **−14.5 (31)** | **−8.0 (31)** |

| NTRU+1152 | normal | reversed |
|---|---:|---:|
| tobytes Official (absolute) | 538.1 | 536.1 |
| freeze2op − Official | −25.6 (31) | −20.7 (31) |
| **pack − freeze2op** | **−42.0 (31)** | **−34.6 (31)** |
| madd − freeze2op | −1.7 (25) | −14.5 (31) |
| pack − Official | −67.6 (31) | −55.3 (31) |
| frombytes Official (absolute) | 437.3 | 434.6 |
| **word route − Official** | **−21.9 (31)** | **−14.4 (31)** |

Linked instruction counts per call (`make codec8-scratch-count`, `results/codec8-scratch-instructions-20260923.json`; each count includes about 7 (tobytes) or 10 (frombytes) instructions of dispatch):

| | Official | freeze2op | pack | madd | frombytes Official | word route |
|---|---:|---:|---:|---:|---:|---:|
| NTRU+768 | 719 | 671 | 654 | 690 | 533 | 482 |
| NTRU+1152 | 1073 | 1001 | 972 | 1023 | 791 | 713 |

### Reading

- **The measurements come in at 60–80 % of the uop model.** Pack gives −19.5 (768) and −38.3 (1152) per tobytes, and the word route gives −11.3 and −18.2 per frombytes (means of the two link orders). Both link orders agree in sign, 31/31.
- **exp002 transcribed literally does not help here.** madd is +7.5 to −14.5 against freeze2op. It swaps p01 shifts for 32 shuffle uops per iteration, and Official's layout-specific shift pack is already cheaper than `vpmaddwd` + `vpshufb`.
- **The frombytes gain is small** because the word route needs 32 in-lane shuffles per iteration, against Official's 12 plus 6 permutes. It removes only 11 vector uops per iteration.
- **Per coefficient, the pack variant only reaches parity with NTRU+864 exp002.** That is 104 instructions per 128 coefficients, or 78 per 96, against exp002's 78.6 per 96. Official 768/1152 was already at 83 per 96 with freeze2op.

### Projected KEM effect (not measured)

The projection uses the mean component deltas, stacked on the lazy+freeze2op candidate:

| cycles (share of the lazy+freeze2op op) | keypair (3 tobytes) | encap (2 + 1 frombytes) | decap (2 + 3) |
|---|---:|---:|---:|
| NTRU+768 | −59 (0.09 %) | −50 (0.18 %) | −73 (0.38 %) |
| NTRU+1152 | −115 (0.12 %) | −95 (0.22 %) | −131 (0.44 %) |

For comparison, NTRU+864 exp002 − lazy was −835 (encap) and −1380 (decap), 2.5–5.8 %.
These projected deltas are the same size as the freeze2op increment. In the same ELF, link placement alone moved that increment by up to 245 cycles: 1152 encap was +52 in normal order and −193 in reversed.
Only an extended Native campaign could resolve an effect this small.

## 5. Decision

The gate fails for both functions of both parameters: every measured saving per call is below 50, and the largest is 1152 tobytes at −42 (normal).
**Stopped for NTRU+768 and NTRU+1152.**

The upside was small because Official 768/1152 `pack.s` already is a single-pass direct codec from the 8-way layout.
exp002 won on NTRU+864 by removing a natural-order transpose and a stack round trip, and neither exists here.

What remains is a 20–40-cycle tobytes and a 10–20-cycle frombytes micro-win. Turning it into a candidate would need:
- a hash-pinned generator;
- the guard, mutation, KEM and audit gates;
- Native evidence for a ≤ 0.45 % effect.

Reopen only if one of these holds:
1. A candidate is being qualified anyway, and this is folded in as one more pinned kernel.
2. Hand scheduling shows the tobytes pack variant at about 50 or more per call on 1152, against the ~48 port-model ceiling.
3. A frombytes design needs clearly fewer than about 50 vector uops per iteration.

## Reproduce

```sh
A=ntruplus-ntt-Optimized/Additional_Implementation/avx2
T=../../../common/official_opt_lazy/tools
# E = $A/NTRU+768/experiments/avx2_official_opt_freeze_001 (p=768) or $A/NTRU+1152/experiments/avx2_official_opt_001 (p=1152)
cd $E
make codec8-scratch-check          # differential sweep, release + ASan/UBSan/LSan
make codec8-scratch-count          # dynamic instructions per call (perf stat instructions:u, CPU 1)
make codec8-scratch-bench          # build/bench_codec8_scratch{,_swapped}
python3 $T/phase_b_batch.py --result-dir results/codec8-scratch-normal-TAG --metadata metadata.json -- \
  python3 $T/run_codec8_scratch.py --param $p --experiment . --launches 31 --result-dir {RESULT}
python3 $T/phase_b_batch.py --result-dir results/codec8-scratch-reversed-TAG --metadata metadata.json -- \
  python3 $T/run_codec8_scratch.py --param $p --experiment . --launches 31 \
  --binary build/bench_codec8_scratch_swapped --result-dir {RESULT}
```

Evidence (per experiment): `results/codec8-scratch-{normal,reversed}-20260923/{summary,metadata}.json`, which record the source hashes, `elf_text_sha256`, the cpucycles identity and the host-hygiene record; `results/codec8-scratch-check-20260923.json`; and `results/codec8-scratch-instructions-20260923.json`.
