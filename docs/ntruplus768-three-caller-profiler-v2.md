# NTRU+768：同版本、同 counter、同 residency 的三個 caller profiler

## 結論與證據邊界

2026-09-22，branch `avx2-gt-ntt`。本輪只新增診斷工具，不修改 clean、
Official、Mask-store、API 或任何優化 ASM；未重跑 Native，也沒有 promotion。

- **Keygen**：首次用目前 clean 的 P Forward／J1 BaseInv／F0×J1 完成
  matched cumulative 分帳。Forward、BaseInv 和 product 都有收益，不是單靠
  「有 batch inversion」：兩邊原本都有 batch inversion。
- **Encap**：Current 的 Forward 優勢確實被部分 decode、packing 和 MulAdd
  成本抵銷。Mask-store 保留了一部分 serializer credit，但本輪完整 caller
  差值仍不確定，不能拿局部勝出改寫之前 qualification 未通過的結論。
- **Decap**：decode→inverse 有約 +103 cycles 的前半段成本；後半 recovered
  message Forward 與避免第二次 serialization 的 M equality 有明確收益。
- **重要限制**：長 hash prefix 的 cumulative 差分不足以解析所有小步驟。
  原始負增量保留並標記 invalid-as-physical-cost，不截零、不硬湊 Native。
  因此另以 caller 內的短 cumulative windows 定位較小的差值。

下列差值一律 candidate − control；負值較快。未特別註明者，數字為 pooled
StQ2。它們是 `supercop-derived-poly` caller diagnostics，**不是 Native KEM**。

## 固定來源、counter 與測量方法

Official：pinned SUPERCOP **20260831**，根目錄名稱仍是
`/home/nuc/supercop-20260627`。768 AVX2 tree SHA-256：
`8db00172e705b67e231b63708295781d65681fef2c7422d717fe91ab48d576e7`。
完整 version／URL／archive hashes 存在 campaign 的 `metadata.json`。

Current／Mask-store 使用上一輪 Native qualification 的實際 installed sources：

```text
/home/nuc/src/supercop-maskstore-qualification-20260922/crypto_kem/ntruplus768/
    avx2-gt32-clean
    avx2-gt32-maskstore-exp-sc20260831
```

Current 與 clean 逐檔核對；唯一容許的 flatten 差異是 inverse constants include
路徑，include 內容另驗 hash。Mask-store 的改動只在 Encap lazy/highrange pack。
Keygen P codec、Decap centered codec 不變，本輪不替兩者假造 Mask-store 原型。

- CPU 1、performance、turbo disabled、normal placement／ASLR on，預先固定。
- SMT sibling `1-2` 保留，未離線、未修改 sysfs；不是完全隔離的主機。
- 共用 O3GC recipe，GCC 15.2.0，所有命令與 headers／sources／ELF hashes 已保存。
- 直接使用 pinned `libcpucycles.a`；每個 process 回報
  **`default-perfevent`、1400000000**。不是 RDPMC、不是 repository RDTSCP。
- 9 fresh processes，每 cutpoint／variant 96 observations，共 864。
- StQ1/2/3 使用 pinned `stq.h` 定義，240 組資料與 C estimator exact 相同。
- 8 個 deterministic input banks；所有 variants 輪流使用**同一個實體 mutable
  bank**。reset、完整 warmup、驗證與輸出都在 timing 外。Caller 自己需要的
  stack／scratch 保留，不幫 Official in-place NTT 加 copy。
- 兩方 AB/BA、三方六種 balanced order；block 交錯正／反 cutpoint traversal。
- 不扣 empty-harness cycles；每個 region 的 absolute 數字包含 counter boundary
  與實際進入成本。不同 region 起點的 absolute 數字不能當成同一成本相加。

### Cumulative 實作：完整執行，不提早 return

Generator 以 exact source anchors 插入 compile-time-selected endpoint。
每個測項仍**從完整 caller 的相同初始狀態重新執行**，只在選定終點讀 counter；
suffix 繼續執行但不計時，最後核對完整 output。沒有 runtime operation dispatch
在 timed region 內，也沒有以前一個 cutpoint 留下的 warm intermediate 當起點。

另外量未插 counter 的 `external_total`。這可顯示插入 counter、compiler/code
geometry 與 estimator 造成的 residual，而不是把 residual 當成遺漏算術。

### 為什麼增加 caller-local windows

第一批九-process campaign 使用三份獨立 hash image；之後改用共用 helper 與
相鄰 cutpoint 交錯。兩批都發現 Encap 在長 hash 前綴之後的 SOTP 等小差分
不能可信解析。它們保留為測量方法修正紀錄，不拿最漂亮的一批當 headline。

