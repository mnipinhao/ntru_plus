.PHONY: prepare static-check

prepare:
	python3 prepare_producer.py
	python3 prepare_consumers.py
	python3 generate_linked.py

static-check: prepare
	python3 verify_boundary.py
	python3 audit_slothy.py
