# SLOTHY runs for NTRU+1152, one directory per microarchitecture.
#
# Modelled on mlkem-native's dev/aarch64_opt/src/Makefile, with the target
# microarchitecture as a variable rather than a constant: SUPERCOP selects among
# sibling implementations per host, so shipping more than one is useful.
#
#   make cortex_a76          the Pi 5; the only target measurable in this repo
#   make apple_m1_firestorm  the local development host
#   make neoverse_n1         mlkem-native's target, for comparison
#   make all

PYTHON      ?= /Users/chenpinhao/slothy_and_ra/.venv/bin/python
SLOTHY_ROOT ?= /Users/chenpinhao/slothy
TIMEOUT     ?= 300
SPLIT       ?= 8

KERNELS = basemul_rinv_lane
TARGETS = cortex_a76 neoverse_n1 apple_m1_firestorm

CLEAN_SRC = ../ntruplus1152_clean/src

.PHONY: all clean regen $(TARGETS)

all: $(TARGETS)

# Regenerate the clean tier first; SLOTHY's input must match the generator.
regen:
	$(PYTHON) ../ntruplus1152_clean/generate.py

define TARGET_RULE
$(1): regen
	@for k in $$(KERNELS); do \
	  echo "--- $$$$k -> $(1) ---"; \
	  SLOTHY_ROOT=$$(SLOTHY_ROOT) $$(PYTHON) optimize.py $$$$k $(1) \
	      --timeout $$(TIMEOUT) --split-factor $$(SPLIT) || exit 1; \
	done
endef
$(foreach t,$(TARGETS),$(eval $(call TARGET_RULE,$(t))))

clean:
	-$(RM) -r $(addsuffix /build,$(TARGETS))