最終 campaign 共用相同 hash／SHAKE／Keccak machine body；C source byte exact，
Keccak source 僅 trailing whitespace 差異。Mask-store 除 pack 外共用 Current
primitives。**這是歸因映像，不代表三個 Native ELF 的 placement。**

新增 windows 在原 caller 內先正常執行 prefix（untimed），到真實起點讀一次
counter，再於指定終點讀一次。不是免費準備 synthetic intermediate：

```text
Encap dual: prehash/CBD 完成 → r Forward → pack → hash_g
Encap m:    SOTP 完成        → m Forward → MulAdd → CT pack
Encap tail: m Forward 完成   → MulAdd → CT pack
Decap recovery: crepmod3 完成 → message Forward → recovery product → pack
Decap late: hash_h 完成       → CBD/Forward → equality → clear
```

123 個 linked diagnostic entries 已驗 counter calls：一般 prefix 1 次、window
2 次、external-total 0 次 internal counter；所有 diagnostic entry 32-byte aligned。
完整 reachable functions 與反組譯存於 `linked-counter-audit.json`。

## Correctness 與 retry

100 組 deterministic keys；每個 cutpoint 都執行到底，Official／Current／Mask
完整 PK、SK、CT、shared secret exact。Invalid PK、noncanonical CT、canonical
tampered CT 的 return／zero shared secret 一致；coins、輸入與邊界 canary 檢查通過。
最終 window harness 另經 ASan／UBSan；LSan 因執行環境關閉，不能聲稱做過 leak audit。

Keygen 保留原本兩個 retry loops。`randombytes` 改用共同、預先生成的 64×32-byte
coin stream，timing 包含 memcpy 取 coins、sampling、Forward、inversion 與重試
控制流；**不包含系統 entropy acquisition**。Official／GT 使用相同 coins。

本輪 **100/100 keys 的 f、g 都一次成功，觀察到的失敗 retry = 0**。
`preflight.out` 保留每個 vector 的 f/g attempts。程式沒有將 retry loop 移除，
但不能宣稱已量到實際失敗重試的額外成本。成功 attempt 分帳使用各 trace 中最後
成功的 f/g coin，與含 retry 的完整 Keygen 分帳分開，不相加假造重試成本。

## Keygen：真正 P/J1 的分帳

完整 caller cumulative StQ2：

| 終點 | Official | Current GT | GT−Official |
|---|---:|---:|---:|
| f retry loop 完成 | 4609.94 | 4511.28 | −98.66 |
| g retry loop 亦完成 | 8968.44 | 8776.10 | −192.34 |
| 第一個 product | 9511.66 | 9199.64 | −312.02 |
| PK packing | 9742.50 | 9445.37 | −297.13 |
| 第二個 product＋f packing | 10474.66 | 10096.10 | −378.56 |
| hinv packing | 10701.66 | 10328.13 | −373.53 |
| hash_f | 21371.31 | 21030.87 | −340.44 |
| 清除完成（internal endpoint） | 21540.59 | 21275.02 | −265.56 |
| 未插 counter 的完整 caller | 21615.50 | 21250.31 | **−365.19** |

兩邊第二個 product 和 f packing 的原生順序不同，因此保留為同一 cumulative
region，不改 caller 順序來湊單項表。

成功 attempt 的相鄰 cumulative StQ2 差分：

| Stage | Official f | GT f | 差值 | Official g | GT g | 差值 |
|---|---:|---:|---:|---:|---:|---:|
| SHAKE/CBD/triple/adjust（含 entry） | 2809.03 | 2819.06 | +10.03 | 2816.72 | 2819.99 | +3.26 |
| Forward（GT 是 P） | 764.62 | 707.91 | **−56.71** | 755.73 | 706.07 | **−49.66** |
| BaseInv（GT 是 J1） | 1030.94 | 978.00 | **−52.94** | 1030.11 | 973.94 | **−56.18** |

此外第一個 product 的 prefix increment 是 543.22→423.54，約 −119.68；
第二 product＋f pack 為 732.17→650.73，約 −81.44。這是實際
`ntruplus768_basemul_f0_j1_avx2`，不是 M Basemul 或歷史未整合的 BaseInv。

完整 Keygen launch-mean delta −363.77，bootstrap CI95 [−387.32,−339.01]，9/9。
CI 是本診斷映像的 process variation，不包含任意 placement 的不確定性。

## Encap：Official／Current／Mask-store

### 起點 decode

