#!/usr/bin/env python3
"""Adapt the frozen Wave25 contract harness for Wave31 endpoints."""

from __future__ import annotations

import argparse
from pathlib import Path


DECLARATIONS = r"""
void wave31_invntt_native_rminus1_algebraic_avx2(
	int16_t out[NTRUPLUS_N], const int16_t native[NTRUPLUS_N]);
void wave31_invntt_native_rminus1_branch_fold_lazy_avx2(
	int16_t out[NTRUPLUS_N], const int16_t native[NTRUPLUS_N]);
void wave31_invntt_native_rminus1_branch_fold_exact_avx2(
	int16_t out[NTRUPLUS_N], const int16_t native[NTRUPLUS_N]);
"""


LAZY_VALIDATION = r"""
		wave31_invntt_native_rminus1_branch_fold_lazy_avx2(
			candidate_output[set].coeffs,
			native_rminus1_product[set].coeffs);
		if (!equal_mod_q(&official_output, &candidate_output[set])) {
			fprintf(stderr,
				"Wave31 lazy Branch Fold mismatch set=%u\n", set);
			return 1;
		}
		for (unsigned i = 0; i < NTRUPLUS_N; i++) {
			const int value = candidate_output[set].coeffs[i];
			if (value < -5053 || value > 5053) {
				fprintf(stderr,
					"Wave31 lazy range set=%u i=%u value=%d\n",
					set, i, value);
				return 1;
			}
		}
"""


EXTRA_OPERATIONS = r"""
static int op_inverse_algebraic(unsigned set)
{
	wave31_invntt_native_rminus1_algebraic_avx2(
		candidate_output[set].coeffs,
		native_rminus1_product[set].coeffs);
	return 0;
}

static int op_inverse_fold_lazy(unsigned set)
{
	wave31_invntt_native_rminus1_branch_fold_lazy_avx2(
		candidate_output[set].coeffs,
		native_rminus1_product[set].coeffs);
	return 0;
}
"""


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{name} audit changed: count={text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = args.source.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "int wave20_probe_call2(",
        DECLARATIONS + "\nint wave20_probe_call2(",
        "declaration insertion",
    )
    exact_range = """\
\t\tfor (unsigned i = 0; i < NTRUPLUS_N; i++) {
\t\t\tconst int value = candidate_output[set].coeffs[i];
\t\t\tif (value < -(NTRUPLUS_Q - 1) ||
\t\t\t    value > NTRUPLUS_Q - 1) {
\t\t\t\tfprintf(stderr,
\t\t\t\t\t\"direct inverse range set=%u i=%u value=%d\\n\",
\t\t\t\t\tset, i, value);
\t\t\t\treturn 1;
\t\t\t}
\t\t}"""
    canonical_range = """\
\t\tfor (unsigned i = 0; i < NTRUPLUS_N; i++) {
\t\t\tconst int value = candidate_output[set].coeffs[i];
\t\t\tif (value < -(NTRUPLUS_Q / 2) ||
\t\t\t    value > NTRUPLUS_Q / 2) {
\t\t\t\tfprintf(stderr,
\t\t\t\t\t\"Wave31 exact canonical range set=%u i=%u value=%d\\n\",
\t\t\t\t\tset, i, value);
\t\t\t\treturn 1;
\t\t\t}
\t\t}"""
    text = replace_once(
        text,
        exact_range,
        canonical_range + LAZY_VALIDATION,
        "candidate range validation",
    )

    abi_old = """\
\t    wave20_probe_call2(
\t\t    (void (*)(void *, void *))
\t\t\t    wave25_invntt_native_rminus1_official_direct_avx2,
\t\t    output.coeffs, native_rminus1_product[0].coeffs) != 0) {"""
    abi_new = """\
\t    wave20_probe_call2(
\t\t    (void (*)(void *, void *))
\t\t\t    wave25_invntt_native_rminus1_official_direct_avx2,
\t\t    output.coeffs, native_rminus1_product[0].coeffs) != 0 ||
\t    wave20_probe_call2(
\t\t    (void (*)(void *, void *))
\t\t\t    wave31_invntt_native_rminus1_algebraic_avx2,
\t\t    output.coeffs, native_rminus1_product[0].coeffs) != 0 ||
\t    wave20_probe_call2(
\t\t    (void (*)(void *, void *))
\t\t\t    wave31_invntt_native_rminus1_branch_fold_lazy_avx2,
\t\t    output.coeffs, native_rminus1_product[0].coeffs) != 0) {"""
    text = replace_once(text, abi_old, abi_new, "ABI insertion")

    text = replace_once(
        text,
        "static int op_island_materialized(unsigned set)",
        EXTRA_OPERATIONS + "\nstatic int op_island_materialized(unsigned set)",
        "operation function insertion",
    )
    operation_old = """\
\t{\"inverse-materialized\", op_inverse_materialized},
\t{\"inverse-direct\", op_inverse_direct},"""
    operation_new = """\
\t{\"inverse-materialized\", op_inverse_materialized},
\t{\"inverse-algebraic\", op_inverse_algebraic},
\t{\"inverse-fold-lazy\", op_inverse_fold_lazy},
\t{\"inverse-fold-exact\", op_inverse_direct},"""
    text = replace_once(
        text, operation_old, operation_new, "operation table insertion"
    )
    text = text.replace(
        "wave25 direct-ingest Official inverse DAG: passed",
        "wave31 algebraic/lazy/exact inverse differential: passed",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
