#ifndef PROTOTYPE_KEYPAIR_ADAPTER_H
#define PROTOTYPE_KEYPAIR_ADAPTER_H

int prototype_crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
int prototype_crypto_kem_keypair_no_clear(unsigned char *pk, unsigned char *sk);

#endif
