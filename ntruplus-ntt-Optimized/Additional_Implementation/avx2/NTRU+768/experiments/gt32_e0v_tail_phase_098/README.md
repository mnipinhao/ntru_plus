# 098A — E0V RX-tail entry-phase search

This experiment searches one deterministic code-geometry variable: the entry
offset of `ntruplus768_pack_m_sum_highrange12699_avx2` within its page-aligned
RX tail.  It tests offsets 0 through 480 bytes in 32-byte increments.

Frozen production contract:

- source baseline `b2a4bea`;
- E0V current caller topology and arithmetic;
- 6592-byte frame and `h,r,m,c` slot order;
- 611-byte Encap caller reservation;
- all pre-existing hot text, rodata, constants, and the common helper object;
- CPU 1, fresh SUPERCOP processes, host-default ASLR enabled.

Only the caller-to-helper relative displacement and the helper page-relative
entry phase may change.  The tail is after `.bss`, so no pre-existing hot symbol
moves.

Run:

```sh
python3 tools/build.py
python3 tools/correctness.py
python3 tools/run_sweep.py
python3 tools/run_formal.py
python3 tools/run_confirmation.py
```

The completed decision is in `RESULTS.md`.  No phase was promoted.
