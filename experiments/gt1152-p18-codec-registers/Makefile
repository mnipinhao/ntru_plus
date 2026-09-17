PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd

.PHONY: check verify clean

check: verify

codec_pairs.h: generate_pairs.py
	$(PYTHON) generate_pairs.py

harness: harness.c pack.c shim.c pack.h pack_asm.h codec_pairs.h
	$(CC) $(CFLAGS) -I. harness.c pack.c shim.c -o $@

verify: harness
	$(PYTHON) verify.py

clean:
	$(RM) harness verify-report.json
	$(RM) -r __pycache__ harness.dSYM
