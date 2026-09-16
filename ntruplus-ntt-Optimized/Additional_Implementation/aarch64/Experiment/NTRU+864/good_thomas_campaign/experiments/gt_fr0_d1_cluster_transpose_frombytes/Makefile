PYTHON?=python3
CC?=cc
CFLAGS:=-O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes
BUILD:=build
.PHONY:prepare check clean
prepare:
	$(PYTHON) ../gt_fr0_d1_cluster_tbl_frombytes/prepare.py
	$(PYTHON) prepare.py
check:prepare
	$(CC) $(CFLAGS) -I. -I$(BUILD) -I../gt_fr0_d1_cluster_tbl_frombytes/build harness.c $(BUILD)/cluster_transpose_frombytes.c -o $(BUILD)/test
	$(BUILD)/test
clean:
	rm -rf $(BUILD)
