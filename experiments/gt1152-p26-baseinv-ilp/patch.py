"""Split baseinv's batch inversion into K independent chains.

P25 measured the serial phase at 1,928 cycles of baseinv's 6,498: a 35-step
`fqmul` prefix chain, then `fqinv`'s addition chain, then 35 recover steps each
carrying `inv = fqmul(inv, di)`.  Every one is strictly serial, so one vector is
in flight and the multiply pipe idles.

Splitting into K chains of 36/K is the same algorithm applied recursively, and
is correct by associativity alone: the chain products are batch-inverted by the
identical routine, one level up.  No range or representation changes -- `fqinv`
still sees the product of all 36, in the same Montgomery representation as
before -- so no bound is re-derived.

Serial depth goes from 2*35 to 2*(36/K - 1) + 2*(K - 1); K = 6 minimises it at
20 steps against 70, with K = 4 close behind.
"""
import pathlib, sys

K = int(sys.argv[1])
assert 36 % K == 0, K
M = 36 // K
src = pathlib.Path(sys.argv[2]).read_text()

old_start = src.index("    /* ---- prefix, one inversion, recover ---- */")
old_end = src.index("    /* ---- finish: apply with the +,-,+,- conjugation signs ---- */")

new = f"""    /* ---- {K} independent prefix chains, one inversion, {K} recover chains ---- */
    {{
        const int K = {K}, M = {M};
        int16x8_t cpre[{K}], ip[{K}], carry[{K}];

        for (int c = 0; c < K; c++)
            prefix[c * M] = den[c * M];
        for (int j = 1; j < M; j++)
            for (int c = 0; c < K; c++)
                prefix[c * M + j] = fqmul(prefix[c * M + j - 1], den[c * M + j]);

        /* the same batch inversion, one level up, over the K chain products */
        cpre[0] = prefix[M - 1];
        for (int c = 1; c < K; c++)
            cpre[c] = fqmul(cpre[c - 1], prefix[c * M + M - 1]);

        /*
         * cpre[K-1] is the product of all 36, exactly what the single-chain
         * version inverted.  Prefix values lie inside (-q,q), so only integer
         * zero represents zero; vminvq_u16 folds all eight lanes with no early
         * exit and the branch depends on public non-invertibility.
         */
        if (!vminvq_u16(vreinterpretq_u16_s16(cpre[K - 1]))) {{
            for (int i = 0; i < BASE_COEFFICIENTS; i++)
                out[i] = 0;
            return 1;
        }}

        {{
            int16x8_t t = fqinv(cpre[K - 1]);
            for (int c = K - 1; c > 0; c--) {{
                ip[c] = fqmul(cpre[c - 1], t);
                t = fqmul(t, prefix[c * M + M - 1]);
            }}
            ip[0] = t;
        }}

        for (int c = 0; c < K; c++)
            carry[c] = ip[c];
        for (int j = M - 1; j > 0; j--)
            for (int c = 0; c < K; c++) {{
                int16x8_t di = den[c * M + j];
                den[c * M + j] = fqmul(prefix[c * M + j - 1], carry[c]);
                carry[c] = fqmul(carry[c], di);
            }}
        for (int c = 0; c < K; c++)
            den[c * M] = carry[c];
    }}

"""
pathlib.Path(sys.argv[3]).write_text(src[:old_start] + new + src[old_end:])
print(f"K={K}, M={M}: serial depth {2*(M-1) + 2*(K-1)} steps against 70")
