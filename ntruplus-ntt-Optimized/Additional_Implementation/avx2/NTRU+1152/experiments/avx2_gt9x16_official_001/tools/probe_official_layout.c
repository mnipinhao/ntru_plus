#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 1152
#define Q 3457

extern void poly_ntt(int16_t value[N]);

static int canonical(int16_t value) {
  int result = value % Q;
  return result < 0 ? result + Q : result;
}

int main(int argc, char **argv) {
  _Alignas(32) int16_t probe[8][N];
  _Alignas(32) int16_t value[N];
  FILE *output;
  int coefficient, index, exponent;
  if (argc != 2) {
    fputs("usage: probe_official_layout OUTPUT\n", stderr);
    return 2;
  }
  for (coefficient = 0; coefficient < 4; ++coefficient) {
    memset(value, 0, sizeof value);
    value[coefficient] = 1;
    poly_ntt(value);
    memcpy(probe[coefficient], value, sizeof value);
    memset(value, 0, sizeof value);
    value[4 + coefficient] = 1;
    poly_ntt(value);
    memcpy(probe[4 + coefficient], value, sizeof value);
  }
  output = fopen(argv[1], "w");
  if (output == NULL) {
    perror(argv[1]);
    return 2;
  }
  fputs("{\n  \"derivation\": \"basis probes through pinned Official AVX2 poly_ntt\",\n"
        "  \"positions\": [\n", output);
  for (index = 0; index < N; ++index) {
    int owner = -1;
    int root = 0;
    for (coefficient = 0; coefficient < 4; ++coefficient) {
      int marker = canonical(probe[coefficient][index]);
      if (marker == 1) {
        if (owner != -1) {
          fputs("ambiguous terminal-coefficient owner\n", stderr);
          return 1;
        }
        owner = coefficient;
        root = canonical(probe[4 + coefficient][index]);
      } else if (marker != 0) {
        fputs("unexpected basis marker\n", stderr);
        return 1;
      }
    }
    if (owner == -1) {
      fputs("missing terminal-coefficient owner\n", stderr);
      return 1;
    }
    value[0] = 1;
    for (exponent = 0; exponent < Q - 1 && value[0] != root; ++exponent) {
      value[0] = (int16_t)((value[0] * 7) % Q);
    }
    if (value[0] != root) {
      fputs("factor is not in the field generator table\n", stderr);
      return 1;
    }
    fprintf(output,
            "    {\"position\": %d, \"terminal_coefficient\": %d, "
            "\"factor_exponent_base_g\": %d}%s\n",
            index, owner, exponent, index + 1 == N ? "" : ",");
  }
  fputs("  ]\n}\n", output);
  if (fclose(output) != 0) {
    return 2;
  }
  return 0;
}
