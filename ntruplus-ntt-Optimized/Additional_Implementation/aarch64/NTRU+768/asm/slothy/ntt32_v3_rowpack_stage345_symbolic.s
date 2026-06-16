/*
 * Symbolic handoff stub for the NTRU+768 rowpack Forward NTT v3 experiment.
 *
 * This file is intentionally not a buildable candidate and is not wired into
 * any poly_ntt path.  It records the register-order contract for the next
 * Slothy/ASM iteration.  Do not promote it, and do not treat it as an
 * optimized .opt.s artifact.
 *
 * Goal:
 *   Keep the stage12 and stage345 arithmetic contract from
 *   asm/slothy/ntt32_v2_symbolic.s, but make the stage345 live-out register
 *   order rowpack-ready so the current final 8x8 transpose is not needed.
 *
 * Existing v2 boundary:
 *   q[k32].h[0..3] = branch0 quartic lanes 0..3 for fixed row,k32
 *   q[k32].h[4..7] = branch1 quartic lanes 0..3 for fixed row,k32
 *
 * Required v3 stage345 live-out for one row and one k32 block b:
 *   plane[row][b][0].h[v] = q[8*b + v].h[0] -> branch0 lane0 k32=8*b+v
 *   plane[row][b][1].h[v] = q[8*b + v].h[1] -> branch0 lane1 k32=8*b+v
 *   plane[row][b][2].h[v] = q[8*b + v].h[2] -> branch0 lane2 k32=8*b+v
 *   plane[row][b][3].h[v] = q[8*b + v].h[3] -> branch0 lane3 k32=8*b+v
 *   plane[row][b][4].h[v] = q[8*b + v].h[4] -> branch1 lane0 k32=8*b+v
 *   plane[row][b][5].h[v] = q[8*b + v].h[5] -> branch1 lane1 k32=8*b+v
 *   plane[row][b][6].h[v] = q[8*b + v].h[6] -> branch1 lane2 k32=8*b+v
 *   plane[row][b][7].h[v] = q[8*b + v].h[7] -> branch1 lane3 k32=8*b+v
 *
 * Store contract:
 *   rowpack_index(branch,row,lane,k32) =
 *     branch*384 + row*128 + lane*32 + k32
 *
 *   For block b and vector lane v:
 *     k32 = 8*b + v
 *     branch = plane / 4
 *     lane = plane % 4
 *     plane[row][b][plane].h[v] stores to rowpack_index(branch,row,lane,k32)
 *
 * Current evidence:
 *   Gate 4 measured current scatter/transpose at about 319 cycles/NTT and the
 *   store-ready load+store floor at about 109 cycles/NTT.  A successful v3
 *   register-order candidate should recover a meaningful part of the roughly
 *   210 cycle/NTT permutation gap while keeping vector stores.
 *
 * Validation gates:
 *   make test_gt_rowpack_forward_v3_register_order_contract
 *   make bench_gt_rowpack_forward_v3_register_order_cycles
 */
