# BaseInv 與 ToBytes 下一個 gate：2026-09-10

狀態：`candidate`。沒有修改 production；已完成 Mac physical differential、
Pi 5 KAT／rejection／PMU 與完整 KEM benchmark。
Official 僅指已取回的 SUPERCOP 20260831 `ntruplus864/aarch64`；尚未核對 upstream 最新版。

## 1. BaseInv no-centering：consumer range gate 通過

範圍：q=3457，FR0 的各 cubic leaf `Fq[Y]/(Y^3-z)`，R=65536。
輸入／輸出為 signed-int16 R0；wide accumulator 為 signed-int32。
秘密值不改變控制流或位址。這次只改模型中的 finish，不修改 public wrapper。

精確 active caller 路徑由 `Makefile`、`kem.c`、`gt864_poly_api.c` 核對：

```text
BaseInv(f) → finv ── g × finv → D1 → h    → small ToBytes → pk
BaseInv(g) → ginv ── f × ginv → D1 → hinv → small ToBytes → sk
```

finv／ginv 不會直接送入 ToBytes。f 本身的 full ToBytes 路徑沒有改動。

不依賴 Forward 的 sampled 最大值：直接允許另一個 operand 的完整
signed-int16 範圍 `[-32768,32767]`，BaseInv operand 使用 `[-1972,1972]`。
令 `P=32768×1972=64,618,496`，zetaR 的絕對值至多1728。

| D1 步驟 | 絕對值上界 |
|---|---:|
| early cross0 的兩個乘積和 | 129,236,992 |
| early cross1 的一個乘積 | 64,618,496 |
| cross0 REDC 後 | 3,700 |
| cross1 REDC 後 | 2,714 |
| final accumulator 0 | 71,012,096 |
| final accumulator 1 | 133,926,784 |
| final accumulator 2 | 193,855,488 |

REDC 使用 `t=signed16(x*(-12929))`、`(x+t*q)/65536`。
早期 accumulator 加上最壞 correction 也不超過 signed-int32。
兩個 early REDC 的 int16 narrowing 安全，三個 final sums 不溢位。

對整個 `[-193855488,193855488]` 區間做 exact SQRDMULH quotient-bucket
證明，共覆蓋 **387,710,977 個整數**：D1 最後 `SQRDMULH(621199)+MLS`
輸出落在 **[-1845,1845]**。因此仍嚴格位於 `(-q,q)`，small ToBytes
的 sign canonicalization 足夠；模 q 相同的值會輸出完全相同的 bytes。

finish 保留一次 inverse-denominator R1→R0 correction，也保留三次產品
REDC；只刪最後 centering。相對 fixed-scale baseline：

| 每個8-leaf tile | 原本 | 候選 |
|---|---:|---:|
| finish instructions，不含 RET | 57 | 37 |
| 其中 centering arithmetic | 18 | 0 |

整次 BaseInv 少648條 arithmetic，加上 halfq 常數建立省72條，共少720條
模型指令。這不是 cycle 估計。23組完整36-tile symbolic batch 通過，
並確認一組全零輸入在 batch failure check 被攔下。這不取代實體 KEM
KAT／failure／alias／cleanup 測試。

## 2. Fused-wide numerator：R1 contract 不變，七次 REDC

不照搬 Official 的 physical table ordering。使用 GT 現有 FR0 zetaR，
保留三個 input 的 R0→R1 conversion。以下 a,b,c 均已是 R1，zR=z×R：

```text
u  = REDC(b*c)
w  = REDC(c*c)
n2 = REDC(b*b - a*c)
n0 = REDC(a*a - u*zR)
n1 = REDC(w*zR - a*b)
h  = REDC(n2*b + n1*c)
d  = REDC(h*zR + n0*a)
```

每個加減都先在32-bit wide accumulator 完成，之後才 reduction。
所有七個結果皆為 R1；n0/n1/n2 是 adjugate，d 是 determinant。
所以既有 prefix、inverse、recover 的 scale ABI 不需更換。

已用模 q 多項式係數字典做 formal identity 比較（不是 random sampling），
另外測108,000組 root／邊界／隨機 leaf cases。range chain：

