# NTRU+ 768 / 864 / 1152 AVX2 統整與 Benchmark（SUPERCOP 20260831）

產生時間：2026-09-20T05:15:35.287726+00:00。正式 Native headline 使用 pinned SUPERCOP 的未修改 `crypto_kem/measure.c`；component 數字均標為 **supercop-derived-component**。

## 結論

- **768 GT32**：Native keygen、decap 勝出；encap pooled StQ2 小幅退步，且 fixed-ELF 在 ASLR/placement 間方向不一致，因此不是完整 production winner。
- **864**：只報 Official Native。D3/MR32 是 component research，重新量測仍比 baseline 慢，不能冒充 KEM candidate。
- **1152 exp017**：已整合 Serializer V2 direct `hash_g` stage，但 Native encap 仍穩定慢約 0.9k cycles；不 promotion。Forward 已在同一 harness 接近 Official，主要剩餘 debt 位於 fanout/tail/caller integration。

## Provenance 與方法

- SUPERCOP `20260831`；archive SHA-256 `9a258febbfbbf6de0c09cee73f343d4014597c259415e78a598b7af4b1787208`。
- Official tree hashes：768 `8db00172e705b67e231b63708295781d65681fef2c7422d717fe91ab48d576e7`；864 `13e0d983221e430a3cc5097042aa04dd1197981fb39761b02fbc845253107006`；1152 `78daf6b9a6350c02d61cbd9f4dd1e717503b91183fe399005e1369eb5c365010`。
- 768 candidate：`avx2-gt32-clean`；1152 candidate：`avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831`。
- Host：Intel Core Ultra 7 155H，Linux 7.0.0-31-generic；CPU 1；performance governor；Intel turbo disabled；SMT siblings `1-2`。
- Native compiler policy：SUPERCOP native selection。Fixed/component policy：`gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections -gdwarf-4 -Wall`。
- Native：9 fresh processes、864 observations/operation、StQ2 headline。
- Fixed common compiler：O3GC；16 blocks、64 launches/setting；normal/reversed × ASLR on/off。
- PMU：4096 operations/process、3 fresh processes、empty-harness subtraction；只作診斷。

## Native SUPERCOP headline

| n | operation | Official StQ2 | Candidate StQ2 | delta cycles | delta % | candidate faster launches |
|---:|---|---:|---:|---:|---:|---:|
| 768 | keypair | 21585.12 | 21259.69 | -325.43 | -1.51% | 9/9 |
| 768 | enc | 28279.75 | 28309.01 | +29.26 | +0.10% | 3/9 |
| 768 | dec | 19451.19 | 19256.62 | -194.57 | -1.00% | 9/9 |
| 1152 | keypair | 34394.51 | 34702.51 | +308.00 | +0.90% | 2/9 |
| 1152 | enc | 43035.34 | 43919.88 | +884.53 | +2.06% | 0/9 |
| 1152 | dec | 30534.19 | 30564.10 | +29.92 | +0.10% | 2/9 |
| 864 | keypair | 23832.44 | N/A | N/A | N/A | N/A |
| 864 | enc | 32969.19 | N/A | N/A | N/A | N/A |
| 864 | dec | 23776.84 | N/A | N/A | N/A | N/A |

> 864 的 N/A 是刻意的：目前沒有完整、通過 caller/KAT 的 AVX2 KEM candidate。

## Fixed-ELF paired control（normal placement, ASLR off）

| n | operation | paired delta | bootstrap 95% CI | favorable blocks |
|---:|---|---:|---:|---:|
| 768 | keypair | -445.43 | [-457.13, -433.77] | 16/16 |
| 768 | enc | -53.11 | [-85.23, -19.98] | 13/16 |
| 768 | dec | -302.08 | [-329.43, -275.37] | 16/16 |
| 1152 | keypair | +101.34 | [-346.47, +599.80] | 7/16 |
| 1152 | enc | +886.68 | [+846.94, +926.69] | 0/16 |
| 1152 | dec | +35.18 | [+9.85, +58.72] | 4/16 |

完整四種設定見 [`paired.csv`](../results/ntruplus-avx2-768-864-1152-20260920/paired.csv)。768 encap 在 normal/ASLR-off 是負值，但 normal/ASLR-on 與 reversed/ASLR-on 反向；1152 encap 四種設定全部是大幅正值。

