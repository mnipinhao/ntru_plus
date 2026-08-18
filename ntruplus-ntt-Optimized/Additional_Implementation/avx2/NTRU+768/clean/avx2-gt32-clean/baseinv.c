/* Flat-directory P-J1 BaseInv instantiation for the SUPERcop export. */
#include <stdint.h>

#include "basemul.h"

/* P-layout lambda tables are owned by the selected J1 implementation. */
#include "baseinv_tables.inc"

/* The standard P instance owns gt_native_lambda and its qinv table. */
#define GT_RINV 1
#define GT_RINV_QINV 12929
#define GT_BATCH_INVERSE_EXTERNAL ntruplus768_baseinv_batch_tree_avx2

#define gt_baseinv_native_centered_avx2 ntruplus768_baseinv_j1_avx2
#include "baseinv_impl.inc"
