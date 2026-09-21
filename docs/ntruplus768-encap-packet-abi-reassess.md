# 768-ENCAP-PACKET-ABI-REASSESS：ownership gate

本輪完成 semantic ownership 與歷史候選去重；**未完成 instruction schedule，
未授權 ASM，沒有 benchmark 或 performance claim**。Clean 保持不動。

## 可機械驗證的新座標

連續 96-byte wire block = 64 coefficients = 16 quartic leaves = 4 YMM。
12 個 wire blocks 對應的 current M blocks 順序為：

```text
0, 1, 9, 8, 4, 5, 11, 10, 6, 7, 3, 2
```

每個 wire block 恰好對應一個 M block，沒有跨 M block 混合。
這與既有 Q24 decoder metadata 交叉核對，不是新發現一個尚未利用的
全域 gather 優化：current codec 已使用這種 locality。

第一個 block 的 wire leaf → M lane：

```text
7,3,15,11,14,10,2,6,12,8,0,4,13,9,1,5
```

因此「只換 store address」不能把 M planes 變成 wire AoS。

## 三種 presentation

以 wire leaf L0..L15 表示同一個 96-byte block：

```text
W（wire AoS）第一個 YMM：
low half:  L0.c0 L0.c1 L0.c2 L0.c3 L1.c0 L1.c1 L1.c2 L1.c3
high half: L2.c0 L2.c1 L2.c2 L2.c3 L3.c0 L3.c1 L3.c2 L3.c3

WP（wire-order planes）第一個 YMM：
L0.c0 L1.c0 ... L15.c0
第二個 YMM：L0.c1 ... L15.c1

Current M：也是 degree planes，但第一個 block 的 wire L0.cj
位於 M plane j 的 lane 7，L1.cj 位於 lane 3，而非 lane 0、1。
```

| Edge | M control | W | WP |
| --- | --- | --- | --- |
| r/m producer，各一次 | 現有 terminal transpose | 必須直接落 AoS；不能先產 M 再轉 | 改 terminal lane order |
| h decode，一次 | decode + M formation | 保留 quartic packets，仍驗證 | 仍有 AoS→plane formation |
| h×r+m | 已測 B3 | 新 AoS quartic schedule，成本未知 | B3 lane identity與 λ 一起重排 |
| r hash bytes，一次 | M→wire Q24 | contiguous packet pack，仍 canonicalize | planes→AoS 仍存在 |
| ciphertext，一次 | M→wire Q24 | 同上 | 同上 |
| register allocation | linked 已有 | 未完成 | 未完成 |

W 的假說不是「AoS 一定比較好」，而是讓 arithmetic 多付的費用，小於
兩個 producer terminal、一次 decode、兩次 serialization 的淨節省。
這必須完整計價。WP 只換 leaf order，並沒有取消 AoS/SoA boundary。

## Arithmetic 與 range

各 ABI 的 leaf identity、quartic degree、lambda 與 e=0 不變。
排列本身不改範圍；新 AoS arithmetic 的中間範圍不能直接沿用 B3 proof。
若採 vpmaddwd，需要重新證 dword sum、REDC、compaction、scale finalizer；
不能把固定常數 Barrett 技巧套到任意 h×r runtime product。

本輪 Python semantic test 使用 scalar quartic multiplication，對 M/W/WP
各自存取、加 m、canonical pack，並確認 retained r 沒被修改。
128 組測試覆蓋 h∈[0,3456]、r/m∈[-15592,15592] 的隨機值。
這是 permutation／scalar consumer self-consistency，不是新 AVX2 correctness
或獨立 full-transform proof。768 個唯一標籤驗證完整 bijection；48 個 packet
另與既有 codec metadata 對照。

## 舊方向不要換名重做

Asymmetric D01 已有完整 edge accounting：decoder 少 48 routes，被 consumer
pair formation 補回；既有 schedule 總數 +96 instructions。它**未經實測**，
所以不稱為已證較慢；但目前沒有新機制，不重開同一 realization。
其舊 r bound 10788 metadata 也不能作為目前 Encap proof。

Decode2→B3 streaming 與本輪 W 不同：前者保留 M arithmetic、只 fuse decoder，
已有退步 evidence。W 則必須讓 arithmetic 真正接受 AoS，不能偷偷重建完整 M
而又宣稱消掉 representation boundary。

## 下一個受限問題／停止條件

選 W 作**下一個 schedule 研究對象**，不是 machine winner：

1. 從真實 D1 live registers 到 W packet，逐 instruction 證明 ownership，
   包含必要 half/qword permutation；不得漏算兩個 forwards。
