/* Official-main Keypair retained as a decap-only benchmark control edge. */
#include "crypto_kem.h"
#undef crypto_kem_keypair
#undef crypto_kem_enc
#undef crypto_kem_dec
#define crypto_kem_keypair crypto_kem_keypair_official_control
#define crypto_kem_enc crypto_kem_enc_official_unused
#define crypto_kem_dec crypto_kem_dec_official_unused
#include "tile4_official_kem.inc"
