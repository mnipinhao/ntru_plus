OFFICIAL_ROOT ?= ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
CC ?= gcc
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -mavx2
BUILD := build

.PHONY: d4-aos-ref-test d4-aos-generated-check d4-aos-api-coverage d4-aos-avx2-proto-test d4-aos-f32x3-ref-test d4-aos-f32x3-ntt32-stage0-test d4-aos-f32x3-ct-l0-l2-generated-check d4-aos-f32x3-ct-l3-l4-generated-check d4-aos-f32x3-dft3-generated-check d4-aos-f32x3-terminal-generated-check d4-aos-f32x3-ct-merged-l0-l2-asm-test d4-aos-f32x3-ntt32-ct-merged-asm-test d4-aos-f32x3-compact-dft3-test d4-aos-f32x3-complete-inverse-asm-test d4-aos-f32x3-complete-inverse-bench d4-aos-f32x3-compact-dft3-bench d4-aos-f32x3-ntt32-ct-merged-bench official-invntt-deconstruction clean
d4-aos-generated-check:
	python3 tools/d4aos_metadata.py --check-dir generated
d4-aos-ref-test: d4-aos-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_ref d4_aos_ref.c test_d4_aos_ref.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_ref
d4-aos-api-coverage:
	test -f D4_AOS_BACKEND_COVERAGE.md
	rg -q 'unavailable' D4_AOS_BACKEND_COVERAGE.md
	rg -q 'native-d4aos-reference' D4_AOS_BACKEND_COVERAGE.md
d4-aos-avx2-proto-test: d4-aos-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_avx2_proto d4_aos_ref.c d4_aos_avx2_proto.c test_d4_aos_avx2_proto.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_avx2_proto
d4-aos-f32x3-ref-test: d4-aos-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_ref d4_aos_ref.c d4_aos_f32x3_ref.c test_d4_aos_f32x3_ref.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_ref
d4-aos-f32x3-ntt32-stage0-test:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_stage0 d4_aos_f32x3_ref.c d4_aos_f32x3_invntt_avx2_asm.S test_d4_aos_f32x3_stage0.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_stage0
d4-aos-f32x3-ct-l0-l2-generated-check:
	python3 tools/generate_f32x3_ct_l0_l2.py --check-dir generated/f32x3_ct_l0_l2
d4-aos-f32x3-ct-l3-l4-generated-check:
	python3 tools/generate_f32x3_ct_l0_l2.py --l3-l4-check-dir generated/f32x3_ct_l3_l4
d4-aos-f32x3-dft3-generated-check:
	python3 tools/generate_f32x3_ct_l0_l2.py --dft3-check-dir generated/f32x3_dft3
d4-aos-f32x3-terminal-generated-check:
	python3 tools/generate_f32x3_ct_l0_l2.py --terminal-check-dir generated/f32x3_terminal
