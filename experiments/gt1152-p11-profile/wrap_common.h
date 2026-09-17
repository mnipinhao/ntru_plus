#ifndef WRAP_COMMON_H
#define WRAP_COMMON_H
#include <stdint.h>
extern uint64_t prof_start(void);
extern void prof_end(int, uint64_t);
#define WRAP_V(id, name, proto, args) \
    void name proto; void prof_##name proto; \
    void prof_##name proto { uint64_t t = prof_start(); name args; prof_end(id, t); }
#define WRAP_I(id, name, proto, args) \
    int name proto; int prof_##name proto; \
    int prof_##name proto { uint64_t t = prof_start(); int prof_ret_ = name args; prof_end(id, t); return prof_ret_; }
#endif
