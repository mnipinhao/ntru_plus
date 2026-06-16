#!/usr/bin/env python3
import argparse
import collections
import os
import re
from pathlib import Path


ROW_START = "slothy_start_ntruplus768_invntt32_rowpack_soa_row"
ROW_END = "slothy_end_ntruplus768_invntt32_rowpack_soa_row"
ROWPACK_STAGE_ORDER = [
    ("loads", 18),
    ("entry_normalize", 12),
    ("stage1", 16),
    ("stage2", 40),
    ("stage3", 40),
    ("stage4", 10),
    ("stage5", 10),
    ("row_end_reduce", 12),
    ("stores", 4),
]

ARITH_OPS = {
    "add", "sub", "mul", "mla", "mls", "sqdmulh", "sqrdmulh",
    "sqrdmlah", "sqrdmlsh", "smull", "smull2", "smlal", "smlal2",
    "smlsl", "smlsl2", "umull", "umull2", "umlal", "umlal2",
    "umlsl", "umlsl2", "sqdmull", "sqdmull2", "saddw", "saddw2",
    "ssubw", "ssubw2",
}
SHIFT_REDUCE_OPS = {
    "srshr", "sshr", "ushr", "shl", "sshll", "sshll2", "sxtl", "sxtl2",
    "sqrshrn", "sqrshrn2", "sqshrn", "sqshrn2", "sqxtn", "sqxtn2",
}
PERMUTE_OPS = {
    "rev16", "rev32", "rev64", "ext", "trn1", "trn2", "zip1", "zip2",
    "uzp1", "uzp2", "tbl", "tbx",
}
MOVE_SELECT_OPS = {
    "orr", "mov", "movi", "dup", "ins", "umov", "smov", "fmov", "bit",
    "bif", "bsl", "bic", "eor", "and",
}
LOAD_OPS = {"ldr", "ldp", "ld1", "ld2", "ld3", "ld4", "ldur"}
STORE_OPS = {"str", "stp", "st1", "st2", "st3", "st4", "stur"}
CONTROL_OPS = {
    "b", "bl", "br", "blr", "ret", "cbz", "cbnz", "tbz", "tbnz", "cmp",
    "cmn", "subs", "adds",
}


def strip_comment(line):
    line = line.split("//", 1)[0]
    line = line.split(";", 1)[0]
    return line.rstrip()


def decode_asm_line(line):
    raw = strip_comment(line).strip()
    if (not raw or raw.startswith(".") or raw.startswith("#") or
            raw.startswith("/*") or raw.startswith("*") or raw.startswith("*/")):
        return None
    if raw.endswith(":"):
        return None
    if ":" in raw:
        # objdump: "  1234: 4e...  add v0.8h, ..."
        raw = raw.split(":", 1)[1].strip()
        raw = re.sub(r"^([0-9a-fA-F]{2,8}\s+)+", "", raw).strip()
    if not raw:
        return None
    parts = raw.split(None, 1)
    if not parts:
        return None
    op = parts[0].lower()
    operands = parts[1] if len(parts) > 1 else ""
    return op, operands, raw


def read_region(path, start=None, end=None, symbol=None):
    lines = Path(path).read_text().splitlines()
    if symbol:
        out = []
        in_symbol = False
        label_re = re.compile(r"^\s*([A-Za-z_.$][\w.$]*)\s*:")
        for line in lines:
            m = label_re.match(strip_comment(line))
            if m:
                label = m.group(1)
                if label == symbol:
                    in_symbol = True
                    continue
                if in_symbol and not label.startswith("."):
                    break
            if in_symbol:
                out.append(line)
        return out
    if start is None:
        return lines
    out = []
    in_region = False
    for line in lines:
        if start in line:
            in_region = True
            continue
        if end and end in line:
            break
        if in_region:
            out.append(line)
    return out


def classify(op, operands):
    if op in LOAD_OPS:
        if "[x1" in operands or "[x1," in operands:
            return "constant_load"
        return "load"
    if op in STORE_OPS:
        return "store"
    if op in ARITH_OPS:
        return "arithmetic"
    if op in SHIFT_REDUCE_OPS:
        return "shift_reduce"
    if op in PERMUTE_OPS:
        return "permute"
    if op in MOVE_SELECT_OPS:
        return "move_select"
    if op in CONTROL_OPS:
        return "control"
    return "other"


