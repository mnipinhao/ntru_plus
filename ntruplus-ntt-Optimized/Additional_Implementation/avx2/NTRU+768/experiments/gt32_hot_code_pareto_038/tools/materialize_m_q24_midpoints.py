#!/usr/bin/env python3
"""Emit equal-size M-Q24 midpoint probes without editing GT Clean."""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ROOT = EXPERIMENT.parent
BASE = ROOT / "gt32_compact_q24_037/generated/pack_037.s"
OUT = EXPERIMENT / "generated/m_q24_midpoints"
SYMBOL = "gt32_q24_encode_soa_lazy10788_compact_037a_asm"

GROUPS = [
    ("A", 0, "%ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75", 0),
    ("A", 128, "%ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75", 0),
    ("B", 1152, "%ymm4,%xmm4,228,%ymm5,%xmm5,228,%ymm6,%xmm6,228,%ymm7,%xmm7,228", 0),
    ("C", 1024, "%ymm6,%xmm6,228,%ymm7,%xmm7,228,%ymm5,%xmm5,228,%ymm4,%xmm4,30", 0),
    ("D", 512, "%ymm5,%xmm5,30,%ymm4,%xmm4,177,%ymm7,%xmm7,30,%ymm6,%xmm6,177", 0),
    ("D", 640, "%ymm5,%xmm5,30,%ymm4,%xmm4,177,%ymm7,%xmm7,30,%ymm6,%xmm6,177", 0),
    ("E", 1408, "%ymm6,%xmm6,30,%ymm7,%xmm7,30,%ymm5,%xmm5,30,%ymm4,%xmm4,177", 0),
    ("D", 1280, "%ymm5,%xmm5,30,%ymm4,%xmm4,177,%ymm7,%xmm7,30,%ymm6,%xmm6,177", 0),
    ("A", 768, "%ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75", 0),
    ("A", 896, "%ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75", 0),
    ("B", 384, "%ymm4,%xmm4,228,%ymm5,%xmm5,228,%ymm6,%xmm6,228,%ymm7,%xmm7,228", 0),
    ("F", 256, "%ymm6,%xmm6,228,%ymm7,%xmm7,228,%ymm5,%xmm5,228,%ymm4,%xmm4,30", 1),
]


def replace_function(text: str, replacement: str) -> str:
    start = text.index(f"{SYMBOL}:\n")
    size_line = f" .size {SYMBOL},.-{SYMBOL}"
    end = text.index(size_line, start) + len(size_line)
    return text[:start] + replacement + text[end:]


def inline_macro() -> str:
    return r""".macro Q24_038_INLINE_BLOCK input,a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
 vmovdqu \input+0(%rsi), %ymm0
 vmovdqu \input+32(%rsi), %ymm1
 vmovdqu \input+64(%rsi), %ymm2
 vmovdqu \input+96(%rsi), %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
 Q24_037_PACK4 \a,\ax,\ap,\b,\bx,\bp,\c,\cx,\cp,\d,\dx,\dp,\safe
.endm
"""


def candidate(shared: set[str], tag: str) -> str:
    lines = [inline_macro(), f"{SYMBOL}:", f".L038_{tag}_begin:",
             " vmovdqa .Lq24_q(%rip), %ymm15",
             " vmovdqa .Lq24_v(%rip), %ymm13"]
    definitions: dict[str, tuple[str, int]] = {}
    for index, (shape, source, arguments, safe) in enumerate(GROUPS):
        args = f"{arguments},{safe}"
        if shape in shared:
            lines += [f" leaq {source}(%rsi), %rax", f" call .L038_{tag}_{shape.lower()}"]
            definitions.setdefault(shape, (arguments, safe))
        else:
            lines.append(f" Q24_038_INLINE_BLOCK {source},{args}")
        if index != len(GROUPS) - 1:
            lines.append(" addq $96, %rdi")
    lines += [" vzeroupper", " ret"]
    for shape, (arguments, safe) in definitions.items():
        lines += [f".L038_{tag}_{shape.lower()}:",
                  f" Q24_037_BLOCK {arguments},{safe}", " ret"]
    lines += [f" .org .L038_{tag}_begin + 5120, 0x90",
              f" .size {SYMBOL},.-{SYMBOL}"]
    return "\n".join(lines)


def main() -> int:
    text = BASE.read_text()
    OUT.mkdir(parents=True, exist_ok=True)
    variants = {
        "share_a": {"A"},
        "share_ad": {"A", "D"},
        "share_adb": {"A", "D", "B"},
    }
    for name, shared in variants.items():
        rendered = replace_function(text, candidate(shared, name))
        (OUT / f"pack_{name}.s").write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
