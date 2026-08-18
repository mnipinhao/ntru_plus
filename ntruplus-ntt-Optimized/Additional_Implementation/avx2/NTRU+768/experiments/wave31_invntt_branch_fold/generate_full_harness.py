#!/usr/bin/env python3
"""Add Wave31 Dec correctness and PMU operations to Wave24's full harness."""

from __future__ import annotations

import argparse
from pathlib import Path


DECL = r"""
int wave31_algebraic_crypto_kem_dec(
	unsigned char *ss, const unsigned char *ct, const unsigned char *sk);
int wave31_fold_lazy_crypto_kem_dec(
	unsigned char *ss, const unsigned char *ct, const unsigned char *sk);
int wave31_fold_exact_crypto_kem_dec(
	unsigned char *ss, const unsigned char *ct, const unsigned char *sk);
"""

VALIDATE = r"""
static int validate_wave31(void)
{
	uint8_t reference[NTRUPLUS_SSBYTES];
	uint8_t algebraic[NTRUPLUS_SSBYTES];
	uint8_t lazy[NTRUPLUS_SSBYTES];
	uint8_t exact[NTRUPLUS_SSBYTES];
	uint8_t malformed[NTRUPLUS_CIPHERTEXTBYTES];

	const int reference_rc =
		crypto_kem_dec(reference, fixed_ct, fixed_sk);
	const int algebraic_rc =
		wave31_algebraic_crypto_kem_dec(algebraic, fixed_ct, fixed_sk);
	const int lazy_rc =
		wave31_fold_lazy_crypto_kem_dec(lazy, fixed_ct, fixed_sk);
	const int exact_rc =
		wave31_fold_exact_crypto_kem_dec(exact, fixed_ct, fixed_sk);
	if (reference_rc != algebraic_rc ||
	    reference_rc != lazy_rc || reference_rc != exact_rc ||
	    memcmp(reference, algebraic, sizeof reference) != 0 ||
	    memcmp(reference, lazy, sizeof reference) != 0 ||
	    memcmp(reference, exact, sizeof reference) != 0) {
		fputs("Wave31 valid-input Dec byte differential failed\n", stderr);
		return 1;
	}
	for (unsigned round = 0; round < 128U; round++) {
		memcpy(malformed, fixed_ct, sizeof malformed);
		malformed[(37U * round + 11U) % sizeof malformed] ^=
			(uint8_t)(1U << (round & 7U));
		const int rc0 = crypto_kem_dec(reference, malformed, fixed_sk);
		const int rca =
			wave31_algebraic_crypto_kem_dec(
				algebraic, malformed, fixed_sk);
		const int rc1 =
			wave31_fold_lazy_crypto_kem_dec(lazy, malformed, fixed_sk);
		const int rc2 =
			wave31_fold_exact_crypto_kem_dec(exact, malformed, fixed_sk);
		if (rc0 != rca || rc0 != rc1 || rc0 != rc2 ||
		    memcmp(reference, algebraic, sizeof reference) != 0 ||
		    memcmp(reference, lazy, sizeof reference) != 0 ||
		    memcmp(reference, exact, sizeof reference) != 0) {
			fprintf(stderr,
				"Wave31 malformed Dec differential failed round=%u\n",
				round);
			return 1;
		}
	}
	puts("wave31 valid/malformed full Dec byte differential: passed");
	return 0;
}

"""

OPS = r"""
static int op_dec_wave31_algebraic(void)
{
	uint8_t ss[NTRUPLUS_SSBYTES];
	const int rc =
		wave31_algebraic_crypto_kem_dec(ss, fixed_ct, fixed_sk);
	sink ^= checksum(ss, sizeof ss);
	return rc;
}

static int op_dec_wave31_lazy(void)
{
	uint8_t ss[NTRUPLUS_SSBYTES];
	const int rc =
		wave31_fold_lazy_crypto_kem_dec(ss, fixed_ct, fixed_sk);
	sink ^= checksum(ss, sizeof ss);
	return rc;
}

static int op_dec_wave31_exact(void)
{
	uint8_t ss[NTRUPLUS_SSBYTES];
	const int rc =
		wave31_fold_exact_crypto_kem_dec(ss, fixed_ct, fixed_sk);
	sink ^= checksum(ss, sizeof ss);
	return rc;
}

"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = args.source.read_text(encoding="utf-8")
    marker = "int wave24_keygen_current("
    if marker not in text:
        raise RuntimeError("declaration marker changed")
    text = text.replace(marker, DECL + "\n" + marker, 1)
    marker = "static int validate(void)"
    if marker not in text:
        raise RuntimeError("validation marker changed")
    text = text.replace(marker, VALIDATE + marker, 1)
    old = '\tif (argc == 2 && strcmp(argv[1], "--validate") == 0) return validate();'
    new = (
        '\tif (argc == 2 && strcmp(argv[1], "--validate") == 0)\n'
        '\t\treturn validate() != 0 || validate_wave31() != 0;'
    )
    if text.count(old) != 1:
        raise RuntimeError("main validation dispatch changed")
    text = text.replace(old, new, 1)
    marker = "struct entry { const char *name; operation run; };"
    if marker not in text:
        raise RuntimeError("operation marker changed")
    text = text.replace(marker, OPS + marker, 1)
    old = '\t{"dec-official", op_dec_official},'
    new = (
        old
        + '\n\t{"dec-wave31-algebraic", op_dec_wave31_algebraic},'
        + '\n\t{"dec-wave31-fold-lazy", op_dec_wave31_lazy},'
        + '\n\t{"dec-wave31-fold-exact", op_dec_wave31_exact},'
    )
    if text.count(old) != 1:
        raise RuntimeError("operation table changed")
    text = text.replace(old, new, 1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