| 值 | 絕對值界 |
|---|---:|
| a,b,c | 3013 |
| u,w | 1867 |
| n2 | 2005 |
| n0,n1 | 1916 |
| h | 1908 |
| d | 1866 |

符合既有後段 `operand ≤4000` contract；d 甚至小於2000。
結合上述 no-centering finish，完整 symbolic batch 的 inverse identity 通過。

## 3. Kernel 組織：先共享常數，不預設需要巨大排程

| Numerator 模型 | Instructions，不含 RET |
|---|---:|
| fixed-scale baseline，一 tile | 114 |
| fused-wide，一 tile | 84 |
| fused-wide，兩 tile 依序處理、共享常數 | 160 |

兩 tile 的160不是 arithmetic 再減半：它只是兩次76條 tile work，
加一次8條 common-constant setup。q、qi、Rmod、Rhat 可以保留；
每個 tile 的 zeta 仍要載入，不能當成共同常數。

兩 tile 模型先採依序處理以控制 lifetime，並未建立 interleaved scheduling。
模型的 vector liveness peak 為一tile 11、兩tile 13；增加的兩個是跨tile
保留的 conversion constants。這是資料流分析，不是 numerator RA 證明。
與兩次獨立84條相比，再省8條setup。若 public wrapper 改為18次呼叫，
還能少18次 call／return 及部分 pointer setup，但這些尚未寫入實體 wrapper。
public d8–d15 保存本來就只有一次，不能重複列為收益。

37條 finish 與84條 numerator 已完成 physical assembly／differential，並已
接入隔離 package 做完整 BaseInv／Keygen；結果見第6節。雙 tile 仍是獨立後續
實驗，不是本輪候選的一部分。

## 4. ToBytes：共同 DAG、RA 與 Mac 實體 execution 通過

新 internal kernel 的輸入：第三 pair 的兩條 FR0 coefficient streams，
前兩個 pair 的216-byte scratch 各一份，routing／merge tables。
輸出：一個 top 的648 final bytes。這不是整個 public ToBytes wrapper。

完整767／805條區域 RA 於60秒 timeout，不能判為不可行。
改成 frontend＋九個 row regions，跨邊界 live registers 由前一區 Slothy
的 allocation 傳遞，不增加 copy、load、store：

- frontend 由 Slothy 在v0–v19中配置，留下連續12個 work registers。
- row regions 重新開放v0–v31；未參與本 row 的 live values 明確保留。
- 任意碎片化的 frontend allocation 曾讓 full row0 無解；保留連續 work bank
  後，small／full 各10個區域全部通過。
- 小／完整輸入版本的 vector liveness peak 分別29／30。
- 本地 TBL3 extension 明定三個 source registers 連續；沒有修改主 Slothy。
- TBL3 的 timing 是 functional-only placeholder，**禁止拿來報 A76 cycles**。

| 每 top（第三 pair＋九列 merge） | Small | Full |
|---|---:|---:|
| baseline pair + 9 merge calls 的 core instructions | 785 | 823 |
| 新共同 DAG，含明確地址計算 | 767 | 805 |
| TBL3 groups，逐組驗證連續 | 45 | 45 |
| spill accesses | 0 | 0 |
| Mac allocated assembly 實測 top calls | 272 | 274 |

所有測試 exact wire bytes、output canaries、輸入及常數／scratch不變通過。
RA 只改 register assignment，instruction order／immediates 維持。
generic static checker 缺 TBL-def、INS-read/write 分類，本地補上真實語義後
重跑通過；沒有假造 live-ins 繞過檢查。
通用 log parser 將 `Setting timeout` 設定訊息誤判成失敗，且將RA的零值當作
cycles；因此本輪不採用其performance欄位。測試腳本另外核對每份log的
10個真正solver終止狀態均為OPTIMAL，再檢查allocated assembly並執行實機。

前兩 pair 仍各自產生 scratch。整次 ToBytes 少18個 scratch ST3與36個
scratch loads，少432B寫入及432B讀取；但新增／保留的地址運算把 core
instruction 淨收益縮到 **36條／完整呼叫**。未含 wrapper call reduction
及較小scratch wipe，這兩者尚未整合。TBL／ORR 大部分仍在，不能減去380 cycles。

