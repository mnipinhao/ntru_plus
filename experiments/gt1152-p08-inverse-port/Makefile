PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd
FWD := ../gt1152-p04-forward-8bank
SRC := inverse.c inverse16_tail.c inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S
ASM := $(FWD)/ntt.S $(FWD)/ntt_top.S $(FWD)/ntt_tail.S $(FWD)/ntt9.S

.PHONY: check generate verify clean

check: verify

generate:
	$(PYTHON) ../gt1152-p07-inverse/generate_driver.py
	$(PYTHON) ../gt1152-p07-inverse/generate_kernels.py

harness: harness.c $(SRC)
	$(CC) $(CFLAGS) -I. harness.c $(SRC) $(ASM) -o $@

verify: harness
	$(PYTHON) verify.py

clean:
	$(RM) harness verify-report.json
	$(RM) -r __pycache__ harness.dSYM
