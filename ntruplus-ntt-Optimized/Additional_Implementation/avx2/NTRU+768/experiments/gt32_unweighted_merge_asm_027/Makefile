CC ?= gcc
CFLAGS := -O3 -mavx2 -Wall -Wextra -Werror -std=c11
BASE := ../avx2_gt16_quadratic_official_001
INCLUDES := -Isrc -I$(BASE)/src -I$(BASE)/generated
ORACLES := $(BASE)/src/qbm_intrinsic.c $(BASE)/src/inverse_stage1_intrinsic.c

.PHONY: all check clean

all: check

generated/merge_basis_asm.S generated/asm_metadata.json: tools/generate_asm.py $(BASE)/generated/quadratic-constants.h
	python3 tools/generate_asm.py

generated/exact_conjugation_gate.json: tools/prove_exact_conjugation.py $(BASE)/generated/quadratic-constants.h
	python3 tools/prove_exact_conjugation.py

build/merge_normal.o: generated/merge_basis_asm.S
	mkdir -p build
	$(CC) $(CFLAGS) -c $< -o $@

build/merge_reversed.o: generated/merge_basis_asm.S
	mkdir -p build
	$(CC) $(CFLAGS) -DREVERSED=1 -c $< -o $@

build/test_normal: tests/test_merge_basis.c build/merge_normal.o
	$(CC) $(CFLAGS) $(INCLUDES) $< $(ORACLES) build/merge_normal.o -o $@

build/test_reversed: tests/test_merge_basis.c build/merge_reversed.o
	$(CC) $(CFLAGS) $(INCLUDES) $< $(ORACLES) build/merge_reversed.o -o $@

check: generated/exact_conjugation_gate.json build/test_normal build/test_reversed
	build/test_normal
	build/test_reversed
	python3 -m json.tool generated/exact_conjugation_gate.json >/dev/null
	python3 -m json.tool generated/asm_metadata.json >/dev/null

clean:
	rm -rf build
