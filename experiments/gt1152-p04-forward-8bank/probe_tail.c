/* Probe: which input lane does ntt_tail_asm move where? */
#include <stdio.h>
#include <stdint.h>
void ntt_tail_asm(int16_t *buf);
int main(void){
    static int16_t b[128];
    for (int t = 0; t < 16; t++)
        for (int k = 0; k < 8; k++)
            b[8*t + k] = (int16_t)(100*t + k);   /* encode (t,lane) */
    ntt_tail_asm(b);
    for (int i = 0; i < 128; i++) printf("%d%c", b[i], i==127?'\n':',');
    return 0;
}
