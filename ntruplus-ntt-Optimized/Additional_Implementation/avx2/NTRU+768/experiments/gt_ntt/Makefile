CC ?= clang
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing

REFERENCE = ../../../../aarch64/NTRU+768/ntt.c
SOURCES = gt_ntt_avx2.c gt_ntt_tables.c test_gt_ntt.c $(REFERENCE)
HEADERS = gt_ntt_avx2.h gt_ntt_tables.h
BUILD = build

ifeq ($(shell uname -s),Darwin)
ARCHFLAGS = -arch x86_64
RUNNER = arch -x86_64
endif

.PHONY: all test compile check sanitize asm clean

all: test

test: $(BUILD)/test_gt_ntt
	$(RUNNER) $<

compile: $(BUILD)/test_gt_ntt

check:
	$(CC) $(CFLAGS) $(ARCHFLAGS) -Werror -I. -fsyntax-only \
		gt_ntt_avx2.c gt_ntt_tables.c test_gt_ntt.c

sanitize: $(BUILD)/test_gt_ntt_sanitize
	$(RUNNER) $<

$(BUILD)/test_gt_ntt: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -o $@ $(SOURCES)

$(BUILD)/test_gt_ntt_sanitize: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -I. -o $@ $(SOURCES)

asm: $(BUILD)/gt_ntt_avx2.s

$(BUILD)/gt_ntt_avx2.s: gt_ntt_avx2.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_ntt_avx2.c

clean:
	$(RM) -r $(BUILD)
