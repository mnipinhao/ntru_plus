# P13-B — fused Inverse16 terminal scale and top CRT

This experiment replaces only the six-call `lazy_i16` main kernel.  It keeps
the tail, natural scatter, P8 raw-to-ternary consumer, wrapper and scratch
boundaries unchanged.  `RESULTS.md` is the decision record; `generate.py` and
`prove.py` define the exact DAG, tables and range proof.  `candidate.sym.S` is
the readable source of truth and `candidate.opt.S` is the tested Slothy output.

Reproduce the algebra/oracle with `python3 generate.py`, `python3 prove.py`,
and `python3 oracle.py`.  Slothy uses `PYTHONPATH=/Users/chenpinhao/slothy`
with `/Users/chenpinhao/slothy_and_ra/.venv/bin/python optimize.py`, followed
by `optimize.py --timing`.  Pi evidence is in `pi-results.json`; large build
products and raw run files are ignored.
