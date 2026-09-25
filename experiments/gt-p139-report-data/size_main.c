/* P139: linked KEM size.  Built twice with gc-sections: against the implementation, and with
 * -DSTUB against three empty entry points; the text difference is the KEM's. */
#include <stdint.h>
#include "api.h"
void rb_seed(void);
#ifdef STUB
int crypto_kem_keypair(unsigned char *pk, unsigned char *sk){ (void)pk; (void)sk; return 0; }
int crypto_kem_enc(unsigned char *c, unsigned char *k, const unsigned char *pk){ (void)c; (void)k; (void)pk; return 0; }
int crypto_kem_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk){ (void)k; (void)c; (void)sk; return 0; }
#endif
static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
int main(void){ rb_seed(); return crypto_kem_keypair(pk, sk) | crypto_kem_enc(ct, ss, pk) | crypto_kem_dec(ss, ct, sk); }
