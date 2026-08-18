.PHONY: all check clean

PYTHON ?= python3
OUT := generated/joint_transform_superspace_gate.json

all: $(OUT)

$(OUT): tools/generate_superspace_gate.py
	@mkdir -p generated
	$(PYTHON) $< --output $@

check: $(OUT)
	$(PYTHON) tools/generate_superspace_gate.py --output /tmp/joint_transform_superspace_gate.check.json
	diff -u $(OUT) /tmp/joint_transform_superspace_gate.check.json

clean:
	rm -f $(OUT)
