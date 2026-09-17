"""Run SLOTHY on one clean kernel for one microarchitecture.

Two passes, as the NTRU+864 campaign established: `ra` allocates registers with
reordering disabled, then `timing` reorders the allocated code under the split
heuristic.  Splitting the two keeps each solve tractable and makes a failure
attributable to one or the other.
"""
import argparse, hashlib, json, logging, os, sys, time
from pathlib import Path

# The venv's bundled SLOTHY has no cortex_a76 model.  Insist on the checkout
# that does, and assert it, so a wrong model cannot be used silently.
SLOTHY_ROOT = Path(os.environ.get("SLOTHY_ROOT", "/Users/chenpinhao/slothy"))
sys.path.insert(0, str(SLOTHY_ROOT))
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
assert Path(Arch.__file__).resolve().is_relative_to(SLOTHY_ROOT.resolve()), Arch.__file__

TARGETS = {
    "cortex_a76":         "cortex_a76",
    "neoverse_n1":        "neoverse_n1_experimental",
    "apple_m1_firestorm": "apple_m1_firestorm_experimental",
    "apple_m1_icestorm":  "apple_m1_icestorm_experimental",
}

HERE = Path(__file__).resolve().parent
CLEAN = HERE.parent / "ntruplus1152_clean" / "src"

p = argparse.ArgumentParser()
p.add_argument("kernel")
p.add_argument("target", choices=sorted(TARGETS))
p.add_argument("--timeout", type=int, default=300)
p.add_argument("--split-factor", type=int, default=8)
p.add_argument("--ra-only", action="store_true",
               help="stop after register allocation; its output is the testable clean tier")
a = p.parse_args()

Target = __import__(f"slothy.targets.aarch64.{TARGETS[a.target]}",
                    fromlist=["x"])
if a.target.startswith("apple_m1"):
    # SLOTHY's M1 models lack the six signed widening multiply-accumulate
    # classes and subs_imm.  See dev/slothy_models/apple_m1_ntruplus.py for the
    # numbers and where they come from.
    sys.path.insert(0, str(HERE.parent / "slothy_models"))
    import apple_m1_ntruplus
    apple_m1_ntruplus.patch(Target)

out = HERE / a.target
out.mkdir(exist_ok=True)
build = out / "build"
build.mkdir(exist_ok=True)

src = CLEAN / f"{a.kernel}.sym.S"
loop = f"{a.kernel}_loop"
assert Path(Target.__file__).resolve().is_relative_to(SLOTHY_ROOT.resolve()), Target.__file__

report = {"kernel": a.kernel, "target": a.target,
          "arch": Arch.__file__, "model": Target.__file__,
          "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
          "stages": []}

cur = src
for stage in (("ra",) if a.ra_only else ("ra", "timing")):
    logging.basicConfig(level=logging.INFO, force=True,
                        handlers=[logging.FileHandler(build / f"{stage}.log", mode="w"), logging.StreamHandler()])
    s = Slothy(Arch, Target, logger=logging.getLogger(f"{a.kernel}/{a.target}/{stage}"))
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"] \
                             + ["v0", "v1", "v2", "v3", "v4"] \
                             + [f"v{i}" for i in range(8, 16)]
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = (stage == "ra")
    s.config.constraints.allow_reordering = (stage == "timing")
    s.config.constraints.allow_renaming = (stage == "ra")
    s.config.variable_size = True
    s.config.timeout = a.timeout
    s.config.sw_pipelining.enabled = (stage == "timing")
    if stage == "timing":
        s.config.sw_pipelining.minimize_overlapping = False
        s.config.sw_pipelining.allow_post = True
        s.config.constraints.stalls_first_attempt = 64
        s.config.split_heuristic = True
        s.config.split_heuristic_estimate_performance = False
        s.config.split_heuristic_factor = a.split_factor
        s.config.split_heuristic_stepsize = 0.05
    s.load_source_from_file(str(cur))
    t0 = time.monotonic()
    s.optimize_loop(loop)
    dst = build / f"{a.kernel}.{stage}.S"
    s.write_source_to_file(str(dst))
    report["stages"].append({"stage": stage, "seconds": round(time.monotonic() - t0, 1),
                             "output_sha256": hashlib.sha256(dst.read_bytes()).hexdigest()})
    cur = dst

final = out / f"{a.kernel}.S"
text = "\n".join(l.split("//")[0].rstrip() for l in cur.read_text().splitlines()
                 if l.split("//")[0].strip())
# The symbolic tier stays free of preprocessor directives so SLOTHY never has
# to parse them; the Mach-O underscore alias is added on the way out instead.
final.write_text(f"// SLOTHY, {a.target}, from ntruplus1152_clean/src/{a.kernel}.sym.S.\n"
                 f"// Do not edit; regenerate with `make {a.target}`.\n"
                 f"#ifdef __APPLE__\n#define {a.kernel}_kernel _{a.kernel}_kernel\n#endif\n"
                 + text + "\n")
report["final_sha256"] = hashlib.sha256(final.read_bytes()).hexdigest()
report["instructions"] = sum(1 for l in final.read_text().splitlines()
                             if l.startswith("    ") or l.startswith("\t"))
(build / f"{a.kernel}.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("kernel", "target", "stages", "instructions")}, indent=2))