## 5. 入口與出口為何限制 ToBytes

### 入口一：FR0 physical layout

FR0 是為 GT transform 與 cubic leaf arithmetic 選擇的布局，不是 wire order。
每個 pair 讀兩條 stream，各讀九個16-byte vectors，stride=48bytes。
每 top 三個 pair 的 byte offsets 是 `(0,16)`、`(32,432)`、`(448,464)`。
入口若保持FR0、不多讀 coefficients，就必須保留 route9／transpose 的工作
或建立等價替代 DAG，不能以省掉函式名當成省掉 permutation。

### 入口二：integer representative range

full：Keygen f、Encaps r、Decaps r1，須保留寬範圍的 Barrett normalization。
small：Keygen h/hinv、Encaps c、Decaps r2，已有 `(-q,q)` producer contract，
只需 sign canonicalization。兩者的 routing／packing相同，但full多108組
Barrett操作，因此不可用small timing代表所有KEM入口。

### 出口：固定 wire order、canonical residue、12-bit packing

每兩個 canonical coefficients a,b 必須輸出三 bytes：

```text
a & 255, (a >> 8) | ((b & 15) << 4), b >> 4
```

這是在 transform-domain 對 coefficient 編碼，不是做 inverse NTT。
完整輸出1296bytes，必須與既有 public key／secret key／ciphertext／hash
input byte contract一致。不能因本地解碼器也配合改動，就當成相容。

每個 final row 的72bytes由三個 pair 交错貢獻：

```text
row[9*k+3*p+c] = pair[p][3*k+c]
```

因此單一pair只擁有八段各3bytes，不擁有連續24bytes。
若要 full-vector stores，每個output chunk需要多個pair的值。
本輪折衷是將前兩pair放scratch，第三pair在register裡直接消費；
不是把三個完整pair的54個data vectors同時放進32個registers。
本輪也沒有使用 lane ST3：第三pair以TBL3接final STR Q／STR D。

## 重跑與證據

```sh
python3 baseinv-proof.py
python3 bytes-build.py
PYTHONPATH=/Users/chenpinhao/slothy /Users/chenpinhao/slothy_and_ra/.venv/bin/python bytes-allocate.py --windows small full
python3 bytes-test.py --physical
```

BaseInv：`baseinv-results.json`、`fused-numerator-model.json`。
ToBytes：`bytes-small/`、`bytes-full/` 的 contract、symbolic、allocated、log、
allocation mapping，及 `bytes-physical-results.json`。
## 6. BaseInv 84＋37 實體驗證

Mac Apple arm64 直接執行 Slothy physical assembly：

- numerator 84條，100,096個 lane cases；exact integer output。
- finish 37條，300,288個 lane cases；exact integer output。
- input unchanged、output canary 全部通過，無 spill。

Pi 5 的 PMU instruction 差值與 DAG **逐條精確對上**：

| 路徑 | 靜態預期 | Pi 5 measured |
|---|---:|---:|
| failure：numerator `40×36` | -1440 | -1440 |
| success：numerator `1440` + finish `22×36` | -2232 | -2232 |
| Keygen：兩次 successful BaseInv | -4464 | -4464 |

這也確認目前 production baseline 實際是124條 numerator、59條 finish；本輪
不是拿114／57的中間模型冒充 active baseline。

Pi 5 paired PMU（median，ondemand governor，56°C）：

| Boundary | Baseline cycles | BaseInv candidate | Delta |
|---|---:|---:|---:|
| BaseInv success | 7798.062 | 5588.375 | -28.34% |
| BaseInv failure | 5171.141 | 3620.516 | -29.99% |
| Keygen | 51859.625 | 47471.375 | -8.46% |

Encaps／Decaps 沒有呼叫 BaseInv，變化分別+0.02%／-0.05%，視為噪音。

## 7. TBL3 實測、timing schedule 與 wrapper／cleanup

Pi 5隔離microbenchmark（扣除empty loop）：

| Primitive | Throughput cycles/instruction | Dependency cycles/instruction |
|---|---:|---:|
| TBL2 | 0.4376 | 1.9379 |
| TBL3 | 0.9808 | 3.9384 |

