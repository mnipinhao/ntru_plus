# Shared GT9x16 research support

This directory contains parameter-neutral descriptions and generators for the
864/1152 AVX2 experiments. It is research tooling, not production code.

`model.py` describes only the decomposition and index bijection. It deliberately
does not guess arithmetic constants. `generate_gt9x16.py` validates that model
and writes reproducible JSON metadata for an experiment. Generated assembly or
tables must be reviewed against an independent reference before use.

`EDGE-CONTRACT.md` defines the architecture-neutral producer/consumer
representation-edge schema used by G1. It keeps permutation, terminal basis,
frequency gauge, scale, absorption points, runtime debt, and range obligations
separate so AVX2 and NEON can share algebra without sharing a cost model.

Production sources under `clean/` must not import Python or depend on this tree.
