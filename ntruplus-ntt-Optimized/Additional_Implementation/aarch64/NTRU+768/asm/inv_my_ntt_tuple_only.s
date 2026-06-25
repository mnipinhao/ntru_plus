/*
 * Candidate A direct-tuple inverse NTT wrapper.
 *
 * The C KEM adapter owns the public poly_invntt ABI and calls
 * gt_tuple_poly_invntt directly.  Avoid exporting a second poly_invntt symbol,
 * which is a hard duplicate on Mach-O and unnecessary on ELF.
 */
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_NO_POLY_ALIAS, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif
.include "asm/slothy/invntt_opt.production.s"
