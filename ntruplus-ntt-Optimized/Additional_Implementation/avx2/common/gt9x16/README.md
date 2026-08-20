# Shared GT9x16 research support

This directory contains parameter-neutral descriptions and generators for the
864/1152 AVX2 experiments. It is research tooling, not production code.

`model.py` describes only the decomposition and index bijection. It deliberately
does not guess arithmetic constants. `generate_gt9x16.py` validates that model
and writes reproducible JSON metadata for an experiment. Generated assembly or
tables must be reviewed against an independent reference before use.

Production sources under `clean/` must not import Python or depend on this tree.