def audit_lines(lines):
    counts = collections.Counter()
    op_counts = collections.Counter()
    decoded = []
    for line in lines:
        item = decode_asm_line(line)
        if not item:
            continue
        op, operands, raw = item
        cls = classify(op, operands)
        counts[cls] += 1
        op_counts[op] += 1
        decoded.append((op, operands, raw, cls))
    counts["total"] = sum(counts.values())
    return counts, op_counts, decoded


def add_counter(dst, src, scale=1):
    for key, value in src.items():
        dst[key] += value * scale


def stage_from_comment(line, current):
    if "//" not in line:
        return current
    comment = line.split("//", 1)[1].strip().lower()
    if comment.startswith("row-input barrett normalization"):
        return "entry_normalize"
    if comment.startswith("stage 1:"):
        return "stage1"
    if comment.startswith("stage 2:"):
        return "stage2"
    if comment.startswith("stage 3:"):
        return "stage3"
    if comment.startswith("stage 4:"):
        return "stage4"
    if comment.startswith("stage 5:"):
        return "stage5"
    if "row-end barrett reduction" in comment:
        return "row_end_reduce"
    return current


def stage_from_index(index):
    seen = 0
    for stage, count in ROWPACK_STAGE_ORDER:
        seen += count
        if index < seen:
            return stage
    return ROWPACK_STAGE_ORDER[-1][0]


def audit_symbolic_stages(path):
    lines = read_region(path, ROW_START, ROW_END)
    stages = collections.OrderedDict(
        (name, (collections.Counter(), collections.Counter()))
        for name in [
            "loads",
            "entry_normalize",
            "stage1",
            "stage2",
            "stage3",
            "stage4",
            "stage5",
            "row_end_reduce",
            "stores",
        ]
    )
    current = "loads"
    for line in lines:
        current = stage_from_comment(line, current)
        item = decode_asm_line(line)
        if not item:
            continue
        op, operands, _ = item
        cls = classify(op, operands)
        stage = "stores" if cls == "store" else current
        counts, op_counts = stages.setdefault(
            stage, (collections.Counter(), collections.Counter()))
        counts[cls] += 1
        op_counts[op] += 1
    for counts, _ in stages.values():
        counts["total"] = sum(counts.values())
    return stages


def print_stage_breakdown(name, stages):
    print(f"{name}:")
    print("  stage,total,arith,shift_reduce,permute,move_select,load,const_load,store,arith_datapath,top_ops")
    for stage, (counts, op_counts) in stages.items():
        if not counts.get("total", 0):
            continue
        arith_datapath = counts.get("arithmetic", 0) + counts.get("shift_reduce", 0)
        top = " ".join(f"{op}={count}" for op, count in op_counts.most_common(8))
        print(
            "  "
            f"{stage},{counts.get('total', 0)},"
            f"{counts.get('arithmetic', 0)},"
            f"{counts.get('shift_reduce', 0)},"
            f"{counts.get('permute', 0)},"
            f"{counts.get('move_select', 0)},"
            f"{counts.get('load', 0)},"
            f"{counts.get('constant_load', 0)},"
            f"{counts.get('store', 0)},"
            f"{arith_datapath},"
            f"{top}"
        )


def read_macro(path, name):
    lines = Path(path).read_text().splitlines()
    out = []
    in_macro = False
    macro_re = re.compile(r"^\s*\.macro\s+(\S+)")
    for line in lines:
        m = macro_re.match(line)
        if m:
            in_macro = m.group(1) == name
            continue
        if in_macro and re.match(r"^\s*\.endm\b", line):
            break
        if in_macro:
            out.append(line)
    return out


