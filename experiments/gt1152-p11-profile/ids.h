/* Component list covering both the GT and the official NTRU+1152 APIs.
 * They differ: GT has basemul_rinv, tobytes_small/compare and the fused
 * invntt_ternary; the official has a separate invntt plus crepmod3. */
static const char *component_names[] = {
  "poly_tobytes","poly_tobytes_small","poly_tobytes_compare","poly_frombytes",
  "poly_cbd1","poly_sotp_encode","poly_sotp_decode",
  "poly_ntt","poly_invntt","poly_invntt_ternary","poly_baseinv",
  "poly_basemul","poly_basemul_add","poly_basemul_rinv",
  "poly_sub","poly_triple","poly_crepmod3",
  "hash_f","hash_g","hash_g_fr0","hash_h","shake256","poly_basemul_scale"};
#define NCOMP 23
