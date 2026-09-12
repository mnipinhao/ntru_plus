#!/usr/bin/env python3
"""Create isolated P11-A4 from A2 with exact two-way pure unfolding."""
import hashlib,shutil,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;BUILD=P/"build"
subprocess.run(["python3",str(P/"prepare_a2.py")],check=True);subprocess.run(["python3",str(P/"generate_a4.py")],check=True);subprocess.run(["python3",str(P/"check_a4.py")],check=True)
source=BUILD/"candidate-a2";candidate=BUILD/"candidate-a4"
if candidate.exists():shutil.rmtree(candidate)
shutil.copytree(source,candidate);shutil.copyfile(P/"candidate-route-a4.S",candidate/"gt864_p11_route_ternary.S")
manifest=candidate/"SOURCE-MANIFEST.sha256";paths=[line.split(None,1)[1] for line in manifest.read_text().splitlines() if line.strip()]
manifest.write_text("".join(f"{hashlib.sha256((candidate/path).read_bytes()).hexdigest()}  {path}\n" for path in paths));print(candidate)
