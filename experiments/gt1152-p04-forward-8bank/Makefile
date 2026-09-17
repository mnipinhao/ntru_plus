PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd
ASM := ntt.S ntt_top.S ntt_tail.S ntt9.S

.PHONY: check generate verify bound clean

check: verify bound

generate ntt9.S:
	$(PYTHON) generate_ntt9.py

harness: harness.c $(ASM)
	$(CC) $(CFLAGS) harness.c $(ASM) -o $@

probe_tail: probe_tail.c ntt_tail.S
	$(CC) $(CFLAGS) probe_tail.c ntt_tail.S -o $@

verify: harness
	$(PYTHON) verify.py

bound: harness verify
	$(PYTHON) bound.py

clean:
	$(RM) harness probe_tail verify-report.json forward-bound.json
	$(RM) -r __pycache__ harness.dSYM probe_tail.dSYM
