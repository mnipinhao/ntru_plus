#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "params.h"
#include "poly.h"
int main(void){
  for (int t = 0; t < 1000; t++) {
    uint8_t *b = malloc(NTRUPLUS_POLYBYTES);            /* exact size: ASan flags any byte past it */
    for (int i = 0; i < NTRUPLUS_POLYBYTES; i++) b[i] = (uint8_t)rand();
    poly r; volatile int x = poly_frombytes(&r, b); (void)x; free(b);
  }
  puts("asan frombytes: no out-of-bounds read"); return 0; }
