# GT768：同 M ABI 的 block-wide decoder schedule

2026-09-22，`avx2-gt-ntt`。本關承接 codec-boundary audit，只做研究模型與
physical-register allocation，沒有新增優化 ASM、benchmark、fusion 或修改
Forward／clean／wire API。上一關的 +32.13 Encap、+89.88 Decap ingress
是研究動機，不是本候選能追回的 cycle 預測。

## 結論

保留 **aligned-packet** 作為下一輪優先 ASM 對象：三個連續 YMM loads
覆蓋一個96-byte wire block，利用 VPERM2I128＋VPALIGNR 建立12-byte decode
視窗，再由 PSHUFB 同時完成 byte extraction 與既有 packet orientation。
後面的 shift/blend/AND、validation、M transpose及store ownership不變。

模型與allocation已通過，但尚無linked-binary／performance證據。
並未證明這是最便宜的decoder，也未全面否決direct-M或更大block方案。

## 為什麼用96 bytes，不先用128 coefficients？

目前一個M block包含16個quartic leaves、64 coefficients，正好佔96 wire
bytes。每 polynomial 12 blocks，三個unaligned32-byte loads即可完整覆蓋一個
block，不跨界、不重疊讀取。這是現有M ownership的自然邊界；不是宣稱
Official的128-coefficient geometry不值得研究。

本輪三個對照都從wire開始、直接store同一M：

1. **packet gather**：對每個packet合成兩份partial byte shuffle，再OR。
2. **aligned-packet**：用共同half內offset的aligned window，改為單次PSHUFB。
3. **direct-M gather**：直接聚合四個degree planes，不再有獨立transpose。

三者都保留獨立decoder函式及materialized h/c/f/hinv；沒有MA2 fusion，
沒有先建Official或M temporary再轉換，也沒有新增scratch array。

## 全 polynomial ledger

Current counts沿用source-bound codec audit；候選為executable instruction
model。**不是linked counts或cycles**。下表比較相同payload、validation終點。

| 類別 | Current | packet gather | aligned-packet | direct-M gather |
|---|---:|---:|---:|---:|
| data load instructions | 97 | 36 | **36** | 36 |
| load operand bytes（含重疊） | 1532 | 1152 | **1152** | 1152 |
| YMM stores | 48 | 48 | **48** | 48 |
| VINSERTI128 | 48 | 0 | 0 | 0 |
| VPERM2I128 | 0 | 48 | **61** | 131 |
| VPALIGNR | 0 | 0 | **48** | 0 |
| PSHUFB | 48 | 96 | **48** | 262 |
| OR merging | 0 | 48 | **0** | 214 |
| M transpose unpacks | 144 | 144 | **144** | 0 |
| VPSRLW | 48 | 48 | **48** | 24 |
| VPBLENDW | 48 | 48 | **48** | 0 |
| VPAND | 48 | 48 | **48** | 48 |
| validation VPMAXUW | 51 | 51 | **51** | 51 |
| decode shuffle table bytes | 128 | 768 | **128** | 3392 |
| model peak live YMM | 不重新估計 | 11 | **11** | 10 |

四條max accumulators、low12 constant、一次最終compare/movemask均計入。
mask以memory-form operand使用；不隱藏為免費常駐register。
對齊padding及最終text bytes須由ASM/linker實測，這裡不報虛構的機器碼大小。

aligned-packet正規化instruction delta：

```text
−61 data loads −48 inserts +61 half permutations +48 alignr = 0
```

也就是把load pressure換成routing/dependency，而不是把61條load直接當成
61-cycle credit。Shuffle-mask memory operands不變（48），table大小不變。
其是否能在AVX2上更快，必須靠相同counter/residency的machine benchmark。

direct-M的transpose雖然消失，但byte fragments變得零碎，額外PSHUFB/OR
非常多。這是此gather模板的成本，不是「direct-M已被benchmark否決」；
不以instruction數較多直接宣稱它一定慢。本輪優先aligned-packet是因為
其變動較小、table無新增debt、同時已形成完整可分配schedule。

## 第一個packet的 register-flow

三個load的byte ownership：

```text
A: [ wire  0..15 | 16..31 ]
B: [ wire 32..47 | 48..63 ]
C: [ wire 64..79 | 80..95 ]
```

目前第一個packet需要0..11與12..23兩個12-byte payload，並使用1032 mask。
aligned-packet的一個實現是：

```text
VPERM2I128(A,A,0x00) → L = [0..15 | 0..15]
VPALIGNR(low=L, high=A, shift=12)
    → [12..15,0..11 | 12..27]
PSHUFB(new mask)
    → 精確等於目前load/insert後PSHUFB的32-byte結果
VPSRLW 4 → VPBLENDW 0xaa → VPAND 0xfff
    → 相同16個12-bit decoded values
VPMAXUW → 同一validation stream
```

低half前四個bytes只是視窗中的不使用位置，被mask跳過；不是讀取負地址。
`VPALIGNR`模型的兩個sources明確命名low/high；未來AT&T lowering應為
`vpalignr $12, low, high, dst`，不可把source順序寫反。