2. 選一個 compact AoS quartic MulAdd schedule，包含 lambda、R²、m、validation
   lifetime、packet canonicalization；instruction def/use 驗證 ≤16 YMM。
3. 用相同 taxonomy 列 current / W 的 producer+ingress+arithmetic+egress。
   本輪的 source-group / vector 數不是該 instruction ledger。
4. 沒有 executable allocation、合法 range 或新機制就停；不能用 static
   instruction 較多直接判 cycles 輸，也不能因較少就進 promotion。

本輪不產生 ASM。完整 exact schedule gate 尚未完成，這個缺口明確保留，
不把 semantic mapping pass 包裝成 machine feasibility pass。

## 重跑

在 `NTRU+768/experiments/avx2_gt32_tile4_official_001/`：

```sh
python3 tools/generate_encap_packet_abi_gate.py
```

結果：`generated/tile4_encap_packet_abi_gate.json`，含全部 768-slot mappings、
12 個 block 的 lane／lambda tables、source hashes、測試與未完成項目。

## Wire AoS 全 Encap schedule gate（後續 checkpoint）

此後續 gate 已把 W 的六條 Encap edge 放進同一個**可重跑 instruction-model**，
artifact 為 `generated/tile4_encap_wire_schedule.json`。它沒有新增 ASM、沒有執行
benchmark，也沒有修改 clean。表中的 opcode 數是 proposed schedule 展開數，
不是 linked machine object 或 cycle 數。

### D1 live → W：direct path 成立

從 clean `ntt_m.s` 的 `FR_MONT_QWORD_PACKED` 輸出接既有 `vpshufb`，
每個 AoS YMM 再用一條 `vpermq` 直接寫入 W packet 位址。48 個 packet 各來自
**單一** D1 後 AoS YMM；每個 packet 的 qword 選擇與 store displacement 都列在
artifact。六次 D1 loop 的 `rdi` 照舊每次前進 256 bytes，目標位址用組譯時
固定 displacement 表示，沒有 M buffer 中轉，也沒有新增 polynomial scratch。
標籤 replay 覆蓋 768/768 owners，並和原 Q24 codec 的 48 個 packet 對照。
例如第一個 wire packet 直接取 D1 後 AoS vector 3，qwords 排列
`[1,0,3,2]`（`vpermq $177`），寫 `W+0`；第二個 packet 取 vector 2、
排列 `[3,2,0,1]`（`$75`），寫 `W+32`。

| Encap 全部兩次 Forward 的 terminal | current M | direct W |
| --- | ---: | ---: |
| 既有 `vpshufb` | 96 | 96 |
| M plane unpack routing | 192 | 0 |
| W qword `vpermq` | 0 | 96 |
| vector stores | 96 | 96 |

因此 terminal routing 的靜態淨差是 −96，而**不是**「完全免費落 W」。
現有 D1 live registers `ymm0:7`、mask `ymm14`、q `ymm15` 不變；
deposit 的 `vpshufb`／`vpermq` 可原位覆寫。這是 source/machine-model
推論，不冒充 full macro-expansion 的 linked liveness proof。

### PK ingress、兩次 pack 與生命週期

PK 仍先 decode/validate，`Q24_DECODE_REG` 的 `vpmaxuw` validation 累積
保持在 W store 之前；只把現有 AoS→M transpose 改為每 packet 一個 qword
`vpermq`，直接寫 `h(W)`。`q−1=3456` 接受，`q=3457`、`4095` 拒絕；
每個 packet 都測了最後一個 coefficient 無效。invalid-PK 的 ct 歸零、ss
清除及提前 return 順序不變，沒有 validation-only pass。靜態 ingress routing
從 144 個 transpose op 變成 48 個 `vpermq`（−96）。

`r(W)` 在 hash_g、SOTP、第二次 Forward 期間 materialized 且不被 pack 修改，
直到 MulAdd 才 last-read。`m(W)` 直到 MulAdd 存活。原 `c` scratch 先供
frontend 使用，在 m Forward 完成後才重用為 MulAdd output；h/r/m/c/work
沿用 clean 的五個 1536-byte、64-byte-aligned arrays。沒有第六份多項式。

r hash input 和 c ciphertext 共用 48-packet 的 canonicalization／12-bit
packing body；其 v=9 reducer 仍執行，不把 lazy W 誤當 wire bytes。W packet
已在 exact wire order，省掉每次 M→AoS 的 144 routes 與 48 個 `vpermq`，
兩次 pack 合計 −384 routes。前 47 個 packet 可用通常的兩次 XMM store；
第 48 個必須使用既有 8+4-byte safe tail，最後寫入 byte 1151，
不得 16-byte 越界寫。外部 ct 與 W scratch 必須分離。

### Packet-native MulAdd：兩種保留的 schedule

