# GT768 Encap：逐函式研究與 eager BaseMul

日期：2026-09-22。Branch：`avx2-gt-ntt`。

## 結論與證據範圍

**不改 M ABI、不做跨函式 fusion，也找到一個完整 polynomial island 的短測改善。**
本輪只用了第一個 ASM 名額：把 BaseMul 的 R² finalizer 提早到各 output 完成時。
BaseMul 本身約 −27.53 cycles，完整 island 約 −47.57 cycles，三次 launch 同向。
這是 **ready for serious pricing**，不是 Native／production winner。

第二個名額保留。W aggregate-λ 有完整模型，但仍須新 ABI 的 machine realization；
目前沒有理由為湊滿名額同時改所有 functions。這不否決 W，也不證明 M 最佳。
本輪沒有整合 prefixed-hash-buffer，也沒有 fusion add-m／serializer。

完整結果在既有 768 experiment 的
`results/encap-fn-eager-short-20260922/`；
可重跑來源、全部 owner、range certificate、逐指令 def/use、caller ledger 在
`tools/generate_encap_fn_eager.py` 與 `generated/encap_fn_eager.json`。

## 1. Hwang 的方法，哪些已經有、哪些不能照搬

依附件《Pushing the Limit of Vectorized Polynomial Multiplications for NTRU Prime》
§§3、4.1.2、4.2.1，以及固定 artifact
`3eb881fb4aa83a9c424a121acefb1b8d35cf6f93`：

| 機制 | Hwang artifact | Current GT768 | 本輪判斷 |
|---|---|---|---|
| 整向量 GT index | 3×2 pre/post 以 A0,A4,A2,A3,A1,A5 load order 實作 | GT3 frontend 的一個 YMM 需三個 source 的 qwords | 地址重排只能省特定 ownership 的 permutation |
| Twist 與搬移 | pre twist 和後續 transform 共用 pass；twist 仍執行 | top split、GT formation、twist、DFT3 同一 frontend | 已採用共用 pass，不等於 twist 已免費 |
| Interleaving | 對同形狀小環作 transpose，同 degree 跨 rings 算 | M 的 degree planes 正是同 degree、不同 quartic leaf | M arithmetic 並非沒有配合 vectorization |
| Terminal arithmetic | cyclic/negacyclic rings 配 CT/Bruun/Karatsuba | 192 個不同 λ 的 quartic factors | 不直接移植乘法數量或加速比例 |
| ISA 差異 | AVX2 permutation-friendly；Neon 另有 vector-by-scalar 路線 | AVX2 16-bit lanes、128-bit half 限制 | 不套用 Neon 三指令乘加成本 |

一個 Hwang 96-coefficient block：六個 YMM 各有 16 個 lanes，load offsets
0,128,64,96,32,160 bytes。pre 先做六個 twist Montgomery，再做兩個 radix-3
Montgomery；這個 block 內的 whole-vector GT 沒有 lane permutation。
後面的 16×16 transpose 仍要 48 unpacks＋16 cross-half permutations／256
coefficients，並存成同 degree、跨 16 rings 的 representation。
這個 conversion 是讓後續 arithmetic 可重用，不是完全消失。

本輪重跑既有 artifact/model `--check` 和七個 regression tests，包含
pre/post basis、transpose owners、四種 stage cuts、全部 GT owner 和 codec 邊界。
證據／hash 延用 `ref/hwang-vector-mapping-sources.json`。
這不是 Hwang 任意輸入的完整 machine range proof。

## 2. Forward：從 coefficient 到 M，逐段 register flow

### Frontend

- **輸入 ownership**：六個 coefficient YMM，offset 0,256,…,1280 加目前 packet
  displacement；每 qword 是同一組四個 degrees。
- **指令／依賴**：small-input top split 用 raw `vpmullw`，形成
  l−722h、l+723h；`vpblend*` 做 GT indexing；fixed Montgomery 做 twist；
  DFT3 用加減與固定 ω multiply。
- **輸出**：六個 (branch,k3) tiles，每 tile 八個 YMM。GT index
  n=(64n3+33n32) mod 96；branch weight s^(−n)，s=2 或 22。
- **數學／scale**：terminal quartic decomposition，fixed table 存 weight×R，
  materialized state 保持 e=0。
- **為什麼需要 blend**：packet0/n3=0 的 qword owners 是 [0,33,66,3]；
  它們並非一個現成 YMM，單純重命名 32-byte load 不能得到。
- **下一個 consumer**：NTT32 要同 (branch,k3) 的 32 positions，四個 degrees
  各自沿此軸變換。

實際 vector：

```text
128-bit low : n0.c0 c1 c2 c3 | n33.c0 c1 c2 c3
128-bit high: n66.c0 c1 c2 c3 | n3.c0  c1 c2 c3
```

