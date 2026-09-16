#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(path, needles):
    text=(ROOT/path).read_text()
    for n in needles:
        if n not in text: raise SystemExit(f"{path}: missing {n!r}")
require("gt864_secure_clear.h",("GT_SECURE_CLEAR_AUDIT_HOOK","explicit_bzero","volatile uint8_t *p"))
require("kem.c",("secure_clear(&f, sizeof f);","secure_clear(&ginv, sizeof ginv);",
                 "secure_clear(msg,sizeof msg);","secure_clear(&m,sizeof m);"))
require("symmetric.c",("secure_clear(data, sizeof data);",))
require("gt864_native_public.S",("movi v8.16b, #0","movi v31.16b, #0"))
print("P54 production zeroization source coverage: ok")
