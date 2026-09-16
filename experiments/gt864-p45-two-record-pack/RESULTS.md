# P45 — two-record joint packing

P45 is complete and is **rejected at the static route/read gate**. Production
remains P24.

## Exact joint packing result

For adjacent normalized vectors A and B, one pair can be packed as:

```text
UZP1, UZP2
SHL, ORR, USHR
TBL2 index0, TBL2 index1
STR Q, STR D
```

This is nine instructions for 24 bytes, versus P24's eighteen instructions for
two independent six-instruction packs plus two D/MOV/W store sequences. The
identity passed all 11,950,849 canonical coefficient pairs and 10,003 complete
24-byte cases.

## Route/register result

The saving requires A and B to remain live together. The exact budget also
needs q, reciprocal, pack indices and one work vector. Three variants were
searched for 10,000 precedence-preserving mutations each:

| Route registers | Resident indices | Route instructions | Coefficient loads | Candidate total/top | Complete delta vs P24 |
|---:|---:|---:|---:|---:|---:|
| 27 | 2 | **384** | 121 | **897** | **-288 instructions** |
| 28 | 1 | 381 + 27 index loads | 119 | 921 | -240 instructions |
| 29 | 0 | 378 + 54 index loads | 117 | 945 | -192 instructions |

The 27-register form is the best total instruction ledger, but it misses both
predeclared gates:

```text
route/index instructions: 384 > 300
coefficient loads:        121 > 61
```

It also fails the requirement to beat P24 and P44 on the read ledger: retaining
one normalized record while producing its partner destroys the global route
cache reuse and adds 120 coefficient reads per complete call.

No candidate assembly or Slothy run was produced. Although the arithmetic
count looks attractive, P41 already showed that only 30 extra reads can erase
a smaller terminal saving on A76; P45 would add four times that read deficit.
Reopen only if a producer can emit adjacent A/B roots without this pair-route
reload cost. The next independent gate is P46 Full normalization.
