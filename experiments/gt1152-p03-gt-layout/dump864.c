/* Dump NTRU+864 production GT forward output for a given input.
 * Correctness/layout probe only; this is not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

void ntt_asm(int16_t out[864], const int16_t in[864]);

int main(int argc, char **argv)
{
    static int16_t in[864], out[864];
    if (argc != 2) { fprintf(stderr, "usage: dump864 <864 comma values>\n"); return 2; }
    char *p = argv[1];
    for (int i = 0; i < 864; i++) {
        in[i] = (int16_t)strtol(p, &p, 10);
        if (*p == ',') p++;
    }
    ntt_asm(out, in);
    for (int i = 0; i < 864; i++) printf("%d%c", out[i], i == 863 ? '\n' : ',');
    return 0;
}
