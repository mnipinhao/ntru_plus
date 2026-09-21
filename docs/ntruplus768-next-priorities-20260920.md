# NTRU+768 AVX2：Encap residual、serializer co-design 與 Decap ingress

日期：2026-09-20  
Official baseline：SUPERCOP 20260831 `crypto_kem/ntruplus768/avx2`  
Current GT baseline：`crypto_kem/ntruplus768/avx2-gt32-clean`  
CPU：Intel Core Ultra 7 155H，CPU 1，`performance` governor，turbo disabled

本輪沒有修改 clean production。所有候選只安裝到 disposable SUPERCOP
campaign，並以新的 implementation name 執行。

## 結論

1. 先前約 `+238 cycles` 的 Encap 差值不是一個仍待尋找的固定 caller
   stage。current GT 的 polynomial island 已比 Official 快約 57--64 cycles，
   shared prework／middle／tail 也沒有穩定的局部差值；新的四象限 fixed-ELF
   結果顯示 Encap 主要受 ASLR 與整體 executable placement 影響。
2. 用一個 lazy M-to-wire serializer 同時服務 Encap ciphertext 與 Decap
   recovered-r，在語義上成立，也確實可刪除 3,840 bytes `.text`；但
   promotion-grade paired benchmark 四象限全部變慢，因此拒絕。
3. Decap `decode → BaseMulScale` ingress 已有的兩種 AVX2 fusion realization
   都被 machine evidence 否決。現階段保留 materialization boundary；沒有新
   mechanism 時不再重寫同一 DAG。

## Gate 1：重新定位 Encap residual

### 版本座標

目前統整 campaign 的 Native StQ2 並不是 `+238`：

| implementation | Keygen | Encap | Decap |
|---|---:|---:|---:|
| Official | 21,585.12 | 28,279.75 | 19,451.19 |
| current GT clean | 21,259.69 | 28,309.01 | 19,256.62 |
| GT − Official | −325.43 | **+29.26** | −194.57 |

因此 `+238` 應視為較早 Native campaign 的座標，而不是目前 frozen image 的
固定差值。Native SUPERCOP 的 compiler selection 仍是 production headline；
下面的 common-O3GC paired result 用於因果定位。

### Current GT 對 Official 的 fixed-ELF paired result

每種設定 16 paired blocks、ABBA／BAAB、64 fresh launches。數字是
`GT − Official` 的 paired mean；CI 是 block bootstrap 95% CI。

| setting | Keygen | Encap | Encap 95% CI | Decap |
|---|---:|---:|---:|---:|
| normal, ASLR off | −428.80 | **−2.80** | [−64.45, 52.05] | −258.14 |
| normal, ASLR on | −415.21 | **+18.34** | [−109.62, 120.86] | −341.85 |
| reversed, ASLR off | −400.29 | **−6.37** | [−43.41, 31.82] | −216.09 |
| reversed, ASLR on | −373.61 | **+74.51** | [17.58, 138.20] | −296.92 |

Keygen／Decap 在四象限皆穩定勝出。Encap 在 ASLR-off 兩個 placement 都接近
parity，ASLR-on 才向較慢方向移動，而且 normal／reversed 的幅度不同。

這與先前 matched attribution 一致：

- GT polynomial island 相對 Official：normal `−57.27`、reversed `−64.04`
  cycles；
- shared prework、middle glue、shared tail 是相同 physical code，沒有穩定的
  50--100 cycle 局部 GT penalty；
- dead-code pruning 曾把 `.text` 128,919 B 降到 64,407 B，並一次改善 Encap
  約 194 cycles；
- hot-function regrouping、padding removal、compact-loop serializer 都曾因
  code geometry 反而退步。

所以目前 Encap residual 的正確分類是：

> polynomial work 已經勝出；剩餘差值主要是 whole-image frontend delivery、
> ASLR 與相對 symbol placement 的交互作用，而不是一段可直接刪除的
> `+238-cycle` arithmetic work。

這不授權重新做無機制的 alignment／padding sweep。若再處理這一類問題，必須
有能保持 hot-symbol relative geometry 的 source-level replacement，而不是只
縮小總 `.text`。

## Gate 2：共同設計 M→wire recovered-r 與 ciphertext serializer

### 假說與 candidate

Current clean 使用兩個實體 body：

```text
Encap r / ciphertext:
    M lazy/high-range → ntruplus768_pack_m_lazy10788_avx2

Decap recovered-r:
    centered M        → ntruplus768_pack_m_centered_avx2
```

因為 centered range `[-1728,1728]` 是 lazy serializer 已驗證輸入範圍的
子集合，可以讓 recovered-r 也使用 lazy body，wire bytes 不變。候選：

```text
avx2-gt32-serializer-unify-exp003-sc20260831
```

只改兩件事：

1. `decap.c` 的 recovered-r call 改指向 lazy body；
2. 在 disposable candidate 的 `pack.s` 移除已無 caller 的 centered function
   emission。

exp002 曾只做第一項，但 Native compiler recipe 沒有保證 `--gc-sections`，
centered symbol 仍出現在 ELF。exp003 因此採用 source-resolved deletion；這是
本輪一個重要的 build-system lesson。

### Correctness 與 linked audit

