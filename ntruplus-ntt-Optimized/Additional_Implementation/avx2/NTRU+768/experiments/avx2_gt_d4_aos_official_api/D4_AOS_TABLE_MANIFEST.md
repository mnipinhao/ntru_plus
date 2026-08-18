# Generated-table manifest

`tools/d4aos_metadata.py` deterministically derives all files in `generated/`
from field identities; it does not copy assembler constants.  The checked-in
manifest is `generated/MANIFEST.sha256` and records the nine exact artifacts:

- logical and physical AoS maps;
- forward and inverse roots;
- DFT3 constants and terminal `zeta` order;
- normalization/CRT constants;
- natural output map; and
- machine-readable metadata.

Reproduce and byte-compare the full set (including the expected mapping digest
`8c1aecfa7391fe8b75c9c4dac4ee6538ea95787d0291ab1a5a89d5697587f8b3`) with:

```sh
make d4-aos-generated-check
# equivalently: python3 tools/d4aos_metadata.py --check-dir generated
```

The checker regenerates into a temporary directory, verifies names, hashes,
and bytes, then removes the temporary output.  Generated artifacts are
persistent evidence; binaries and sanitizer executables remain under the
gitignored `build/` directory.
