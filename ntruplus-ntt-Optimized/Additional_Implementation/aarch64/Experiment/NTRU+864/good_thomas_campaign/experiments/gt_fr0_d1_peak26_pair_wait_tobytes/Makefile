PYTHON?=python3
CC?=cc
CFLAGS:=-O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes
BASE:=../gt_fr0_d1_pair_wait_tobytes
BUILD:=build
.PHONY:prepare check clean
prepare:
	$(PYTHON) prepare.py
check:prepare
	$(PYTHON) analyze.py
	$(CC) $(CFLAGS) -I$(BASE) -I$(BUILD) $(BASE)/harness.c $(BUILD)/pair_wait_tobytes.c -o $(BUILD)/test
	$(BUILD)/test
clean:
	rm -rf $(BUILD)
