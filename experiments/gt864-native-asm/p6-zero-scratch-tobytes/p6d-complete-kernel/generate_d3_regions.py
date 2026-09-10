#!/usr/bin/env python3
"""Generate the P6-D3 full-ToBytes semantic allocation regions."""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = [0, 3, 6, 1, 4, 7, 2, 5, 8]
MERGE = 368


def loads(keys: list[str]) -> list[str]:
    return [f"ldr Q<{key}>, [x3, #{16*i}]" for i, key in enumerate(keys)]


def stores(keys: list[str]) -> list[str]:
    return [f"str Q<{key}>, [x4, #{16*i}]" for i, key in enumerate(keys)]


def transpose(prefix: str, base: int) -> list[str]:
    out = []
    for j in range(8):
        off = base + (8-j)*48
        out.append(f"ldr Q<{prefix}j{j}>, [x29, #{off}]")
        if j: out.append(f"ext V<{prefix}j{j}>.16b, V<{prefix}j{j}>.16b, V<{prefix}j{j}>.16b, #{16-2*j}")
    out.append(f"ldr Q<{prefix}ninth>, [x29, #{base}]")
    for j in range(0, 8, 2):
        out += [f"trn1 V<{prefix}u{j}>.8h, V<{prefix}j{j}>.8h, V<{prefix}j{j+1}>.8h",
                f"trn2 V<{prefix}u{j+1}>.8h, V<{prefix}j{j}>.8h, V<{prefix}j{j+1}>.8h"]
    for j in range(2):
        out += [f"trn1 V<{prefix}z{j}>.4s, V<{prefix}u{j}>.4s, V<{prefix}u{j+2}>.4s",
                f"trn2 V<{prefix}z{j+2}>.4s, V<{prefix}u{j}>.4s, V<{prefix}u{j+2}>.4s",
                f"trn1 V<{prefix}z{j+4}>.4s, V<{prefix}u{j+4}>.4s, V<{prefix}u{j+6}>.4s",
                f"trn2 V<{prefix}z{j+6}>.4s, V<{prefix}u{j+4}>.4s, V<{prefix}u{j+6}>.4s"]
    for j in range(4):
        out += [f"trn1 V<{prefix}t{j}>.2d, V<{prefix}z{j}>.2d, V<{prefix}z{j+4}>.2d",
                f"trn2 V<{prefix}t{j+4}>.2d, V<{prefix}z{j}>.2d, V<{prefix}z{j+4}>.2d"]
    return out


def route_row(prefix: str, row: int) -> list[str]:
    name = f"{prefix}{row}"
    if row == 0:
        out = [f"orr V<{name}>.16b, V<{prefix}t0>.16b, V<{prefix}t0>.16b",
               f"ins V<{name}>.h[0], V<{prefix}ninth>.h[0]"]
    elif row < 7:
        out = [f"ldr Q<{prefix}mask{row}>, [x30, #{16*(row-1)}]",
               f"and V<{name}>.16b, V<{prefix}t{row-1}>.16b, V<{prefix}mask{row}>.16b",
               f"bic V<{prefix}other{row}>.16b, V<{prefix}t{row}>.16b, V<{prefix}mask{row}>.16b",
               f"orr V<{name}>.16b, V<{name}>.16b, V<{prefix}other{row}>.16b",
               f"ins V<{name}>.h[{row}], V<{prefix}ninth>.h[{row}]"]
    elif row == 7:
        out = [f"orr V<{name}>.16b, V<{prefix}t6>.16b, V<{prefix}t6>.16b",
               f"ins V<{name}>.h[7], V<{prefix}ninth>.h[7]"]
    else:
        out = [f"orr V<{name}>.16b, V<{prefix}t7>.16b, V<{prefix}t7>.16b"]
    out += [f"ldr Q<{prefix}idx{row}>, [x30, #{160+16*row}]",
            f"tbl V<{name}>.16b, {{V<{name}>.16b}}, V<{prefix}idx{row}>.16b"]
    return out


def route_region(name: str, held: list[str], prefix: str, base: int) -> tuple[list[str], list[str]]:
    out = loads(held) + transpose(prefix, base)
    for row in range(9): out += route_row(prefix, row)
    result = held + [f"{prefix}{i}" for i in range(9)]
    out += stores(result)
    return out, result


