#include <stdint.h>
#include <stdio.h>

#include "params.h"

#define NTRUPLUS_QINV 12929
#define NTRUPLUS_R (-147)
#define NTRUPLUS_RSQ 867

static int16_t montgomery_reduce(int32_t a)
{
	int16_t t;

	t = (int16_t)a * NTRUPLUS_QINV;
	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static int16_t barrett_reduce(int16_t a)
{
	int16_t t;
	const int16_t v = ((1 << 26) + NTRUPLUS_Q / 2) / NTRUPLUS_Q;

	t = ((int32_t)v * a + (1 << 25)) >> 26;
	t *= NTRUPLUS_Q;
	return a - t;
}

static void basemul_raw(int16_t r[4], const int16_t a[4],
                        const int16_t b[4], int16_t zeta)
{
	r[0] = montgomery_reduce(a[1] * b[3] + a[2] * b[2] + a[3] * b[1]);
	r[1] = montgomery_reduce(a[2] * b[3] + a[3] * b[2]);
	r[2] = montgomery_reduce(a[3] * b[3]);

	r[0] = montgomery_reduce(r[0] * zeta + a[0] * b[0]);
	r[1] = montgomery_reduce(r[1] * zeta + a[0] * b[1] + a[1] * b[0]);
	r[2] = montgomery_reduce(r[2] * zeta + a[0] * b[2] +
	                         a[1] * b[1] + a[2] * b[0]);
	r[3] = montgomery_reduce(a[0] * b[3] + a[1] * b[2] +
	                         a[2] * b[1] + a[3] * b[0]);

	r[0] = montgomery_reduce(r[0] * NTRUPLUS_RSQ);
	r[1] = montgomery_reduce(r[1] * NTRUPLUS_RSQ);
	r[2] = montgomery_reduce(r[2] * NTRUPLUS_RSQ);
	r[3] = montgomery_reduce(r[3] * NTRUPLUS_RSQ);
}

static void basemul_add_raw(int16_t r[4], const int16_t a[4],
                            const int16_t b[4], const int16_t c[4],
                            int16_t zeta)
{
	r[0] = montgomery_reduce(a[1] * b[3] + a[2] * b[2] + a[3] * b[1]);
	r[1] = montgomery_reduce(a[2] * b[3] + a[3] * b[2]);
	r[2] = montgomery_reduce(a[3] * b[3]);

	r[0] = montgomery_reduce(r[0] * zeta + a[0] * b[0]);
	r[1] = montgomery_reduce(r[1] * zeta + a[0] * b[1] + a[1] * b[0]);
	r[2] = montgomery_reduce(r[2] * zeta + a[0] * b[2] +
	                         a[1] * b[1] + a[2] * b[0]);
	r[3] = montgomery_reduce(a[0] * b[3] + a[1] * b[2] +
	                         a[2] * b[1] + a[3] * b[0]);

	r[0] = montgomery_reduce(c[0] * NTRUPLUS_R + r[0] * NTRUPLUS_RSQ);
	r[1] = montgomery_reduce(c[1] * NTRUPLUS_R + r[1] * NTRUPLUS_RSQ);
	r[2] = montgomery_reduce(c[2] * NTRUPLUS_R + r[2] * NTRUPLUS_RSQ);
	r[3] = montgomery_reduce(c[3] * NTRUPLUS_R + r[3] * NTRUPLUS_RSQ);
}

static int in_canonical_range(int16_t x)
{
	return x >= -(NTRUPLUS_Q / 2) && x <= NTRUPLUS_Q / 2;
}

static int check_barrett_idempotence(void)
{
	for (int x = -(NTRUPLUS_Q / 2); x <= NTRUPLUS_Q / 2; x++)
	{
		const int16_t reduced = barrett_reduce((int16_t)x);

		if (reduced != x)
		{
			fprintf(stderr,
			        "barrett idempotence failed at %d: got %d\n",
			        x,
			        reduced);
			return 0;
		}
	}

	return 1;
}

static int check_montgomery_output_to_canonical(void)
{
	for (int x = -NTRUPLUS_Q + 1; x <= NTRUPLUS_Q - 1; x++)
	{
		const int16_t reduced = barrett_reduce((int16_t)x);

		if (!in_canonical_range(reduced))
		{
			fprintf(stderr,
			        "barrett range failed at %d: got %d\n",
			        x,
			        reduced);
			return 0;
		}
		if (barrett_reduce(reduced) != reduced)
		{
			fprintf(stderr,
			        "barrett canonical result not idempotent at %d: got %d\n",
			        x,
			        reduced);
			return 0;
		}
	}

	return 1;
}

static int check_current_basemul_counterexample(void)
{
	const int16_t a[4] = { -124, 1662, -319, 1203 };
	const int16_t b[4] = { 2270, -546, -697, -478 };
	const int16_t c[4] = { 0, 0, 0, 0 };
	const int16_t zeta = -1130;
	int16_t r[4];
	int16_t r_add[4];

	basemul_raw(r, a, b, zeta);
	basemul_add_raw(r_add, a, b, c, zeta);

	if (r[1] != -1737 || r_add[1] != -1737)
	{
		fprintf(stderr,
		        "unexpected counterexample result: basemul=%d basemul_add=%d\n",
		        r[1],
		        r_add[1]);
		return 0;
	}
	if (in_canonical_range(r[1]))
	{
		fprintf(stderr, "counterexample did not leave canonical range\n");
		return 0;
	}
	if (barrett_reduce(r[1]) != 1720)
	{
		fprintf(stderr,
		        "unexpected counterexample normalization: got %d\n",
		        barrett_reduce(r[1]));
		return 0;
	}

	return 1;
}

int main(void)
{
	if (!check_barrett_idempotence() ||
	    !check_montgomery_output_to_canonical() ||
	    !check_current_basemul_counterexample())
	{
		return 1;
	}

	printf("rowpack basemul output range proof: ok\n");
	printf("canonical convention: each stored basemul lane is in [-1728,1728]\n");
	printf("current raw convention counterexample: r[1] = -1737, barrett = 1720\n");
	return 0;
}
