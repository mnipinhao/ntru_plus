#ifndef GT144_CRYPTO_KEM_H
#define GT144_CRYPTO_KEM_H
#define crypto_kem_keypair crypto_kem_ntruplus768_gt144_keypair
#define crypto_kem_enc crypto_kem_ntruplus768_gt144_enc
#define crypto_kem_dec crypto_kem_ntruplus768_gt144_dec
#define crypto_kem_PUBLICKEYBYTES 1152
#define crypto_kem_SECRETKEYBYTES 2336
#define crypto_kem_BYTES 32
#define crypto_kem_CIPHERTEXTBYTES 1152
#define crypto_kem_IMPLEMENTATION "NTRU+768/GT144"
#define crypto_kem_VERSION "-"
extern int crypto_kem_keypair(unsigned char *,unsigned char *);
extern int crypto_kem_enc(unsigned char *,unsigned char *,const unsigned char *);
extern int crypto_kem_dec(unsigned char *,const unsigned char *,const unsigned char *);
#endif
