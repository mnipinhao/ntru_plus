/* The local differential harness does not run under TIMECOP. */
void crypto_declassify(const void *value, unsigned long long length) {
    (void)value;
    (void)length;
}