def infer_production_motifs(path):
    motifs = collections.OrderedDict()

    fqm = collections.Counter({"arithmetic": 3, "total": 3})
    motifs["production_fqmul_lane_inferred"] = (fqm, collections.Counter({
        "sqrdmulh": 1, "mul": 1, "mls": 1,
    }))

    butterfly = collections.Counter({"arithmetic": 5, "move_select": 1, "total": 6})
    motifs["production_inv_butterfly_lane_lazy_inferred"] = (
        butterfly,
        collections.Counter({
            "sqrdmulh": 1, "mul": 1, "mls": 1, "mov": 1,
            "add": 1, "sub": 1,
        }),
    )

    stage123_block = collections.Counter({
        "load": 8,
        "arithmetic": 60,
        "move_select": 12,
        "store": 8,
        "total": 88,
    })
    motifs["production_stage123_block_lazy_inferred"] = (
        stage123_block,
        collections.Counter({
            "ldr": 8, "sqrdmulh": 12, "mul": 12, "mls": 12,
            "mov": 12, "add": 12, "sub": 12, "str": 8,
        }),
    )

    stage123_full = collections.Counter()
    add_counter(stage123_full, stage123_block, 4)
    stage123_full["constant_load"] += 2
    stage123_full["total"] += 2
    motifs["production_stage123_full4_lazy_inferred"] = (
        stage123_full,
        collections.Counter({
            "ldr": 34, "sqrdmulh": 48, "mul": 48, "mls": 48,
            "mov": 48, "add": 48, "sub": 48, "str": 32,
        }),
    )

    stage45_lines = read_macro(path, "INVNTT32_STAGE45_STRIPE_SLOTHY")
    if stage45_lines:
        counts, op_counts, _ = audit_lines(stage45_lines)
        motifs["production_stage45_reduce_fused_slothy_stripe_actual"] = (
            counts, op_counts)
        full_counts = collections.Counter()
        add_counter(full_counts, counts, 8)
        full_ops = collections.Counter()
        add_counter(full_ops, op_counts, 8)
        motifs["production_stage45_reduce_fused_slothy_full8_inferred"] = (
            full_counts, full_ops)

    reduce_lines = read_macro(path, "BARRETT_REDUCE")
    if reduce_lines:
        counts, op_counts, _ = audit_lines(reduce_lines)
        motifs["production_barrett_reduce_macro"] = (counts, op_counts)

    return motifs


def print_motifs(name, motifs):
    print(f"{name}:")
    for motif, (counts, op_counts) in motifs.items():
        top = ", ".join(f"{op}={count}" for op, count in op_counts.most_common(10))
        print(f"  {motif}:")
        for key in [
            "total", "arithmetic", "shift_reduce", "permute", "move_select",
            "load", "constant_load", "store", "control", "other",
        ]:
            if counts.get(key, 0):
                print(f"    {key}: {counts[key]}")
        print(f"    top_ops: {top}")


def reg_base(operand):
    m = re.match(r"\s*([vq])([0-9]+)", operand, re.IGNORECASE)
    if not m:
        return None
    return f"v{m.group(2)}"


def first_vector_reg(operands, skip_first=False):
    regs = re.findall(r"\b[vq][0-9]+(?:\.[0-9a-zA-Z]+)?", operands)
    if skip_first and regs:
        regs = regs[1:]
    if not regs:
        return None
    return reg_base(regs[0])


def replacement_for(line, variant):
    item = decode_asm_line(line)
    if not item:
        return line
    op, operands, raw = item
    cls = classify(op, operands)
    dest = first_vector_reg(operands)
    src = first_vector_reg(operands, skip_first=True)
    if not dest:
        return line

    keep = False
    base_variant = variant.replace("_nop", "")
    if base_variant == "arithmetic":
        keep = cls in {"load", "constant_load", "store", "arithmetic", "shift_reduce"}
    elif base_variant == "shuffle":
        keep = cls in {"load", "constant_load", "store", "permute", "move_select"}
    else:
        keep = True

    if keep:
        return line

    indent = re.match(r"^\s*", line).group(0)
    if variant.endswith("_nop"):
        return f"{indent}nop // audit skeleton removed: {raw}\n"
    if src:
        if op in {"mls", "mla", "bit", "bif", "bsl"}:
            return f"{indent}eor {dest}.16b, {dest}.16b, {src}.16b // audit skeleton replaced: {raw}\n"
        return f"{indent}orr {dest}.16b, {src}.16b, {src}.16b // audit skeleton replaced: {raw}\n"
    return f"{indent}orr {dest}.16b, {dest}.16b, {dest}.16b // audit skeleton replaced: {raw}\n"


def generate_variant(src, dst, variant):
    lines = Path(src).read_text().splitlines(keepends=True)
    out = []
    in_region = False
    for line in lines:
        if ROW_START in line:
            in_region = True
            out.append(line)
            continue
        if ROW_END in line:
            in_region = False
            out.append(line)
            continue
        if in_region:
            out.append(replacement_for(line, variant))
        else:
            out.append(line)
    Path(dst).write_text("".join(out))