原 caller entry→PK decode/validate：389.05／425.42／423.89。
Current 多 **36.38**，Mask 多 **34.85** cycles。這包含 caller entry／scratch
setup，不能全數歸給 permutation。Mask 沒有改 decoder。

### r 的雙 consumer（短 window）

| Region | Official | Current | Mask-store | Current−Official | Mask−Current |
|---|---:|---:|---:|---:|---:|
| r Forward | 961.10 | 883.75 | 886.14 | **−77.36** | +2.39 |
| r Forward＋exact hash-input bytes | 1168.44 | 1130.13 | 1109.26 | **−38.31** | **−20.87** |
| 再包含 hash_g | 13046.65 | 12999.92 | 12978.69 | −46.73 | −21.23 |

因此 Current 的新增 packing increment 是 246.38，Official 為 207.33：
**packing 約吃掉 39.05 cycles 的 Forward credit**。
Mask 的 increment 223.12，相對 Current 少 23.26，但相對 Official 仍多 15.79。
不要把差分稱為獨立 serializer latency；這是同一 window family 的邊際成本。

Current 與 Mask 的 Forward 完全相同，表中 +2.39 是 caller/code geometry 的
control 差異，不能稱為 Mask 改了 Forward。Hash staging 沿用原版；沒有 prefixed
buffer 整合。

### m 與 arithmetic／ciphertext packing

| Window | Official | Current | Mask-store |
|---|---:|---:|---:|
| m Forward | 956.49 | 883.06 | 882.43 |
| m Forward＋MulAdd | 1509.49 | 1476.32 | 1477.68 |
| m Forward＋MulAdd＋CT pack | 1745.93 | 1731.18 | 1720.54 |
| 另外從 m Forward 後開始：MulAdd | 779.64 | 801.25 | 804.17 |
| 同一起點：MulAdd＋CT pack | 1011.42 | 1050.48 | 1042.32 |

從 tail window 看，Current 的 MulAdd 約多 21.60，連 CT pack 約多 **39.06**；
Mask 將 tail 差距縮為 **30.91**。Mask 與 Current arithmetic 一樣，表中的
約 +2.93 也不是算術改動收益／成本。

從較長 m window 看，Current 的 m Forward 優勢 −73.43，至 MulAdd＋packing
只剩 −14.75；Mask 留下 −25.38。不同起點的 window 不混相減。

### 完整 Encap：仍然不能宣告勝負

| 完整 deterministic caller | Official | Current | Mask |
|---|---:|---:|---:|
| StQ2 | 28107.14 | 28129.56 | 28122.36 |
| 相對 Official | — | +22.43 | +15.22 |

九次 launch 的 mean delta／CI95：

- Current−Official：+12.77，**[−25.52,+52.98]**，4/9 較快。
- Mask−Official：+6.61，**[−38.26,+49.55]**，4/9 較快。
- Mask−Current：−6.16，**[−22.15,+10.90]**，5/9 較快。

完整 caller 結論是 **inconclusive**。不能將 windows 的 credit 相加後取代這個結果。
Full-prefix SOTP 的 Official 增量 −56.07、Mask 清除增量 −145.12 是解析不足／
instrumentation geometry，不是負的物理成本；raw 保留，禁止拿來排序優化。

## Decap：前半 ingress 與後半 recovery/equality

前半 cumulative 與同 family 增量：

| 終點 | Official cumulative | GT cumulative | 差值 | GT 相對上一終點的額外成本 |
|---|---:|---:|---:|---:|
| decode/validate | 683.77 | 775.58 | **+91.81** | +91.81 |
| BaseMulScale | 1109.61 | 1217.41 | +107.80 | +16.00 |
| inverse（core＋tail） | 1881.79 | 1984.63 | **+102.84** | −4.96 |
| crepmod3 | 2067.12 | 2161.51 | +94.39 | −8.45 |

所以現在不應把 Decap 前半落後都歸因於 inverse：最大可定位區域是
**decode/validation＋caller ingress setup**。Inverse 的小 delta 不能外推成全平台勝負。

Recovery window（真實 crepmod3 後開始）：

| 累計工作 | Official | GT | GT−Official |
|---|---:|---:|---:|
| message Forward（Official 包含必要的 f=m copy） | 999.58 | 893.76 | −105.82 |
| 再加 subtraction＋recovery product | 1573.85 | 1498.43 | −75.42 |
| 再加 recovered-r packing | 1797.43 | 1693.43 | **−104.00** |

GT recovery product 的邊際成本較高約 30.40，但 centered packing 約少 28.58。
這裡使用獨立的 centered pack，**不是 Mask-store Encap serializer**。

Late window（hash_h 後開始）：

