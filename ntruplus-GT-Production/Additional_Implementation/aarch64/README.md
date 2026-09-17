# NTRU+ AArch64 production sources

Each parameter-set directory owns its KEM source, polynomial backend, SHAKE
backend, tests, KATs, source manifest, and release checks:

```text
aarch64/
  NTRU+768/
  NTRU+864/
```

Run `make check` inside the selected directory on Linux/AArch64. Performance
figures in the validation records were measured on a Raspberry Pi 5
Cortex-A76.