每 Forward：24 raw top-split vector multiplies、48 twist Montgomery、
16 DFT3 Montgomery、96 routes、48 loads＋48 stores。
48 twists **仍執行**；GT inter-axis twiddles 不存在，不表示 ring embedding 免費。

### NTT32：D16 → D8/D4 → D2/D1 → terminal

- **進入**：ymm0…7 含一 tile 的 32 positions×4 degrees；ymm15=q、
  ymm14=terminal byte mask。
- **D16**：pairs (0,4),(1,5),(2,6),(3,7)，raw add/sub，不做 twiddle multiply。
- **D8/D4**：每層四條獨立 Montgomery 高支路；low-word companion multiply、
  signed high multiply、q correction、sum/difference。四路交錯提供 ILP。
- **D2**：每 pair 先用兩個 `vperm2i128` 取 low/high halves，做 butterfly，
  再用兩個 `vperm2i128` 重組；四 pairs／tile。
- **D1**：每 pair 兩個 qword unpacks，乘高支路 twiddle，輸出 sum/difference。
- **terminal**：每四向量組做四個 `vpshufb`＋八個 unpacks，形成四個 M planes。
  每 tile 兩組，共 24 terminal routes。
- **離開**：48 個 M YMM，所有 lanes 有效；沒有新增 scale conversion。
- **bound**：沿用 hash-verified refined ternary proof |Forward|≤15592；
  這是 proof envelope，不是實測最大值。
- **下一個 consumer**：BaseMul 可直接以 degree planes 做逐 lane quartic arithmetic；
  codec 則必須恢復 wire quartic grouping。

NTT32 共 96 Montgomery chains；D2 routing 96、D1 routing 48、
terminal routing 144，總 288。與 frontend 合計 160 Montgomery chains、384 routes。
**目前 Encap 選中的 Forward 沒有獨立 Barrett vectors**。Source 內其他 macro、
其他 caller 或歷史參數的 reduction 不可算到此路徑。

D2 的重組再被 D1 拆開，值得做 exact ownership search，但不是已證明可直接刪除：
twiddle lane 與下一 pair ownership 必須一起驗。舊 orientation/schedule 只有在出現
新機制時才重開。未改 arithmetic 的任意新 network 仍須 raw exact。

## 3. M → BaseMul → wire 的完整例子

一個 M block 有四個 YMM，各自是 degree j=0,1,2,3。每個 vector：

```text
physical q:
low half  [0,4,8,12,1,5,9,13]
high half [2,6,10,14,3,7,11,15]
```

全部 λ 隨 leaf identity 對應，不是依「看起來連續的 lane」推測。
generator 驗全部 768 owners、192 λ，以及 λ^192−λ^96+1=0。

以第一 wire packet 為例，它需要 M word indices：

```text
[7,23,39,55, 3,19,35,51, 15,31,47,63, 11,27,43,59]
```

也就是 M block0 的 lanes [7,3,15,11]，每 leaf 取四個 degrees。
例如 wire coefficient0 是 (branch0,k3=0,physical-q13,degree0)，在 M word7；
它與同 leaf 的 degree1，即 M word23，一起成為前三個 wire bytes。
若 canonical values 是 a,b，bytes 為
`a&255, (a>>8)|((b&15)<<4), b>>4`。
因此「M 很適合 quartic arithmetic」與「M 並非免費可 serialize」可以同時成立。

### BaseMul control

- **進入 registers**：h0…h3=ymm1…4；h×QINV low-word companions=ymm5…8；
  r0…r3=ymm9…12；q=ymm0；tmp=ymm13/14；acc=ymm15。
- **數學**：對每 leaf，
  c_j = Σ(i+k=j) h_i r_k + λ Σ(i+k=j+4) h_i r_k。
- **實作**：16 runtime Montgomery products／block，加三個 λ corrections；
  然後四個 R² finalizers。每 polynomial 192＋36＋48=276 chains。
- **scale**：runtime products 為 e=−1；λ×R correction 保持 e=−1；
  R² finalizer 回 e=0；獨立 add-m 之後才送 serializer。
- **layout**：完全沒有 routing。M 的 producer→arithmetic 已經直接匹配。
- **原有額外工作**：c0/c1/c2 先存 raw e=−1，再 reload，與 c3 一起四路 finalization。
  這是 schedule 選擇，不是 quartic 數學要求。

### 唯一新原型：eager finalizer

```text
control: raw c0/c1/c2 stores → c3 → reload → four-way finalizer → final stores
eager:   raw cj → same R² finalizer using ymm13/14 → one final store, for j=0..3
```

不重讀 h，不重建 M，不融合 add 或 packing。所有 arithmetic instructions 的 expression
DAG 完全相同，僅獨立操作排序不同。Bit-word symbolic proof 保留 `vpmullw` 的 intentional
wrap，四個 output expressions 相同；所有 pre-operation values 與舊 proof 相同。

