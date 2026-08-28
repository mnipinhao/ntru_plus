CC ?= cc
CFLAGS ?= -O2 -std=c99 -Wall -Wextra -Wpedantic -Werror
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_gt864_top_split

.PHONY: check inspect clean

check: $(TARGET)
	./$(TARGET)

inspect: $(TARGET)
	objdump -d $(TARGET) | sed -n '/gt864_top_split_ld3/,/ret/p'

$(TARGET): gt864_top_split.s gt864_top_split.h test_gt864_top_split.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ gt864_top_split.s test_gt864_top_split.c

clean:
	$(RM) -r $(BUILD_DIR)
