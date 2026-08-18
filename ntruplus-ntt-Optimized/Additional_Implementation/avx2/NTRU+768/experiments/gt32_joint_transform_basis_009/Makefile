PYTHON ?= python3
OUTPUT := generated/joint_transform_basis_gate.json

.PHONY: all generate check

all: check

generate:
	$(PYTHON) tools/generate_joint_basis_gate.py --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) tools/generate_joint_basis_gate.py --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
