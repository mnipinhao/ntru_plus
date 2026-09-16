/* Exact current Decaps boundary, extracted from production kem.c. */
gt864_fr0_tobytes_full(buf2, &f);
fail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);

/* buf2 is 1296 bytes and is later cleared in full.  Before this boundary its
 * only live use is hash_g's 216-byte output. */
secure_clear(buf2, sizeof buf2);