四個packet完成後，用目前完全相同的12-unpack network形成M planes。
第一個degree-0 plane仍為：

```text
[40 56 24 4 44 60 28 0 | 36 52 20 12 32 48 16 8]
```

這些是wire coefficient identities。Degree1/2/3為各位置+1/+2/+3，
leaf、λ身份、degree、e=0均未改。

## Schedule搜尋與allocation的限制

- packet/direct-M gather只在選定的source-half partition模板中配對，尋找
  可直接重用原始YMM的排列；不宣稱全AVX2 permutation network最優。
- aligned-packet枚舉共同shift0..15，找覆蓋兩half payload的16-byte視窗。
  優先重用原始load／本block已形成的half pair；只有payload未使用的half
  才能任選現有合法half，沒有越界load或隱藏zero source。
- 保持目前block及packet traversal；沒有搜尋所有packet順序。
- SSA每一instruction都保存operands、immediate、mask、destination，另做
  last-use與實際YMM編號配置。死source可被VEX destination覆寫；所有live
  inputs、四個validation accumulators及q mask都計入，峰值11，無spill。
- 所有操作均為YMM；沒有XMM alias隱含存活。所有data loads/stores以unaligned
  契約處理，不從code alignment推導data alignment。
- 第一版完整12-block straight-line schedule，不新增per-vector dispatch、
  secret index或loop/address-table load；全部offset已明列。Ret/test/setne等
  scalar wrapper成本留在既有入口外殼，未聲稱省掉。未來ASM需重核三份decode
  的共享validation與early-return/zeroization語義。
- 模型假設實際caller的input/output分離；不擴張in-place/overlap支援。
- 未來code／constant table須`.p2align 5`。11-YMM模型不取代linked def/use、
  ABI、stack/alignment、guard-page、KAT或constant-time audit。

## Range與驗證

這裡是bit extraction，不是新的modular arithmetic：mask後每lane在0..4095；
validation接受0..3456，保持e=0。Shift前word可用完整unsigned16-bit範圍，
沒有有號加減overflow、Montgomery或額外reduction。

三個schedule各通過：

- 全部768個unique owners，與獨立scalar 12-bit decode及既有wire↔M map核對。
- 每個position測1、2048、q−1、q、4095，共3840cases。
- 64組random 12-bit payload（包含invalid input），驗完整raw decoded M與
  accept/reject；不只測已合法PK。
- 36個load範圍精確覆蓋0..1151，48個store各寫一次且覆蓋0..1535。
- Input immutability；full-polynomial final validation；physical-register
  def/use replay；不同PYTHONHASHSEED重跑artifact exact。

沒有新ASM，因此本輪沒有新的sanitizer／linked／KEM correctness聲明。

## Artifacts與下一關

Experiment：`NTRU+768/experiments/avx2_gt32_tile4_official_001`。

```sh
python3 tools/research_decode_wide.py
PYTHONHASHSEED=7919 python3 tools/research_decode_wide.py --check
```

`generated/decode_wide_schedule.json`保存三個完整instruction graphs、concrete
YMM allocation、masks、source hashes與test ledger。模型可重跑，不輸出ASM。

下一關只建議一個ASM：**aligned-packet decoder**。保持M、獨立函式、Forward
及原本validation/clear時序；先做primitive exact differential與完整caller
correctness，再量上一關同cutpoint的decode windows及完整Encap／Decap。
若load credit被shuffle/dependency抵銷，保留反例；不因此自動改ABI或改fusion。

## ASM／短測 closure：本 realization 停止，不進 serious

2026-09-22，後續使用者授權 ASM 與 decoder／完整 caller 短測後完成。
前面各節保留為事前模型證據；此節為實際 machine 結果。

### 實作與 model-to-machine 差異

`generated/decode_aligned.S` 提供三個 namespaced symbols：

```text
ntruplus768_exp_aligned_decode_body
ntruplus768_exp_aligned_decode
ntruplus768_exp_aligned_decode3
```

Body依frozen aligned-packet schedule與physical allocation逐條lower，包含
正確AT&T VPALIGNR source順序。Linked operands、immediates及每一個RIP
constant的32-byte內容均與模型核對，不只比opcode總數。

- Data loads 36、M stores48、VPERM2I128 61、VPALIGNR48、PSHUFB48、
  transpose144：全部對上。無新增reduction／scale／M conversion。
- Peak live YMM11；body無stack、call、vector spill或vzeroupper。
- Body `.text` 3470→3396 bytes，−74 B；兩個wrapper仍各為27／65 bytes。
  不包含函式間padding，因此不把−74 B當整個ELF footprint差值。
- 四個PSHUFB masks128 B，加low12／qm1各32 B，候選constant section192 B。
- 單份與三份wrapper保留一個outer `vzeroupper`；沒有新internal AVX cleanup。
- **明示ABI成本**：wrapper以`sub/add $8,%rsp`維持內部call的16-byte stack
  alignment，使用8 B frame而不是scratch／vector spill。
- **明示triple成本**：low12 constant由body初始化。三份decoder載入3次，
  control只在wrapper初始化1次，因此多2個constant operands。
  單份總constant operands仍為50；三份為150 vs control148。