W-Montgomery 每一個 YMM 同時持有四個 quartic leaves 的 16 個**輸出係數**。
四輪 `vpshufb` 在各 128-bit half 內產生 `h_i` broadcast 與
`r_(j−i mod 4)`；每輪做 runtime Montgomery product。`i>j` 的 wrapped
lanes 再乘 λ，其他 lanes 乘 Montgomery identity `R mod q`，最後乘 R²
回到 `e=0`、加 m、寫 c(W)。λ 及 QINV companion 以兩個 packet-local
constant vectors 載入，用 0x11／0x33／0x77 `vpblendw` 選出 wrapped lanes。
這不是四個完整 M degree planes 的重建。

W-VPMADDWD 對每個 packet 的兩組 8 個 output coefficients，分別形成
direct／wrapped 的兩個 paired dots；`vpmaddwd` 的 signed-i32 結果相加，
各自 REDC32，再以 `vpackssdw`＋`vpshufb` 回到 quartic AoS。wrapped
部分乘 λ，然後和 direct 相加、乘 R²、加 m。零填充 masks 只在同一個
128-bit half 內取 source，已逐 lane 由 scalar oracle 檢查。

| 每個 W packet 的 proposed body | W-Mont | W-VPMADDWD |
| --- | ---: | ---: |
| 展開 AVX2 opcode 數（含 h/r load、m add、c store） | 60 | 73 |
| 全 48 packet opcode 數，未含 loop 地址 | 2880 | 3504 |
| 單／雙 packet 虛擬 YMM 峰值 | 9／14 | 8／12 |
| 實際分配的 YMM 峰值（模型） | 8／13 | 7／11 |
| runtime product Mont chains／paired dots | 192 | 384 dots |
| 額外 λ-or-identity／R² Mont chains | 144／48 | 48／48 |
| REDC32 vectors | 0 | 192 |

Current B3 的來源算術是 192 runtime product、36 λ、48 R² Montgomery
vector chains（合計 276），另外用一次 `poly_add` pass。W-Mont 因每
packet 只有四個 leaves，需 384 chains；W-VPMADDWD 則把 runtime
product 換成 paired-dot＋REDC32。不能把 instruction 數差直接當 cycle 差。
兩個 W schedule 都把 add-m 放在 e=0 finalizer 後，**只消除舊 `poly_add`
的 48 次 c reload、48 次 c store**；48 次 m load 與 48 次 `vpaddw`
仍存在，這筆融合收益與 W layout 收益分列。

常數不是免費：compact W-Mont 的 48 份 λ 與 companion 約 3072 bytes，
另需 256-byte half-local shuffle masks；W-VPMADDWD 同樣要 packet λ／
companion，另有 512-byte dot masks。常數及 code 預定 `.p2align 5`。
W 算術可做一 packet×48 或兩 packet×24 的 compact loop，decoder
保留 48 個 unrolled source descriptors，packer 用 47+safe-tail body。
address-generation、constant operands、完整 opcode taxonomy 均在 JSON
ledger；這裡不以估計 `.text` bytes 宣稱 frontend bottleneck。

### Range、測試與決策

輸入 contract 是 h∈[0,3456]、r/m∈[−15592,15592]、e=0。
保守逐操作 envelope：W-Mont runtime product ≤2552、λ side ≤1797、
R² 前累積 ≤10208、加 m 後 ≤17457；W-VPMADDWD 四項 dot
≤215543808（小於 2³¹）、REDC direct／wrapped ≤5018／4196、
加 m 後 ≤17412。QINV 的 `vpmulld` low-word wrap 是刻意的模 2³²；
其餘 i16/i32 pre-operation 沒有溢位。packer 沿用既有完整 signed-i16
domain reducer proof；不能把舊 10788 名稱當限制。

驗證涵蓋 768 owners、192 λ identities、48 packets、40,012 個 scalar
quartic random cases、576 個邊界 packet、128 個完整 768-coefficient
pack cases。模型的 r/c bytes exact 與 r immutability 都已通過。
這些是**模型／scalar oracle**，不替代未來 ASM 的 KAT、linked ABI、
sanitizer、constant-time 或 Native SUPERCOP。

決策：direct-W、兩種 arithmetic、一／雙 packet 的 instruction model
和 range 均合格；**不宣稱 W 比 M 快**。若下一輪授權 ASM，優先
W-Montgomery 作較小 arithmetic realization，W-VPMADDWD 保留為
dependency/REDC 對照。只有完整 Encap island 實測後才能判斷 movement
credit 是否足以支付每 packet arithmetic 與常數成本。

重跑：

```sh
python3 tools/generate_encap_wire_schedule.py
```
