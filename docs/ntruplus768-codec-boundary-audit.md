# GT768 codec boundary audit

2026-09-22；`avx2-gt-ntt`。本關只新增可執行模型、caller counter windows
與診斷報告；沒有修改 clean、Official、ASM、ABI 或 hash staging。
沒有 Native 重測，也不改寫 Eager／Mask-store qualification 結論。

## 1. 結論：ingress 差值主要仍留在 decode region

以下是**本次同一 campaign**的 pooled StQ2，GT − Official；不是 Native。

| 測量邊界 | Official | Current GT | 差值 |
|---|---:|---:|---:|
| Encap entry → decode/validate 完成 | 391.02 | 427.53 | +36.50 |
| Encap decoder 呼叫前 → validate 完成 | 359.63 | 391.77 | **+32.13** |
| Decap entry → 三份 decode/validate 完成 | 681.57 | 774.26 | +92.69 |
| Decap decoder 呼叫前 → validate 完成 | 649.33 | 739.21 | **+89.88** |

內部 windows 的九個 fresh processes 全部 GT 較慢。逐 launch delta 的平均值及
bootstrap 95% CI：Encap +32.16 [31.53,32.83]，Decap +89.85 [88.52,91.19]。
這是此 diagnostic image 的證據，不是跨 placement 的 causal proof。

因此「先前差值主要是大 stack frame」不獲支持。但兩種 instrumented entry
有不同 counter 邊界／compiler geometry，+36.50−32.13 和 +92.69−89.88
**不能直接標成精確 prologue cycles**。內部窗口仍包括 argument preparation、
函式呼叫、驗證結果與分支，不是假裝純 ASM body。

Mask-store 與 Current 共用同一 decoder body，Encap ingress 卻為393.75 vs
391.77：這約2 cycles是 caller/code geometry 對照，不是 Mask 改了 decoder。

## 2. 必要解碼、validation、M formation 分開看

每 polynomial 768 coefficients，1152 wire bytes → 1536 lazy-state bytes。
有效 decoder output 是 [0,3456]、Montgomery exponent e=0。

| 動態 source ledger | Official | Current M |
|---|---:|---:|
| 輸入 data load 指令 | 36 × YMM | 95 × XMM + vmovq + vpinsrd = 97 |
| load operands 請求 bytes（含重疊） | 1152 | 1532 |
| 最終 YMM data stores | 48 | 48 |
| 公開迴圈 | 6 × 128 coefficients | 12 blocks 展開 |
| validation `vpmaxuw` | 42 | 51 |
| validation compare／movemask | 6／6 | 1／1 |

1532 不是 cache-line traffic 或 cache-miss 數；97 不是97 cycles，也不是已量測
load uops。GT讀取的**唯一**有效 wire bytes仍為1152，沒有越界讀取。
Decap GT共用 decoder body三次，shared mask初始化與最終boolean處理只做一次。
Official valid path呼叫三次；invalid path可能short-circuit。不能用valid timing
推論invalid path時間相同。

GT每16-coefficient packet實際做：

1. 兩個12-byte payload分別載入XMM；一般使用16-byte重疊load，末尾改8+4安全load。
2. `vinserti128` 組成YMM兩個128-bit halves。
3. `vpshufb`：同時展開12-bit pair的byte ownership及half內leaf順序。
4. `vpsrlw $4`、`vpblendw $0xaa`、`vpand 4095`：取出完整16個12-bit值。
5. `vpmaxuw` 累入四條validation streams之一。
6. 四個packet經12條`vpunpck{l,h}{wd,dq,qdq}`形成四個degree planes，直接store M。

完整polynomial有48 insert、48 PSHUFB、48 shift/blend/AND、144 transpose。
validation最後合併四個max streams，再對3456比較。比較前值在0..4095，
故這裡signed `vpcmpgtw`與所需canonicality判斷一致。

其中byte extraction與canonical validation是語義需求，實作方式仍可改善；
144 transpose服務**固定M ownership**，不是額外完整projection pass。
跨leaf順序已有部分由load地址、四種PSHUFB masks及store offsets吸收。
不能把全部routing列為冗餘，也尚未證明144是最低instruction bound。
Official同樣支付unpack、blend與cross-half routing，只是以128-coefficient
compact block處理，不能把Official那邊視為零排列。

## 3. 一個實際16-lane M例子

以下數字是wire coefficient index，不是原始多項式coefficient index。
第一個M block的degree-0 vector（word offset 0）為：

```text
low 128:  40 56 24  4 44 60 28  0
high128:  36 52 20 12 32 48 16  8
```

