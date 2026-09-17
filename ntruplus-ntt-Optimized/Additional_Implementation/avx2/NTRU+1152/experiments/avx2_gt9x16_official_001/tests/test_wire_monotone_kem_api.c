#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "rng.h"

int main(void) {
  unsigned char entropy[48];
  unsigned char pk[CRYPTO_PUBLICKEYBYTES];
  unsigned char sk[CRYPTO_SECRETKEYBYTES];
  unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
  unsigned char ss1[CRYPTO_BYTES];
  unsigned char ss2[CRYPTO_BYTES];
  int trial;

  for (trial = 0; trial < 48; ++trial)
    entropy[trial] = (unsigned char)trial;
  randombytes_init(entropy, NULL, 256);
  for (trial = 0; trial < 16; ++trial) {
    if (crypto_kem_keypair(pk, sk) || crypto_kem_enc(ct, ss1, pk) ||
        crypto_kem_dec(ss2, ct, sk) || memcmp(ss1, ss2, sizeof ss1)) {
      fprintf(stderr, "wire KEM round-trip failed at trial %d\n", trial);
      return 1;
    }
  }

  memset(pk, 0xff, sizeof pk);
  memset(ct, 0xa5, sizeof ct);
  memset(ss1, 0xa5, sizeof ss1);
  if (crypto_kem_enc(ct, ss1, pk) != 1) {
    fputs("wire KEM accepted invalid public key\n", stderr);
    return 1;
  }
  for (size_t i = 0; i < sizeof ct; ++i)
    if (ct[i] != 0) {
      fputs("wire KEM did not clear invalid ciphertext\n", stderr);
      return 1;
    }
  for (size_t i = 0; i < sizeof ss1; ++i)
    if (ss1[i] != 0) {
      fputs("wire KEM did not clear invalid shared secret\n", stderr);
      return 1;
    }
  puts("wire-monotone complete KEM API: ok");
  return 0;
}
