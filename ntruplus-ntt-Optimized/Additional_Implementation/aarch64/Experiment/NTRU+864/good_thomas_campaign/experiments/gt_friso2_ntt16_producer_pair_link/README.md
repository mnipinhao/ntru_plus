# M5U-CF5-A — NTT16 producer to CF3 pair link

This experiment closes the register/layout boundary between the frozen M5R-D
NTT16 producer and the four CF3 scaled two-block NTT9 consumers.

It intentionally avoids one monolithic Slothy solve.  Slothy first schedules a
345-instruction producer with eighteen symbolic live-outs, then each
279/309-instruction consumer is solved with those exact physical registers as
fixed live-ins.  `v13`, `v14`, and `v15` remain preserved across every bank.

The generated `gt864_forward_six_bank_cf5.S` duplicates the producer four
times only to close linked arithmetic correctness without adding dynamic
handoff instructions.  It is not the code-size-faithful benchmark candidate.

Run:

```sh
make static-check
```

Slothy was run on `pinhao@172.25.166.141:51208` with
`/home/pinhao/slothy/venv/bin/python`.  Linked correctness was run on the
Cortex-A76 Pi 5 and is recorded in `pi5-correctness.log`.
