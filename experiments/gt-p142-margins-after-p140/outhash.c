/* Output check for every build of the comparison: the same seeded key pair and
 * encapsulation must give the same bytes in every Official variant and in GT.
 * perop5's selftest cannot see a broken hash (encaps and decaps agree anyway). */
#include <stdio.h>
#include <stdint.h>
#include "api.h"
#include "randombytes.h"
void rb_seed(void);
int crypto_kem_keypair(unsigned char *, unsigned char *);
int crypto_kem_enc(unsigned char *, unsigned char *, const unsigned char *);
static unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
static uint64_t fnv(const unsigned char *p, size_t n){ uint64_t h = 1469598103934665603ULL; while (n--) { h ^= *p++; h *= 1099511628211ULL; } return h; }
int main(int argc, char **argv){ rb_seed(); crypto_kem_keypair(pk, sk); crypto_kem_enc(ct, ss, pk);
  printf("%-14s pk %016llx ct %016llx ss %016llx\n", argc > 1 ? argv[1] : "?", (unsigned long long)fnv(pk, sizeof pk),
         (unsigned long long)fnv(ct, sizeof ct), (unsigned long long)fnv(ss, sizeof ss)); return 0; }