- 100/100 deterministic KAT byte-exact；
- ASan／UBSan 通過；
- 32 組 valid／tampered／invalid-PK API semantics、zeroization、immutability、
  canary 通過；
- `.text`: 64,407 → 60,567 B，`−3,840 B`；
- centered serializer symbol：完全不存在；
- `.rodata`: +32 B（manifest／link layout effect，無新 arithmetic table）。

### Native directional result

exp003 的 Native StQ2 是：Keygen 21,207.57、Encap 28,179.89、Decap
19,200.21。這些數字單看很漂亮，但它與 Official/current clean 是不同時間的
campaign，不能作 promotion claim；必須以 paired fixed ELF 判斷 candidate
本身的影響。

### Exp003 相對 current clean 的 paired result

數字是 `exp003 − current clean`；正值代表退步。

| setting | Keygen | Encap | Decap |
|---|---:|---:|---:|
| normal, ASLR off | +48.35 | **+214.05** | +150.80 |
| normal, ASLR on | +23.05 | **+193.51** | +209.51 |
| reversed, ASLR off | +49.89 | **+216.98** | +233.73 |
| reversed, ASLR on | +5.01 | **+131.85** | +256.50 |

除了 ASLR-on 的 Keygen CI 含 0，其他主要結果都明確指向退步。原因有兩層：

- Decap 每次 recovered-r 改用較重的 lazy reduction／packing body；舊 component
  StQ2 為 centered 419.75、lazy 486.27 cycles；
- 刪除 centered body 將 lazy serializer 及所有後續 hot symbols 前移約 3.8 KiB，
  連 Keygen／Encap 這些不執行 centered serializer 的 operation 都改變。

因此「shared representation」在 semantic／static level 成立，但這個 physical
realization 不成立。exp003 拒絕，不修改 clean production。

## Gate 3：Decap decode→BaseMulScale→inverse ingress

### Current ingress

```text
Q24 ct / sk bytes
→ one Q24_DECODE_INIT
→ compact decoder body ×3: c, f, hinv
→ combined validation / early reject
→ materialized private-M c/f/hinv
→ BaseMulScale(c,f)
→ inverse
```

decoder attribution 的 D0 約 184.92 core cycles／609.5 instructions。其中
validation 與 return aggregation 約 18.43 core cycles／63 instructions，不能在
保持 invalid-input contract 時移除。current masks 已同時完成 unpack 與 GT
private-M placement。

### 已測的 streaming frontier

`GT32-Q24-DECODE2-B3-FRONTIER-001` 直接把 c/f decode 接入第一個
BaseMulScale B3 block：

- 刪除 96 vector stores + 96 vector reloads；
- 刪除 6,144 bytes materialization traffic；
- 淨少至少 160 memory operands；
- 靜態預測至少少 146 dynamic instructions；
- zero spill，peak 16 YMM，B3 arithmetic 不變。

但 machine result 是：

| placement | candidate − control | negative launch medians |
|---|---:|---:|
| normal | +65.81 cycles | 0/16 |
| reversed | +64.27 cycles | 0/16 |

原因不是 correctness 或 spill，而是把原本 compact、可獨立排程的 decoder/B3
loops 展成 13.7 KiB streaming straight-line body。materialization 在這裡提供了
OoO decoupling 與 hot-loop reuse；memory-op 數下降沒有轉成 cycle credit。

另一個 blocked-D01 `h × r → M` mixed-TMVP 提案，在完整 edge accounting 後
比 current decode route + B3 多 96 instructions，未進 ASM。

### 決策

Current materialized ingress 保留。下列新機制出現前不重跑同類 fusion：

- compact streaming form 能保留目前 decoder loop throughput；
- consumer 接受 D01／另一個 representation，從 contract 上消除 private-M
  transpose；
- ISA 提供跨完整 vector 的 byte permutation（不是 AVX2 lane-local
  `vpshufb`／`vpalignr`）。

延後 `hinv` decode 也未採用：current contract 在任何 secret arithmetic 前先
完成三份 decode/validation 並 early reject。單純把 hinv 移到 inverse 後方會
改變 invalid-key control/timing semantics；若另加 validation-only pass，則會
重複 decode work，沒有結構收益。

## 本輪 production 判斷

| item | decision |
|---|---|
| Current GT clean | 保持不變 |
| Encap `+238` local-debt hypothesis | 關閉；分類為 placement-sensitive residual |
| Serializer-unify exp002 | 結構 gate 失敗；dead body 未被 Native linker 移除 |
| Serializer-unify exp003 | correctness pass、performance reject |
| Decode2→B3 streaming ingress | performance reject |
| D01 mixed-TMVP ingress | static reject |

本輪沒有可 promotion 的 candidate。這不是沒有進展：三個優先項現在都有硬
邊界。下一個有效方向必須提供新的 code-delivery mechanism 或新的 consumer
contract，不能只刪 memory ops、縮 `.text`，或再次展開相同的 streaming DAG。

## Artifacts

- `results/ntruplus768-next-priorities-20260920/summary.json`
- `results/ntruplus768-next-priorities-20260920/paired-current/`
- `results/ntruplus768-next-priorities-20260920/serializer-unify-source-resolved/`
- `results/ntruplus768-next-priorities-20260920/paired-serializer-unify-vs-current/`
- installer: `scripts/install_supercop_768_serializer_unify.py`

