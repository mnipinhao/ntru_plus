# E24：E20 cleanup promotion／768 worktree 收尾

日期：2026-09-08。使用者授權依 correctness／效能 gate promotion E20，
並先保存 archive tags 再整理乾淨 worktrees。沒有 push，沒有合併 main。

## 結論與精確版本

Gate：**通過 cleanup promotion 的預定 0.3% regression margin**。
這不是宣稱 E20 全面加速，也不是所有環境下無退步的統計證明。

- Previous Production：`b2f9ee83350a3e11dc2eae802ae0e5d7651586d4`。
- E20 implementation：`561b6aa50dc0e237c3c884ec7174a208baf869e5`。
- E20 測量來源 branch head：`c6099ba6bc4e5493c06bdd7ac6a1f06e6ef7f89e`。
- Package-only promotion commit：`8282a30e`。
- 已核對 promotion package 與被測 E20 package 完全相同；不是整支 merge
  E20，也不帶入 E21–E23 的 P／N／Slothy 候選。
- 正式 branch 的更新採 fast-forward，另保留證據文件 commit。

## 原生 SUPERCOP 八輪比較

預先固定8輪，順序 B→E／E→B 交替，三項 KEM 都測量。
每輪取 SUPERCOP 三個 emitted cycles 值的中位數。

| Operation | Production round-medians 中位數 | E20 round-medians 中位數 | 配對中位數差 E−B | 配對百分比 |
|---|---:|---:|---:|---:|
| Keygen | 36322 | 36347.5 | +34 | +0.0936% |
| Encap | 37122 | 37112 | −7.5 | −0.0202% |
| Decap | 32506 | 32512.5 | +14.5 | +0.0446% |

配對差不是兩個獨立中位數相減。Keygen 7/8輪偏慢，這個小成本不能抹成
「完全沒退步」，但仍低於事先宣布的0.3%工程容忍範圍。Encap、Decap
亦未越過門檻；所以作為清理／contract 修正版接受，而非新 speed record。

配對差值按輪次：

- Keygen：[14,9,-35,71,45,23,52,58]。
- Encap：[79,11,-26,-112,-35,20,-61,39]。
- Decap：[48,17,26,-10,12,-3,99,-9]。

Pi `pi@100.99.191.9`，core3，Linux6.18.33+rpt-rpi-2712，GCC14.2。
實際 `run-ntruplus768-aarch64.sh`／`do-part` 在獨立 physical-copy staging
執行；未改原始 `/home/pi/supercop-20260627`。選用 compiler／classifications
見 results.json；SUPERCOP flags 包含 native O3/fwrapv/fPIC/fPIE/gdwarf-4/Wall。
所有記錄的前後 throttle 都0x0。沒有新增 Official／KPQC 比較，因此不能
由本輪宣稱相對 Official 的新百分比。

## Correctness、link 與清除覆蓋

- B/E Mac `make check` 通過。
- B/E Pi `make check` 通過：release/manifest、KEM、required ABI、
  canonical/failure、小輸入NTT、zeroization、KAT；E20新增 support oracle。
- 匯出 leaf 再跑 req/rsp bit-exact KAT；export manifest 對來源SHA逐項核對。
- 匯出 leaf 的三個公開 KEM ABI sentinel masks 都為0。
- 已套用至 promotion worktree 的 package 再跑一次 Mac `make check` 通過。
- KAT response SHA256：`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`。

兩版 clear interposition trace 完全一致（相同 fixture）：

| Operation | Calls | Bytes |
|---|---:|---:|
| Keygen | 20 | 13352 |
| Encap | 16 | 6410 |
| valid／invalid Decap | 9 | 10930 |
| noncanonical Decap | 2 | 8608 |
| invalid-PK Encap | 2 | 128 |

这验证保留的对象清除与coverage，不是 whole-machine remanence proof。
Keygen retry-dependent counts 不应推广为所有输入固定不变。
linked KAT executable text：124991→117543，减少7448bytes；含测试 harness
和tables，不当作热代码 footprint，也不当作动态instructions节省。

## Promotion 内容

保留已正式纳入的G5、D1、checked unpack；`pack.S`与旧正式版一致。
改动是：poly_sub/add.S、util.h/secure_clear 命名；crepmod3先q-center
再mod3；移除未调用entry/private tables；legacy verification移到测试closure。
crepmod3的语义改动不是纯rename：q mod3=1，在中心区间外可能有差异；
E20 exhaustive support oracle覆盖[-3456,3456]和alias/out-of-place。
不宣称之前存在已证实的valid-ciphertext漏洞。

## Branch／worktree 整理

使用者指定的12支branches：全部创建 `archive/gt768/20260908/<suffix>`
annotated tags，逐个验证target SHA；保留所有原branch名称。
其中11个存在worktree，检查无tracked修改／untracked文件后移除。
被忽略内容只允许已知 `.build`、`build`、`__pycache__` 目录。
`consumer-native-pm` 原先没有worktree，因此仅建立tag。
精确清单在 archive-inventory.json。

E20在保存本轮记录并promotion后另外建立archive tag再移除worktree；
临时promotion worktree也在正式fast-forward后移除。分支／commits均保留。
已有 `aarch64-production` 工作目录继续使用：
`/Users/chenpinhao/ntruplus-aarch64-production`。
其中用户原有未追踪 `Additional_Implementation/aarch64/benchmark/` 不动。
其他768实验、864/1152工作目录、远端实验目录均不在此次清理范围。

删除的是工作副本和生成物；原始码、proof、summaries可从tag/commit恢复。
原始未提交benchmark samples删除后不能由Git恢复，只能重新运行生成。

## Reproduction／保存

prepare.py 从旧正式commit创建B，对当前E20 package创建E并跑Mac checks。
pi_gate.py 重用固定 `/home/pi/gt768-four-gates-20260907-e09/common.py` helper，
源码／leaf hashes、flags、环境、轮次摘要保留在preflight.json/results.json。
本轮远端目录 `/home/pi/gt768-e20-promotion-20260908-e24`，raw logs在.build。
本机原始数据在清理前亦置于gitignored.build；保留scripts而非整份source copies。

本轮之后768先收尾；新的性能工作需独立假设与新gate。
