# Fastest clean GT32 composite versus Official Main (2026-08-14)

## Selected implementation

The independent SUPERcop implementation is
`crypto_kem/ntruplus768/avx2-gt-fastest-clean-native-rcheck`:

- Keypair: P-J1 BaseInv, F0xJ1 finalizer-free native BaseMul, SP1 Q24.
- Encap: qualified Q24/M/B3/H1 path.
- Decap: qualified Q24/M/global-inverse path with native-domain final
  verification.
- Unreachable experimental assembly emissions are pruned and the benchmark
  compiler uses function/data sections plus linker section GC.

Linked-symbol audit confirms:

- `gt32_p_j1_baseinv_direct_avx2`
- `gt_basemul_native_f0_j1_e0_asm_avx2`
- `gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm`
- `gt32_tile4_soa_equal_modq_12699_asm`
- `crypto_kem_dec_gt32_native_rcheck_candidate`

Canonical 100-vector KAT request and response files are byte-exact.  The
request SHA-256 is
`36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa`;
the response SHA-256 is
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Method

- Official Main and GT were freshly compiled once using the same forced
  SUPERcop O3/function-section/data-section/linker-GC flags.
- Fixed ELF SHA-256: Official
  `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217`;
  GT `471d94af9c18298042db857e01d3c210e7a983f9e565badebe9f34d73fe8fc66`.
- `.text` sizes: Official 42007 bytes, GT 66519 bytes.
- Cycle backend: SUPERcop `default-perfevent`,
  `PERF_COUNT_HW_CPU_CYCLES`.
- CPU 1 pinned; CPU 2 is its non-isolated SMT sibling.
- 16 balanced blocks, 64 fresh process launches.
- Odd blocks: Official--GT--GT--Official.  Even blocks reverse the order.
- Each launch supplies 96 native observations for each KEM operation.
- The analysis uses launch-level stabilized Q2, paired block deltas, and a
  deterministic 100,000-resample bootstrap interval for the block median.

## Results

Negative delta means GT is faster.

| Operation | Official Q2 | GT Q2 | GT - Official | Percent | GT wins | 95% bootstrap CI | ABBA / BAAB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keypair | 21500.56 | 21120.46 | **-388.24 cycles** | **-1.806%** | 16/16 | [-426.44, -358.06] | -382.68 / -393.79 |
| Encap | 28043.79 | 28114.38 | **+65.46 cycles** | **+0.233%** | 3/16 | [+17.04, +164.06] | +61.58 / +121.79 |
| Decap | 19350.09 | 19131.85 | **-222.78 cycles** | **-1.151%** | 16/16 | [-267.67, -191.54] | -249.10 / -195.97 |

Both ordering families agree in sign for all operations.  Keypair and Decap
win every paired block.  Encap remains slower and has larger block spread,
but its confidence interval still excludes zero in the losing direction.

## Decision

- This is the current fastest clean complete GT32 benchmark candidate.
- GT Keypair and GT Decap are formally faster than Official on this host.
- GT Encap is still slower by about 65 core cycles (0.23%).
- The complete GT implementation therefore wins two of the three operations,
  but is not a strict per-operation replacement for Official.
- The strongest selector is GT Keypair + Official Encap + GT Decap.  Keep
  Official Encap until its remaining caller/delivery debt is removed.

Artifacts:

- `results/tile4-supercop-fastest-clean-native-rcheck-vs-official-20260814.json`
- `results/tile4-supercop-fastest-clean-native-rcheck-vs-official-raw-20260814/`
- `results/kat-supercop-fastest-clean-native-rcheck-20260814/`
- `results/supercop-fastest-clean-native-rcheck-measure-20260814`
- `results/supercop-fastest-clean-native-rcheck-official-measure-20260814`