所以TBL3不能沿用TBL2 timing。實驗專用model使用兩條vector pipes、每次佔用
2 model cycles、dependency latency 4；沒有修改 `/Users/chenpinhao/slothy`
主target。排程固定既有physical registers、不允許renaming/spill，並以已通過
allocation的frontend＋九個row自然邊界處理。每個row得到OPTIMAL或timeout內
FEASIBLE解；Slothy selfcheck通過。model cycle只用於排序，不作Pi 5性能宣稱。

排程後再次通過Mac exact-wire differential、45組TBL3 consecutive-register
檢查／top、canary與input-unchanged。public wrapper現在只配置432-byte scratch，
前兩pair寫入；第三pair直接餵merge。回傳前以27次`STP XZR,XZR`清除全部
432 bytes。沒有lane ST3。

相對未排程候選，排程後 isolated ToBytes：full再少約19.8 cycles，small再少
約15.6 cycles。相對同輪active GT baseline：

| Boundary | Baseline cycles | Scheduled candidate | Delta | Instructions | Branches |
|---|---:|---:|---:|---:|---:|
| ToBytes full | 1794.637 | 1768.578 | -1.45% | -380 | -76 |
| ToBytes small | 1466.992 | 1372.758 | -6.42% | -380 | -76 |

full收益遠小於small，因為full仍有108組必要的wide-range normalization，且
90個TBL3／完整call比被替換的TBL2昂貴。刪除scratch traffic與call/loop雖省
380條動態instructions，並不等價於同量cycles。

## 8. 隔離整合與完整KEM benchmark

四個彼此獨立的package：baseline、BaseInv-only、ToBytes-only、combined。
全部通過：

- `test_kem`：64次round-trip與tampered ciphertext rejection。
- KAT完全相同：SHA-256 `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`。
- unified harness：24 valid、24 tampered、BaseInv mod-q/failure、ToBytes exact bytes。

combined相對同輪GT baseline：

| Operation | Baseline cycles | Combined cycles | Delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen | 51929.500 | 47203.375 | -9.10% | -5604 | -228 |
| Encaps | 46148.850 | 46014.875 | -0.29% | -760 | -152 |
| Decaps | 44337.125 | 44219.225 | -0.27% | -760 | -152 |

上表baseline是當前GT production package，用來隔離本輪改動的收益。

另以使用者指定的
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64` 原始碼未修改重建
Official shared object，和同一個combined binary做6-process、AB/BA交替、
42 samples/process的equal-policy paired PMU。100組exact KEM outputs與100組
tampered rejection逐process通過：

| Operation | SUPERCOP 20260831 Official | GT combined candidate | GT delta |
|---|---:|---:|---:|
| Keygen | 44303.375 | 47234.750 | +6.62% |
| Encaps | 46420.600 | 45999.150 | -0.91% |
| Decaps | 40756.425 | 44183.075 | +8.41% |

這是指定SUPERCOP source的standalone equal-policy GCC 14.2 build，不是整套
SUPERCOP compiler-selection sweep；該source也尚未獨立核對為upstream最新版。
結論是Encaps已領先，但Keygen即使本輪大幅改善仍落後，Decaps主要缺口也
沒有被這輪BaseInv改動觸及。

證據：`pi-results/unscheduled/`保存排程前結果；`pi-results/scheduled/`保存
排程後JSON、raw CSV、build/test/KAT logs與四個實測shared objects；
`official-comparison.json`與`official-results/`保存指定SUPERCOP source、hash、
paired CSV與兩個comparison binaries。

## 9. 決策

- BaseInv 84＋37：`candidate`，實體instruction accounting、correctness與完整
  Keygen speedup均通過；尚未寫回production。
- ToBytes共同DAG：`candidate`，small明顯收益、full小幅收益，排程後沒有回退；
  尚未寫回production。
- combined：`candidate`；已完成SUPERCOP 20260831一致邊界比較。下一個
  production promotion gate應是精確linked-object audit、production source整合，
  再重跑相同KAT/rejection/PMU，確保隔離package收益能完整穿透production。