d4-aos-f32x3-ct-merged-l0-l2-asm-test: d4-aos-f32x3-ct-l0-l2-generated-check d4-aos-f32x3-ntt32-stage0-test
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -DD4AOS_F32X3_ASM_CHECKPOINTS=1 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_ct_l0_l2 d4_aos_f32x3_ref.c d4_aos_f32x3_invntt_avx2_asm.S test_d4_aos_f32x3_ct_l0_l2.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_ct_l0_l2
d4-aos-f32x3-ntt32-ct-merged-asm-test: d4-aos-f32x3-ct-merged-l0-l2-asm-test d4-aos-f32x3-ct-l3-l4-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -DD4AOS_F32X3_ASM_CHECKPOINTS=1 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_ct_merged d4_aos_f32x3_ref.c d4_aos_f32x3_invntt_avx2_asm.S test_d4_aos_f32x3_ct_merged.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_ct_merged
d4-aos-f32x3-compact-dft3-test: d4-aos-f32x3-ntt32-ct-merged-asm-test d4-aos-f32x3-dft3-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_dft3 d4_aos_ref.c d4_aos_f32x3_ref.c d4_aos_f32x3_invntt_avx2_asm.S d4_aos_f32x3_dft3_probe.c test_d4_aos_f32x3_dft3.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_dft3
d4-aos-f32x3-complete-inverse-asm-test: d4-aos-f32x3-compact-dft3-test d4-aos-f32x3-terminal-generated-check
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -I$(OFFICIAL_ROOT) -fsanitize=address,undefined -fno-omit-frame-pointer -o $(BUILD)/test_d4_aos_f32x3_complete_inverse d4_aos_ref.c d4_aos_f32x3_ref.c d4_aos_f32x3_invntt_avx2_asm.S test_d4_aos_f32x3_complete_inverse.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_d4_aos_f32x3_complete_inverse
d4-aos-f32x3-complete-inverse-bench:
	mkdir -p $(BUILD)
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -fomit-frame-pointer -fno-strict-aliasing -I$(OFFICIAL_ROOT) -I../../../NTRU+768/experiments/gt_ntt -o $(BUILD)/bench_d4_aos_f32x3_complete_inverse d4_aos_f32x3_invntt_avx2_asm.S ../../../NTRU+768/experiments/gt_ntt/gt_invntt_fused_soa.S ../../../NTRU+768/experiments/gt_ntt/gt_invntt_soa.c $(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c bench_d4_aos_f32x3_complete_inverse.c
	$(BUILD)/bench_d4_aos_f32x3_complete_inverse
d4-aos-f32x3-compact-dft3-bench:
	mkdir -p $(BUILD)
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -fomit-frame-pointer -fno-strict-aliasing -I$(OFFICIAL_ROOT) -o $(BUILD)/bench_d4_aos_f32x3_dft3 d4_aos_f32x3_invntt_avx2_asm.S d4_aos_f32x3_dft3_probe.c bench_d4_aos_f32x3_dft3.c
	$(BUILD)/bench_d4_aos_f32x3_dft3
d4-aos-f32x3-ntt32-ct-merged-bench:
	mkdir -p $(BUILD)
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -fomit-frame-pointer -fno-strict-aliasing -I$(OFFICIAL_ROOT) -o $(BUILD)/bench_d4_aos_f32x3_ct_merged d4_aos_f32x3_invntt_avx2_asm.S bench_d4_aos_f32x3_ct_merged.c
	$(BUILD)/bench_d4_aos_f32x3_ct_merged
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -fomit-frame-pointer -fno-strict-aliasing -I$(OFFICIAL_ROOT) -I../../../NTRU+768/experiments/gt_ntt -o $(BUILD)/bench_d4_aos_f32x3_ct_yang d4_aos_f32x3_invntt_avx2_asm.S ../../../NTRU+768/experiments/gt_ntt/gt_invntt_fused_soa.S ../../../NTRU+768/experiments/gt_ntt/gt_invntt_soa.c bench_d4_aos_f32x3_ct_yang.c
	$(BUILD)/bench_d4_aos_f32x3_ct_yang
official-invntt-deconstruction:
	mkdir -p $(BUILD)/official_invntt_deconstruction
	python3 tools/generate_official_invntt_instrumented.py --source $(OFFICIAL_ROOT)/asm/invntt.s --output $(BUILD)/official_invntt_deconstruction/official_invntt_instrumented.S
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 -fomit-frame-pointer -fno-strict-aliasing -I$(OFFICIAL_ROOT) -I../../../NTRU+768/experiments/gt_ntt -o $(BUILD)/official_invntt_deconstruction/bench_official_invntt_deconstruction bench_official_invntt_deconstruction.c $(BUILD)/official_invntt_deconstruction/official_invntt_instrumented.S $(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s $(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c ../../../NTRU+768/experiments/gt_ntt/gt_basemul_soa.c ../../../NTRU+768/experiments/gt_ntt/gt_invntt_soa.c ../../../NTRU+768/experiments/gt_ntt/gt_basemul_layout_asm.S ../../../NTRU+768/experiments/gt_ntt/gt_invntt_fused_soa.S d4_aos_f32x3_invntt_avx2_asm.S
	$(BUILD)/official_invntt_deconstruction/bench_official_invntt_deconstruction > $(BUILD)/official_invntt_deconstruction/benchmark.txt
	cat $(BUILD)/official_invntt_deconstruction/benchmark.txt
	objdump -d -M intel $(BUILD)/official_invntt_deconstruction/bench_official_invntt_deconstruction > $(BUILD)/official_invntt_deconstruction/objdump.txt
	nm -anS $(BUILD)/official_invntt_deconstruction/bench_official_invntt_deconstruction > $(BUILD)/official_invntt_deconstruction/nm.txt
	sha256sum $(BUILD)/official_invntt_deconstruction/bench_official_invntt_deconstruction $(BUILD)/official_invntt_deconstruction/official_invntt_instrumented.S > $(BUILD)/official_invntt_deconstruction/hashes.sha256
clean:
	rm -rf $(BUILD)