| 累計工作 | Official | GT | GT−Official |
|---|---:|---:|---:|
| CBD＋reencryption Forward | 1073.02 | 1007.59 | −65.43 |
| 再加 equality path | 1358.36 | 1112.07 | **−246.29** |
| 再加 shared-secret masking／clear | 1575.51 | 1331.30 | −244.21 |

Equality 的邊際成本為 **285.34→104.48，約 −180.86**。
Official：第二次 `poly_tobytes`＋byte verify；GT：retained recovered-r M state
對新 Forward M state 做 modulo equality。第一份 recovered-r hash bytes 仍存在。
因此這個收益來自 caller representation reuse，不是「NTT 本身省掉了 181 cycles」。

完整 uninstrumented diagnostic Decap：19514.30→19202.78，**−311.52**。
Launch-mean −312.31，CI95 [−320.18,−303.52]，9/9。

## Residual：不強迫 waterfall 等於 Native

同一 pooled estimator 的 cumulative increments 可代數加總回最後 internal cut，
但不能消除 instrumentation、code placement 或全 caller build 的差異。

| 比較（GT−Official） | 最後 internal cut | Diagnostic full | full−internal residual | 上輪 Native | Native−diagnostic |
|---|---:|---:|---:|---:|---:|
| Keygen Current | −265.56 | −365.19 | −99.63 | −292.13 | +73.06 |
| Encap Current | +55.17 | +22.43 | −32.75 | +127.58 | +105.16 |
| Encap Mask | +37.12 | +15.22 | −21.90 | +30.21 | +14.99 |
| Decap Current | −247.23 | −311.52 | −64.29 | −247.45 | +64.07 |

Native 是同 installed source／counter 的既有 GCC O2 qualification campaign；本輪
是共同 O3GC、shared helper、deterministic RNG／coins 的診斷映像。Residual 不是
新發現的某個函式成本，也不單獨證明 I-cache bottleneck。

## 判斷與下一步

1. **Keygen 的 P/J1 優勢有實際 caller 證據**。保留此路線；不能再使用舊的
   「GT 尚无 J1，Keygen attribution 只能 Official」報告。Retry 失敗成本仍未實測。
2. **Encap 沒有單一上百-cycle serializer 冗餘可直接由這輪斷言**。
   Current r packing 約消耗 39 cycles Forward credit，tail 約落後 39 cycles，
   decode/entry 約落後 36 cycles。Mask 改善局部 packing，但完整 caller 不確定。
   不以各項數字相加預測 Native，也不重啟已被拒絕的 fusion。
3. **Decap ingress 是最清楚的成本區域**：到 inverse 前後約 +103 cycles，
   decode/entry 佔其中約 +92；後半 M equality 則是值得保留的已實測優勢。
4. 本輪未新增优化、未改 clean，未推翻 Mask-store qualification failure。

## Artifacts 與重跑

Experiment 相對路徑：
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001`。

- 採用：`results/caller-profiler-v2-windowed-20260922/`。
- 最終 sanitizer：`results/caller-profiler-v2-window-sanitize-20260922/`。
- 方法修正紀錄：`caller-profiler-v2-serious-20260922`（獨立 helper images）、
  `caller-profiler-v2-matched2-20260922`（shared helpers、無 local windows）。
- `summary.json`：全部 StQ1/2/3 和逐 launch deltas。
- `waterfall.csv`：同 estimator cumulative 與 increments，未截零。
- `attribution-evidence.json`：九-process uncertainty、無法解析的負增量。
- `residual.json`：internal/full/既有 Native 差值，分開存。
- `launch-*.csv/.err`、`preflight.out/.err`：raw observations、backend、retry。
- `installed-sources/`、`harness-sources/`、`metadata.json`：凍結來源與命令。
- `linked-counter-audit.json`、`annotated-counter-disassembly.txt`、`symbols.txt`、
  `sections.txt`：linked counter、reachable call graph、alignment 與 placement。

在 experiment 目錄執行；使用新 tag，不覆寫已完成 campaign：

```sh
python3 tests/test_stq_pinned.py /home/nuc/supercop-20260627/include/stq.h
python3 tools/run_caller_profile_v2.py --tag caller-v2-new-sanitize --launches 0 --sanitize
python3 tools/run_caller_profile_v2.py --tag caller-v2-new --launches 9
python3 tools/close_caller_profile_v2.py results/caller-v2-new
```

CI 為九個 process 的 launch-mean bootstrap，不是 pooled StQ2 的 CI；兩種 estimator
的絕對數字不混寫。所有 win 都限於本診斷映像，未經本輪新的 placement／Native qualification。