## Component profiler

### Official common primitives（StQ2 cycles）

| n | forward small | BaseMul | BaseMulScale | BaseInv | inverse | frombytes | tobytes | poly mul small |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 768 | 981.40 | 722.21 | 633.69 | 1245.00 | 993.23 | 350.50 | 423.23 | 2927.60 |
| 864 | 1125.69 | 656.93 | 564.16 | 1185.96 | 1183.73 | 642.51 | 694.70 | 3315.31 |
| 1152 | 1433.44 | 965.12 | 837.09 | 1590.12 | 1487.16 | 424.03 | 528.25 | 4509.69 |

### Official caller building blocks（StQ2 cycles）

| n | hash_f | hash_g | hash_h | SOTP encode | SOTP decode | add | sub | CBD1 | crepmod3 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 768 | 10896.33 | 12093.58 | 2655.15 | 315.71 | 352.47 | 241.00 | 236.30 | 317.62 | 431.69 |
| 864 | 12139.20 | 13354.26 | 3835.94 | 367.49 | 399.09 | 240.47 | 240.84 | 349.84 | 461.48 |
| 1152 | 15642.26 | 18057.62 | 4901.35 | 382.59 | 439.40 | 276.79 | 276.31 | 431.98 | 556.62 |

### 768 GT32 caller-private components

| component | StQ2 cycles |
|---|---:|
| forward_frontend | 455.42 |
| forward_m_full | 886.71 |
| forward_p_full | 902.35 |
| baseinv_j1 | 1200.66 |
| basemul_f0_j1 | 612.56 |
| basemul_general_m | 717.93 |
| basemul_scale_m | 632.47 |
| inverse_m_core | 613.73 |
| inverse_m_tail | 587.09 |
| inverse_m_full | 972.70 |
| q24_unpack_m | 396.78 |
| q24_pack_m_centered | 419.75 |
| q24_equal_m | 336.63 |

### 864 D3/MR32 research

- Packed-T3 baseline：`246.46` cycles。
- Direct `vpmaddwd`/MR32：`266.09` cycles，delta `+19.63`。
- 16-block paired：ASLR-off `+16.72` cycles；ASLR-on `+17.19` cycles，兩者皆 0/16 favorable blocks。
- 結論：MR32 此 realization 被拒絕；雖然 stores 較少，instruction/load pressure 更高。

### 1152 current cumulative components

- Official Forward：`1491.89`；GT full Forward：`1489.07`，同 harness delta `-2.82` cycles。
- Top split：`311.44` cycles。
- Serializer V2：`682.07` cycles。
- Serializer V2 + `hash_g`：`18444.91` cycles。
- Official tail：`1632.97`；H4 exact egress：`1986.75`，delta `+353.78` cycles。

> Component 數字是 isolated/caller-shaped diagnostics；不得直接相加預測 Native KEM。特別是 SHAKE 的 warm repeated PMU/cycle geometry和 fresh Native caller不同。

## Keygen / Encap / Decap caller stage map

