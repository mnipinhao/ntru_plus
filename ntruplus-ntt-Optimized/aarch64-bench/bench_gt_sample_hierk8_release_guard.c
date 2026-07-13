/*
 * Link-only release guard binary for the production SAMPLE-DAG + HIERK8 tree
 * promotion.  The Python guard inspects this binary with nm/objdump; this
 * file only keeps the relevant production KEM symbols and build-mode marker
 * symbols alive.
 */
#include <stdint.h>

int bench_crypto_kem_keypair_current(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_current(uint8_t *ct, uint8_t *ss,
                                 const uint8_t *pk);
int bench_crypto_kem_dec_current(uint8_t *ss, const uint8_t *ct,
                                 const uint8_t *sk);

#if defined(GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3)
int gt_release_guard_sample_dag_enabled = 1;
#else
int gt_release_guard_sample_dag_disabled = 1;
#endif

#if defined(GT_BASEINV_USE_HIER_K8_TREE)
int gt_release_guard_hierk8_tree_enabled = 1;
#else
int gt_release_guard_hierk8_tree_disabled = 1;
#endif

typedef int (*keypair_fn)(uint8_t *pk, uint8_t *sk);
typedef int (*enc_fn)(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
typedef int (*dec_fn)(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

static keypair_fn keypair_symbols[] = {
    bench_crypto_kem_keypair_current,
};

static enc_fn enc_symbols[] = {
    bench_crypto_kem_enc_current,
};

static dec_fn dec_symbols[] = {
    bench_crypto_kem_dec_current,
};

int main(void)
{
    int marker = 0;

#if defined(GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3)
    marker |= gt_release_guard_sample_dag_enabled;
#else
    marker |= gt_release_guard_sample_dag_disabled;
#endif

#if defined(GT_BASEINV_USE_HIER_K8_TREE)
    marker |= gt_release_guard_hierk8_tree_enabled;
#else
    marker |= gt_release_guard_hierk8_tree_disabled;
#endif

    return keypair_symbols[0] == 0 || enc_symbols[0] == 0 ||
           dec_symbols[0] == 0 || marker == 0;
}
