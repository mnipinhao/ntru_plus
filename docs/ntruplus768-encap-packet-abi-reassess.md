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
