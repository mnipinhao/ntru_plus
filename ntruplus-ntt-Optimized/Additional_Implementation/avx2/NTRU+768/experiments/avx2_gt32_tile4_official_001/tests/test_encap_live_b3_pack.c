#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { N = 768, BYTES = 1152, Q = 3457 };

void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void ntruplus768_pack_m_highrange12699_avx2(uint8_t *, const int16_t *);
void ntruplus768_exp001_encap_live_b3_pack(uint8_t *, const int16_t *,
                                             const int16_t *, const int16_t *);
void ntruplus768_exp001_encap_live_b3_pack_raw_debug(int16_t *, const int16_t *,
                                                       const int16_t *);

static uint64_t rng_state = UINT64_C(0xc018fae723214d69);
static uint32_t random32(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (uint32_t)rng_state;
}

static struct __attribute__((aligned(64))) {
    int16_t h[N], r[N], m[N], c[N], work[N], input[N];
    int16_t raw_debug[N];
    uint8_t expected[BYTES];
    uint8_t guarded[BYTES + 64];
} s;

static void forward(int16_t *out) {
    ntruplus768_ntt_frontend_avx2(s.work, s.input);
    ntruplus768_ntt_m_avx2(out, s.work);
}

int main(void) {
    for (unsigned trial = 0; trial < 1003; trial++) {
        for (int i = 0; i < N; i++) {
            s.h[i] = (int16_t)(random32() % Q);
            s.input[i] = trial < 3 ? (int16_t)((i == (int)trial) ? 1 : 0)
                                   : (int16_t)((int)(random32() % 3) - 1);
        }
        forward(s.r);
        for (int i = 0; i < N; i++)
            s.input[i] = trial < 3 ? (int16_t)((i == (int)trial) ? -1 : 0)
                                   : (int16_t)((int)(random32() % 3) - 1);
        forward(s.m);
        ntruplus768_basemul_general_m_avx2(s.c, s.h, s.r);
        ntruplus768_exp001_encap_live_b3_pack_raw_debug(s.raw_debug, s.h, s.r);
        if (memcmp(s.c, s.raw_debug, sizeof s.c)) {
            for (int i=0;i<N;i++) if(s.c[i]!=s.raw_debug[i]) {
                fprintf(stderr,"raw B3 mismatch trial %u cell %d got %d expected %d\n",
                        trial,i,s.raw_debug[i],s.c[i]);
                break;
            }
            return 1;
        }
        for (int i = 0; i < N; i++) s.c[i] = (int16_t)(s.c[i] + s.m[i]);
        ntruplus768_pack_m_highrange12699_avx2(s.expected, s.c);
        memset(s.guarded, 0xa5, sizeof s.guarded);
        int16_t h_copy[N], r_copy[N], m_copy[N];
        memcpy(h_copy, s.h, sizeof h_copy);
        memcpy(r_copy, s.r, sizeof r_copy);
        memcpy(m_copy, s.m, sizeof m_copy);
        ntruplus768_exp001_encap_live_b3_pack(s.guarded + 32, s.h, s.r, s.m);
        if (memcmp(s.guarded + 32, s.expected, BYTES) ||
            memcmp(s.h, h_copy, sizeof h_copy) ||
            memcmp(s.r, r_copy, sizeof r_copy) ||
            memcmp(s.m, m_copy, sizeof m_copy)) {
            fprintf(stderr, "live B3 pack mismatch or modified input: trial %u\n", trial);
            for (int i = 0; i < BYTES; i++) if (s.guarded[32+i] != s.expected[i]) {
                fprintf(stderr, "first byte %d: got %u expected %u\n", i,
                        (unsigned)s.guarded[32+i], (unsigned)s.expected[i]);
                break;
            }
            fprintf(stderr, "h/r/m modified %d/%d/%d\n",
                    memcmp(s.h,h_copy,sizeof h_copy) != 0,
                    memcmp(s.r,r_copy,sizeof r_copy) != 0,
                    memcmp(s.m,m_copy,sizeof m_copy) != 0);
            return 1;
        }
        for (int i = 0; i < 32; i++) {
            if (s.guarded[i] != 0xa5 || s.guarded[32 + BYTES + i] != 0xa5) {
                fprintf(stderr, "live B3 pack canary changed: trial %u\n", trial);
                return 1;
            }
        }
    }
    puts("live B3→Q24: 1003 semantic/immutability/canary cases pass");
    return 0;
}
