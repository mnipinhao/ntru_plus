CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Werror
PYTHON ?= python3

.PHONY: check clean

check: build/test_delayed_twist
	$(PYTHON) prove_delayed_twist.py
	./build/test_delayed_twist

build/test_delayed_twist: test_delayed_twist.c
	mkdir -p build
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f build/test_delayed_twist
