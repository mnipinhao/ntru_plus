#include <stdio.h>
#include <stdint.h>
#include <string.h>
void p65_rebase(const int16_t *src, int16_t *dst);
static int16_t src[1152], got[1152], want[1152];
int main(void){
    for (int i = 0; i < 1152; i++) src[i] = (int16_t)(i + 1);
    /* reference: dst[j*128 + t*8 + c + 4h] = src[h*576 + j*64 + tg*32 + c*8 + u] */
    for (int h = 0; h < 2; h++)
     for (int j = 0; j < 9; j++)
      for (int tg = 0; tg < 2; tg++)
       for (int c = 0; c < 4; c++)
        for (int u = 0; u < 8; u++)
          want[j*128 + (tg*8+u)*8 + c + 4*h] = src[h*576 + j*64 + tg*32 + c*8 + u];
    memset(got, 0, sizeof got);
    p65_rebase(src, got);
    int bad = 0, first = -1;
    for (int i = 0; i < 1152; i++) if (got[i] != want[i]) { if (first < 0) first = i; bad++; }
    printf("  rebase: %d/1152 mismatches%s\n", bad,
           bad ? "" : "  -> exact");
    if (bad) printf("    first at %d: got %d want %d\n", first, got[first], want[first]);
    return bad != 0;
}
