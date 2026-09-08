# NTRU+768 branch 盤點與 Production／E20 比較

盤點日期：2026-09-08。只整理既有證據，未重跑 benchmark。
本次只新增此文件，不合併 implementation、不刪除 branch/worktree、不 push。
不能把不同年代、不同 cleanup／link／benchmark contract 的 cycles 混成排行榜。

## 1. aarch64-production 與 E20 到底差在哪裡？

核對基準：

- `aarch64-production`: `b2f9ee83350a3e11dc2eae802ae0e5d7651586d4`。
- `codex/gt768-pack-util-cleanup-20260908-e20`: 文件加入前 `64ae41c2`，
  implementation revision `561b6aa50dc0e237c3c884ec7174a208baf869e5`。

兩個 branches 由 G5 基準分開：正式版 promotion checked unpack；E20 則同時
有 checked unpack、support 語義修正與完整 cleanup。不是「正式版比 E20
多了新 NTT 優化」，也不是「E20 已完整合併到正式版」。

| 面向 | aarch64-production | E20 |
|---|---|---|
| G5 lazy Encap NTT／既有 D1 | 已有 | 已有 |
| pack／checked unpack | direct output mapping | **pack.S byte-identical** |
| active NTT／basemul | 保留現有 hot path，另有 legacy/dead symbols | 清除未使用內容；不是新排程候選 |
| subtraction | poly_sub_decap，decap_add.S | poly_sub，add.S；原有運算 contract 保留 |
| centered mod3 | support.S 直接 centered mod3 | crepmod3.S：先 q-center 再 centered mod3 |
| 清除 helper | secure_clear.h／gt_secure_clear | util.h／secure_clear；coverage 保留 |
| legacy verification | 仍在原 source closure | 移到 test/legacy，回歸／ABI 測試明確連結 |
| support regression | 既有 package checks | 另加入 exhaustive support-check |
| 正式狀態 | 正式 branch | 整理候選，尚非完整 cleanup promotion |

`ntt.S` diff 主要移除未呼叫的 reference forward 與其私有 constants；
`base.S` diff 主要將 legacy verification 移至 test/legacy，移除未使用的
basemul_scale／basemul_add／baseinv_1。不能把這些刪行數當成 hot-path
instruction savings。`Makefile` 明確更換 support/add source，移出
decap_verify.c 的 production closure，將 legacy sources 加到 test_abi。

### crepmod3 是實質語義差異，不只是檔名

q=3457，q mod3=1，因此 raw centered-mod3 與 q-centering 後 mod3 在
[-1728,1728] 外不保證相同。E20 對 [-3456,3456] 驗證修正後的 helper。
既有追蹤看到 malformed ciphertext 的中間值可觸及差異；測得的 valid
cases 沒有差異，但其 observed range 不是一般性的可達值證明。
這不能宣稱為已知有效 ciphertext 錯誤或漏洞，也不能省略 promotion review。

### 效能比較：沒有新的直接 paired 結果

E20 當時四輪原生 SUPERCOP 結果（round medians 的中位數）：

| 版本 | Keygen | Encap | Decap |
|---|---:|---:|---:|
| G5 baseline | 36352.5 | 37152 | 32501 |
| unpack-only | 36335.5 | 37140 | 32493.5 |
| E20 full cleanup | 36377.5 | 37128 | 32513.5 |

unpack-only 是最接近目前正式版 promotion 範圍的歷史 control；**不能把
它冒稱為本次對 b2f9ee83 重測**。E20 相對該 control 的表內差為
+42／−12／+20 cycles，差值小且未證明穩定全面勝出。
E20 更乾淨有實作證據；「目前最快」沒有充分完整 KEM 證據。
linked KAT text 的既有 -7832 bytes 是相對 G5 baseline，不是相對
已刪除 384 bytes unpack 指令的當前正式版，也不是熱 instruction-cache footprint。

E21–E23 的 baseline 都是 b2f9ee83，沒有測 E20 full cleanup。
其 P＋N 完整 Encap 較慢結果不改變此分別。詳見 POST-E20-CLOSEOUT.md。

## 2. 指定 branches 索引

以下以完整名稱與 HEAD 固定身分。「收尾建議」是文件分類，不代表本次
實際刪除、合併或套用任何 branch。所有舊結果只適用其記錄的基準。
每節所列 source record 都能用 `git show <HEAD>:<path>` 取回；標準前綴 D 為：

`ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/`

### 01 — codex/gt768-allkem-official-policy-supercop-20260907-e07