| Linked dynamic per polynomial | Current M | Eager M |
|---|---:|---:|
| Montgomery chains | 276 | 276 |
| data-load instructions | 132 | 96 |
| data-store instructions | 84 | 48 |
| constant operands | 217 | 217 |
| routing | 0 | 0 |
| expanded instructions, excluding padding | 1614 | 1530 |
| peak live YMM | 16 | 16 |
| symbol bytes | 684 | 655 |
| vector spill / stack frame | 0 | 0 |

減少 36 stores＋36 reloads，另少 12 register moves。代價是 finalizer 的四路平行被拆散；
linked cycles 才能決定是否划算。原有 return-boundary `vzeroupper` 保留一個，
沒有新增 internal AVX boundary。唯一 branch 是公開的 12-block loop。

## 4. Decode 與 serializer：哪些可疑，哪些不能宣稱免費

### PK decode

wire bytes → 兩個 12-byte sources／packet → XMM loads＋`vinserti128` →
`vpshufb` → shift/blend/mask 提取 12-bit values → unsigned validation accumulator →
transpose 到 M planes → store。

其數學是解碼 canonical h∈[0,3456]，e=0；invalid q/4095 不能因為 arithmetic
可以模 q 而接受。validation 在 arithmetic 前完成。最後 packet 用 safe loads，
不能為省指令越界讀取。97 data loads 含尾端安全拆分，不全是 layout penalty。
288 routes 混合必需 unpack、half formation 與 M formation，不能全稱為冗餘。

### r／c pack

M planes load → Q24 transpose/ownership → v=9 signed-word canonicalization →
12-bit pair packing → byte shuffle／extract → wire stores。
q／v、pair factor／mask 與 temporaries 的 lifetime 已計入，source peak=7 YMM。

每次 pack 有 48 Barrett-like vectors、288 routes、48 loads、97 stores。
r 與 c 使用同一核心，c entry 另有一個 tail jump。r 不修改；r 必須跨過
hash_g、SOTP、m Forward 供 arithmetic 再使用。相同 pack 核心可接受完整 signed-i16，
函式名中的 10788/12699 不是硬體契約。

這裡的兩次 canonical wire bytes 是必要外部輸出，不是「多算兩遍」。
可研究更便宜的 ownership network；若改成 W，必須讓 BaseMul 的額外廣播／shuffle、
constant operands 一起入帳。

## 5. 同 taxonomy 的完整 source ledger

下表是 reachable expanded source ledger；只有 BaseMul 的改動另有 linked replay。
不是整個 C caller 的精確 dynamic instruction trace。

| 函式，一次 | chains | Barrett | routing | data loads/stores | constant operands | peak YMM |
|---|---:|---:|---:|---:|---:|---:|
| frontend | 64 | 0 | 96 | 48/48 | 153 | 10 |
| NTT32＋terminal | 96 | 0 | 288 | 48/48 | 194 | 14 |
| PK decode＋validate | 0 | 0 | 288 | 97/48 | 50 | 10 |
| BaseMul current | 276 | 0 | 0 | 132/84 | 217 | 16 |
| independent add-m | 0 | 0 | 0 | 96/48 | 0 | 6 |
| pack，一次 | 0 | 48 | 288 | 48/97 | 98 | 7 |

完整 Encap multiplicity 為兩個 frontend、兩個 NTT32、一次 decode、一次 BaseMul、
一次 add、兩次 pack。Current 共 1632 routes、613 loads、566 stores、1157 constant
operands。Eager 只各減 36 loads/stores；**add-m fusion credit=0**。
這是 static mechanism ledger，不是可相加的 cycle waterfall。

## 6. 新 cycle-counter campaign

SUPERCOP 20260831 source hash verified；Official objects 在 disposable result directory
用 objcopy namespace，沒有修改 pristine。共同 O3GC、CPU1/performance/turbo-off，
normal placement/ASLR-on 預先固定、三個 fresh processes。
Backend 實際回報 `default-perfevent`，不是 RDPMC、不是 process-wide perf stat。

每 operation 每 variant 每 launch 96 samples；使用 pinned `stq.h`。
operation pointer 在 t0 前選好，三方只有相同 indirect-call overhead，沒有 timed
variant dispatch／sink。8 個 input banks、平衡順序、物理 slots rotation；
相同 untimed reset/warmup。Official in-place Forward 的 input reset 在 timing 外，
GT 所需 frontend scratch 留在 timing 內。所有起點獨立重新準備。

