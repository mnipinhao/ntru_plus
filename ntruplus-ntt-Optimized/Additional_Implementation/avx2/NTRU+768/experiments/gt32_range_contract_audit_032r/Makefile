ROOT := ../..
CC ?= gcc
CFLAGS := -O3 -mavx2 -march=native -mtune=native -fomit-frame-pointer \
	-ffunction-sections -fdata-sections -Wall -Wextra -Wpedantic
LDFLAGS := -Wl,--gc-sections
BUILD := build

.PHONY: check clean

check: generated/range_audit.json $(BUILD)/test_032r
	./$(BUILD)/test_032r
	python3 tools/generate_range_audit.py --pack $(ROOT)/pack.s \
		--bound 20296 --output generated/range_audit.json --check

generated/range_audit.json: tools/generate_range_audit.py $(ROOT)/pack.s
	@mkdir -p generated
	python3 tools/generate_range_audit.py --pack $(ROOT)/pack.s \
		--bound 20296 --output $@

$(BUILD)/test_032r: tests/test_032r.c $(ROOT)/pack.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ $^

clean:
	$(RM) -r $(BUILD)
