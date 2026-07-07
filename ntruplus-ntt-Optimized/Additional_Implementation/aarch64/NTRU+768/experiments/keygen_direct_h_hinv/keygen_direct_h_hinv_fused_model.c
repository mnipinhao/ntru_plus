/*
 * Task 6D starting point: larger direct h/hinv fused dataflow model.
 *
 * This file is intentionally not wired into production or benchmarks yet.
 * It records the operation-count model that must be beaten before writing ASM.
 *
 * Frozen oracle:
 *   VARIANT=gt_production_default
 *   GT_BASEINV_USE_HIER_K8=1
 *   GT_BASEINV_USE_FQINV15_ASM=1
 *   GT_BASEINV_BATCH_USE_ASM_FINISH=1
 *
 * Current path:
 *   finv = baseinv_scaled_r(f)
 *   ginv = baseinv_scaled_r(g)
 *   h    = basemul_scaled_r_input(g, finv)
 *   hinv = basemul_scaled_r_input(f, ginv)
 *
 * Task 6 v1 model:
 *   combines the f/g group-product denominator inversion into one x2 tree,
 *   but still materializes finv/ginv and still calls both basemul kernels.
 *
 * Task 6D target:
 *   expose inverse parts per quartic block:
 *     f^{-1} = num_f * den_f^{-1}
 *     g^{-1} = num_g * den_g^{-1}
 *   and test whether:
 *     h    = (g * num_f) * den_f^{-1}
 *     hinv = (f * num_g) * den_g^{-1}
 *   can remove enough materialization/public-arithmetic cost.
 *
 * Important stop rule:
 *   If the C model only changes store order but keeps the same two full
 *   quartic products and the same number of reductions, it is unlikely to
 *   clear the 300-cycle promotion bar.  Do not write ASM for that shape.
 */

#include <stdint.h>

enum
{
	GT_6D_DEN_VECTORS = 24,
	GT_6D_GROUPS = 8,
	GT_6D_GROUP_SIZE = 3,
	GT_6D_QUARTIC_COEFFS = 4,
	GT_6D_LANES = 8
};

struct gt_6d_opcount
{
	const char *name;
	int prepare_blocks;
	int denominator_tree_fqmul;
	int fqinv15_calls;
	int finish_den_scale_products;
	int public_quartic_products;
	int materialized_full_polys;
	int expected_cycle_floor;
};

/*
 * Current production x2 shape:
 *   - prepare f and g independently.
 *   - each hier_k8 tree has 69 ordinary vector fqmul and 1 fqinv15.
 *   - finish materializes finv/ginv as two full polys.
 *   - public arithmetic runs two full scaled basemul kernels.
 */
static const struct gt_6d_opcount current_hier_k8_x2 = {
	"current_hier_k8_baseinv_plus_public_arith",
	.prepare_blocks = 48,
	.denominator_tree_fqmul = 2 * 69,
	.fqinv15_calls = 2,
	.finish_den_scale_products = 2 * 24 * GT_6D_QUARTIC_COEFFS,
	.public_quartic_products = 2 * 192,
	.materialized_full_polys = 4,
	.expected_cycle_floor = 13463,
};

/*
 * Task 6 v1 measured model:
 *   - same prepare.
 *   - combines 16 group products into one batch inversion.
 *   - still materializes finv/ginv and still runs public basemul x2.
 */
static const struct gt_6d_opcount direct_model_v1 = {
	"direct_h_hinv_model_v1",
	.prepare_blocks = 48,
	.denominator_tree_fqmul = (2 * 69) + 3,
	.fqinv15_calls = 1,
	.finish_den_scale_products = 2 * 24 * GT_6D_QUARTIC_COEFFS,
	.public_quartic_products = 2 * 192,
	.materialized_full_polys = 4,
	.expected_cycle_floor = 13229,
};

/*
 * Desired v2 is only worth implementing if it removes at least one of these:
 *   - finv/ginv full-poly materialization,
 *   - one full read pass of finv/ginv by public basemul,
 *   - a reduction/final-scale pass that can be folded after g*num_f/f*num_g.
 *
 * If v2 still has two full quartic products plus two full denominator-scale
 * passes, the operation count is too close to v1 and should remain design-only.
 */
static const struct gt_6d_opcount fused_model_v2_required_target = {
	"direct_h_hinv_fused_model_v2_required_target",
	.prepare_blocks = 48,
	.denominator_tree_fqmul = (2 * 69) + 3,
	.fqinv15_calls = 1,
	.finish_den_scale_products = 0,
	.public_quartic_products = 2 * 192,
	.materialized_full_polys = 2,
	.expected_cycle_floor = 13463 - 300,
};

int gt_6d_model_has_promotion_shape(void)
{
	return fused_model_v2_required_target.materialized_full_polys <
	           direct_model_v1.materialized_full_polys &&
	       fused_model_v2_required_target.finish_den_scale_products <
	           direct_model_v1.finish_den_scale_products &&
	       fused_model_v2_required_target.expected_cycle_floor <= 13163;
}
