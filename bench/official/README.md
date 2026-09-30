# The official implementation

Every tool under `../aarch64/` compares GT against the official NTRU+
implementation as published: `github.com/ntruplus/ntruplus` main at
`3991b2ae08d6f0008d37e41b8aceaaab27b4ec89` (2026-08-14).  The tools build it in
SUPERCOP 20260831's leaf form, the form SUPERCOP measures.

SUPERCOP's `crypto_kem/ntruplus{768,864,1152}/aarch64` leaves come from that
repository's `NO_CE` build at an earlier snapshot.  They differ from main only
in `crepmod3.s`.  `setup.sh` takes the leaves and main's four newer files and
assembles every official build the tools need:

| directory | contents |
|---|---|
| `off<set>/` | SUPERCOP's leaf, unmodified |
| `offm<set>/` | the leaf with main's `crepmod3.s`: main's `NO_CE` build |
| `cemain/` | main's `NTRU+768/CE/` sponge and permutation: main's default build on FEAT_SHA3 cores |
| `shim/` | SUPERCOP's `crypto_*.h` types and a `randombytes.h`, so a leaf builds outside SUPERCOP |
| `IDENTITY` | the inputs' versions and the SHA-256 of every assembled file |

Neither upstream is copied into this repository.  `inputs.sha256` pins every
file `setup.sh` takes from them, and `setup.sh` refuses to run if any of them
differs.

## Setup

```sh
./setup.sh /tmp/official /path/to/supercop-20260831
```

The second argument is a SUPERCOP 20260831 tree, or any directory that holds
its three `crypto_kem/ntruplus<set>/aarch64` leaves.  On a machine without
SUPERCOP, copying the three leaves from one that has it is enough, because the
hashes are checked either way.

`setup.sh` clones `github.com/ntruplus/ntruplus` into `OUT/src/` and checks
out the pinned commit.  To use an existing checkout of it instead, pass the
checkout as a third argument.

The assembled builds are identical, file for file, to the ones behind the
figures in the package READMEs.
