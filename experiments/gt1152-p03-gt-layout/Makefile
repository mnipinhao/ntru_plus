PYTHON ?= python3
CC ?= cc
GT864 := ../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd

.PHONY: check measure predict clean

check: measure predict

dump864: dump864.c darwin_shim.S
	$(CC) $(CFLAGS) -I$(GT864) dump864.c darwin_shim.S \
	  $(GT864)/ntt.S $(GT864)/ntt_top.S $(GT864)/ntt_tail.S $(GT864)/ntt9.S -o $@

measure: dump864
	$(PYTHON) probe864.py

predict: measure
	$(PYTHON) predict1152.py

clean:
	$(RM) dump864 perm864.txt layout-report.json
	$(RM) -r __pycache__ dump864.dSYM
