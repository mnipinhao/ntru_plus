/*
 * Symbolic Slothy boundary source for Candidate A direct-tuple layout.
 *
 * This is not a full NTT32 implementation.  It records the two layout
 * handoff pieces needed by the Candidate A direct-tuple route:
 *
 *   1. complete NTT32 stage5 live-out q-registers -> k-major tuple stores
 *   2. k-major tuple memory -> basemul ld4/st4 lane deinterleave/reinterleave
 *
 * Candidate A direct-tuple memory contract:
 *
 *   tuple_index(branch,row,k32,lane) =
 *     branch*384 + row*128 + 4*k32 + lane
 *
 * For one row and one k32 block b, q[k].h[0..3] are branch 0 lanes and
 * q[k].h[4..7] are branch 1 lanes for fixed k32 = 8*b + k.  Therefore the
 * final NTT store needs no 8x8 transpose:
 *
 *   str low D(q[k])  -> branch0 row tuple + 8*k
 *   ext high D(q[k]) -> branch1 row tuple + 8*k
 *
 * Slothy 0.2.1 does not parse general "str D<...>, [xN,#imm]" stores.  The
 * store region below therefore uses Q stores as an allocation/scheduling model
 * only.  The production NTT32 integration must replace these Q stores with the
 * D stores described above.
 *
 * For basemul, eight consecutive tuple leaves are stored as:
 *
 *   [k0 l0 l1 l2 l3][k1 l0 l1 l2 l3] ... [k7 l0 l1 l2 l3]
 *
 * so ld4 deinterleaves them into four lane-major vectors, production GT
 * quartic arithmetic can operate on those vectors, and st4 writes the tuple
 * shape back.
 */

	.text
	.align 2

	.global candidate_a_direct_tuple_ntt_store_kernel
	.global _candidate_a_direct_tuple_ntt_store_kernel
candidate_a_direct_tuple_ntt_store_kernel:
_candidate_a_direct_tuple_ntt_store_kernel:
	/*
	 * x0 = branch0 tuple row block base + 8*b
	 * x1 = branch1 tuple row block base + 8*b
	 * x2 = temporary q-vector source for this standalone boundary check
	 *
	 * In the real NTT32 integration, q00..q07 are live-out stage5 registers,
	 * not loaded from x2.  The ldr instructions here only make this boundary
	 * file self-contained for Slothy allocation.
	 */
slothy_start_candidate_a_direct_tuple_ntt_store:
	ldr Q<q00_tuple>, [x2, #16*0]
	ldr Q<q01_tuple>, [x2, #16*1]
	ldr Q<q02_tuple>, [x2, #16*2]
	ldr Q<q03_tuple>, [x2, #16*3]
	ldr Q<q04_tuple>, [x2, #16*4]
	ldr Q<q05_tuple>, [x2, #16*5]
	ldr Q<q06_tuple>, [x2, #16*6]
	ldr Q<q07_tuple>, [x2, #16*7]

	ext V<q00_hi_tuple>.16b, V<q00_tuple>.16b, V<q00_tuple>.16b, #8
	ext V<q01_hi_tuple>.16b, V<q01_tuple>.16b, V<q01_tuple>.16b, #8
	ext V<q02_hi_tuple>.16b, V<q02_tuple>.16b, V<q02_tuple>.16b, #8
	ext V<q03_hi_tuple>.16b, V<q03_tuple>.16b, V<q03_tuple>.16b, #8
	ext V<q04_hi_tuple>.16b, V<q04_tuple>.16b, V<q04_tuple>.16b, #8
	ext V<q05_hi_tuple>.16b, V<q05_tuple>.16b, V<q05_tuple>.16b, #8
	ext V<q06_hi_tuple>.16b, V<q06_tuple>.16b, V<q06_tuple>.16b, #8
	ext V<q07_hi_tuple>.16b, V<q07_tuple>.16b, V<q07_tuple>.16b, #8

	str Q<q00_tuple>, [x0, #16*0]
	str Q<q01_tuple>, [x0, #16*1]
	str Q<q02_tuple>, [x0, #16*2]
	str Q<q03_tuple>, [x0, #16*3]
	str Q<q04_tuple>, [x0, #16*4]
	str Q<q05_tuple>, [x0, #16*5]
	str Q<q06_tuple>, [x0, #16*6]
	str Q<q07_tuple>, [x0, #16*7]

	str Q<q00_hi_tuple>, [x1, #16*0]
	str Q<q01_hi_tuple>, [x1, #16*1]
	str Q<q02_hi_tuple>, [x1, #16*2]
	str Q<q03_hi_tuple>, [x1, #16*3]
	str Q<q04_hi_tuple>, [x1, #16*4]
	str Q<q05_hi_tuple>, [x1, #16*5]
	str Q<q06_hi_tuple>, [x1, #16*6]
	str Q<q07_hi_tuple>, [x1, #16*7]
slothy_end_candidate_a_direct_tuple_ntt_store:
	ret

	.global candidate_a_direct_tuple_basemul_io_kernel
	.global _candidate_a_direct_tuple_basemul_io_kernel
candidate_a_direct_tuple_basemul_io_kernel:
_candidate_a_direct_tuple_basemul_io_kernel:
	/*
	 * x0 = output tuple block
	 * x1 = input a tuple block
	 * x2 = input b tuple block
	 *
	 * This is an I/O contract probe, not quartic multiplication.  The add
	 * operations only keep all deinterleaved lane vectors live until st4.
	 */
slothy_start_candidate_a_direct_tuple_basemul_io:
	ld4 {V<a_lane0>.8h, V<a_lane1>.8h, V<a_lane2>.8h, V<a_lane3>.8h}, [x1]
	ld4 {V<b_lane0>.8h, V<b_lane1>.8h, V<b_lane2>.8h, V<b_lane3>.8h}, [x2]

	add V<r_lane0>.8h, V<a_lane0>.8h, V<b_lane0>.8h
	add V<r_lane1>.8h, V<a_lane1>.8h, V<b_lane1>.8h
	add V<r_lane2>.8h, V<a_lane2>.8h, V<b_lane2>.8h
	add V<r_lane3>.8h, V<a_lane3>.8h, V<b_lane3>.8h

	st4 {V<r_lane0>.8h, V<r_lane1>.8h, V<r_lane2>.8h, V<r_lane3>.8h}, [x0]
slothy_end_candidate_a_direct_tuple_basemul_io:
	ret
