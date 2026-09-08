# NTRU+768：E20 後續 Slothy／P＋N 實驗收尾

日期：2026-09-08。此檔是回存至 E20 的單一結果摘要；不帶入候選 source、
benchmark harness、JSON、生成 assembly，也不合併 E21–E23 branch。
本次僅新增文件，E20 package source 不變。

## 版本定位：E20 不等於目前正式 Production

- 完整整理版 branch：`codex/gt768-pack-util-cleanup-20260908-e20`。
  文件加入前 HEAD `d09afbb4`；實作 commit `561b6aa50dc0e237c3c884ec7174a208baf869e5`。
- 正式 branch：`aarch64-production`，HEAD
  `b2f9ee83350a3e11dc2eae802ae0e5d7651586d4`。
- 兩者共有 G5 等既有改善，以及 checked unpack direct output mapping；
  正式 branch 只從 E20 promotion 了 checked unpack，沒有整套 cleanup。
- E20 額外包含 `poly_sub`／`add.S`、`crepmod3.S`、`util.h`／`secure_clear`
  命名整理、恢復 q-centering 後取 centered mod3、移除無 caller 的內容，
  並把仍供回歸測試使用的 legacy code 移至 `test/legacy`。
- 這不是全為改名：`crepmod3` 的數學 contract 確有修正。E20 有既有
  exhaustive support oracle、KAT／ABI／zeroization 等驗證記錄。

因此可以把 E20 當作「本階段完整、較乾淨的整理版」保存與閱讀，
但不能聲稱它已證實是所有 Keygen／Encap／Decap 都最快的正式版本。
E20 原始結論仍是 keep-experimental pending promotion review。

E20 已有四輪 SUPERCOP 結果（round medians 的中位數）：

| 同輪版本 | Keygen | Encap | Decap |
|---|---:|---:|---:|
| G5 baseline | 36352.5 | 37152 | 32501 |
| unpack-only | 36335.5 | 37140 | 32493.5 |
| E20 full cleanup | 36377.5 | 37128 | 32513.5 |

小幅差值不構成穩定全面加速；詳細來源為同目錄 `REPORT.md` 與
`final-runs-summary.json`。E20 此次沒有重跑 benchmark。

## E21／E22：最後一輪 bounded scheduling

E21 固定所有原有 register；E22 只固定真正的 boundary assignments，
讓內部 temporaries renaming，每個窗口限 30 秒、zero spill，數學與
reduction 不变。兩輪基準均為上述正式 Production，不是 E20 full cleanup。

| E22 項目 | E21→E22 模型 cycles/window | Pi component 配對中位數差 | 決策 |
|---|---:|---:|---|
| checked unpack | 46→46 | +0.786 cycles，慢 0.154% | 不採用 |
| loose reducer＋canonical correction＋bitpack consumer | 130→75 | −10.377 cycles，快 1.071% | 僅保留實驗 |
| lazy Stage12 stripes6/7 | 33→25 | 完整 Forward −6.929 cycles，快 0.331% | 僅保留實驗 |

NTT 窗口含原有 block3 stores，但沒有包含後續 Stage345 register consumer；
不能視為完整 Stage12/345 融合。P 保留 reduced entry，獨立 loose core 使
pack text 增加 344 bytes，完整 polynomial 增加 12 次 branch。
Mac／Pi package checks、KAT、SSA selfcheck 與 differential 通過。
模型改善不是實機 cycle 收益，也不是完整 KEM 收益。

E22 記錄：`3c1368cb`，branch `codex/gt768-bounded-ra-20260908-e22`。

## E23：P＋N 合併較長完整 Encap gate

記錄 commit：`35f6ceb46cac83e656cbc50b85756fb719f5a198`。
branch：`codex/gt768-pn-long-encap-20260908-e23`。
候選為 E22 的 P＋N exact patches，不重新跑 Slothy。
只有 `pack.S`、`ntt.S` 與 source manifest 相對 Production 不同。

預先固定 24 組 alternating paired runs，每個 process 100000 次 Encap，
500 warmups，Pi `pi@100.99.191.9` core3。相同 checked decode、清除政策、
deterministic RNG、SUPERCOP leaf exporter、hash backend 與 link flags。
編譯：`-O3 -march=native -mtune=native -fwrapv -fPIC -fPIE -D_DEFAULT_SOURCE`。
PMU 分 cycles/instructions 與 ld_spec/st_spec/stall_backend 兩組，無低於
99.9% 的 multiplexing。沒有看結果追加輪數。

| 完整 Encap metric（各自中位數） | Production | P＋N |
|---|---:|---:|
| cycles | 37387.090 | 37457.143 |
| instructions | 107205.278 | 107215.328 |
| ld_spec | 15330.640 | 15336.969 |
| st_spec | 9274.249 | 9276.384 |
| stall_backend | 6909.636 | 6977.142 |

- 配對中位數（候選−基準）：**+71.093 cycles，慢 0.190%**。
- 17/24 組較慢，7/24 組較快；平均差 +36.938 cycles。
- 差值範圍 −92.103 至 +127.034 cycles。
- baseline-first 中位數 +85.158；candidate-first +41.652。
- 前半段 +69.231；後半段 +80.866。
- Mac／Pi B/PN `make check` 通過，包含 KEM、ABI、canonical/failure、
  small-input、zeroization 與 KAT。
- 另通過 4096 unpack/full-int16 pack/small-NTT differential，以及
  256 identical-RNG Encap ciphertext/shared-secret comparisons。
- KAT SHA256：`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`。
- Pi 前後 throttle `0x0`，結束溫度 65.3°C。

結論：**reject 這個合併 performance candidate，不 promotion。**
局部收益未轉成完整 Encap 加速。Backend stalls 上升不是已證明的根因；
不能僅憑這輪把差值歸咎於 branch、cache 或 code size。

注意：E23 是完整 Encap perf harness，使用匯出的 SUPERCOP leaves，
不是原生 SUPERCOP timing driver。也未重新測 Official。
它與 E20 的 timing 方法不同，不可直接拿兩表的絕對 cycles 排名。
E23 與 E22 的 operation count 也不同，warmup 占比分別 0.5%／5%。

## 收尾決定與保存方式

1. NTRU+768 本階段先停在現有實作，不追加 Slothy 或新 candidate。
2. E20 保留完整整理版；正式 Production 保留既有 promotion 狀態。
3. 不把 P＋N 複製到 E20，不把 E23 的拒絕結果冒稱為 E20 實測。
4. 本次只回存此 Markdown；E23 原始記錄仍可由上述 commit 取得。
   E23 臨時 worktree／生成檔已移除，E22 原始 patches 仍保留。
5. 此次沒有 push、沒有合併 main，也沒有修改 aarch64-production。
6. 若將來要以 E20 取代正式版，仍須明確的 cleanup／semantic-fix promotion
   決策；不能因「較乾淨」自動推導「已正式合併」或「已證明最快」。
