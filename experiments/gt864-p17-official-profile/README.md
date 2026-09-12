# P17 — post-P13/P16 selected-Official profiler checkpoint

P17 is a measurement-only gate.  It compares current GT864 production with
the user-selected SUPERCOP 20260831 AArch64 implementation and refreshes the
22-group KEM call-site profiler after P13-B/C and P16.

The prepared runner reuses the reviewed P12 harnesses, but injects the current
production source and revision into an isolated bundle.  Raw logs and binaries
remain under the remote run directory and local ignored `build/`.

Result: passed. Current GT production is faster than the selected Official
implementation in Keygen, Encaps and Decaps. The remaining common positive
cycle gap is ToBytes; see `RESULTS.md` for the same-boundary profile and the
updated work queue.

```sh
python3 run_pi5.py
```
