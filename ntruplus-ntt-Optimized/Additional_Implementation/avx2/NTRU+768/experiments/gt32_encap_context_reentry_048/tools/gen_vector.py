#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--rsp", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
text = a.rsp.read_text()
value = re.search(r"^pk = ([0-9A-F]+)$", text, re.M).group(1)
data = bytes.fromhex(value)
coins = bytes((17 * i + 3) & 255 for i in range(96))

def arr(name, body):
    values = ",".join("0x%02x" % x for x in body)
    return f"static const unsigned char {name}[{len(body)}] = {{\n {values}\n}};\n"

a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(
    "#ifndef VECTOR_048_H\n#define VECTOR_048_H\n"
    + arr("kat_pk", data)
    + arr("test_coins", coins)
    + "#endif\n"
)
