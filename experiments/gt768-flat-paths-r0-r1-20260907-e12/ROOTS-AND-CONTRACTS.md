# R0：roots、active paths 與必須保留的 contract

## 1. 三組 roots 不可混為一談

### KEM release roots

`crypto_kem_keypair`、`crypto_kem_enc`、`crypto_kem_dec` 在 `kem_api.S`，各自呼叫
`crypto_kem_*_internal`（kem.c）。這是使用者／SUPERCOP 的外部 ABI。

### poly.h 宣告／維護介面 roots

`poly_tobytes`、`poly_frombytes`、`poly_cbd1`、`poly_sotp_encode`、`poly_sotp_decode`、
`poly_basemul`、`poly_invntt`、`poly_basemul_add`、`poly_sub`、`poly_triple`、
`poly_crepmod3`。

有宣告不代表每個 leaf 都獨立 AAPCS64 callable。既有 custom-ABI 限制仍保留，
不能因平鋪或名稱看似 public 就擴大對外支援承諾。

### Validation roots

`test/test_abi.c` 的 sentinel roots 包含上述維護介面，以及 Keygen CQ、Decap、
舊 QSoA verification helpers。`test/test_ntt_small.c` 另外以 generic loose NTT
作 differential oracle。`test/test_canonical.c` 保留 canonical pack/unpack gate。
`kat/PQCgenKAT_kem.c` 以三個 KEM roots 與獨立 KAT RNG 驗證 canonical wire bytes。

因此 generic inverse、reference forward、old QSoA wrappers 或 alias 沒出現在
kem.c，不能直接判為可刪。R1 沒有刪除任何 root 或 table。

## 2. 實際 KEM data flow（不是以檔案名稱猜測）

### Keygen

```text
randombytes → shake256 → poly_cbd1 → poly_triple (+ f[0] += 1)
  → gt_keygen_poly_ntt_to_cq
  → gt_keygen_baseinv_cq_to_cq_scaled_r（可能重試）
      → gt_keygen_baseinv_cq_prepare
      → gt_keygen_baseinv_hier_k8 → gt_fqinv15_asm
      → gt_keygen_baseinv_cq_finish
  → gt_keygen_basemul_cq_cq_to_cq_scaled_r（兩次，產生 h/hinv）
  → gt_keygen_tobytes_cq → canonical pk/sk + hash_f
```

`keygen.c` 使用 `gt_keygen_bpq_lambda8`（keygen_lambda.c）和檔案內常數。
baseinv failure 清空 out；numerator、denominator 的 C 清除不變。

### Encap

```text
pk → poly_frombytes（完整 checked decode，GT block-major）
hash_f / hash_h → poly_cbd1 → r
  → gt_internal_poly_ntt_encap_small(r,r)
  → gt_internal_poly_tobytes_from_loose(ct,r)
  → hash_g(ct,ct) → poly_sotp_encode → m
  → gt_internal_poly_ntt_encap_small(m,m)
  → poly_basemul_add(m,h,r,m)
  → poly_tobytes(ct,m)
```

這裡 `ct` 在中途作為 r 的 serialization/hash buffer，最後才覆寫為 ciphertext。
`poly_basemul_add` 必須保留 `out == m == c` 的 exact alias，以及立即 pack 的
byte-consumer contract；不能將它當成一般 centered-output product。

### Decap

```text
packed ct/f → gt_decap_checked_ct_f_basemul_scale64
             （保留 decoded ct，不 materialize f，產生 scaled first product）
packed hinv → gt_decap_poly_frombytes
first product → gt_decap_poly_invntt_scale（in-place）→ poly_crepmod3
  → gt_decap_poly_ntt → gt_decap_poly_sub
  → gt_decap_poly_basemul（D1）→ gt_decap_poly_tobytes
  → hash_g → poly_sotp_decode → hash_h → poly_cbd1
  → gt_decap_poly_ntt → gt_decap_poly_tobytes → verify
```

實際 inverse 在 **decap_ntt.S**，不是頂層 **invntt.S**。
實際 Decap Forward 在 **decap_forward.S**，不是 decap_ntt.S 的 reference Forward。
`poly.h` 仍有歷史上稱 generic basemul/invntt 為 production decapsulation pair 的
註解；這輪不改 contract 內容，以 kem.c 的 actual callers 為準。

## 3. Representation／range／alias 清單

所有 poly storage 為 768 個 signed int16（1536 bytes、16-byte aligned）；相同
storage size 不代表可互換 layout／scale。q=3457，wire polynomial 為 1152 bytes。

