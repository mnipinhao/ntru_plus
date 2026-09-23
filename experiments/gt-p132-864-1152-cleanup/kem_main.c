#include <stdint.h>
int crypto_kem_keypair(unsigned char*,unsigned char*); int crypto_kem_enc(unsigned char*,unsigned char*,const unsigned char*); int crypto_kem_dec(unsigned char*,const unsigned char*,const unsigned char*);
static unsigned char pk[4000], sk[8000], ct[4000], ss[64];
int main(void){ crypto_kem_keypair(pk,sk); crypto_kem_enc(ct,ss,pk); return crypto_kem_dec(ss,ct,sk); }