- HEAD `0a9acee86545b0103ee71aa8cb8cd1a29cbb0742`。
- 用途：三個 KEM operation 對齊 Official 清除政策與原生 SUPERCOP 比較。
- 當輪 matched-classification GT／Official：Keygen36372／38537，
  Encap37599／38577，Decap32751／33555；改善5.62%／2.54%／2.40%。
- 是 sequential full runs，不是62-sample paired protocol；不是當前 E20 排名。
- Official 是 Pi `/home/pi/supercop-20260627/crypto_kem/ntruplus768/aarch64`。
- 清除 coverage 的政策等價不等於呼叫次數／bytes 相同；GT 特有秘密物件仍清除。
- 收尾：保存政策／provenance 證據，不整支 merge。
- Source: D + `gt768-allkem-official-policy-supercop-20260907-e07/experiment-record.md`。

### 02 — codex/gt768-basemul-mixed-layout-20260901-e01

- HEAD `26c5837ae69f537f5667034917463529837d1844`。
- 將 h/r/m 的 SoA input benefit 分開：保留 AoS output 時三者共約132cycles，
  各自約36／50／37；舊433cycles不能全部算作 input-load budget。
- 額外 m:A→S 的 Forward+basemul+pack 路徑慢約139.72cycles；
  checked h 轉換也未改善完整 checked local path。
- 收尾：保存 attribution，已實作的 production-candidate shapes 不採用。
- Source: D + `gt768-basemul-mixed-layout-20260901-e01/experiment-record.md`。

### 03 — codex/gt768-basemul-output-simple-soa-20260901-e01

- HEAD `60a1671a90aebe1220c2e56cdf42e41761232239`。
- O0 static locality reject：每個 canonical pack group 橫跨6個 simple-S
  stripes、24個 q vectors；128bytes/group 變384bytes/group。
- 沒有進 assembly／Pi gate；不是一個測過但慢的完整 KEM。
- 收尾：保存 mapping proof，關閉此物化 output route。
- Source: D + `gt768-basemul-output-simple-soa-20260901-e01/experiment-record.md`。

### 04 — codex/gt768-basemul-soa-boundary-20260901-e01

- HEAD `0696d34db0ab83ad4ec48aea89405be59de52f59`。
- 已備妥 SoA inputs 的 basemul-only 快433cycles；加入兩次 Forward SoA
  materialization 後，local chain 仍快209–213cycles。
- 尚未包含 checked unpack／其餘 serialization 的完整成本；不能 promotion Encap。
- 收尾：保留正向 component result；由後續 mixed/output gates 限定適用範圍。
- Source: D + `gt768-basemul-soa-boundary-20260901-e01/experiment-record.md`。

### 05 — codex/gt768-bounded-ra-20260908-e22

- HEAD `3c1368cb882e75ac95cb1756bc50a8e1523a8361`。
- 邊界固定、internal renaming、zero spill：pack 快10.38cycles；完整
  Forward 快6.93cycles；checked unpack 慢0.79cycles。
- 後續 E23 P＋N 24組長測慢71.09cycles（0.19%），17/24組較慢。
- 收尾：保存 proof／patch 身分，這批候選不 promotion；不再加 solver 時間。
- Source: `experiments/gt768-bounded-ra-20260908-e22/REPORT.md`。

### 06 — codex/gt768-consumer-native-pm-20260831-e02

- HEAD `71c880bcab8904f0cd4cb2c2b9ac40281a646e4d`，沒有現存專屬 worktree。
- 完整 overlay correctness 通過，Encap49844 vs37827，慢12017cycles。
- 大部分差值是不同的 explicit scratch/coin clear 成本；no-clear diagnostic
  仍慢2700cycles，但此消除清除版本不等於公平政策 gate、不可 promotion。
- 收尾：完整候選 reject；保留跨 kernel mapping／ABI 教訓。
- Source: D + `gt768-consumer-native-pm-20260831-e02/experiment-record.md`。

### 07 — codex/gt768-decap-basemul-d1-q31-20260904-e02

- HEAD `aa442e62f01a6e72cddb19264c669272a94478a8`。
- 改到真正連結的 Decap basemul，直接 Q31 finalizer；accumulator bound
  452984832、residual[-2001,2001]，支援 left full-int16/right canonical。
- 當輪完整 Decap33003→32728，約275cycles；後續同 package paired gate補強。
- 收尾：保留 D1 range／correctness 原始證據；不是另一個仍需整支 merge 的版本。
- Source: D + `gt768-decap-basemul-d1-q31-20260904-e02/results.md`。

