PYTHON ?= python3

.PHONY: check check-reference check-registry check-root-topology check-scalar-reference check-montgomery-reference check-radix3-orientation check-ld3-top-split

check: check-registry check-root-topology check-scalar-reference check-montgomery-reference check-radix3-orientation check-ld3-top-split

check-reference: check-montgomery-reference

check-registry:
	$(PYTHON) tools/check_experiment_registry.py

check-root-topology:
	$(MAKE) -C experiments/gt_9x32_root_gate check PYTHON=$(PYTHON)

check-scalar-reference:
	$(MAKE) -C experiments/gt_9x32_scalar_reference check

check-montgomery-reference:
	$(MAKE) -C experiments/gt_9x32_montgomery_reference check

check-radix3-orientation:
	$(MAKE) -C experiments/gt_9x32_radix3_orientation_reference check

check-ld3-top-split:
	$(MAKE) -C experiments/gt_2x9x16_ld3_top_split check
