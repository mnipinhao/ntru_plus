#!/usr/bin/env python3
"""Static source-coverage gate for the production P0 zeroization policy."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(relative: str, needles: tuple[str, ...]) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"{relative}: missing {needle!r}")


require(
    "internal/secure_clear.h",
    (
        "static inline void gt_secure_clear",
        "GT_SECURE_CLEAR_AUDIT_HOOK",
        "volatile uint8_t *cursor",
    ),
)
require(
    "kem.c",
    (
        "if (!genf_derand(&f, &finv, coins))",
        "if (!geng_derand(&g, &ginv, coins))",
        "gt_secure_clear(&f, sizeof f);",
        "gt_secure_clear(&finv, sizeof finv);",
        "gt_secure_clear(&g, sizeof g);",
        "gt_secure_clear(&ginv, sizeof ginv);",
        "poly forward;",
        "poly m_then_r;",
        "gt_decap_checked_ct_f_basemul_scale64(",
        "gt_secure_clear(&scratch, sizeof scratch);",
    ),
)
require(
    "internal/keygen.c",
    (
        "gt_secure_clear(numerator, sizeof numerator);",
        "gt_secure_clear(den, sizeof den);",
    ),
)
require(
    "asm/internal/keygen_baseinv_prepare.S",
    tuple(
        [f"movi v{register}.16b, #0" for register in range(0, 8)]
        + [f"ins v{register}.d[1], xzr" for register in range(8, 16)]
        + [f"movi v{register}.16b, #0" for register in range(16, 32)]
    ),
)
require(
    "symmetric.c",
    (
        "gt_secure_clear(data, sizeof data);",
        "HASH_F_INBYTES",
        "HASH_G_INBYTES",
        "HASH_H_INBYTES",
    ),
)
require(
    "NO_CE/fips202.c",
    (
        "gt_secure_clear(state->ctx, PQC_SHAKECTX_BYTES);",
        "gt_secure_clear(state->ctx, PQC_SHAKEINCCTX_BYTES);",
        "state->ctx = NULL;",
        "gt_secure_clear(t, sizeof t);",
        "gt_secure_clear(s, sizeof s);",
    ),
)
require("asm/ntt.S", ("mov x10, #106", ".Lp0b_clear_1696:"))
require("asm/invntt.S", ("mov x17, #134", ".Lp0b_invntt_clear:"))
require(
    "asm/internal/keygen_baseinv_tree.S",
    ("mov x10, #21", "Lbpq_tree_clear:"),
)
require(
    "asm/internal/keygen_baseinv_finish.S",
    ("erase secret vector temporaries", "movi v31.16b, #0"),
)
require(
    "asm/internal/fqinv.S",
    ("v0 is the return value", "movi v21.16b, #0"),
)
require(
    "asm/kem_api.S",
    (
        "clear every caller-saved lane",
        "mov x17, xzr",
        "movi v31.16b, #0",
        "ins v15.d[1], xzr",
    ),
)
for relative in (
    "asm/base.S",
    "asm/pack.S",
    "asm/internal/keygen_pack.S",
    "asm/internal/encap_muladd.S",
    "asm/internal/decap_verify.S",
    "asm/internal/unpack.S",
    "asm/internal/decap_packed64.S",
    "asm/internal/decap_base.S",
    "asm/internal/decap_ntt.S",
    "asm/internal/decap_pack.S",
):
    require(relative, ("erase the complete handwritten spill frame",))
require(
    "asm/internal/decap_forward.S",
    ("erase the complete 1696-byte handwritten frame",),
)

print("P0 production zeroization source coverage: ok")
