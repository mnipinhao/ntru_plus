PYTHON?=python3
CC?=cc
CFLAGS:=-O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes
BUILD:=build
.PHONY: prepare check clean
prepare:
	$(PYTHON) prepare.py
check: prepare
	$(CC) $(CFLAGS) -I. -I$(BUILD) harness.c $(BUILD)/pair_wait_tobytes.c -o $(BUILD)/test
	$(BUILD)/test
clean:
	rm -rf $(BUILD)
