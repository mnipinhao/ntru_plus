# NTRU+768 GT Encap consumer edges：研究重啟

日期：2026-09-22。Branch：`avx2-gt-ntt`。

後續決策：依使用者要求，direct prefixed-buffer hash staging **只保留為
experiment，暫停 Native qualification 與整合**。下列既有量測不刪除，
但不納入新的 GT 設計。最新研究見
[GT vector mapping co-design](ntruplus768-gt-vector-mapping-codesign.md)。

本輪找到兩個不同尺度的新機制：

1. 保留 M layout，讓既有 serializer 直接寫入 `hash_g` 的帶 prefix buffer，
   刪除 1152-byte copy。C research caller 已通過 correctness、sanitizer 與
   9-process same-ELF confirmation；完整 deterministic Encap 約快 109 cycles。
2. 保留已驗證的 Wire AoS producer/codec，改寫 packet MulAdd 的 λ placement：
   先累加 wrapped products，再用一次 `(λ−1)` correction。可執行模型將
   384 chains 降至 288，峰值 9 YMM。尚未新增此算術的 ASM／cycle evidence。

兩者都沒有修改 clean production。第一項收益可移植到其他 decomposition，
不能歸功於 GT；第二項是重新檢驗 GT consumer ABI 的具體新機制。

## 1. 先修正研究座標

Control 是 `clean/avx2-gt32-clean`，Official 是 lock 中的 SUPERCOP
20260831。Frozen clean 全部檔案 hash、既有 W source 與 range artifact hash
記錄於本輪 JSON；hash C campaign 另保存 source／ELF／compiler provenance。

舊的 Encap `+238 cycles` 並不是可直接定位、刪除的固定 codec stage。
`ntruplus768-next-priorities-20260920.md` 已顯示 matched polynomial island
約贏 57–64 cycles，而完整 Encap 受 placement/ASLR 影響。此次目標是創造
更多可保留到完整 caller 的 headroom；不把所有 Native residual 歸因於 codec。

| 已做的方向 | 已有證據 | 本輪處理 |
|---|---|---|
| Current M→wire | arithmetic 快，codec 有實際 routing 工作 | 保留完整 control |
| decode 後另產 W 再轉 M | current Q24 已融合 unpack/mapping；拆開增加工作 | 不重做 |
| D01 h ingress + mixed consumer | consumer pair formation 補回 decoder saving；僅 static gate | 不稱為實測失敗，但沒有新機制不重開 |
| Decode2→B3 streaming | Decap 實驗刪 96 stores/reloads 卻慢約 65 cycles | 不能把它當成 Encap h-stream 的直接性能證據，也不重用同一展開策略 |
| 統一 centered/lazy serializer | code size 降，但 paired KEM 回退 | 不重做 |
| 已實作 W-Mont single packet | r state＋hash bytes −48.56，完整 island +345.67 | 保留為 arithmetic 對照；新方案必須改掉多付的 λ chains |
| 已實作 W-Mont double packet | 完整 island +433.10 | 不把 interleave 當成免費收益 |

W 的舊 timing 是三個 fresh processes 的診斷。其 harness 在 timed function
中仍有 region/variant dispatch，且 bank index 跟 slot 綁定。這不抹去已有
correctness 或強烈退步訊號，但下一個新 W 比較須先修正這兩項，不能用舊
數字減去新模型估計來預測 cycles。

## 2. 六條 edge：什麼必須存在，什麼可以改

```text
PK bytes → decode/validate → h state ─────────────────┐
r coeff → Forward → retained r state ────────────────┤
                       └→ serialize → hash_g → SOTP │
                                             ↓      │
                                         m coeff    │
                                             ↓      │
                                         Forward    │
                                             ↓      │
                                           m state ─┤
                                                    ↓
                                               h×r + m
                                                    ↓
                                               c → bytes
```

- `r` arithmetic state 必須跨 hash_g、SOTP、m Forward 存活，serializer 不可
  修改它。這不是適合把整個 hash serializer 塞進 D1 live registers 的邊界。
