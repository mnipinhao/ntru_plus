PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build
TARGET := $(BUILD)/test_full_polymul
TABLES := $(BUILD)/gt864_friso2_inverse_tables.h
FR0_TABLES := $(BUILD)/gt864_fr0_inverse_tables.h
FWD := ../gt_friso2_forward_absorption
BASEMUL := ../gt_friso2_basemul_cycle
FRISO2 := ../gt_friso2_leaf_basis_abi
INV := ../gt_fr0_inverse_consumer
TOP := ../gt_2x9x16_ld3_top_split

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

$(TABLES): generate_tables.py | $(BUILD)
	$(PYTHON) generate_tables.py --header $@ > $(BUILD)/factor-proof.json

$(FR0_TABLES): $(INV)/generate_tables.py | $(BUILD)
	$(PYTHON) $(INV)/generate_tables.py --header $@ > $(BUILD)/fr0-map.json

$(TARGET): test_full_polymul.c gt864_friso2_inverse.c \
		gt864_friso2_inverse.h $(TABLES) $(FR0_TABLES) \
		$(FWD)/gt864_forward_poly_ntt_friso2.S \
		$(FWD)/gt864_forward_six_bank_friso2.S \
		$(TOP)/gt864_top_split.s \
		$(BASEMUL)/gt864_friso2_basemul_neon.c \
		$(FRISO2)/gt864_friso2.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(BUILD) -I$(INV) -I$(BASEMUL) -I$(FRISO2) \
		-o $@ test_full_polymul.c gt864_friso2_inverse.c \
		$(FWD)/gt864_forward_poly_ntt_friso2.S \
		$(FWD)/gt864_forward_six_bank_friso2.S \
		$(TOP)/gt864_top_split.s \
		$(BASEMUL)/gt864_friso2_basemul_neon.c \
		$(FRISO2)/gt864_friso2.c

check: $(TARGET)
	$(PYTHON) -m json.tool $(BUILD)/factor-proof.json >/dev/null
	$(PYTHON) -m json.tool $(BUILD)/fr0-map.json >/dev/null
	$(PYTHON) prove_ranges.py > $(BUILD)/range-proof.json
	$(PYTHON) -m json.tool $(BUILD)/range-proof.json >/dev/null
	$(PYTHON) cost_ledger.py > $(BUILD)/cost-ledger.json
	$(PYTHON) -m json.tool $(BUILD)/cost-ledger.json >/dev/null
	$(TARGET)

clean:
	$(RM) -r $(BUILD)
