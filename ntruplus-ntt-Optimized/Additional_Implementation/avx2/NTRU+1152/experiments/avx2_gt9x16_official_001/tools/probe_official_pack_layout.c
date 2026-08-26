#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "poly.h"

int main(int argc, char **argv) {
  FILE *output;
  int physical;

  if (argc != 2) {
    fprintf(stderr, "usage: %s OUTPUT.json\n", argv[0]);
    return 2;
  }
  output = fopen(argv[1], "w");
  if (output == NULL) {
    perror(argv[1]);
    return 2;
  }
  fprintf(output, "{\n  \"schema\": \"official-pack-layout/v1\",\n");
  fprintf(output, "  \"physical_to_serialized\": [\n");
  for (physical = 0; physical < NTRUPLUS_N; ++physical) {
    __attribute__((aligned(32))) poly value;
    uint8_t bytes[NTRUPLUS_POLYBYTES];
    int serialized;
    int found = -1;
    memset(&value, 0, sizeof value);
    value.coeffs[physical] = 1;
    poly_tobytes(bytes, &value);
    for (serialized = 0; serialized < NTRUPLUS_N; ++serialized) {
      int pair = serialized / 2;
      uint16_t decoded = serialized % 2 == 0
          ? (uint16_t)(bytes[3 * pair] |
                       ((uint16_t)(bytes[3 * pair + 1] & 15) << 8))
          : (uint16_t)((bytes[3 * pair + 1] >> 4) |
                       ((uint16_t)bytes[3 * pair + 2] << 4));
      if (decoded != 0) {
        if (decoded != 1 || found != -1) {
          fprintf(stderr, "pack basis is not a permutation at physical=%d\n",
                  physical);
          fclose(output);
          return 1;
        }
        found = serialized;
      }
    }
    if (found == -1) {
      fprintf(stderr, "pack basis disappeared at physical=%d\n", physical);
      fclose(output);
      return 1;
    }
    fprintf(output, "    %d%s\n", found,
            physical + 1 == NTRUPLUS_N ? "" : ",");
  }
  fprintf(output, "  ]\n}\n");
  if (fclose(output) != 0) {
    perror(argv[1]);
    return 2;
  }
  return 0;
}
