#include <stdint.h>
/* exact image of signed Montgomery-by-constant and rounding Barrett (q=3457, v=9) */
void mont_image(int lo, int hi, int c, int *mn, int *mx) {
    int16_t cq = (int16_t)(c * 12929);
    int a = 1 << 30, b = -(1 << 30);
    for (int x = lo; x <= hi; x++) {
        int16_t m = (int16_t)(x * cq);
        int r = ((x * c) >> 16) - ((m * 3457) >> 16);
        if (r < a) a = r;
        if (r > b) b = r;
    }
    *mn = a; *mx = b;
}
void barrett_image(int lo, int hi, int *mn, int *mx) {
    int a = 1 << 30, b = -(1 << 30);
    for (int x = lo; x <= hi; x++) {
        int r = x - 3457 * ((x * 9 + (1 << 14)) >> 15);
        if (r < a) a = r;
        if (r > b) b = r;
    }
    *mn = a; *mx = b;
}