### 08 — codex/gt768-decap-basemul-d1-q31-slothy-20260905-e04

- HEAD `82b3f5b514887c25838067890d353f8a8f08271d`。
- 24-instruction tail，N1 proxy39→36，correctness通過；Pi完整basemul
  卻1992→2015（慢23cycles／1.15%），相同instructions及code size。
- 當時 window 未包含後續 tuple store，模型不能代表完整 consumer 成本。
- 收尾：reject generated schedule，保留反例／模型限制記錄。
- Source: D + `gt768-decap-basemul-d1-q31-slothy-20260905-e04/results.md`。

### 09 — codex/gt768-decap-basemul-d1-q31-stagger-20260904-e03

- HEAD `954832c6acfcbbf1590976bdfe860ee03445694d`。
- 相同24 instructions交錯兩個component，basemul1997→1992（5cycles）。
- 後來 e04 Slothy 替換更慢；本 branch 手排是此 family 當時保留的版本。
- 後續 package gate 支持 D1 full-path收益，但未區分出 stagger 相對 e02
  的完整 Decap 額外收益。不要把兩個結論混為一談。
- 收尾：保存選定 D1 family 的 schedule 證據；不用重新 import 整支branch。
- Source: D + `gt768-decap-basemul-d1-q31-stagger-20260904-e03/results.md`。

### 10 — codex/gt768-decap-encap-package-gates-20260907-e01

- HEAD `9183dea868bda892e1150f9117d280a71da703f4`。
- 同 package contract 下，三輪 e03 Decap 穩定快約0.8%，減190instructions；
  stagger 比 e02 的5cycle局部差，在 full Decap 未能區分。
- 歷史 Experimental Encap38509 vs38348.5，慢160.5cycles；
  兩次Forward淨估計各多約88／84cycles，basemul-add多161cycles。
- 這些 component 估計不可直接相加當完整profile；還識別出assembly-frame
  clear政策差異，因此舊比較不能當今天正式版的性能數字。
- 收尾：保留 package linkage／D1 gate 與成本定位證據。
- Source: D + `gt768-decap-encap-package-gates-20260907-e01/experiment-record.md`。

### 11 — codex/gt768-decap-vfy-d1-q31-20260904-e01

- HEAD `343d66ee6509614c8a3b6b1b16093e476e158ff3`。
- verification pipeline 當時快694cycles，但 production-shaped binary
  並不呼叫 gt_decap_verify_pointwise；該候選被 linker GC移除。
- 因此不能把2.10%提升套到正式 Decap；它促成後續 e02 改真正的 hot path。
- 收尾：保留 quotient/range proof 與「先確認實際連結」教訓；不 promotion此入口。
- Source: D + `gt768-decap-vfy-d1-q31-20260904-e01/results.md`。

### 12 — codex/gt768-encap-c0-simple-s-boundary-20260902-e01

- HEAD `b0501ea1c0283cebf8fef94fa27f43480633dc43`。
- 使用者列的末尾 `...-e0` 不存在；唯一匹配的實際 branch 是 `...-e01`。
- 固定 h/r/m、只改 c store/pack route；static gate比較
  AoS192 d-load+96moves vs simple-S288 q-load+576transpose。
  讀取bytes1536→4608，這個 compact-core重建路徑關閉，未跑新assembly／Slothy。
- 結論限定此物化 simple-S route，不否定所有 producer-to-pack融合。
- 收尾：與03同類歸檔但保留不同 proof 身分，不當重複 source直接刪除。
- Source: D + `gt768-encap-c0-simple-s-boundary-20260902-e01/experiment-record.md`。

## 3. 建議的知識分類與後續管理

- 政策與比較基準：01。
- 正向 arithmetic／選定 schedule／package evidence：07、09、10。
- 有界 component／attribution 證據：02、04、05。
- 否決路徑／linkage 教訓：03、06、08、11、12。

上述分類可用作後續 archive 清單，但本次沒有刪任何 branch 或worktree。
刪除前仍須檢查各 worktree 的未提交／未追蹤內容，保留必要 commit/tag
與重現依賴；「實驗不採用」不代表所有 proof 可拋棄。
也不應把這12支 branch merge到 E20：E20已有目前保留的演算法主線，
直接合併會帶回舊layout、舊cleanup policy或未採用的替代實作。

此索引只支持目前768收尾，不授權新的 promotion、benchmark或遙端變更。