- PK validation 在 sampling／secret arithmetic 前完成，invalid PK 仍提前
  return 並清除 ct/ss。新 W 仍沿用已驗證的 early materialized h。
- r hash input 的 1152 wire bytes 是必要的**語義序列**；不必先存成一份
  ct，再複製成另一份同樣的 hash input。這正是第一個實驗。
- ciphertext 的 1152 bytes 是外部輸出，packing 不能消失；可消除的是為了
  迎合 packer 而重複做的 ownership conversion。
- 現有 M 是每 vector 同 degree、16 leaves；W 是每 vector 四個完整 quartics。
  W 的 16 lanes 都做有用輸出工作，四 leaves 本身不代表只有 25% SIMD 利用率。

## 3. 已實測的小改動：直接 hash staging

Current：

```text
pack_M(ct, r)
hash_g(ct, ct):
    data[0] = 0x01
    memcpy(data + 1, ct, 1152)
    shake256(ct, 192, data, 1153)
    secure_clear(data, 1153)
```

Research helper：

```text
data[0] = 0x01
pack_M(data + 1, r)
shake256(ct, 192, data, 1153)
secure_clear(data, 1153)
```

同一個 M pack、同一個 SHAKE、同一個 domain prefix、同一個 secure_clear。
每次 Encap 刪除 1152-byte memcpy 的讀＋寫：2304 logical bytes。沒有宣稱
刪除完整 serializer、Keccak permutation 或 r arithmetic materialization。
輸出 192 bytes 仍直接供 SOTP 使用，最終 ct 仍由原 ciphertext packer 產生。

Linked helper 確認：原 `hash_g` 有 `memcpy@plt`，新 helper 無此 call；
兩者 stack adjustment 同為 1176 B，皆保留 `shake256` 和 explicit clear，
新 helper 沒有 `vzeroupper`。預先分配的 polynomial scratch 沒有改變。
此 helper 保留 noinline，避免將 hash staging buffer 無條件延長到整個 caller。

Correctness：

- 10,391 組 stage tests，含 100 組實際 ternary-input Forward、邊界、
  32 個 output alignment offsets；wire/hash byte-exact、r immutable。
- guard page 檢查最後一個 packet 的寫入；canaries 與 staging wipe 通過。
- 完整 caller：16 組實際 keys 上的 100 組 deterministic coins，ct/ss exact；
  valid Decap、100 組 tampered CT、48 個 invalid-PK packet 位置皆通過。
- C harness ASan/UBSan 通過。Assembly extent 由 guard page/canary 另驗，
  不把 sanitizer 當作手寫 ASM 的記憶體證明。這不是官方 KAT 檔案全套比較。

### 測量

CPU 1、performance、turbo disabled、SMT sibling 1–2（沒有 offline 或干擾追蹤）；
normal placement、ASLR on；共同 O3GC recipe、pinned SUPERCOP cpucycles。
Official/GT 的 clean code 不重建為新的 performance baseline；比較是 current
GT 與只替換 hash staging 的 research caller。

模式與 function pointer 在 timer 外選定；兩邊共用相同 input banks、輸出
地址、bank traversal 與 warmup。所有 setup、validation、IO 均在計時外。
每 process／region／variant 有 512 observations；8 blocks 使用 ABBA/BAAB。

| Region，candidate−current GT | 3-process short | 獨立 9-process confirmation | 9-process 方向 |
|---|---:|---:|---|
| retained M r → hash output | −53.55 cycles | **−65.16 cycles** | 9/9 |
| 完整 deterministic Encap | −115.20 cycles | **−108.74 cycles** | 9/9 |

Confirmation StQ1/2/3：

| Region | Current | Candidate |
|---|---|---|
| r→hash | 12358.26 / 12410.78 / 12467.53 | 12297.81 / 12345.62 / 12401.99 |
| Encap | 28192.44 / 28290.15 / 28378.32 | 28086.48 / 28181.41 / 28281.00 |