def reduction_probe_replaces(stage, cls, variant):
    if variant in {"no_entry", "no_entry_no_end", "fully_lazy_lower_bound"}:
        if stage == "entry_normalize":
            return True
    if variant in {"no_entry_no_end_stage23_select_copy"}:
        if stage == "entry_normalize":
            return True
    if variant in {"no_row_end", "no_entry_no_end", "fully_lazy_lower_bound"}:
        if stage == "row_end_reduce":
            return True
    if variant in {"no_entry_no_end_stage23_select_copy"}:
        if stage == "row_end_reduce":
            return True
    if variant in {
        "stage23_select_copy",
        "no_entry_no_end_stage23_select_copy",
        "fully_lazy_lower_bound",
    }:
        if stage in {"stage2", "stage3"} and cls in {"permute", "move_select"}:
            return True
    return False


def reduction_probe_replacement(line, stage, cls, variant):
    item = decode_asm_line(line)
    op, operands, raw = item
    indent = re.match(r"^\s*", line).group(0)
    if (stage in {"stage2", "stage3"} and cls in {"permute", "move_select"} and
            variant in {
                "stage23_select_copy",
                "no_entry_no_end_stage23_select_copy",
                "fully_lazy_lower_bound",
            }):
        dest = first_vector_reg(operands)
        src = first_vector_reg(operands, skip_first=True)
        if dest and src:
            if op in {"bit", "bif", "bsl"}:
                return (
                    f"{indent}eor {dest}.16b, {dest}.16b, {src}.16b "
                    f"// reduction probe {variant} replaced {stage}: {raw}\n"
                )
            return (
                f"{indent}orr {dest}.16b, {src}.16b, {src}.16b "
                f"// reduction probe {variant} replaced {stage}: {raw}\n"
            )
        if dest:
            return (
                f"{indent}orr {dest}.16b, {dest}.16b, {dest}.16b "
                f"// reduction probe {variant} replaced {stage}: {raw}\n"
            )
    return f"{indent}nop // reduction probe {variant} removed {stage}: {raw}\n"


def generate_reduction_probe(src, dst, variant):
    lines = Path(src).read_text().splitlines(keepends=True)
    out = []
    in_region = False
    current = "loads"
    instruction_index = 0
    for line in lines:
        if ROW_START in line:
            in_region = True
            current = "loads"
            instruction_index = 0
            out.append(line)
            continue
        if ROW_END in line:
            in_region = False
            out.append(line)
            continue
        if not in_region:
            out.append(line)
            continue

        current = stage_from_comment(line, current)
        item = decode_asm_line(line)
        if not item:
            out.append(line)
            continue
        op, operands, raw = item
        cls = classify(op, operands)
        stage = stage_from_index(instruction_index)
        if current != "loads":
            stage = current
        instruction_index += 1
        if reduction_probe_replaces(stage, cls, variant):
            out.append(reduction_probe_replacement(line, stage, cls, variant))
        else:
            out.append(line)
    Path(dst).write_text("".join(out))


def generate_no_entry_no_end_candidate(src, dst):
    lines = Path(src).read_text().splitlines(keepends=True)
    out = []
    in_region = False
    current = "loads"
    instruction_index = 0
    skipped = 0
    wrote_before_bounds = False
    for line in lines:
        if line.startswith("// Output representation:"):
            out.append(
                "// Output representation: same rowpack SoA plane, lazy "
                "rowkernel output; row-end Barrett delayed.\n"
            )
            continue
        if (line.startswith("// Coefficient bounds before:") or
                line.startswith("// Coefficient bounds after row-input normalization:")):
            if not wrote_before_bounds:
                out.append(
                    "// Coefficient bounds before: rowpack basemul/add output "
                    "validated by test_gt_rowpack_no_entry_no_end_range_contract.c.\n"
                )
                wrote_before_bounds = True
            continue
        if line.startswith("// Coefficient bounds after:"):
            out.append(
                "// Coefficient bounds after: lazy row output validated to "
                "remain within signed int16 range for product/add envelopes.\n"
            )
            continue
        if ROW_START in line:
            in_region = True
            current = "loads"
            instruction_index = 0
            out.append(line)
            out.append(
                "        // no-entry/no-end candidate: row-input Barrett and "
                "row-end Barrett removed by range contract.\n"
            )
            continue
        if ROW_END in line:
            in_region = False
            out.append(line)
            continue
        if not in_region:
            out.append(line)
            continue

        current = stage_from_comment(line, current)
        item = decode_asm_line(line)
        if not item:
            out.append(line)
            continue
        op, operands, _ = item
        cls = classify(op, operands)
        stage = stage_from_index(instruction_index)
        if current != "loads":
            stage = current
        instruction_index += 1
        if stage in {"entry_normalize", "row_end_reduce"}:
            skipped += 1
            continue
        out.append(line)

    if skipped != 24:
        raise RuntimeError(f"expected to remove 24 reduction instructions, removed {skipped}")
    Path(dst).write_text("".join(out))


