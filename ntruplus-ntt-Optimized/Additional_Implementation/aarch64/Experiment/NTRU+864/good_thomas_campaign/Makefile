PYTHON ?= python3

.PHONY: check check-reference check-registry check-root-topology check-scalar-reference check-montgomery-reference check-radix3-orientation check-ld3-top-split check-layout-consumer-abi check-tile-abi-search check-boundary-cost check-fr0-realization check-ntt16-producer-range check-fr0-basemul check-fr0-inverse

check: check-registry check-root-topology check-scalar-reference check-montgomery-reference check-radix3-orientation check-ld3-top-split check-layout-consumer-abi check-tile-abi-search check-boundary-cost check-fr0-realization check-ntt16-producer-range check-fr0-basemul check-fr0-inverse

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

check-layout-consumer-abi:
	$(MAKE) -C experiments/gt_layout_consumer_abi_gate check PYTHON=$(PYTHON)

check-tile-abi-search:
	$(MAKE) -C experiments/gt_transform_domain_tile_abi_search check PYTHON=$(PYTHON)

check-boundary-cost:
	$(MAKE) -C experiments/gt_boundary_cost_campaign check PYTHON=$(PYTHON)

check-fr0-realization:
	$(MAKE) -C experiments/gt_fr0_kernel_realization check PYTHON=$(PYTHON)

check-ntt16-producer-range:
	$(MAKE) -C experiments/gt_ntt16_producer_range check PYTHON=$(PYTHON)

check-fr0-basemul:
	$(MAKE) -C experiments/gt_fr0_basemul_arithmetic check PYTHON=$(PYTHON)

check-fr0-inverse:
	$(MAKE) -C experiments/gt_fr0_inverse_consumer check PYTHON=$(PYTHON)