因此事前「normalized payload instruction delta=0」仍成立，但完整entry
另付上述wrapper與triple初始化差異。不能把本輪當成只改load count的單因子實驗。

### Correctness 與安全邊界

- Primitive：3840逐位置cases、10003 random（交替valid／arbitrary12-bit），
  對Current raw byte-exact，另對scalar wire decode＋M map驗證。
- Triple decoder逐一覆蓋三份input的每個invalid coefficient位置，核對
  aggregate return、全部raw output與input immutability。
- Input各byte alignment、output各合法int16 alignment、canary、guard-page
  首尾邊界通過。没有擴張原本caller的in-place/overlapping-buffer合約。
- Normal及ASan/UBSan primitive harness通過。Assembly memory檢查另靠
  guard-page／canary，不把sanitizer當成ASM load/store proof。
- 完整caller100組deterministic vectors、全部instrumented cutpoints輸出、
  invalid PK／noncanonical CT／canonical tamper及ASan/UBSan通過。
- 無觀察到natural keygen retry；本輪不聲稱覆蓋failed-retry path。
- 147個linked diagnostic entries的counter呼叫數及32-byte alignment核對通過。
  Body地址為`0x2b680`，single `0x2c3e0`，triple `0x2c400`（本次ELF）。

### 三個 fresh-process 短測

Pinned SUPERCOP20260831 `cpucycles()`，實際backend `default-perfevent`、
1400000000；common O3GC、CPU1 performance/turbo disabled、normal/ASLR-on。
同一ELF、同physical input banks/reset/warmup、三方balanced ordering，
每launch每region/variant96obs，共288obs；StQ依pinned `stq.h`。
不是Native、不是perf score，也不是九-process serious campaign。

| 邊界，pooled StQ2 | Official | Current GT | Aligned | Aligned−Current |
|---|---:|---:|---:|---:|
| Encap decode/validate window | 354.82 | 388.35 | 402.29 | **+13.94** |
| Decap triple decode/validate window | 648.68 | 742.47 | 809.81 | **+67.33** |
| 完整 deterministic Encap | 28048.58 | 28033.54 | 28077.64 | **+44.10** |
| 完整 deterministic Decap | 19476.58 | 19238.36 | 19290.78 | **+52.42** |

四個邊界都是 **0/3 launches勝出**。逐launch candidate−Current：

```text
Encap ingress:  +13.375, +13.500, +14.708
Decap ingress:  +64.833, +66.208, +70.167
Encap total:    +42.833, +34.375, +56.042
Decap total:    +88.500, +20.042, +65.958
```

完整caller使用未插internal counter的entry；decoder windows是在實際caller
中從decoder呼叫前開始，保留全部suffix但不計suffix時間。
Candidate除了decode之外共用Current primitives，包括pack、Forward與hash。
Hash staging未改，不整合prefixed-buffer或Mask-store結果。
Keygen保留Official/Current診斷作input preparation；沒有獨立Aligned Keygen
變體，也不假造其Native regression測試。

### 如何解讀

**已證實**：loads減少、body稍小、語義與allocation成立，但此次cycle-counter
短測沒有收益。保持Current decoder，這個realization不進serious／Native。
Aligned Decap仍比Official快約186cycles，是它繼承的GT完整路徑優勢，不能
把它誤寫成這次decoder改動成功。

**機制假說**：新增half permutations及alignr使packet extraction依賴變長，
也可能增加shuffle執行資源競爭；wrapper與constant初始化、code placement
亦可能影響結果。沒有分離對照或PMU證據，不能精確說哪一項造成幾cycles。
尤其不能把+67.33直接推為3×single或全歸給兩次constant loads。

此結果只否決目前aligned-packet realization的進階qualification；不宣稱
寬load全無價值、M decode已到下限，或GT representation失敗。
本輪不追加peephole、重排mask、換ABI或fusion來追最好看的樣本。

### 可重跑命令與保存位置

從experiment目錄執行（tag必須未存在）：

```sh
python3 tools/generate_decode_aligned.py --check
python3 tools/check_decode_aligned.py --tag UNIQUE_VALIDATION
python3 tools/run_caller_profile_v2.py --tag UNIQUE_SANITIZE --launches 0 --sanitize --aligned-decoder
python3 tools/run_caller_profile_v2.py --tag UNIQUE_SHORT --launches 3 --aligned-decoder
python3 tools/close_decode_aligned_short.py results/UNIQUE_SHORT
```

- `results/decode-aligned-validation-20260922/`：primitive logs、commands、hashes、
  normal/sanitized linked audits。
- `results/decode-aligned-caller-sanitize-20260922/`：完整caller sanitizer closure。
- `results/decode-aligned-caller-short-20260922/`：raw observations、StQ1/2/3、
  source archives、counter/host/compiler metadata、ELF SHA、全部symbol addresses、
  linked operand audit及`aligned-short-summary.json`。

新runner以`--aligned-decoder`明確把variant `m`標為Aligned（不是Mask-store），
預設仍維持舊Mask-store模式。既有campaign archives未改。
