# Inverse AoS register plan

| interval | live values | peak | spill |
| --- | --- | ---: | --- |
| root accumulation | input, twiddle, product/reduction temporaries, accumulator | 8 YMM | none |
| canonical checkpoint | accumulator, masks, q/qinv | 7 YMM | none |
| pair completion | accumulator and qword swap | 3 YMM | none |
| branch merge/normalization | branch values, delta/alpha products, low/high | 8 YMM | none |
| final stores | low/high XMM halves | 2 YMM + 2 XMM | none |

Unsanitized `gt_d4aos_invntt_avx2_proto` disassembly has no YMM stack spill/reload. It has no DFT3 semantic scratch and stores two contiguous qwords per natural row. Its 96×48 direct evaluation is nevertheless not the requested factorized inverse-DFT3 microtile and is not eligible for ASM.
