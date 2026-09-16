# P3B39 — M5C bound revisit

Scope explore / mode review. NTRU+864, q=3457, existing FR0/R0 cubic leaves,
signed int16 Forward and signed int32 D1 accumulators. Baseline is the P3B37
arithmetic mask (P3B35 passing twist0 mask); P3B37 scheduling does not change
that mathematical DAG. No assembly, production, Slothy or benchmark changes.

## 結論

**值得重新看 M5C，但目前通用 2F multiplication contract 下，三個剩餘
identity reductions 仍不能直接刪。**

這輪不是沿用 P3B35 的 interval failure：重新用目前包含 twist0 bypass 的
mask 計算 exact sparse NTT16 marginals，回溯成具體 864-coefficient inputs，
再以純 scalar arithmetic 重播 target column 的 NTT16 與完整 oriented NTT9。
這是 model witness，不是實機 assembly overflow test。

## 同時包含目前全部 bypass 的結果

每個 natural coefficient 可獨立取 [-3,4]。對兩個 operands 使用同一多項式，
三個 component 由不重疊 input indices 供應，因此可同時取到同一極值。

| 額外刪除 | witness leaf 三個 components | exact accum2 | 第一個 target-path blocker |
|---|---|---:|---|
| main.stage1.node0 | (-27766,-27766,-27766) | 2312852268 | M5C int32 |
| main.stage2.node0 | (-31332,-31332,-31332) | 2945082672 | M5C int32 |
| main.stage3.node0 | (-38979,-38979,-38979) | 不作合法 M5C input 解讀 | Forward int16 |

前兩個 witness 的 target NTT9 intermediate checks 通過；第三個在
Forward 即已違約，不能再拿未截斷的數字宣稱實機 BaseMul 結果。
Signed int32 upper limit 是 2147483647。

目前未額外刪除的 row-zero accumulator exact upper magnitude 是
2143639083；本輪 row-zero audit 不取代既有其他 NTT9 rows/M5E closure。

M5C 實際第三個 accumulator 是：

    a2*b0 + a1*b1 + a0*b2

它沒有 zeta，也沒有中間 Montgomery reduction。每個 component 的來源
可獨立選，因此這裡不能靠不同 components 之間的 correlation 排除反例。
前兩個例子 wrap 後與 exact sum 的 mod-3457 差值都是 2590，不是 0。
最後的 D1 Barrett reduction 只能保留收到的 wrapped int32 residue，
不會自動補回遺失的 2^32。

## 新機會：M5C 應依實際 operand pairing 分開證明

目前通用 proof 允許兩個 operands 都是很大的 Forward outputs。
但 KEM 並不是每一個 BaseMul call 都這樣配對。

重新 machine-check 的條件定理：

    a ∈ [-32768,32767]
    b ∈ [0,4095]
    zeta_R1 ∈ [-1728,1728]
    BaseMulAdd addend ∈ [-32768,32767]

| 中間結果 | 已證明 enclosure |
|---|---|
| single product | [-134184960,134180865] |
| two-product cross | [-268369920,268361730] |
| Montgomery 內部 addition，最大 enclosure | [-381648896,381637249] |
| accum0 | [-144248832,144244737] |
| accum1 | [-274894848,274886658] |
| accum2 | [-402554880,402542595] |
| BaseMulAdd，三 outputs 聯集 | [-402587648,402575362] |

因此這個配對即使 Forward 使用完整 signed-int16 範圍，M5C 也不會接近
int32 overflow。D1 可銜接既有 full-int32 residual <=3023 theorem。
這裡尚未重新做所有 KEM consumers 的 M5E closure，不能宣稱完成 KEM gate。

這不是把「兩邊都很大」的數學界硬改小，而是提出不同、可驗證的 operand
契約。沒有因此新增一個 runtime reduction。

## KEM call-site audit

來源是 frozen P3B37 build/sync/raw/kem_stock.c 與實際 wrapper。

| Caller | 配對 | 目前判断 |
|---|---|---|
| Keygen h | Forward(g) × BaseInv(f) | 必須先核對 BaseInv output range |
| Keygen hinv | Forward(f) × BaseInv(g) | 同上 |
| Encaps c | FromBytes(h) × Forward(r) + Forward(m) | 符合上述條件的有希望路線；仍需完整 Forward/caller closure |
| Decaps m1 | FromBytes(c) × FromBytes(f) | 兩邊都是 decoded operands |
| Decaps r2 | (FromBytes(c) − Forward(m2)) × FromBytes(hinv) | 必須先證明 subtraction 不溢位 |

input_once_frombytes.c 的 unpack8 最後 mask 4095，所以不把 hostile bytes
錯當成 canonical [0,3456]。BaseInv wrapper 只在輸入側 centered-normalize，
不能依此推論其輸出 bound。

另一個重要限制：f 是 3*CBD1 再只對 coefficient 0 加一；g 是 3*CBD1，
r 是 CBD1。這些 producer 的可達集合比獨立 [-3,4] 小，但本轮沒有默默
用較窄集合替換 generic API contract，也沒有聲稱 witness 是可由 KEM
SHAKE seed 生成的樣本。

## 下一個合理 gate

先做 **caller-specific producer → Forward → BaseMul/BaseMulAdd closure**：

1. 精確定義 f、g、r、SOTP(m)、crepmod3(m1) 的輸入集合。
2. 核對 BaseInv output bound；納入 malformed-byte FromBytes 的 [0,4095]。
3. 對剩餘 stage1/stage2 bypass 候選重跑全部 NTT9 rows/int16 intermediate。
4. 另外 closure Decap subtraction，不讓問題從 M5C 移到 poly_sub。
5. 對每個 call-site 套用正確 asymmetric M5C theorem，再接 D1/M5E。

若只有 KEM-specific path 通過，保留 generic 2F polynomial multiplication
使用原本 Forward；需明確區分 API/benchmark contract，不能把通用 gate
刪掉後宣稱同一個候選通過。到這一步才有資格提出 assembly deletion。

## 檔案與重現

- audit.py：exact sets、backtracking witness、scalar target replay。
- asymmetric.py：conditional M5C/BaseMulAdd interval theorem，包含 early
  Montgomery internal add。
- build/audit.json：目前 mask、各 deletion 的全部 row-zero violations、source hashes。
- build/witness-main.stage1.node0.json、witness-main.stage2.node0.json：
  兩組完整 input arrays、目標 components、int32 wrap/residue 差。
- build/witness-main.stage3.node0.json：Forward int16 blocker。
- build/asymmetric.json：conditional theorem 的所有 intermediate bounds。

    python3 audit.py
    python3 asymmetric.py

Generated evidence 在 gitignored build/。未執行 Pi、未測 cycles、
未改 production，也沒有宣稱新 reduction deletion 已通過。
