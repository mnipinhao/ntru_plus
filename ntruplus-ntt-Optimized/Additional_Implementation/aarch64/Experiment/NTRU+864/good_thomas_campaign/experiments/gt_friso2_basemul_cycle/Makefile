CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build

.PHONY: check clean proof remote-audit

check: proof $(BUILD)/test_gt864_friso2_basemul
	./$(BUILD)/test_gt864_friso2_basemul

proof: | $(BUILD)
	$(PYTHON) prove_ranges.py > $(BUILD)/range.json
	$(PYTHON) -m json.tool $(BUILD)/range.json >/dev/null

remote-audit:
	$(PYTHON) audit_remote.py > $(BUILD)/remote-audit.json
	$(PYTHON) -m json.tool $(BUILD)/remote-audit.json >/dev/null

$(BUILD):
	mkdir -p $@

$(BUILD)/test_gt864_friso2_basemul: test_gt864_friso2_basemul.c \
		gt864_friso2_basemul_neon.c gt864_friso2_basemul_neon.h | $(BUILD)
	$(CC) $(CFLAGS) -o $@ test_gt864_friso2_basemul.c \
		gt864_friso2_basemul_neon.c

clean:
	rm -f -r $(BUILD)