def normalize(v: str, suffix: str) -> list[str]:
    return [f"sqrdmulh V<quot{suffix}>.8h, V<{v}>.8h, V<recip>.8h",
            f"mls V<{v}>.8h, V<quot{suffix}>.8h, V<modq>.8h",
            f"sshr V<quot{suffix}>.8h, V<{v}>.8h, #15",
            f"and V<quot{suffix}>.16b, V<quot{suffix}>.16b, V<modq>.16b",
            f"add V<{v}>.8h, V<{v}>.8h, V<quot{suffix}>.8h"]


def pack_region(inputs: list[str]) -> tuple[list[str], list[str]]:
    held, arows = inputs[:13], inputs[13:]
    out = loads(inputs)
    out += ["ldr Q<modq>, [x30, #336]", "ldr Q<recip>, [x30, #352]"]
    for r, a in enumerate(arows):
        out += normalize(a, f"a{r}")
        out += [f"xtn V<lo{r}>.8b, V<{a}>.8h"]
        if r % 2 == 0:
            out += [f"movi V<L{r//2}>.16b, #0", f"mov V<L{r//2}>.d[0], V<lo{r}>.d[0]"]
        else:
            out += [f"mov V<L{r//2}>.d[1], V<lo{r}>.d[0]"]
        out += [f"ushr V<hi{r}>.8h, V<{a}>.8h, #8",
                f"uzp1 V<he{r}>.8h, V<hi{r}>.8h, V<hi{r}>.8h",
                f"uzp2 V<ho{r}>.8h, V<hi{r}>.8h, V<hi{r}>.8h",
                f"sli V<he{r}>.8h, V<ho{r}>.8h, #4",
                f"xtn V<hp{r}>.8b, V<he{r}>.8h"]
        if r < 8:
            h = r // 4
            if r % 4 == 0: out += [f"movi V<H{h}>.16b, #0"]
            out += [f"ins V<H{h}>.h[{2*(r%4)}], V<hp{r}>.h[0]",
                    f"ins V<H{h}>.h[{2*(r%4)+1}], V<hp{r}>.h[1]"]
        else:
            out += ["ins V<L4>.h[4], V<hp8>.h[0]", "ins V<L4>.h[5], V<hp8>.h[1]"]
    result = held + [f"L{i}" for i in range(5)] + ["H0", "H1"]
    out += stores(result)
    return out, result


def source_chunks(physical: int) -> tuple[list[str], list[str]]:
    positions = list(range(6*physical, 6*physical+6))
    used_q = sorted({f"s{d//2}" for d in positions if d < 26})
    lines: list[str] = []
    if physical < 4:
        return [f"s{3*physical+i}" for i in range(3)], used_q
    def make(name: str, d0: int, d1: int) -> None:
        lines.extend([f"movi V<{name}>.16b, #0",
                      f"mov V<{name}>.d[0], x{GPRS[d0-26]}",
                      f"mov V<{name}>.d[1], x{GPRS[d1-26]}"])
    if physical == 4:
        make("rowq1", 26, 27); make("rowq2", 28, 29)
        return ["s12", "rowq1", "rowq2"], used_q + lines
    base = 6*physical
    make("rowq0", base, base+1); make("rowq1", base+2, base+3); make("rowq2", base+4, base+5)
    return ["rowq0", "rowq1", "rowq2"], used_q + lines


GPRS: list[int] = []  # Filled by optimize/compose after pair-1 physical allocation.