def print_audit(name, counts, op_counts):
    print(f"{name}:")
    for key in [
        "total", "arithmetic", "shift_reduce", "permute", "move_select",
        "load", "constant_load", "store", "control", "other",
    ]:
        if counts.get(key, 0):
            print(f"  {key}: {counts[key]}")
    top = ", ".join(f"{op}={count}" for op, count in op_counts.most_common(12))
    print(f"  top_ops: {top}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-kernel", required=True)
    parser.add_argument("--row-symbolic")
    parser.add_argument("--postmerge-asm")
    parser.add_argument("--postmerge-symbol",
                        default="invntt_rowpack_postmerge_branchfold_neon")
    parser.add_argument("--production-asm")
    parser.add_argument("--generate-dir")
    parser.add_argument("--reduction-probe-source")
    parser.add_argument("--generate-no-entry-no-end")
    args = parser.parse_args()

    row_lines = read_region(args.row_kernel, ROW_START, ROW_END)
    counts, op_counts, _ = audit_lines(row_lines)
    print_audit("row_kernel_opt", counts, op_counts)

    if args.postmerge_asm and Path(args.postmerge_asm).exists():
        post_lines = read_region(args.postmerge_asm,
                                 symbol=args.postmerge_symbol)
        post_counts, post_op_counts, _ = audit_lines(post_lines)
        print_audit("native_postmerge_compiler_asm", post_counts,
                    post_op_counts)

    if args.row_symbolic and Path(args.row_symbolic).exists():
        print_stage_breakdown(
            "rowpack_symbolic_stage_breakdown",
            audit_symbolic_stages(args.row_symbolic),
        )

    if args.production_asm and Path(args.production_asm).exists():
        print_motifs(
            "production_invntt_motif_audit",
            infer_production_motifs(args.production_asm),
        )

    if args.generate_dir:
        out_dir = Path(args.generate_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        arithmetic = out_dir / "ntruplus768_invntt32_rowpack_soa_row.arithmetic_skeleton.S"
        shuffle = out_dir / "ntruplus768_invntt32_rowpack_soa_row.shuffle_skeleton.S"
        arithmetic_nop = out_dir / "ntruplus768_invntt32_rowpack_soa_row.arithmetic_nop_skeleton.S"
        shuffle_nop = out_dir / "ntruplus768_invntt32_rowpack_soa_row.shuffle_nop_skeleton.S"
        generate_variant(args.row_kernel, arithmetic, "arithmetic")
        generate_variant(args.row_kernel, shuffle, "shuffle")
        generate_variant(args.row_kernel, arithmetic_nop, "arithmetic_nop")
        generate_variant(args.row_kernel, shuffle_nop, "shuffle_nop")
        print(f"generated_arithmetic_skeleton: {arithmetic}")
        print(f"generated_shuffle_skeleton: {shuffle}")
        print(f"generated_arithmetic_nop_skeleton: {arithmetic_nop}")
        print(f"generated_shuffle_nop_skeleton: {shuffle_nop}")

    if args.generate_dir and args.reduction_probe_source:
        src = Path(args.reduction_probe_source)
        out_dir = Path(args.generate_dir)
        for variant in [
            "no_entry",
            "no_row_end",
            "no_entry_no_end",
            "stage23_select_copy",
            "no_entry_no_end_stage23_select_copy",
            "fully_lazy_lower_bound",
        ]:
            out = out_dir / f"ntruplus768_invntt32_rowpack_soa_row.{variant}.S"
            generate_reduction_probe(src, out, variant)
            print(f"generated_reduction_probe_{variant}: {out}")

    if args.reduction_probe_source and args.generate_no_entry_no_end:
        generate_no_entry_no_end_candidate(
            Path(args.reduction_probe_source),
            Path(args.generate_no_entry_no_end),
        )
        print(f"generated_no_entry_no_end_candidate: {args.generate_no_entry_no_end}")


if __name__ == "__main__":
    main()
