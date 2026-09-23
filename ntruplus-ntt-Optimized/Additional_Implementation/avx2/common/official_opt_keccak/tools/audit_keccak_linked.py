#!/usr/bin/env python3
"""Linked audit of the mlkem-native-Keccak NTRU+ KEM candidates (768/864/1152).

On the linked KEM test ELFs (candidate build/test_<base>_keccak, keccak-only
control build/test_kem_keccak; both also hold the Official KEM as the
official_ref_* role) a direct call/tail-jump/rip-reference graph is built
from `objdump -d`.  Gates:

  * the closure reachable from the candidate/control KEM entry points
    (official_lazy_{keypair,enc,dec}) contains NO Official SHAKE/Keccak symbol
    (KeccakP1600_*, KeccakF1600_*, __KeccakF1600, fips202avx_*, the Official
    global hash_f/hash_g/hash_h) and no indirect call; it does contain
    ntruplus_mlkfips202_shake256, ..._keccakf1600_{permute,xor_bytes,
    extract_bytes}, mlk_keccakf1600_permute_c and ntruplus{N}_keccak_hash_{f,g,h};
  * the Official role's closure (official_ref_*) does reach
    KeccakP1600_Permute_24rounds (coexistence sanity);
  * KEM objects: every undefined symbol is listed; none is an Official
    SHAKE/Keccak/hash symbol; relocations to the candidate hash wrappers are
    2/2/2 and to ntruplus_mlkfips202_shake256 >= 1 (genf/geng may inline);
  * libc/PLT calls reachable from the new hash path (the three wrappers and
    mlk shake256) are listed and must be a subset of {memcpy, memset,
    __explicit_bzero_chk, explicit_bzero, __stack_chk_fail} (explicit_bzero
    and memcpy come from the Official symmetric.c / util.h wrapper code,
    __stack_chk_fail from the distro's default -fstack-protector-strong);
  * stack usage (-fstack-usage, same CFLAGS): every new-path function is
    `static` (no VLA/alloca); worst call-chain depth of each hash wrapper is
    computed from the .su frames (+8 bytes return address per call) and
    compared with the Official C driver's frames (its AVX2 asm leaf frames
    are not reported by -fstack-usage).
"""

import argparse
import bisect
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

FORBIDDEN = re.compile(r"^(KeccakP1600_\w+|KeccakF1600_\w+|__KeccakF1600|_?KeccakP1600\w*|fips202avx_\w+|"
                       r"hash_[fgh]|__wrap_fips202avx_shake256|__real_fips202avx_shake256)$")
LIBC_OK = {"memcpy", "memset", "__explicit_bzero_chk", "explicit_bzero", "__stack_chk_fail"}
MLK = "ntruplus_mlkfips202_"


