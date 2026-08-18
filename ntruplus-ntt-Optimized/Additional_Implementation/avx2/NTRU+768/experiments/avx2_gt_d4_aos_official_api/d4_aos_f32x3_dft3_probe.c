#include "d4_aos_f32x3_ref.h"

/* Default-off diagnostic composition. The probe intentionally materializes its output. */
void gt_d4aos_f32x3_yang_idft3_probe_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *native_input)
{
    gt_d4aos_f32x3_invntt32_ct_merged_yang_asm(out, native_input);
    gt_d4aos_f32x3_idft3_barrett_probe_asm(out, out);
}

void gt_d4aos_f32x3_yang_compact_idft3_probe_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *native_input)
{
    gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm(out, native_input);
    gt_d4aos_f32x3_idft3_barrett_probe_asm(out, out);
}