def consumer_region(physical: int, state: list[str], gprs: list[int]) -> tuple[list[str], list[str]]:
    global GPRS
    GPRS = gprs
    logical = ORDER[physical]
    out = loads(state)
    srcs, aux = source_chunks(physical)
    used_q = [x for x in aux if not x.startswith(("movi ", "mov "))]
    out += [x for x in aux if x not in used_q]
    b = f"b{logical}"
    out += ["ldr Q<modq>, [x30, #336]", "ldr Q<recip>, [x30, #352]"] + normalize(b, f"b{logical}")
    out += ["eor V<modq>.16b, V<modq>.16b, V<modq>.16b", f"sli V<modq>.8h, V<{b}>.8h, #4",
            f"xtn V<bmid>.8b, V<modq>.8h", f"ushr V<bhighh>.8h, V<{b}>.8h, #4",
            f"xtn V<bhigh>.8b, V<bhighh>.8h"]
    low = f"L{logical//2}" if logical < 8 else "L4"
    lowvar = low
    if logical < 8 and logical & 1:
        out += [f"ext V<alow>.16b, V<{low}>.16b, V<{low}>.16b, #8"]
        lowvar = "alow"
    high = f"H{logical//4}" if logical < 8 else "L4"
    hoff = 4*(logical%4) if logical < 8 else 8
    highvar = high
    if hoff:
        out += [f"ext V<ahsrc>.16b, V<{high}>.16b, V<{high}>.16b, #{hoff}"]
        highvar = "ahsrc"
    out += ["ldr Q<nibble>, [x30, #608]", f"and V<ahlo>.16b, V<{highvar}>.16b, V<nibble>.16b",
            f"ushr V<ahhi>.16b, V<{highvar}>.16b, #4", "zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b",
            "orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b"]
    for chunk in range(5):
        p0 = "carry" if physical < 8 and physical % 2 == 0 and chunk == 4 else f"p0_{chunk}"
        out += [f"ldr Q<{p0}>, [x30, #{MERGE+48*chunk}]",
                f"tbl V<{p0}>.16b, {{V<{srcs[0]}>.16b, V<{srcs[1]}>.16b}}, V<{p0}>.16b",
                f"ldr Q<p1_{chunk}>, [x30, #{MERGE+48*chunk+16}]",
                f"tbl V<p1_{chunk}>.16b, {{V<{srcs[1]}>.16b, V<{srcs[2]}>.16b}}, V<p1_{chunk}>.16b",
                f"orr V<{p0}>.16b, V<{p0}>.16b, V<p1_{chunk}>.16b",
                f"ldr Q<p2_{chunk}>, [x30, #{MERGE+48*chunk+32}]",
                f"tbl V<p2_{chunk}>.16b, {{V<{lowvar}>.16b, V<bmid>.16b, V<bhigh>.16b}}, V<p2_{chunk}>.16b",
                f"orr V<{p0}>.16b, V<{p0}>.16b, V<p2_{chunk}>.16b"]
        if physical == 8:
            out += [f"str {'D' if chunk == 4 else 'Q'}<p0_{chunk}>, [x29, #{16*chunk}]"]
        elif physical % 2 == 0:
            if chunk < 4: out += [f"str Q<p0_{chunk}>, [x29, #{16*chunk}]"]
        else:
            left = "carry" if chunk == 0 else f"p0_{chunk-1}"
            out += [f"movi V<stream_{chunk}>.16b, #0",
                    f"mov V<stream_{chunk}>.d[0], V<{left}>.d[{0 if chunk == 0 else 1}]",
                    f"mov V<stream_{chunk}>.d[1], V<p0_{chunk}>.d[0]",
                    f"str Q<stream_{chunk}>, [x29, #{16*chunk}]"]

    consumed_q = set(used_q)
    next_state = [x for x in state if x not in consumed_q and x != b]
    if physical % 2 == 1 and "carry" in next_state: next_state.remove("carry")
    # Packed containers die after their final logical row consumer.
    future = set(ORDER[physical+1:])
    for key in list(next_state):
        if key.startswith("L"):
            idx = int(key[1:]); users = {2*idx, 2*idx+1} if idx < 4 else {8}
            if not (users & future): next_state.remove(key)
        elif key == "H0" and not ({0,1,2,3} & future): next_state.remove(key)
        elif key == "H1" and not ({4,5,6,7} & future): next_state.remove(key)
    if physical < 8 and physical % 2 == 0: next_state.append("carry")
    out += stores(next_state)
    return out, next_state


def function(label: str, body: list[str]) -> list[str]:
    contract = [
        "// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.",
        "// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.",
        "// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.",
        "// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.",
    ]
    return [f".global {label}", f"{label}:"] + contract + [f"{label}_slothy_start:"] + ["    "+x for x in body] + [f"{label}_slothy_end:", "    ret", ""]


def main() -> None:
    # Consumer regions require the allocated pair-1 GPR map, written by optimize_d3.py.
    map_path = HERE / "pair1-state-map.json"
    gprs = __import__("json").loads(map_path.read_text())["gpr_slots"] if map_path.exists() else list(range(28))
    saved = [f"s{i}" for i in range(13)]
    ra, state_a = route_region("route_a", saved, "a", 448)
    pa, state_p = pack_region(state_a)
    rb, state_b = route_region("route_b", state_p, "b", 464)
    lines = [".text"] + function("gt864_p6d3_route_a", ra) + function("gt864_p6d3_pack_a", pa) + function("gt864_p6d3_route_b", rb)
    state = state_b
    for physical in range(9):
        body, state = consumer_region(physical, state, gprs)
        lines += function(f"gt864_p6d3_row{physical}", body)
    assert not state, state
    (HERE / "d3-regions.sym.S").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
