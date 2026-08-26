CC ?= cc
CFLAGS ?= -O2 -std=c99 -Wall -Wextra -Wpedantic -Werror
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_gt864_montgomery
SCALAR_REF := ../gt_9x32_scalar_reference
CURRENT_REF := ../../../../../../../Reference_Implementation/NTRU+864

.PHONY: check clean

check: $(TARGET)
	./$(TARGET)

$(TARGET): gt864_montgomery.c gt864_montgomery.h test_gt864_montgomery.c \
	$(SCALAR_REF)/gt864_reference.c $(SCALAR_REF)/gt864_reference.h \
	$(CURRENT_REF)/ntt.c $(CURRENT_REF)/ntt.h $(CURRENT_REF)/params.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(SCALAR_REF) -I$(CURRENT_REF) -o $@ \
		gt864_montgomery.c test_gt864_montgomery.c \
		$(SCALAR_REF)/gt864_reference.c $(CURRENT_REF)/ntt.c

clean:
	$(RM) -r $(BUILD_DIR)
