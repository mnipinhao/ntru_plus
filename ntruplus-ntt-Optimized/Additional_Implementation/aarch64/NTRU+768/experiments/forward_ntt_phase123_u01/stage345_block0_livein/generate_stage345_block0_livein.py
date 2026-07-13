#!/usr/bin/env python3
"""Build a symbolic Stage345 block0 pressure-test candidate.

The candidate starts from the exact production block0 Slothy region and removes
only the eight row-scratch loads for Q0..Q7.  Those values become live-in vector
symbols, which models a future Stage12->Stage345 fused producer without changing
the production arithmetic or scatter DAG.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "experiments/forward_ntt_phase123_u01/stage345_block0_livein/baseline-stage345-block0.s"
OUTPUT = ROOT / "experiments/forward_ntt_phase123_u01/stage345_block0_livein/candidate-stage345-block0-livein.sym.S"

START_OLD = "_gt_ntt32_batch8_ct_stage345_block0_slothy_start:"
END_OLD = "_gt_ntt32_batch8_ct_stage345_block0_slothy_end:"
START_NEW = "slothy_start_stage345_block0_livein:"
END_NEW = "slothy_end_stage345_block0_livein:"

ROW_LOAD_TO_SYMBOL = {
    0: "b0_q0",
    16: "b0_q1",
    32: "b0_q2",
    48: "b0_q3",
    64: "b0_q4",
    80: "b0_q5",
    96: "b0_q6",
    112: "b0_q7",
}

LOAD_RE = re.compile(r"^\s*ldr\s+q(?P<reg>\d+),\s*\[x4,\s*#(?P<off>\d+)\]", re.IGNORECASE)
INSTR_RE = re.compile(r"^\s*(?P<mnemonic>[A-Za-z][A-Za-z0-9_.]*)\b")
TOKEN_RE = re.compile(
    r"\b(?P<kind>[qvd])(?P<reg>3[01]|[12][0-9]|[0-9])(?P<suffix>(?:\.[0-9]+[bhsdq])?(?:\.[bhsdq]\[[0-9]\])?)",
    re.IGNORECASE,
)

DEST_DEFINES = {
    "add",
    "sub",
    "mul",
    "mla",
    "mls",
    "smull",
    "smull2",
    "umull",
    "umull2",
    "smlal",
    "smlal2",
    "umlal",
    "umlal2",
    "sqrdmulh",
    "sqdmulh",
    "sqrshrn",
    "sqrshrn2",
    "shrn",
    "shrn2",
    "xtn",
    "xtn2",
    "sqxtn",
    "sqxtn2",
    "and",
    "orr",
    "eor",
    "bic",
    "movi",
    "dup",
    "ext",
    "zip1",
    "zip2",
    "uzp1",
    "uzp2",
    "trn1",
    "trn2",
    "sshr",
    "ushr",
    "sli",
    "sri",
    "rev64",
    "srshr",
}
DEST_READWRITE = {
    "mla",
    "mls",
    "smlal",
    "smlal2",
    "umlal",
    "umlal2",
    "sqxtn2",
    "xtn2",
    "shrn2",
    "sqrshrn2",
}


class Symbolizer:
    def __init__(self) -> None:
        self.reg_to_symbol: dict[int, str] = {}
        self.temp_idx = 0
        self.twiddle_idx = 0

    def fresh(self, prefix: str = "t") -> str:
        name = f"{prefix}{self.temp_idx:03d}"
        self.temp_idx += 1
        return name

    def fresh_twiddle(self) -> str:
        name = f"tw{self.twiddle_idx}"
        self.twiddle_idx += 1
        return name

    @staticmethod
    def split_comment(line: str) -> tuple[str, str]:
        if "//" not in line:
            return line.rstrip(), ""
        code, comment = line.split("//", 1)
        return code.rstrip(), comment.rstrip()

    @staticmethod
    def first_vector_token(code: str) -> re.Match[str] | None:
        return TOKEN_RE.search(code)

    @staticmethod
    def mnemonic(code: str) -> str:
        match = INSTR_RE.match(code)
        return match.group("mnemonic").lower() if match else ""

    def symbol_for_use(self, reg: int, snapshot: dict[int, str]) -> str:
        if reg not in snapshot:
            sym = self.fresh("uninit")
            snapshot[reg] = sym
            self.reg_to_symbol.setdefault(reg, sym)
        return snapshot[reg]

    def dest_symbol(self, reg: int, mnemonic: str, snapshot: dict[int, str]) -> tuple[str, bool]:
        if mnemonic.startswith("ldr"):
            return self.fresh_twiddle(), True
        if mnemonic in DEST_READWRITE:
            return self.symbol_for_use(reg, snapshot), False
        return self.fresh(), True

    def rewrite_vector_tokens(self, code: str, dest_match: re.Match[str] | None, mnemonic: str) -> str:
        snapshot = dict(self.reg_to_symbol)
        dest_span = dest_match.span() if dest_match else None
        dest_reg = int(dest_match.group("reg")) if dest_match else None
        dest_sym = None
        updates_dest = False
        if dest_match and dest_reg != 0:
            dest_sym, updates_dest = self.dest_symbol(dest_reg, mnemonic, snapshot)

        def repl(match: re.Match[str]) -> str:
            reg = int(match.group("reg"))
            kind = match.group("kind").lower()
            suffix = match.group("suffix").lower()
            if reg == 0:
                return match.group(0)
            is_dest = dest_span == match.span()
            sym = dest_sym if is_dest and dest_sym is not None else self.symbol_for_use(reg, snapshot)
            if kind == "q":
                return f"Q<{sym}>"
            if kind == "d":
                return f"D<{sym}>"
            return f"V<{sym}>{suffix}"

        rewritten = TOKEN_RE.sub(repl, code)
        if dest_reg is not None and dest_sym is not None and updates_dest:
            self.reg_to_symbol[dest_reg] = dest_sym
        return rewritten

    def convert_line(self, line: str) -> list[str]:
        stripped = line.strip()
        if not stripped:
            return [""]
        if stripped == START_OLD:
            return [START_NEW]
        if stripped == END_OLD:
            return [END_NEW]
        if stripped.startswith("//"):
            return []

        code, comment = self.split_comment(line)
        if not code.strip():
            return []

        row_load = LOAD_RE.match(code)
        if row_load:
            offset = int(row_load.group("off"))
            reg = int(row_load.group("reg"))
            if offset in ROW_LOAD_TO_SYMBOL:
                sym = ROW_LOAD_TO_SYMBOL[offset]
                self.reg_to_symbol[reg] = sym
                return [f"        // live-in V<{sym}>.8h replaces {code.strip()}"]

        mnemonic = self.mnemonic(code)
        dest_match = None
        if mnemonic.startswith("ldr") or mnemonic in DEST_DEFINES:
            dest_match = self.first_vector_token(code)

        rewritten = self.rewrite_vector_tokens(code, dest_match, mnemonic)
        if comment:
            return [f"{rewritten}    // {comment.strip()}"]
        return [rewritten]


def main() -> int:
    symbolizer = Symbolizer()
    baseline_lines = BASELINE.read_text().splitlines()
    body: list[str] = []
    for line in baseline_lines:
        body.extend(symbolizer.convert_line(line))

    srshr_defs: list[str] = []
    for line in body:
        stripped = line.strip()
        if not stripped.lower().startswith("srshr "):
            continue
        match = re.search(r"V<([A-Za-z_][A-Za-z0-9_]*)>", stripped)
        if match:
            srshr_defs.append(match.group(1))

    preamble = [
        "/*",
        " * Symbolic pressure-test candidate for NTT32 Stage345 block0.",
        " *",
        " * Live-in: V<b0_q0>..V<b0_q7> are the exact Stage12 out0 Q0..Q7",
        " * values that production currently reloads from row scratch x4+0..112.",
        " * Live-in: x10=scatter pointer, x12=Stage345 twiddle pointer,",
        " * x14=scatter wrap bound, sp=production frame, v0=fixed q/reduction constants.",
        " * Live-out: x10/x12 pointer state and the same public scatter d stores as",
        " * production Stage345 block0.",
        " * Range: b0_q0..b0_q7 match production post-Stage12 row scratch bounds;",
        " * output representatives match production Stage345 block0 stores.",
        " * Reserved physical registers: x18-x30 are reserved; v0 is the only fixed",
        " * physical vector register.  All other vector values are symbolic.",
        " * Static-check note: srshr-defined outputs are "
        + ", ".join(f"V<{name}>" for name in srshr_defs)
        + "; these are not extra live-ins.",
        " */",
        "",
    ]
    OUTPUT.write_text("\n".join(preamble + body) + "\n")
    print(f"wrote {OUTPUT}")
    print(f"twiddle_symbols={symbolizer.twiddle_idx} temp_symbols={symbolizer.temp_idx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
