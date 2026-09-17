PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd

.PHONY: check verify clean

check: verify

harness: harness.c pack.c pack.h gt_perm.h
	$(CC) $(CFLAGS) -I. harness.c pack.c -o $@

verify: harness
	$(PYTHON) verify.py

clean:
	$(RM) harness verify-report.json
	$(RM) -r __pycache__ harness.dSYM