def run(*args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def call_graph(elf):
    """Direct call / jump / rip-reference graph keyed by function START ADDRESS
    (static functions of different objects may share a name, e.g. the two
    crypto_kem_enc_derand), with a name per node for reporting."""
    text = run("objdump", "-d", "--no-show-raw-insn", "-M", "att", elf)
    starts, names = [], {}
    for m in re.finditer(r"^([0-9a-f]+) <([^>]+)>:$", text, re.M):
        starts.append(int(m[1], 16))
        names[int(m[1], 16)] = m[2]
    starts.sort()

    def owner(addr):
        i = bisect.bisect_right(starts, addr) - 1
        return starts[i] if i >= 0 else None

    graph, indirect, current = defaultdict(set), defaultdict(int), None
    for line in text.splitlines():
        head = re.match(r"^([0-9a-f]+) <([^>]+)>:$", line)
        if head:
            current = int(head[1], 16)
            graph[current]
            continue
        m = re.match(r"^\s*[0-9a-f]+:\s+(\S+)\s*(.*)$", line)
        if not m or current is None:
            continue
        op, operands = m[1], m[2]
        if op.startswith(("call", "jmp")) and "*" in operands.split("#")[0]:
            indirect[current] += 1
        for target, sym in re.findall(r"\b([0-9a-f]+) <([^>+]+)(?:\+0x[0-9a-f]+)?>", operands):
            t = owner(int(target, 16))
            # data references (GOT slots, constants) are not functions: keep an
            # edge only when the target lies in the function the symbol names
            if t is not None and t != current and names.get(t) == sym:
                graph[current].add(t)
    return graph, indirect, names


def closure(graph, roots):
    seen, stack = set(), list(roots)
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        stack.extend(graph.get(f, ()))
    return seen


def plt_name(sym):
    return sym[:-4] if sym.endswith("@plt") else None


class Graph:
    def __init__(self, elf):
        self.edges, self.indirect, self.names = call_graph(elf)
        self.by_name = defaultdict(list)
        for addr, name in self.names.items():
            self.by_name[name].append(addr)

    def addr(self, name):
        addrs = self.by_name.get(name, [])
        if len(addrs) != 1:
            raise ValueError(f"{name}: {len(addrs)} definitions")
        return addrs[0]

    def reach(self, roots):
        return closure(self.edges, [self.addr(r) for r in roots])

    def named(self, addrs):
        return sorted({self.names[a] for a in addrs})


def elf_audit(g, elf, roots, required, forbid):
    reach = g.reach(roots)
    names = g.named(reach)
    bad = sorted(f for f in names if forbid and FORBIDDEN.match(f))
    return {"elf": str(elf), "elf_sha256": sha(elf), "roots": roots,
            "reachable_functions": len(reach),
            "forbidden_reached": bad,
            "indirect_calls_in_closure": {g.names[a]: g.indirect[a] for a in sorted(reach)
                                          if g.indirect.get(a) and "@plt" not in g.names[a]},
            "required_present": {r: r in names for r in required},
            "plt_calls": sorted({plt_name(f) for f in names if plt_name(f)})}


def object_audit(obj, names):
    undefined = sorted(set(run("nm", "-u", obj).split()) - {"U"})
    relocs = run("objdump", "-dr", obj)
    counts = {n: len(re.findall(r"R_X86_64_(?:PLT32|PC32)\s+" + re.escape(n) + r"(?:-0x4)?\s*$", relocs, re.M))
              for n in names}
    return {"object": str(obj), "object_sha256": sha(obj), "undefined": undefined,
            "forbidden_undefined": [u for u in undefined if FORBIDDEN.match(u)], "relocations": counts}


def stack_usage(directory):
    frames = {}
    for su in sorted(Path(directory).glob("*.su")):
        for line in su.read_text().splitlines():
            loc, size, kind = line.rsplit("\t", 2)
            name = loc.rsplit(":", 1)[-1]
            frames[name] = {"bytes": int(size), "kind": kind, "file": su.name}
    return frames


def object_graph(objs):
    """Call/tail-jump graph by symbol name over relocatable objects (names are
    unique across the new-path objects: mlk_fips202.o, mlk_keccakf1600.o,
    symmetric_keccak.o; likewise the Official fips202.o + symmetric.o)."""
    edges, current = defaultdict(set), None
    for obj in objs:
        for line in run("objdump", "-dr", "--no-show-raw-insn", obj).splitlines():
            head = re.match(r"^[0-9a-f]+ <([^>]+)>:$", line)
            if head:
                current = head[1].split(".")[0]
                edges[current]
                continue
            if current is None:
                continue
            for t in re.findall(r"R_X86_64_(?:PLT32|PC32)\s+([A-Za-z_][\w.@]*?)(?:-0x4)?$", line) + \
                    re.findall(r"^\s*[0-9a-f]+:\s+(?:call|jmp)\s+[0-9a-f]+ <([^>+]+)>", line):
                t = t.split(".")[0]
                if t != current:
                    edges[current].add(t)
    return edges


def depth(edges, frames, f, seen=()):
    """Worst stack depth (bytes): own .su frame + max(8 + callee depth) over
    callees with a .su frame (libc / asm callees are listed separately)."""
    own = frames.get(f, {}).get("bytes")
    if own is None:
        return None
    worst = 0
    for g in edges.get(f, ()):
        if g in seen:
            continue
        d = depth(edges, frames, g, seen + (f,))
        if d is not None:
            worst = max(worst, 8 + d)
    return own + worst


def frame_names(frames):
    return {k.split(".")[0]: v for k, v in frames.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--candidate-elf", type=Path, required=True)
    ap.add_argument("--control-elf", type=Path, required=True)
    ap.add_argument("--candidate-obj", type=Path, required=True)
    ap.add_argument("--control-obj", type=Path, required=True)
    ap.add_argument("--stack-usage-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n = args.param
    wrappers = [f"ntruplus{n}_keccak_hash_{x}" for x in "fgh"]
    mlk_core = [MLK + "shake256", MLK + "keccakf1600_permute", MLK + "keccakf1600_xor_bytes",
                MLK + "keccakf1600_extract_bytes", "mlk_keccakf1600_permute_c"]
    lazy_roots = [f"official_lazy_{op}" for op in ("keypair", "enc", "dec")]
    ref_roots = [f"official_ref_{op}" for op in ("keypair", "enc", "dec")]
    summary = {"class": "Phase-A linked audit (no timing)", "parameter": f"NTRU+{n}", "elf": {}, "objects": {}}
    ok = True
    for label, elf in (("candidate", args.candidate_elf), ("keccak_only_control", args.control_elf)):
        g = Graph(elf)
        cand = elf_audit(g, elf, lazy_roots, wrappers + mlk_core, True)
        ref = elf_audit(g, elf, ref_roots, ["KeccakP1600_Permute_24rounds", "fips202avx_shake256"], False)
        # the new hash path (wrappers + mlk shake256) in isolation
        hash_path = g.named(g.reach(wrappers + [MLK + "shake256"]))
        hash_libc = sorted({plt_name(f) for f in hash_path if plt_name(f)})
        mlk_only = g.named(g.reach([MLK + "shake256"]))
        entry = {"kem_closure": cand, "official_role_closure": {
                     k: ref[k] for k in ("roots", "reachable_functions", "required_present")},
                 "hash_path_functions": [f for f in hash_path if not plt_name(f)],
                 "hash_path_plt_calls": hash_libc,
                 "mlk_shake256_functions": [f for f in mlk_only if not plt_name(f)],
                 "mlk_shake256_plt_calls": sorted({plt_name(f) for f in mlk_only if plt_name(f)}),
                 "hash_path_forbidden": [f for f in hash_path if FORBIDDEN.match(f)]}
        gate = (not cand["forbidden_reached"] and all(cand["required_present"].values()) and
                not cand["indirect_calls_in_closure"] and all(ref["required_present"].values()) and
                set(hash_libc) <= LIBC_OK and not entry["hash_path_forbidden"])
        entry["pass"] = gate
        ok &= gate
        summary["elf"][label] = entry
        if label == "candidate":
            cand_graph = g
    names = wrappers + [MLK + "shake256", "hash_f", "hash_g", "hash_h", "fips202avx_shake256"]
    for label, obj in (("candidate_kem", args.candidate_obj), ("keccak_only_kem", args.control_obj)):
        o = object_audit(obj, names)
        r = o["relocations"]
        o["pass"] = (not o["forbidden_undefined"] and [r[w] for w in wrappers] == [2, 2, 2] and
                     r[MLK + "shake256"] >= 1 and r["hash_f"] == r["hash_g"] == r["hash_h"] == 0 and
                     r["fips202avx_shake256"] == 0)
        ok &= o["pass"]
        summary["objects"][label] = o
    frames = stack_usage(args.stack_usage_dir)
    su = {f: frames[f] for f in sorted(frames) if f.startswith("mlk_") or f.startswith(MLK)
          or f.startswith(f"ntruplus{n}_keccak")}
    frames = frame_names(frames)
    ksu = args.stack_usage_dir
    new_edges = object_graph([ksu / "mlk_fips202.o", ksu / "mlk_keccakf1600.o", ksu / "symmetric_keccak.o"])
    off_edges = object_graph([ksu / "official_fips202.o", ksu / "official_symmetric.o"])
    worst = {w: depth(new_edges, frames, w) for w in wrappers + [MLK + "shake256"]}
    official_worst = {w: depth(off_edges, frames, w) for w in ("hash_f", "hash_g", "hash_h", "fips202avx_shake256")}
    unframed = {w: sorted(t for t in closure(new_edges, [w]) if t not in frames) for w in wrappers}
    official = {f: frames[f] for f in ("hash_f", "hash_g", "hash_h", "fips202avx_shake256",
                                        "keccak_absorb", "keccak_squeeze") if f in frames}
    stack_ok = all(v["kind"] == "static" for v in su.values()) and all(v is not None for v in worst.values())
    summary["stack_usage"] = {"method": "gcc -fstack-usage with the release CFLAGS; worst depth = own frame "
                                        "+ max(8 + callee depth) over callees with a .su frame",
                              "new_path_frames": su, "new_path_worst_depth_bytes": worst,
                              "new_path_callees_without_frame": unframed,
                              "official_c_frames": official,
                              "official_c_worst_depth_bytes_excluding_asm": official_worst,
                              "official_note": "Official permutation/AddBytes/ExtractBytes are AVX2 asm (no .su)",
                              "pass": stack_ok}
    ok &= stack_ok
    summary["pass"] = bool(ok)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    brief = {"pass": summary["pass"],
             "candidate_forbidden": summary["elf"]["candidate"]["kem_closure"]["forbidden_reached"],
             "hash_path_plt": summary["elf"]["candidate"]["hash_path_plt_calls"],
             "mlk_plt": summary["elf"]["candidate"]["mlk_shake256_plt_calls"],
             "relocs": summary["objects"]["candidate_kem"]["relocations"],
             "worst_stack": worst}
    print(json.dumps(brief, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
