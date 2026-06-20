// Kernel: ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded_asm
// Contract: opt-in bounded-postmerge candidate.  Reduces y1/y2 inside each
// process_lane before the raw 16-bit inverse DFT3 add/sub sequence.

#define ROWPACK_NATIVE_POSTMERGE_ASM_NAME ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded_asm
#define ROWPACK_NATIVE_POSTMERGE_ASM_APPLE_NAME _ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded_asm
#define ROWPACK_NATIVE_POSTMERGE_BOUND_Y1Y2 1

#include "ntruplus768_invntt32_rowpack_postmerge_branchfold.S"