這是 **SUPERCOP-derived caller evidence**，不是 Native。兩個 campaign 都
保留 ELF hash；不能把 full-caller 比 stage 多出的 credit 精確歸因為 copy
本身。完整 image／call geometry 尚需 placement controls。

歷史判斷：曾列為可進 disposable Native qualification；目前依使用者要求暫停。
尚未安裝 Native candidate、
未宣稱能勝 Official-opt，也沒有直接改 clean。

## 4. 較大的新機制：W 的 λ correction 聚合

舊 W-Mont 把每個 product 中需要 wrap 的 lanes 乘 λ，其他 lanes 乘 identity；
每 packet 有三次 λ-or-identity Montgomery。這是該 arithmetic realization
的選擇，不是 wire AoS 的數學下界。

對一個 quartic `h*r mod (x^4−λ)`，degree `j` 定義：

```text
T_i[j] = Mont(h_i, r_((j-i) mod 4))         // e = −1
S_j    = T_0[j] + T_1[j] + T_2[j] + T_3[j]
U_j    = sum(T_i[j] where i > j)
```

則只需要：

```text
Cminus1_j = S_j + Mont(U_j, (λ−1)R)
C0_j     = Mont(Cminus1_j, R²)
c_j      = C0_j + m_j
```

這是 `direct + λ·wrapped = cyclic_sum + (λ−1)·wrapped`。
常數必須為 `centered(lambda_mont − R)`；不能對 Montgomery table 直接減 1。
不改 λ identity、wire ownership、output e=0，也不把不同 scale 的 m 提早相加。

### 實際 packet 和 register schedule

```text
YMM = [L0.c0 c1 c2 c3 | L1.c0 c1 c2 c3 || L2.c0 c1 c2 c3 | L3.c0 c1 c2 c3]
       low 128-bit half                   high 128-bit half
```

每個 lane 計算自己的 output coefficient，不形成 M degree planes。

| Stage | Register state / instruction | 數學與下一個 consumer |
|---|---|---|
| Load | ymm0=h(W), ymm1=r(W), ymm15=q, ymm14=0 | h canonical，r lazy，均 e=0 |
| Product 3 | half-local h broadcast/r rotation；5-op runtime Mont → ymm4 | T3，e=−1 |
| Wrapped 3 | blend imm 0x77 → ymm5 | 保留 degree 0/1/2 的 T3，degree3 為零 |
| Product 2 | 新 product 加入 ymm4；blend 0x33 更新 ymm5 | sum23；degree0/1 wrap 更新 |
| Product 1 | 新 product 加入 ymm4；blend 0x11 更新 ymm5 | sum123；degree0 wrap 更新 |
| Correction | Mont(ymm5,(λ−1)R) → ymm11 | wrapped correction，仍 e=−1 |
| Product 0 | 產生 T0，加到 sum123，再加 correction | 完整 quartic product，e=−1 |
| Finalizer | 原型的 R² Mont；memory-form add-m；W store | e=0，直接交给同一 W packer |

已完成逐 instruction、具體 YMM 編號的 def/use 和 word emulator。
Backward liveness 包含下一 loop iteration 仍需存活的 q／zero，peak **9 YMM**；
模型不需 stack spill、額外 scratch 或跨 half routing。這不等於 linked audit。
新的 suffix-sum dependency 可能影響 latency，只有真實 ASM pricing 才能回答。

### Range / oracle

Input：`h∈[0,3456]`、`r,m∈[−15592,15592]`，來源是已精化的 Encap contract。
每個 packet 使用自己的真實 λ/companion，逐 lane replay 每個 operation：

| State | Conservative max abs |
|---|---:|
| runtime product | 2551 |
| wrapped accumulator U | 7653 |
| cyclic sum S | 10204 |
| λ−1 correction | 1930 |
| corrected e=−1 output | 12134 |
| R² finalizer e=0 | 1889 |
| 加 m 後 | 17481 |

`vpmullw` 的 low-word wrap 明確建模；每個 `vpaddw/vpsubw` 在截斷前檢查
signed-i16 安全。無新 reduction。Canonical pack 可接受其 range。

