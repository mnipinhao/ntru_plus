/*
 * Single-step control-flow / address trace of the mlkem-native-Keccak NTRU+
 * hash path (constant-time evidence for tools/audit_keccak_ct.py).
 *
 * A traced child runs one target (fixed public lengths) on T different
 * secret inputs (trial 0 all-zero, 1 all-0xff, then pseudo-random).  Each
 * run is bracketed by raise(SIGUSR1) / raise(SIGUSR2); the parent
 * PTRACE_SINGLESTEPs through it and, for every executed instruction, writes
 * (rip, effective address of its explicit memory operand or 0) to
 * <outdir>/<target>-<trial>.trace.  The effective address is computed from
 * the pre-execution registers with the table <table> (rip base index scale
 * disp, register ids = user_regs_struct slots) that the audit derives from
 * `objdump -d` of this ELF; instructions outside the table (libc) record 0.
 * All trials of a target run in one process with the same buffers and stack
 * depth, so traces of a constant-time target must be identical.
 */
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

#include "params.h"

void ntruplus_mlkfips202_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void ntruplus_mlkfips202_keccakf1600_permute(uint64_t *);
#define CAT3_(a, b, c) a##b##c
#define CAT3(a, b, c) CAT3_(a, b, c)
#define CAND(s) CAT3(ntruplus, NTRUPLUS_N, _keccak_##s)
void CAND(hash_f)(uint8_t *, const uint8_t *);
void CAND(hash_g)(uint8_t *, const uint8_t *);
void CAND(hash_h)(uint8_t *, const uint8_t *);

#define POLY NTRUPLUS_POLYBYTES
#define HH_IN (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
static _Alignas(64) uint8_t in[2048], out[1024];
static _Alignas(64) uint64_t state[25];

static const char *const targets[] = {"shake_keypair", "shake_hash_g_shape", "hash_f", "hash_g", "hash_h", "permute",
                                     "negative_control"};
/* Negative control: a secret-indexed table lookup; its traces MUST differ. */
static volatile uint8_t sbox[256];
enum { NTARGETS = sizeof targets / sizeof targets[0] };

static void run_target(int t) {
    switch (t) {
    case 0: ntruplus_mlkfips202_shake256(out, NTRUPLUS_N / 4, in, 32); break;
    case 1: ntruplus_mlkfips202_shake256(out, NTRUPLUS_N / 4, in, 1 + POLY); break;
    case 2: CAND(hash_f)(out, in); break;
    case 3: CAND(hash_g)(out, in); break;
    case 4: CAND(hash_h)(out, in); break;
    case 5: ntruplus_mlkfips202_keccakf1600_permute(state); break;
    default: out[0] = sbox[in[7]]; break;
    }
}

static void secret(unsigned trial) {
    uint64_t x = 0x243f6a8885a308d3ULL ^ (trial * 0x9e3779b97f4a7c15ULL);
    for (size_t i = 0; i < sizeof in; i++) {
        x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
        in[i] = trial == 0 ? 0 : trial == 1 ? 0xff : (uint8_t)((x * 0x2545f4914f6cdd1dULL) >> 56);
    }
    memcpy(state, in, sizeof state);
    memset(out, 0, sizeof out);
}

typedef struct { uint64_t rip; int base, index, scale; int64_t disp; } entry;
static entry *table;
static size_t table_size;

static const entry *lookup(uint64_t rip) {
    size_t h = (size_t)(rip * 0x9e3779b97f4a7c15ULL) & (table_size - 1);
    while (table[h].rip) {
        if (table[h].rip == rip) return &table[h];
        h = (h + 1) & (table_size - 1);
    }
    return NULL;
}

static void load_table(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    size_t n = 0, cap = 1 << 16;
    entry *rows = malloc(cap * sizeof *rows);
    entry e;
    while (fscanf(f, "%lx %d %d %d %ld", &e.rip, &e.base, &e.index, &e.scale, &e.disp) == 5) {
        if (n == cap) rows = realloc(rows, (cap *= 2) * sizeof *rows);
        rows[n++] = e;
    }
    fclose(f);
    for (table_size = 1; table_size < 4 * n + 4; table_size <<= 1) {}
    table = calloc(table_size, sizeof *table);
    for (size_t i = 0; i < n; i++) {
        size_t h = (size_t)(rows[i].rip * 0x9e3779b97f4a7c15ULL) & (table_size - 1);
        while (table[h].rip) h = (h + 1) & (table_size - 1);
        table[h] = rows[i];
    }
    free(rows);
}

static uint64_t reg(const struct user_regs_struct *r, int id) {
    return id < 0 ? 0 : ((const unsigned long long *)r)[id];
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: %s table outdir trials\n", argv[0]); return 2; }
    unsigned trials = (unsigned)atoi(argv[3]);
    load_table(argv[1]);
    for (int t = 0; t < NTARGETS; t++) {
        pid_t pid = fork();
        if (pid == 0) {
            ptrace(PTRACE_TRACEME, 0, 0, 0);
            raise(SIGSTOP);
            secret(2);
            run_target(t);                                /* untraced warm-up */
            for (unsigned k = 0; k < trials; k++) {
                secret(k);
                raise(SIGUSR1);
                run_target(t);
                raise(SIGUSR2);
            }
            _exit(0);
        }
        int status;
        unsigned trial = 0;
        FILE *trace = NULL;
        unsigned long long steps = 0;
        waitpid(pid, &status, 0);                         /* SIGSTOP */
        ptrace(PTRACE_CONT, pid, 0, 0);
        for (;;) {
            if (waitpid(pid, &status, 0) < 0) { perror("waitpid"); return 1; }
            if (WIFEXITED(status)) break;
            int sig = WSTOPSIG(status);
            if (sig == SIGUSR1) {
                char name[4096];
                snprintf(name, sizeof name, "%s/%s-%u.trace", argv[2], targets[t], trial);
                trace = fopen(name, "wb");
                if (!trace) { perror(name); return 1; }
                steps = 0;
                ptrace(PTRACE_SINGLESTEP, pid, 0, 0);
            } else if (sig == SIGUSR2) {
                fclose(trace);
                trace = NULL;
                printf("%s trial=%u steps=%llu\n", targets[t], trial, steps);
                trial++;
                ptrace(PTRACE_CONT, pid, 0, 0);
            } else if (sig == SIGTRAP && trace) {
                struct user_regs_struct r;
                ptrace(PTRACE_GETREGS, pid, 0, &r);
                uint64_t rec[2] = {r.rip, 0};
                const entry *e = lookup(r.rip);
                if (e) rec[1] = reg(&r, e->base) + reg(&r, e->index) * (uint64_t)e->scale + (uint64_t)e->disp;
                fwrite(rec, sizeof rec, 1, trace);
                steps++;
                ptrace(PTRACE_SINGLESTEP, pid, 0, 0);
            } else {
                fprintf(stderr, "unexpected stop signal %d\n", sig);
                return 1;
            }
        }
        if (trial != trials) { fprintf(stderr, "%s: %u/%u trials\n", targets[t], trial, trials); return 1; }
    }
    return 0;
}