其餘degree1/2/3 vectors在word offset16/32/48，每個lane分別為上列+1/+2/+3。
因此同lane四個planes確實屬於同一quartic leaf，適合lane-wise BaseMul。
Wire卻要相鄰的degree0,1,2,3，且葉子順序不同。單一`vpshufb`不能從
四個不同register蒐集degree，更不能跨128-bit half；必須有跨register
ownership交換，除非改變輸入load geometry或上游輸出contract。

模型完整保存768個wire↔M owner及192個Official factor/root identities。
沒有將quartic leaf編號與Official pack內部transpose後word index混為一談。

## 4. r hash bytes與ciphertext packing

Current實際呼叫順序：

```text
CBD1 → forward_m(r) → pack_m(r) → hash_g
                     retained r ──────────→ h×r
SOTP → forward_m(m) → product+add → pack_m(c)
```

Official同樣先`poly_ntt(&r)`再`poly_tobytes(ct,&r)`。所以hash輸入是
**transformed r的外部wire序列化**，不是CBD1 coefficient bytes。
不能刪掉這個輸出需求；若想從原始r產生同一串bytes，仍須實現相同transform。
本關不整合prefixed-buffer experiment。

固定M的r/c pack需完成三類不同工作：

- M degree-plane → 連續wire quartic ownership。
- lazy signed-i16 → [0,q) canonicalization。
- 兩個12-bit coefficient → 三個byte，並安全寫出1152 bytes。

既有Mask-store模型／ASM已把qword orientation吸入PSHUFB mask與store-half
選擇，刪掉48個`vpermq`，但保留144 transpose；不可再提一次作為新候選。
其中14個原本為identity；不應把其餘34個的效果當成「數學上沒用」。
同M下更便宜的transpose network仍是未驗證問題，不是已證明沒有空間。
目前pack為48 data loads、97 store instructions；Official pack是48 YMM
loads、36 YMM stores。這同樣是packet/store geometry差异，非cycle預測。

## 5. 測試與可重跑證據

實驗根目錄：

```text
ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001
```

從該目錄執行：

```sh
python3 tools/audit_codec_boundary.py --check
python3 tools/run_caller_profile_v2.py --tag UNIQUE_TAG --launches 9
python3 tools/close_caller_profile_v2.py results/UNIQUE_TAG
```

- `generated/codec_boundary_audit.json`：來源SHA、selected-function動態opcode
  ledger、全owner/root mapping、實際load範圍、16-lane例子。
- 模型通過全部owners、每位置q−1/q/4095共2304cases、128個random decode→pack
  roundtrips（Current與Mask模型）、r immutability、65536 signed-i16 reducer域。
  重跑artifacts byte-exact；是source-bound model，不冒充新的linked memory proof。
- `results/codec-boundary-ingress-20260922/`：9process、每region/variant864obs，
  source/ELF hashes、counter、flags、raw observations、StQ1/2/3、linked disassembly。
- 同pinned SUPERCOP20260831、common O3GC、同實體input banks/reset/warmup、
  normal/ASLR-on、CPU1 performance/turbo disabled；沒有修改sysfs。
  counter為`default-perfevent`、1400000000，不寫成RDPMC。
- 128個diagnostic entries的counter呼叫數及32-byte alignment通過linked audit。
- 100 deterministic vectors全部cutpoints完整輸出exact，invalid PK/CT測試通過；
  沒觀察到自然retry，不宣稱覆蓋failed retries。
- `results/codec-boundary-ingress-sanitize-20260922/`：同新harness ASan/UBSan
  correctness-only通過。這不替代ASM guard-page證據。
- 本次一併保存舊windows重測值，但long-prefix SOTP/clear仍出現負增量，保留
  invalid-as-physical-cost標記，不拿來相加或改寫本關ingress結論。

## 6. 下一個可推翻的假說

優先：**同M ABI的block-wide decoder load／unpack co-design**。
研究能否從連續wire block的YMM loads開始，直接形成目前M planes，減少
重疊小load與packet組裝，同時保留validation與48個最終M stores。
它和舊fused decode→MA2不同：函式邊界、materialized h、M ABI完全保留；
唯一新機制是decoder本身的load geometry／transpose聯合lowering。

不得先decode成完整Official buffer再轉M。若wide-load方案補回更多routing、
reload或無法在16YMM分配，記錄實際trade-off；靜態instructions不能直接判輸。
先完成一個128-coefficient block的bit ownership／range／liveness，再決定ASM。
採同decoder window及完整Encap/Decap caller反證；不預設32/90cycles全可追回。

次要：同M下pack的block-wide store network。它必須指出相對既有Mask-store
的新機制，不能只重做identity刪除。暫不換ABI、不改Forward、不做fusion。
