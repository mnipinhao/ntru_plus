/* Run the NTRU+1152 eight-bank GT forward on one input. Layout/correctness
 * probe only; this is not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
void ntt_asm(int16_t out[1152], const int16_t in[1152]);
int main(int argc, char **argv){
    static int16_t in[1152], out[1152];
    if (argc != 2) { fprintf(stderr, "usage: harness <1152 comma values>\n"); return 2; }
    char *p = argv[1];
    for (int i = 0; i < 1152; i++) { in[i] = (int16_t)strtol(p, &p, 10); if (*p==',') p++; }
    ntt_asm(out, in);
    for (int i = 0; i < 1152; i++) printf("%d%c", out[i], i==1151?'\n':',');
    return 0;
}
