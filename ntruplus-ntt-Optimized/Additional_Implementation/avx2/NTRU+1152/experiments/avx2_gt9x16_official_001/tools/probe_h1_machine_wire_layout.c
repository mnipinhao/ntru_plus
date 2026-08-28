#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-prod3-ma2-qorder-natural-asm.h"

#define N 1152
#define BYTES 1728

static uint16_t decode12(const uint8_t bytes[BYTES], int coefficient) {
  int pair = coefficient / 2;
  if ((coefficient & 1) == 0)
    return (uint16_t)(bytes[3 * pair] |
                      ((uint16_t)(bytes[3 * pair + 1] & 15) << 8));
  return (uint16_t)((bytes[3 * pair + 1] >> 4) |
                    ((uint16_t)bytes[3 * pair + 2] << 4));
}

int main(int argc, char **argv) {
  _Alignas(32) int16_t input[N];
  uint8_t output[BYTES];
  FILE *file;
  int source;
  if (argc != 2) {
    fprintf(stderr, "usage: %s OUTPUT.json\n", argv[0]);
    return 2;
  }
  file = fopen(argv[1], "w");
  if (file == NULL) {
    perror(argv[1]);
    return 2;
  }
  fprintf(file, "{\n  \"schema\": \"h1-machine-wire-layout/v1\",\n");
  fprintf(file, "  \"source_to_wire\": [\n");
  for (source = 0; source < N; ++source) {
    int wire, found = -1;
    memset(input, 0, sizeof input);
    input[source] = 4;
    ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(output, input);
    for (wire = 0; wire < N; ++wire) {
      uint16_t value = decode12(output, wire);
      if (value != 0) {
        if (value != 1 || found != -1) {
          fprintf(stderr, "H1 basis is not a permutation at source %d\n", source);
          fclose(file);
          return 1;
        }
        found = wire;
      }
    }
    if (found < 0) {
      fprintf(stderr, "H1 basis disappeared at source %d\n", source);
      fclose(file);
      return 1;
    }
    fprintf(file, "    %d%s\n", found, source + 1 == N ? "" : ",");
  }
  fprintf(file, "  ]\n}\n");
  if (fclose(file) != 0) {
    perror(argv[1]);
    return 2;
  }
  return 0;
}
