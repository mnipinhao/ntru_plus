PYTHON ?= python3
.PHONY: check remote audit
check:
	$(PYTHON) -m py_compile run_pi5.py
remote: check
	$(PYTHON) run_pi5.py
audit: check
	$(PYTHON) -m json.tool build/summary.json >/dev/null
	grep -q 'p3b4_kem=pass cases=8 mismatches=0' build/raw/build-correctness-object.log
	grep -q 'gt_bytes_poly_tobytes' build/raw/build-correctness-object.log
	grep -q 'gt_bytes_poly_frombytes' build/raw/build-correctness-object.log
