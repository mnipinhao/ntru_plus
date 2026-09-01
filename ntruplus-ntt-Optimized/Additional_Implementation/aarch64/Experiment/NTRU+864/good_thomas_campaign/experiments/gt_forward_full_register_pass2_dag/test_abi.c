#include <stdint.h>
#include <stdio.h>

extern void gt864_m5r_abi_probe(int16_t out[864], const int16_t in[864],
                                uint64_t preserved[8]);

int main(void)
{
    int16_t in[864] __attribute__((aligned(16))) = {0};
    int16_t out[864] __attribute__((aligned(16)));
    uint64_t preserved[8] = {0};

    gt864_m5r_abi_probe(out, in, preserved);
    for (unsigned i = 0; i < 8; ++i) {
        const uint64_t expected = 0x108u + i;
        if (preserved[i] != expected) {
            fprintf(stderr, "d%u expected=%llu actual=%llu\n", 8 + i,
                    (unsigned long long)expected,
                    (unsigned long long)preserved[i]);
            return 1;
        }
    }
    puts("gt864_m5r_d8_d15_abi=pass");
    return 0;
}
