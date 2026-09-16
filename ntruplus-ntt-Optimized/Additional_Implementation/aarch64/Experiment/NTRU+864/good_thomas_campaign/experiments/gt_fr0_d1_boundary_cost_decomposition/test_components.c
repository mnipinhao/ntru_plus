#include "gt864_poly_api.h"
#include "p2_components.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int centered(int value)
{
    value %= NTRUPLUS_Q;
    if (value < 0) value += NTRUPLUS_Q;
    if (value > NTRUPLUS_Q / 2) value -= NTRUPLUS_Q;
    return value;
}

static int same_modq(const poly *a, const poly *b)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        if (centered(a->coeffs[i]) != centered(b->coeffs[i])) return 0;
    return 1;
}

int main(void)
{
    poly natural = {{0}}, official, fr0, temp, roundtrip, normalized;
    poly official_product, fr0_product, inv_official, inv_raw, inv_api;
    poly baseinv_official, baseinv_fr0;
    uint8_t bytes_official[NTRUPLUS_POLYBYTES];
    uint8_t bytes_gt[NTRUPLUS_POLYBYTES];
    int mismatches = 0;
    int forward_map = 0, permutation = 0, normalization = 0;
    int inverse = 0, serializer = 0, deserializer = 0, baseinv = 0;

    natural.coeffs[0] = 1;
    for (int i = 1; i < NTRUPLUS_N; i++)
        natural.coeffs[i] = (int16_t)((37 * i + 11) % 17 - 8);
    poly_ntt(&official, &natural);
    gt_old_poly_ntt(&fr0, &natural);
    gt_p2_official_to_fr0(&temp, &official);
    forward_map += !same_modq(&temp, &fr0);
    gt_p2_fr0_to_official_raw(&roundtrip, &temp);
    permutation += memcmp(&roundtrip, &official, sizeof official) != 0;

    gt_p2_normalize_nonnegative(&normalized, &fr0);
    for (int i = 0; i < NTRUPLUS_N; i++)
        normalization += normalized.coeffs[i] < 0 || normalized.coeffs[i] >= NTRUPLUS_Q;
    gt_p2_normalize_centered(&normalized, &fr0);
    for (int i = 0; i < NTRUPLUS_N; i++)
        normalization += normalized.coeffs[i] < -1728 || normalized.coeffs[i] > 1728;

    poly_basemul(&official_product, &official, &official);
    gt_d1_poly_basemul(&fr0_product, &fr0, &fr0);
    poly_invntt(&inv_official, &official_product);
    gt_p2_inverse_raw(&inv_raw, &fr0_product);
    gt_old_poly_invntt(&inv_api, &fr0_product);
    inverse += !same_modq(&inv_official, &inv_raw);
    inverse += !same_modq(&inv_official, &inv_api);

    poly_tobytes(bytes_official, &official);
    gt_old_poly_tobytes(bytes_gt, &fr0);
    serializer += memcmp(bytes_official, bytes_gt, sizeof bytes_gt) != 0;
    poly_frombytes(&roundtrip, bytes_official);
    gt_old_poly_frombytes(&temp, bytes_official);
    gt_p2_official_to_fr0(&normalized, &roundtrip);
    deserializer += memcmp(&temp, &normalized, sizeof temp) != 0;

    int rc0 = poly_baseinv(&baseinv_official, &official);
    int rc1 = gt_old_poly_baseinv(&baseinv_fr0, &fr0);
    gt_p2_official_to_fr0(&temp, &baseinv_official);
    baseinv += rc0 != 0 || rc0 != rc1 || !same_modq(&temp, &baseinv_fr0);

    mismatches = forward_map + permutation + normalization + inverse
               + serializer + deserializer + baseinv;
    printf("detail,forward_map=%d,permutation=%d,normalization=%d,inverse=%d,"
           "serializer=%d,deserializer=%d,baseinv=%d\n", forward_map,
           permutation, normalization, inverse, serializer, deserializer,
           baseinv);

    printf("d1_p2_components=%s mismatches=%d baseinv_rc=%d\n",
           mismatches == 0 ? "pass" : "fail", mismatches, rc0);
    return mismatches != 0;
}
