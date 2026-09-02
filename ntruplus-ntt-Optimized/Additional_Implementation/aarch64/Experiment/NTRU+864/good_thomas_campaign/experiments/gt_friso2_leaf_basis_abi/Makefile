CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build
TARGET := $(BUILD)/test_gt864_friso2
PROOF := $(BUILD)/proof.json
INV_TABLES := $(BUILD)/gt864_fr0_inverse_tables.h
BASEMUL_TABLES := $(BUILD)/gt864_fr0_basemul_tables.h
TOP := ../gt_2x9x16_ld3_top_split
NTT16 := ../gt_ntt16_producer_range
BOUNDARY := ../gt_boundary_cost_campaign
BASEMUL := ../gt_fr0_basemul_arithmetic
INVERSE := ../gt_fr0_inverse_consumer
REFERENCE := ../../../../../../../Reference_Implementation/NTRU+864

.PHONY: check clean

check: $(PROOF) $(TARGET)
	$(PYTHON) -m json.tool $(PROOF) >/dev/null
	./$(TARGET)

$(BUILD):
	mkdir -p $@

$(PROOF): prove_friso2.py | $(BUILD)
	$(PYTHON) $< > $@

$(INV_TABLES): $(INVERSE)/generate_tables.py | $(BUILD)
	$(PYTHON) $< --header $@ >/dev/null

$(BASEMUL_TABLES): $(BASEMUL)/generate_tables.py | $(BUILD)
	$(PYTHON) $< --header $@ >/dev/null

$(TARGET): test_gt864_friso2.c gt864_friso2.c gt864_friso2.h \
           $(INV_TABLES) $(BASEMUL_TABLES) \
           $(TOP)/gt864_top_split.s $(NTT16)/gt864_ntt16.c \
           $(BOUNDARY)/gt864_boundary.c $(BASEMUL)/gt864_fr0_basemul.c \
           $(INVERSE)/gt864_fr0_inverse.c $(REFERENCE)/ntt.c
	$(CC) $(CFLAGS) -I. -I$(BUILD) -I$(TOP) -I$(NTT16) \
		-I$(BOUNDARY) -I$(BASEMUL) -I$(INVERSE) -I$(REFERENCE) \
		-o $@ test_gt864_friso2.c gt864_friso2.c \
		$(TOP)/gt864_top_split.s $(NTT16)/gt864_ntt16.c \
		$(BOUNDARY)/gt864_boundary.c $(BASEMUL)/gt864_fr0_basemul.c \
		$(INVERSE)/gt864_fr0_inverse.c $(REFERENCE)/ntt.c

clean:
	$(RM) -r $(BUILD)