[`caller-components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/caller-components.csv) 將三個 operation 的 source-resolved stage 對應到本輪實測 building block，並保留 Native total。每個 building block 都從獨立 reset/residency 開始；它們不是 cumulative cutpoints，因此報告刻意不把 isolated medians 相加成假 waterfall。完整 cumulative caller waterfall 尚未達到可發布證據標準；Native totals 才是 operation headline。

- Keygen anchors：CBD1、Forward、BaseInv、BaseMul、serialization、`hash_f`。
- Encap anchors：PK decode、prehash、CBD1、r/m Forward、r serialization + `hash_g`、SOTP、MulAdd、ciphertext egress。1152 另有 fused Serializer V2 + `hash_g` 與 H4 exact-tail cutpoint。
- Decap anchors：decode、BaseMulScale、inverse、crepmod3、message Forward、recovery BaseMul、recovered-r serialization + `hash_g`、SOTP decode + `hash_h`、reencryption。

## PMU 與 linked audit

- 864 D3 PMU：baseline `82.0` instructions、MR32 `125.0`；MR32 retired loads 也明顯增加。
- 1152 PMU：GT Forward約 `3069.0` instructions/op，Official約 `3421.0`；GT instructions較少，但 loads較多。
- 完整 cycles/instructions/loads/stores/IPC 見 [`pmu.csv`](../results/ntruplus-avx2-768-864-1152-20260920/pmu.csv)。

### Fixed Native ELF size（normal placement）

| ELF | .text bytes | .rodata bytes | SHA-256 |
|---|---:|---:|---|
| 768-official-normal | 42007 | 5384 | `edcd87e8e2552e1fd9e0cd118a8048a9369ade3ad25989458a2efdd6107b159f` |
| 768-candidate-normal | 64407 | 56808 | `5657dbb8983c9fcf421b4487ca48f0f54b2c1493403ccbc16af5fb03635cb470` |
| 1152-official-normal | 44951 | 7080 | `2749ae2681bf8d3e5cda0840a9e0a65069451ca69078d7a3b1bd0a1aca14fdcd` |
| 1152-candidate-normal | 96791 | 22952 | `cf2e4c8cc3a2cdfb9260c658ac3f6eaffa2a4f251040ad0c03afb22fa2fc52e3` |

### Hot-symbol audit

- 768 GT32 linked component ELF：`.text=51479`、`.rodata=56992` bytes；除 `baseinv_j1` 為16-byte offset外，其餘列入 audit 的 hot entries為32-byte aligned；leaf functions仍含既有 `vzeroupper`。
- 864 D3 research ELF：`.text=14295`、`.rodata=2848` bytes；baseline/MR32 entries均為32-byte aligned。
- 1152 exp017 component ELF：`.text=78807`、`.rodata=20256` bytes；Forward與H4 entries為32-byte aligned，Serializer V2 `hash_g` C bridge為16-byte aligned。
- 完整 symbol instruction/routing/stack/branch audit 位於 `results/.../audit/`。

## Correctness 與安全 gates

- 768 clean：100-vector frozen KAT byte-exact；ASan/UBSan KAT通過；32 valid/tampered API trials、invalid-PK zeroization、immutability與canary通過。
- 1152 exp017：100-vector frozen KAT byte-exact；ASan/UBSan KAT通過；相同 API/invalid/canary gates通過。
- 1152 Serializer V2：1,000-case exact wire-byte differential、retained scale-1 `r` immutability與direct `hash_g` byte-exact gates通過；H4 C11 exact egress的semantic/canonical/machine-wire、overlap、decoder與linked structural gates通過。
- Public KEM API沒有宣告 overlapping-buffer contract，因此本輪不宣稱 public API alias support；內部 primitive alias gates仍沿用各 clean/experiment 的既有 differential evidence。
- 864 D3/MR32：10,003 tile differential cases、canonical equality、immutability、alignment與canary通過；但 performance rejection維持。
- SUPERCOP Native try/compile/measure均完成，沒有 `tryfails`/`measurefails`。

## 優化盤點

### 已整合

- 768：GT32/TILE4、P/J1 keygen、persistent-M encap/decap、Q24 native codecs、batch BaseInv。
- 1152：persistent-AoS、Natural-Q、T0-beta、scale-1 lazy Forward、MA2、H3 ingress、H4 C11 egress、pair-unpack、Serializer V2 direct `hash_g`。

### 保留研究但未進 production

- 864 D3/MR32：correct但較慢，未接 KEM。
- 1152 W1/multi-row wavefront與其他尚未 caller-complete的 Forward experiments。

### 已拒絕

- 1152 D1 pair-resident fusion：caller-shaped timing regression。
- 864 plane-major relocation與D3 MR32 current realization：無 structural/cycle win。

## Promotion 判定

- **768：不 promotion 為全操作 winner。** Keygen/decap有可靠 win，但 encap方向受 ASLR/placement影響且 Native pooled略退步。
- **864：N/A。** 沒有完整 Native candidate。
- **1152：不 promotion。** Fixed paired encap四種設定全部顯著退步；tail仍是主要可攻 debt之一。

Machine-readable evidence：[`summary.json`](../results/ntruplus-avx2-768-864-1152-20260920/summary.json)、[`native.csv`](../results/ntruplus-avx2-768-864-1152-20260920/native.csv)、[`components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/components.csv)、[`caller-components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/caller-components.csv)、[`paired.csv`](../results/ntruplus-avx2-768-864-1152-20260920/paired.csv)、[`pmu.csv`](../results/ntruplus-avx2-768-864-1152-20260920/pmu.csv)。