獨立普通整數 schoolbook oracle 驗證 13,171 packets／52,684 quartics，
包含全部 192 leaves、正負 basis、uniform/mixed boundary 與 10,003 random
packets。Residue 與 wire bytes 一致；對舊 W 有 792 個 raw-different cells，
這是 normalization placement 改變的結果，不要求 raw exact。

### 全 caller 靜態帳

| Per-EnCap MulAdd | Current M | 舊 W-Mont | 新 W 模型 |
|---|---:|---:|---:|
| runtime product chains | 192 | 192 | 192 |
| λ／correction chains | 36 | 144 | 48 |
| R² chains | 48 | 48 | 48 |
| 總 chains | 276 | 384 | **288** |

新 W 相對舊 W：packet body 58→47 instructions，整個 MulAdd **−528**；
constant-memory operands 每 packet 20→16，合計 **−192**；data loads/stores
不變。λ/companion table 仍為 3072 B，沒有新增 normalization table。
這些是現有 emitted source 與新 executable model 的帳，不是新 linked 數字。

W Forward／decode／pack 原樣沿用已通過 machine correctness 的版本，
因此相對 M 的 caller-weighted layout 帳仍為：

- 兩個 Forward terminal：routing 淨零；不是免費 producer。
- 一次 PK ingress：−96 routes。
- 兩次 packing：−384 routes。
- MulAdd：新模型只比 M 多 12 vector chains，另有不同 routing/dependency。
- add-m fusion：48 c reload＋48 c store 是獨立收益，M fused-add control
  同樣可取得，不能算成 W 的 layout 優勢。

新 W correction vector 的 degree3 lanes 為零，所以其 correction 每 vector
有 12/16 有用 lanes；這解釋了它為何仍比 M 多 12 chains。Runtime product
則四個 degree 全部使用，沒有整體 lane 利用率只有 1/4 的問題。

## 5. 下一個可判斷的 gate

第一條已具有完整 caller signal：把 direct hash stage 做成 disposable
GT candidate，跑 Native Encap 與 Keygen/Decap regression；有 Native 收益
再跑四象限 fixed-ELF。這項技巧也應獨立測 Official-opt，避免把可移植的
memory credit 誤認為 GT 專屬優勢。

第二條建議只實作**單 packet 的 aggregated-λ W-Mont**，使用已驗證的 W
Forward/decode/pack，不同時更改 hash staging、不先追加雙 packet版本。
比 current M、M fused-add、舊 W、new W 的完整 polynomial island；先修正
timed dispatch 與 bank matching。通過新的 ASM differential、range 對應、
linked def/use／spill／ABI 後才短測。沒有完整 island 收益就停止該 realization。

這次 research 並未證明 W 能追回舊版約 346 cycles；它證明舊 W 的大部分
額外 chain count 有一個具體且 range-safe 的消除方法，足以構成新實驗。

## 6. 重跑與 artifacts

以下路徑相對於 `NTRU+768/experiments/avx2_gt32_tile4_official_001/`：

```sh
python3 tools/research_encap_consumer_edges.py
python3 tools/check_encap_hash_direct_stage.py
python3 tools/run_encap_hash_stage_short.py \
  --supercop-root /path/to/pinned-supercop --cpu 1 --launches 9 --tag <new-tag>
```

- `generated/tile4_encap_consumer_edges_research.json`：所有 packet 常數、
  instruction operands、range、liveness、ledger、source hashes。
- `generated/tile4_encap_hash_direct_stage_check.json`：stage correctness、
  sanitizer、compiler、ELF hashes。
- `results/encap-consumer-hash-stage-short-20260922-a1/`：首次三-process timing。
- `results/encap-consumer-hash-stage-confirm-20260922/`：九-process confirmation，
  raw observations、source overlay、metadata、symbols、linked helper audit。

本輪沒有新的 W ASM、Native 結果、clean promotion 或對 Official-opt 的
performance claim。Clean、pristine SUPERCOP、frozen package 保持原樣。
