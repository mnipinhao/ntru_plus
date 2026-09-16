# T7-N0 — Official-style canonicalization lowering

Status: **investigate**. Production is unchanged.

This experiment changes only the final signed-representative correction in all
four GT864 ToBytes cores:

```asm
sshr sign.8h, row.8h, #15
and  sign.16b, sign.16b, q.16b
add  row.8h, row.8h, sign.8h
```

becomes the destructive two-instruction form:

```asm
cmlt sign.8h, row.8h, #0
mls  row.8h, sign.8h, q.8h
```

`CMLT` produces `0` or `-1`. Consequently `MLS row, sign, q` leaves a
non-negative row unchanged and adds `q` to a negative row. This is exactly the
same map as the old three-instruction sequence.

There are 18 groups per core. The four static regions therefore lose 72
instructions. A complete ToBytes call executes four saved-pair cores and two
pair+merge cores, so its exact dynamic reduction is 108 vector instructions.
No load, store, pointer update, scratch byte, route table, packing rule, or wire
position changes.

## Reproduce local gates

```sh
python3 generate.py
python3 static_checks.py
python3 audit.py --exhaustive
PYTHONPATH=/Users/chenpinhao/slothy \
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python run_slothy.py allocate
PYTHONPATH=/Users/chenpinhao/slothy \
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python run_slothy.py timing
python3 audit.py --exhaustive --physical
python3 prepare_package.py
python3 ../verify-production-mac.py build/package build/mac-validation
```

The Pi 5 isolated/full-KEM benchmark is deliberately a later promotion gate.
