#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (*hash_g_fn)(uint8_t *, const uint8_t *);

static uint64_t state = UINT64_C(0x7d4f39a25bc681e0);
static uint64_t next64(void)
{
    state ^= state << 7;
    state ^= state >> 9;
    state ^= state << 8;
    return state;
}

/* Satisfy the KEM shared object's public RNG import; hash_g never calls it. */
void randombytes(uint8_t *out, size_t length)
{
    while (length--) *out++ = (uint8_t)next64();
}

static hash_g_fn load_hash(const char *path)
{
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    hash_g_fn fn;
    if (!handle) {
        fprintf(stderr, "dlopen %s: %s\n", path, dlerror());
        exit(2);
    }
    *(void **)(&fn) = dlsym(handle, "hash_g");
    if (!fn) {
        fprintf(stderr, "dlsym hash_g: %s\n", dlerror());
        exit(2);
    }
    return fn;
}

int main(int argc, char **argv)
{
    uint8_t input[1296], reference[216], candidate[216], alias[1296];
    if (argc != 3) return 2;
    hash_g_fn baseline = load_hash(argv[1]);
    hash_g_fn p53 = load_hash(argv[2]);
    for (size_t trial = 0; trial < 4096; ++trial) {
        for (size_t i = 0; i < sizeof input; ++i) input[i] = (uint8_t)next64();
        baseline(reference, input);
        memset(candidate, 0xa5, sizeof candidate);
        p53(candidate, input);
        if (memcmp(reference, candidate, sizeof reference) != 0) return 1;
        memcpy(alias, input, sizeof input);
        p53(alias, alias);
        if (memcmp(reference, alias, sizeof reference) != 0) return 1;
    }
    puts("PASS: 4096 hash_g differential and exact-alias cases");
    return 0;
}
