/* P139: code executed by one KEM operation, measured by callgrind collecting only inside the entry
 * point (run_extra.sh, footprint.py).  The set-up key pair and encapsulation take the same path as the
 * measured call, so they add no distinct instructions.  usage: footprint 0|1|2 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "api.h"
void rb_seed(void);
__attribute__((noinline)) void marker_begin(void){ __asm__ volatile("" ::: "memory"); }
__attribute__((noinline)) void marker_end(void){ __asm__ volatile("" ::: "memory"); }
static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
int main(int argc, char **argv){
  int op = argc > 1 ? atoi(argv[1]) : 0;
  rb_seed(); crypto_kem_keypair(pk, sk); crypto_kem_enc(ct, ss, pk);
  rb_seed();
  marker_begin();
  if (op == 0) crypto_kem_keypair(pk, sk); else if (op == 1) crypto_kem_enc(ct, ss, pk); else crypto_kem_dec(ss, ct, sk);
  marker_end();
  return 0; }
