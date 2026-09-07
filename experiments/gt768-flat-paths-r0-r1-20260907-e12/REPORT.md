# GT768 R0／R1：引用盤點與路徑平鋪

## 結論

R0、R1 通過。32 個檔案搬到 package root；61 個 release files、28 個 production
編譯單元與編譯順序不變。沒有 function rename、assembly 合併、kernel/table 刪除、
layout／range／alias 變更，也沒有新的效能優化。

候選在 `codex/gt768-flat-paths-r0-r1-20260907-e12`，尚未合併到 `aarch64-production`。
基準／previous champion 是 `d598969f830090de33ca9cc2462e102b668e437e`。
實驗 ID：`gt768-flat-paths-r0-r1-20260907-e12`。

已驗證的 source commit：`739e0472ab6545fcad2264815dbd7cf85cc736d2`。
manifest SHA-256：`93e8536dfc4b64056f306216d27cc5d94487778570023338e636d1c5860f9459`。

本輪以 commit 保存候選，不另留一份永久 source copy。生成物和原始日誌放在
gitignored `.build/`；可讀 inventory、引用 graph、hash／驗證摘要長期保留。

## R0 完成內容

- [ROOTS-AND-CONTRACTS.md](ROOTS-AND-CONTRACTS.md)：三組 roots、實際 KEM DAG、
  ABI／representation／range／alias 邊界、工具鏈與沿用的 benchmark 基準。
- [INVENTORY.md](INVENTORY.md)：完整搬移表、28 個 source/object 的 exports、
  weak/platform aliases、undefined references、named data、153 個明確 assembly
  labels 及其同檔 textual references、KEM-root link 保留的 symbols。
- [reference-graph.json](reference-graph.json)：實際 Pi objects 的 call/jump/data
  relocation edges。局部 PC-relative table 不一定有 relocation，需合看 source index。
- [path-and-include-map.json](path-and-include-map.json)：32 項路徑映射及 45 項
  quoted-include 解析紀錄。

這份 inventory **不是 dead-code 證明**。同一 assembly section 裡的資料或其他
入口可能因 section 粒度一起留在 binary；未出現在 KEM 直接呼叫清單的入口，
仍可能是 public API、ABI test 或 differential oracle。R1 全部保留。

## R1 實際做了什麼

`asm/`、`asm/internal/`、`internal/`、`NO_CE/` 的 source/header 全部平鋪至 root。
檔案 basename 不變，唯一同名衝突是：

| 舊路徑 | 新路徑 | 原因 |
|---|---|---|
| `internal/ntt.h` | `ntt_internal.h` | 不可覆蓋原本根目錄的 `ntt.h` |
| `internal/keygen.c` | `keygen.c` | 尚未進入 `poly.c` 的重新命名／合檔步驟 |
| `internal/secure_clear.h` | `secure_clear.h` | 尚未重新命名為 `util.h` |

Makefile 更新 source paths 與 include search path，保留相同 source order 和 CFLAGS。
release／zeroization 檢查腳本、README、implementation 路徑說明與 manifest 同步更新。
zeroization assembly 掃描也由舊 `asm/` 改為 root `.S`，沒有讓檢查變成空迴圈。

重要 include 細節：原本 `internal/basemul_lambda.c` 的 `"ntt.h"`，因 quote include
搜尋順序而引用 **internal/ntt.h**。搬移後明確使用 `"ntt_internal.h"`，保持原本
預處理內容。不能直覺改成根目錄 ntt.h。

`symmetric.c` 的非預設 `SUPPORTS_SHAKE256_ASM` 分支仍引用缺少的 `CE/fips202.h`；
這是基準原有、未支援的分支，本輪沒有啟用或擴大支援。預設 portable SHAKE 通過。
assembly 內歷史來源註解保留原文；其中舊 `asm/` 字樣不是新的 build dependency。

`test/`、`kat/`、`scripts/`、`docs/` 仍保留。這是可維護 package 的第一階段，
不是已完成的 Linux-only SUPERCOP export；沒有把 `.S` 草率改成 `.s`，也沒有
移除本地 randombytes support。

