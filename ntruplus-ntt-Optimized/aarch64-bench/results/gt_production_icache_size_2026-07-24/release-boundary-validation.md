# GT Production Release-Boundary Validation

Date: 2026-07-24

Host: Raspberry Pi 5 Cortex-A76

The release source was copied to a temporary remote directory and built with a
separate temporary `BUILD_DIR`:

```text
source: /tmp/ntruplus-gt-release-20260724-v2-src
build:  /tmp/ntruplus-gt-release-20260724-v2-build
```

## Result

```text
release file count:          50
release check:               pass
source manifest:             pass
KEM round trips:             100 pass
required ABI mask:           0x00000
canonical KAT comparison:    byte-for-byte pass
release source pollution:    none
```

KAT response SHA-256:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

## Linked Size

| `.text` | Data | BSS | Total allocated |
|---:|---:|---:|---:|
| 80,673 | 696 | 8 | 81,377 |

This validates the external-output Makefile policy. The build, generated KAT,
and test binaries were written outside the release source tree.
