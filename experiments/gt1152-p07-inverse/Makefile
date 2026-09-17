PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -std=c11 -march=armv8-a+simd
GT := ../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864
SHIM := ../gt1152-p03-gt-layout/darwin_shim.S

.PHONY: check analyze verify864 clean

check: analyze verify864

probe864: probe864.c
	$(CC) $(CFLAGS) -I$(GT) probe864.c \
	  $(GT)/inverse_api.c $(GT)/ntt_api.c $(GT)/base.c \
	  $(GT)/inverse.S $(GT)/inverse9.S $(GT)/inverse16.S $(GT)/inverse16_tail.S \
	  $(GT)/crepmod3_raw.S $(GT)/baseinv_num.S $(GT)/baseinv_prefix.S \
	  $(GT)/baseinv_inverse.S $(GT)/baseinv_recover.S $(GT)/baseinv_finish.S \
	  $(GT)/basemul_rinv.S $(GT)/ntt.S $(GT)/ntt_top.S $(GT)/ntt_tail.S \
	  $(GT)/ntt9.S $(SHIM) -o $@

analyze:
	$(PYTHON) analyze.py

verify864: probe864
	$(PYTHON) verify864.py

clean:
	$(RM) probe864 analysis-report.json verify864-report.json
	$(RM) -r __pycache__ probe864.dSYM
