CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build
TOP := ../gt_2x9x16_ld3_top_split
N16 := ../gt_ntt16_producer_range
FR := ../gt_boundary_cost_campaign

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

$(BUILD)/gt864_forward_barrett_tables.h: generate_tables.py | $(BUILD)
	python3 $< $@

$(BUILD)/test: test_gt864_forward_compose.c gt864_forward_compose.c \
		$(TOP)/gt864_top_split.s $(N16)/gt864_ntt16.c $(FR)/gt864_boundary.c \
		$(BUILD)/gt864_forward_barrett_tables.h
	$(CC) $(CFLAGS) -I$(BUILD) -o $@ test_gt864_forward_compose.c \
		gt864_forward_compose.c $(TOP)/gt864_top_split.s \
		$(N16)/gt864_ntt16.c $(FR)/gt864_boundary.c

check: $(BUILD)/test
	python3 prove_barrett.py > $(BUILD)/barrett.json
	python3 prove_schedule.py > $(BUILD)/schedule.json
	./$(BUILD)/test
	python3 -m json.tool $(BUILD)/barrett.json >/dev/null
	python3 -m json.tool $(BUILD)/schedule.json >/dev/null

clean:
	rm -f -r $(BUILD)
