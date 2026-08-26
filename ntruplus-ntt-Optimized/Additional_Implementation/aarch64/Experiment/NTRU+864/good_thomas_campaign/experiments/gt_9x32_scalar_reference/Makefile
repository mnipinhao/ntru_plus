CC ?= cc
CFLAGS ?= -O2 -std=c99 -Wall -Wextra -Wpedantic -Werror
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_gt864_reference

.PHONY: check clean

check: $(TARGET)
	./$(TARGET)

$(TARGET): gt864_reference.c gt864_reference.h test_gt864_reference.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ gt864_reference.c test_gt864_reference.c

clean:
	$(RM) -r $(BUILD_DIR)