| Operation StQ2 cycles | Official | Current GT | Eager GT |
|---|---:|---:|---:|
| Forward r | 951.33 | 886.96 | 886.38 |
| Forward m | 950.72 | 885.99 | 886.94 |
| 2×Forward | 1673.68 | 1556.93 | 1555.35 |
| PK decode | 356.78 | 387.33 | 386.85 |
| BaseMul | 721.53 | 721.22 | 693.69 |
| BaseMul＋independent add | 772.56 | 773.88 | 741.86 |
| r pack | 422.07 | 463.97 | 462.94 |
| c pack | 421.12 | 463.92 | 463.03 |
| r → retained state＋hash input bytes | 1170.40 | 1131.21 | 1133.17 |
| complete polynomial island | 2846.21 | 2834.88 | 2787.31 |
| GT frontend diagnostic | N/A | 448.54 | 449.57 |
| GT NTT32＋terminal diagnostic | N/A | 637.35 | 637.58 |

Eager 未改 Forward／decode／pack：這些欄位是 same-code controls，差值不是優化收益。
Counter overhead、函式切點和 residency 使 isolated rows 不可相加；
例如 frontend＋terminal 不應強迫等於完整 Forward。
GT／Official 的 BaseMul 輸入各自是其原生 transformed layout，不加跨版本 adapter。

Eager−current GT：

- BaseMul：−27.53；launch deltas −29.00, −25.38, −27.67。
- BaseMul＋add：−32.01；launch deltas −36.46, −25.96, −33.88。
- 完整 island：−47.57；launch deltas −49.38, −54.00, −46.00。

完整 island 相對 Official 約 −58.90 cycles，但這不是 Native Encap：
cutpoint 不含 hash_f/g/h、sampling、SOTP、清除。Research KEM wrapper 保留這些原路徑，
僅替換 BaseMul，用於 correctness，不用其結果宣稱 Native speed。
47.57 大於 27.53 的原因未用 PMU 證明；不能把差值直接命名 cache／OoO credit。
Normal placement 短測也無法隔離全部 code-placement 效應。

驗證：10003 raw-exact／獨立 quartic cases；1536 signed impulses、zero／alternating、
random ternary、conservative bound extremes；合法 out=h/out=r、canary、immutability、
guard-page；100 deterministic Encap vectors（同一生成 key、多組 coins）、invalid PK/CT、
ASan/UBSan wrapper。Bench 的八個 banks 另經 Official／GT hash-input及 ciphertext
byte-exact preflight；相同 DAG 的新 ASM 不改 Forward mapping。
既有完整 mapping/model 重播包含2304 decoder boundary cases與65536 signed reducer cases。

## 7. 選型與未決工作

2026-09-22 後續：eager 的九-launch局部訊號已確認，但完整 Native／fixed-ELF
qualification 未通過，不能 production。另已獨立測試14個 identity `vpermq`
刪除，並完成固定 M 的 mask/store network 模型。詳見
[qualification 與 codec follow-up](/home/nuc/src/ntru_plus/docs/ntruplus768-eager-qualification-codec-followup.md)。
下表及本節其餘文字保留原短測 checkpoint 的決策，不作最新 promotion 狀態。

| 提案 | 證據／可處理成本 | 決定 |
|---|---|---|
| M BaseMul eager R² | 原有36＋36內部存取；沒有 ABI 適配成本 | 實作一個 ASM；ready for serious pricing |
| M Forward 再刪 Barrett | reachable Encap Forward 已為0 | 不製造候選 |
| D2/D1 orientation | 96＋48 routing，terminal另144；不代表可全刪 | 待新的 exact lane/twiddle network，不重跑舊版 |
| W aggregate λ | 先前模型276→288 chains相對M，full routing+48、constants+550 | 有模型但未定價；本輪未使用第二名額 |
| M codec network | 本次 decode約+31、各pack約+42 cycles相對Official | 值得下一輪逐函式 search；不能相加為Native debt |
| frontend twist再吸收 | 48固定twist仍在，但跨DFT3 merges的gauge須閉合 | 尚無新identity，沒有偷偷改table |

因此已證明的額外成本是 BaseMul 中可移除的 intermediate memory；
已測的相對成本是 decode／packing。它們與 M layout 的關係有 source 機制支持，
但尚未證明任何新 ABI 可淨省這些 cycles。
M 對 arithmetic 的匹配已成立；對 serialization 的交換仍開放。
本輪未跑 serious／Native／placement confirmation，不動 clean production。

重跑（從 768 experiment）：

```sh
python3 tests/test_stq_pinned.py /home/nuc/supercop-20260627/include/stq.h
python3 tools/correct_live_b3_stq.py
python3 tools/generate_encap_fn_eager.py --check
make encap-fn-eager-check encap-fn-eager-sanitize
python3 tools/run_encap_fn_short.py --supercop-root /home/nuc/supercop-20260627 --tag <new-tag>
```
