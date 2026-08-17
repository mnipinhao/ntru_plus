#include <stdlib.h>
#include "randombytes.h"
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "publickeybytes", "secretkeybytes", "outputbytes", "ciphertextbytes", 0 };
const long long sizes[] = { crypto_kem_PUBLICKEYBYTES, crypto_kem_SECRETKEYBYTES, crypto_kem_BYTES, crypto_kem_CIPHERTEXTBYTES };

static unsigned char *p, *s, *k, *c, *t;
#define TIMINGS 32
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void)
{
  p = alignedcalloc(crypto_kem_PUBLICKEYBYTES);
  s = alignedcalloc(crypto_kem_SECRETKEYBYTES);
  k = alignedcalloc(crypto_kem_BYTES);
  c = alignedcalloc(crypto_kem_CIPHERTEXTBYTES);
  t = alignedcalloc(crypto_kem_BYTES);
  crypto_kem_keypair(p,s);
}

void measure(void)
{
  int i, loop;
  for (loop = 0;loop < LOOPS;++loop) {
    for (i = 0;i <= TIMINGS;++i) {
      cycles[i] = cpucycles();
      crypto_kem_enc(c,k,p);
    }
    for (i = 0;i < TIMINGS;++i) cycles[i] = cycles[i + 1] - cycles[i];
    printentry(-1,"enc_cycles",cycles,TIMINGS);

    /* Preserve the stock runner's keypair-data completion check, after the
       operation under test so it cannot affect encapsulation. */
    for (i = 0;i <= TIMINGS;++i) {
      cycles[i] = cpucycles();
      crypto_kem_keypair(p,s);
    }
    for (i = 0;i < TIMINGS;++i) cycles[i] = cycles[i + 1] - cycles[i];
    printentry(-1,"keypair_cycles",cycles,TIMINGS);
  }
}
