# P35 — KEM-only terminal-reset pruning

P35 implements the consumer-closed P34 decision with separate KEM-only main
and tail I16 helpers.  The centered general Inverse continues to call the
production reset-complete helpers.  Run `generate.py`, `oracle.py`, and
`optimize.py`; isolated integration and Pi 5 evidence are recorded in
`RESULTS.md` after the physical gate.