## 驗證結果

| Gate | Mac | Pi 5 |
|---|---|---|
| 28 個 production units 的 `-E -P` 內容 | 全數相同 | 全數相同 |
| 28 個完整 object bytes | 全數相同 | 全數相同 |
| `make check`／manifest | PASS | PASS |
| 100 KEM round trips | PASS | PASS |
| 9,216 canonical-boundary cases | 0 failures | 0 failures |
| 4,096 Encap-small exact／alias cases | PASS | PASS |
| required ABI mask | `0x00000` | `0x00000` |
| retained internal custom ABI mask | `0x3fc00` | `0x3fc00` |
| KAT request／response | bit-exact | bit-exact |

KAT rsp SHA-256：
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`。

Pi 六個 fresh 同 flags 測試 ELF 的 `.text`、`.rodata`、所有 runtime sections、
地址／尺寸／對齊均相同。整檔 hash 不同的唯一 section 是非載入的 `.strtab`；
不要將「runtime 等價」寫成「整個 executable byte-identical」。28 個單獨編譯
的 production objects 則確實是整檔相同。

先前留存的 e10 test binaries 不能直接視為 fresh 同設定 baseline：初次比較其 `.text` 不同，
因此本輪另外從未改動的 e10 source 用相同預設 flags fresh rebuild 至 e12 build
目錄後才做 ELF 比較。最終結果記錄在 [verification-summary.json](verification-summary.json)。

### 清除政策沒有變

同 deterministic seed 的六路徑 trace 與 e10 byte-for-byte 相同；每次 clear 後
也逐 byte 檢查為零。

| 路徑 | clear calls | cleared bytes |
|---|---:|---:|
| Keygen | 20 | 13,352 |
| Encap valid | 16 | 6,410 |
| Decap valid | 9 | 10,930 |
| Decap verification failure | 9 | 10,930 |
| Decap noncanonical | 2 | 8,608 |
| Encap invalid PK | 2 | 128 |

這仍是 Official-aligned C cleanup，不是 full stack／SIMD register wipe。

## 重現

本機候選 worktree：
`/Users/chenpinhao/ntruplus/.worktrees/gt768-flat-paths-r0-r1-20260907-e12`

package 相對路徑：
`ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768`

Pi：`ssh pi@100.99.191.9`。
獨立 staging：`/home/pi/gt768-flat-paths-r0-r1-20260907-e12/NTRU+768`。
Pi baseline source：`/home/pi/gt768-production-d1-small-official-policy-20260907-e10/NTRU+768`。

`audit.py BASELINE CANDIDATE OUTPUT` 以相同 flags 編譯／預處理兩邊，保存所有
objects、nm、relocations、hash。OUTPUT 放在本實驗 `.build/`。

在兩邊 package 目錄分別執行：

```sh
make check BUILD_DIR=/home/pi/gt768-flat-paths-r0-r1-20260907-e12/.build/baseline-package
make check BUILD_DIR=/home/pi/gt768-flat-paths-r0-r1-20260907-e12/.build/package
```

`finish_pi.py` 位於 Pi staging parent，重用紀錄內明確指定的六路徑 fixture 和
deterministic RNG；保存 fixture hash、link command、cleanup log、ELF 比較與引用 graph。
本機的 `record_patch.py` 由 audit 結果輸出 persistent record patch。
`flatten_patch.py` 僅重現初始搬移／include patch；後續 README 路徑說明修訂見本 commit。

Mac Apple Clang 與 Pi GCC 14.2.0 的確切版本、host、逐 source/object hashes，
見 verification summary。KAT 測試有基準既有 warning，沒有新的編譯失敗。

## 邊界／下一步

本輪沒有跑 SUPERCOP cycles；不能聲稱產生新的 speedup。相同 runtime code/layout
支持「搬檔沒有改變效能路徑」，而不是一個新的實測 benchmark 數值。

下一步若獲准才進 R2 function naming；之後才考慮 assembly 合檔、移除經完整
root closure 證明可移出的內容，以及 Linux SUPERCOP export。尚未 promotion。
