#include <stddef.h>
#include <stdint.h>

typedef struct {
    void (*initialize)(void *);
    void (*add_bytes)(void *, const unsigned char *, unsigned int, unsigned int);
    void (*add_byte)(void *, unsigned char, unsigned int);
    void (*permute)(void *);
    void (*extract)(const void *, unsigned char *, unsigned int, unsigned int);
} ops_t;

typedef void (*shake_fn)(uint8_t *, size_t, const uint8_t *, size_t,
                         const ops_t *);

__attribute__((noinline, section(".text.shake_template")))
void shake_template(uint8_t *out, size_t outlen, const uint8_t *in,
                    size_t inlen, const ops_t *ops) {
    uint64_t state[25] __attribute__((aligned(32)));
    ops->initialize(state);
    while (inlen >= 136) {
        ops->add_bytes(state, in, 0, 136);
        ops->permute(state);
        in += 136;
        inlen -= 136;
    }
    ops->add_bytes(state, in, 0, (unsigned)inlen);
    ops->add_byte(state, 0x1f, (unsigned)inlen);
    ops->add_byte(state, 0x80, 135);
    while (outlen >= 136) {
        ops->permute(state);
        ops->extract(state, out, 0, 136);
        out += 136;
        outlen -= 136;
    }
    if (outlen) {
        ops->permute(state);
        ops->extract(state, out, 0, (unsigned)outlen);
    }
    volatile uint64_t *p = state;
    for (size_t i = 0; i < 25; i++) p[i] = 0;
}

__attribute__((noinline, section(".text.hash_template")))
void hash_template(uint8_t *out, const uint8_t *msg, shake_fn shake,
                   const ops_t *ops) {
    uint8_t data[1153] __attribute__((aligned(32)));
    data[0] = 1;
    for (size_t i = 0; i < 1152; i++) data[i + 1] = msg[i];
    shake(out, 192, data, sizeof(data), ops);
    volatile uint8_t *p = data;
    for (size_t i = 0; i < sizeof(data); i++) p[i] = 0;
}

