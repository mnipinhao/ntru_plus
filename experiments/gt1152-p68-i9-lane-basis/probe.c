#include <stdio.h>
#include <stdint.h>
#include <string.h>
void packed_i9(int16_t *out, int16_t *tail, const int16_t *in, const int16_t *tw);
static int16_t scratch[2304/2], tailbuf[512], in[4096], tw[4096];
int main(void){
    memset(scratch,0,sizeof scratch); memset(tailbuf,0,sizeof tailbuf);
    packed_i9(scratch, tailbuf, in, tw);
    printf("  scratch halfwords that received a tag (value/100 = register slot):\n");
    for (int i = 0; i < 1152; i++) {
        int v = scratch[i];
        if (v >= 100 && v < 1000) printf("    scratch[%3d] = %4d   (slot %d, lane %d)\n",
                                          i, v, v/100, v%100);
    }
    int n=0; for (int i=0;i<256;i++) if (tailbuf[i]>=900) n++;
    printf("  tail buffer received %d tagged halfwords\n", n);
    return 0;
}