| Endpoint family | representation／scale | 本輪保留的限制 |
|---|---|---|
| generic loose Forward | GT block-major，mod-q congruent | header bound `[-27548,27548]`；保留作 oracle |
| Encap-small Forward | 與 generic loose bit-exact | input 每係數 `[-2,2]`；支持 exact in-place；不擴成 Keygen arbitrary input |
| loose pack | GT block-major → canonical bytes | 接受全部 signed-16 representatives；不改 public reduced fast path |
| checked poly_frombytes | canonical 12-bit decode → GT block-major | 任一值 ≥q 回傳 1；valid/invalid 都寫完整 output |
| Encap basemul-add | quartic direct32／Q31；立即 pack | C=621199；不是 general centered-output contract；保留 out==c |
| Keygen NTT / baseinv / basemul | typed CQ，scaled-r operand contract | 保留 `_scaled_r` 命名語意、failure 與 CQ lambda order |
| Decap packed64 first product | packed ct/f → Decap layout、scaled R^-1 | inverse final constants 配對；保留 decoded ct |
| Decap inverse | Decap scaled first product → coefficients | 單指標 in-place；不可換成 generic inverse |
| Decap D1 basemul | Decap layout，Q31 normal-domain finalizer | 保留原輸入 bound／reduce constants／pack closure，不宣稱更寬輸入可用 |
| generic basemul/invntt | R^-1 product / matching inverse | 和 D1 normal-domain endpoint 不可只靠同名合併 |
| poly_triple / poly_crepmod3 | GT 雙指標介面 | 不可直接換 Official 單指標 header；本輪保留 alias 實際呼叫 |

本輪是既有 contract 盤點及 binary-equivalence gate，不是重新做 symbolic bound proof。
沒有對 partial overlap、任意 wider input、外部 library ABI 做新承諾。

## 4. ABI／aliases／tables

`kem_api.S` 每個 wrapper 建立 80-byte frame，保存 x29/x30 與 d8–d15，再呼叫 C
internal body；回傳值與 restore 不變。required sentinel mask=0；已知 private
custom mask=0x3fc00 不變。某些 support leaves 不能單獨供外部 AAPCS64 caller 使用。

Linux generic `poly_invntt` 為 weak alias，同地址另有 `gt_block_major_poly_invntt`；
Apple/Linux 的前綴 `_` aliases 也保留。不要在 R2 把 weak/global binding 當純字串
替換。ntt/decap_forward 的多重 alias 和 end labels 都在 inventory 中。

tables 包括 C 的 `gt_rowbitrev_lambda`、`gt_keygen_bpq_lambda8`、Keygen static
constants、SHAKE round constants，以及 Forward/Inverse/Decap/pack 各 owner 的
inline 或 rodata tables。完整 object data list、local label reference index 和
relocation graph 見 INVENTORY。`t` 類型可能是 text 內常數，不一定是函式。
`.rodata.*unused_twist` 這類名字也不是刪除依據；本輪所有 tables 原樣保留。

## 5. Build／tests／benchmark baseline

相同 KEM_SOURCES 順序；CFLAGS：

```text
-O3 -fomit-frame-pointer -std=c99 -Wall -Wextra -Wpedantic
-ffunction-sections -fdata-sections
```

只有 CPPFLAGS 由 `-I. -Iinternal` 改為 `-I.`，並依原本實際 include target 改引用。
Linux `--gc-sections`、Mac `-dead_strip` 均保留；沒有 LTO、march 或排程新設定。

Mac／Pi `make check` 包含 release manifest、KEM、ABI、canonical、small、
zeroization、KAT。Pi 額外保留六路徑 cleanup trace 的 exact comparison。

Official comparison baseline 仍是 Pi `/home/pi/supercop-20260627/crypto_kem/ntruplus768/aarch64`，
不是 Good-Thomas。Official 是來源 snapshot，以 e10 record 的 source/export hashes
識別，不虛構其 Git revision。本輪沒有修改／重新匯出 Official。

正式 champion 的上一輪 SUPERCOP-style 測量證據在
`experiments/gt768-production-d1-small-official-policy-20260907-e10/gate-summary.json`；
前次記錄 medians GT 36,300 / 37,309 / 32,502 cycles，Official 38,417 / 38,584 /
33,530（Keygen / Encap / Decap）。這些是 **e10 的歷史數據，不是 e12 實測**。
原 wrapper／export／host／flags 由該 gate record 重現，不混用本輪 make-check timing。

本輪不需要 Slothy 或新 SUPERCOP timing；若之後更改 name/order/merge，仍需重新
檢查 link layout，而不能只拿現在的 path-only 結論直接外推。
