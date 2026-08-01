# P1-C：Forward NTT lazy reduction 的逐 store 硬門檻證明

日期：2026-07-29

## 結論

```text
ASM_GENERATION_ALLOWED=false
decision=proof_failed_do_not_generate_assembly
```

因此 P1-C **沒有產生候選 ASM**。這不是尚未完成，而是硬門檻正確地
阻止了一個目前不能證明安全的實作。

## 綁定的 active source

證明腳本以 SHA-256 綁定下列兩份來源；來源若有任何改動，腳本會以
infrastructure failure 停止，而不是沿用過期結論。

```text
ntruplus-GT-Production/.../NTRU+768/asm/ntt.S
  6f874aa58557ba12ed20f36bc3e3bb8c8e642c2f1d70c17bed13453510ecacbc

ntruplus-ntt-Optimized/.../NTRU+768/asm/gt/ntt/
  ntt32_batch8_to_blockmajor.n1.opt.S
  3ff85cc9c56b82d14f6b7bd5dca1173e5fcc22faa8dd8bba68c0c65e5164a355
```

腳本也會確認三個 caller 仍然存在於目前的 `kem.c`，以及 CBD、SOTP、
`poly_triple`、`poly_crepmod3` 的 source marker 未消失。

## 先修正一個舊估算

flattened `asm/ntt.S` 內共有 192 條 final-reduction chain，但那是兩個
互斥 suffix 的總和：

```text
poly_ntt generic block-major suffix       96
gt_keygen_poly_ntt_to_cq direct-CQ suffix 96
```

一次呼叫只會執行其中一個 suffix，所以正確的 per-call 數量是：

```text
3 rows × 4 blocks × 8 output vectors = 96 chains
96 × (sqdmulh + srshr + mls) = 288 vector instructions
```

先前 Wave 4 文件中的「192 chains / 576 instructions per call」把兩個
互斥 endpoint 算在同一次呼叫，已一併修正。

## 算術證明

腳本直接從 active `ntt.S` 取出 40 組 `(twiddle, reciprocal)` lane，
對每組窮舉全部 65,536 個 signed-16 input，共檢查：

```text
40 × 65,536 = 2,621,440 cases
```

模擬的指令語意為：

```text
quotient = SQrdMulh(x, reciprocal)
product  = MUL.s16(x, twiddle)
result   = MLS.s16(product, quotient, q)
```

窮舉得到：

```text
fqmul output = [-3436, 3436]
```

GT frontend 的 active modular source contract 給出 raw 3-point DFT：

```text
[-3(q-1), 3(q-1)] = [-10368, 10368]
```

以每一層最壞情況 `a ± fqmul(b,w)` 傳播，得到：

| 邊界 | signed-16 interval |
|---|---:|
| raw GT DFT | `[-10368, 10368]` |
| lazy CT stage 1 | `[-13804, 13804]` |
| lazy CT stage 2 | `[-17240, 17240]` |
| lazy CT stage 3 | `[-20676, 20676]` |
| lazy CT stage 4 | `[-24112, 24112]` |
| lazy CT stage 5 / final reduction 前 | `[-27548, 27548]` |

所有 NTT 內部加減仍在 signed-16 範圍內；這比舊文件只寫
`[-32767,32767]` 更緊。但它仍不足以通過 downstream contract。

## 逐 caller、逐 store 結果

JSON 逐一列出：

```text
3 callers × 96 logical 8-lane stores = 288 records
288 × 8 = 2,304 lane obligations
```

每筆 record 包含 caller、endpoint、row、block、vector、active source
reduction line、producer bound，以及 machine / semantic / implementation
三個 gate。

| caller | final reduction 前 | machine gate | semantic gate | 可實作？ |
|---|---:|---|---|---|
| `keygen_g` | `[-27548,27548]` | **失敗**：baseinv `vneg` + `vshl #1` 需要約 `[-16383,16383]` | 失敗 | 否 |
| `encap_m` | `[-27548,27548]` | 通過：int16 addend 會 widening | **失敗**：Q31 byte-contract 尚未證明 wider addend | 否 |
| `decap_m1` | `[-27548,27548]` | 通過：仍在 `poly_sub` no-wrap 約 `[-31039,31039]` 內 | **失敗**：verify basemul 尚未證明 wider `c_minus_m2` | 否 |

## 重跑與硬門檻

一般檢查會更新 deterministic JSON，預期 exit 0：

```sh
make -C ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/ntt_loose_contract/range_proof check
```

未來的 ASM generator 必須先執行 `gate`。目前預期 exit 1：

```sh
make -C ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/ntt_loose_contract/range_proof gate
```

只有 `ASM_GENERATION_ALLOWED=true` 時才允許新增 reduction-omitting ASM。
