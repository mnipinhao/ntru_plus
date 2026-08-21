#!/usr/bin/env python3
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--hash", type=Path, required=True)
p.add_argument("--shake", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()

def array(name, data):
    body = ",".join(f"0x{x:02x}" for x in data)
    return f"static const unsigned char {name}[] = {{{body}}};\n"

a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text("#ifndef GT053_TEMPLATES_H\n#define GT053_TEMPLATES_H\n" +
                    array("hash_template_bytes", a.hash.read_bytes()) +
                    array("shake_template_bytes", a.shake.read_bytes()) +
                    "#endif\n")

