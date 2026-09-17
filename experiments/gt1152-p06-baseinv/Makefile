PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd
FWD := ../gt1152-p04-forward-8bank
ASM := $(FWD)/ntt.S $(FWD)/ntt_top.S $(FWD)/ntt_tail.S $(FWD)/ntt9.S

.PHONY: check verify clean

check: verify

harness: harness.c inverse.c inverse.h base_tables.h
	$(CC) $(CFLAGS) -I. harness.c inverse.c $(ASM) -o $@

verify: harness
	$(PYTHON) verify.py

clean:
	$(RM) harness verify-report.json
	$(RM) -r __pycache__ harness.dSYM
