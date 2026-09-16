# P52 — post-P51 selected-Official profiler

Measurement-only checkpoint.  It compares exact committed P51 GT864
production against the user-selected SHAKE256 AArch64 implementation under
`/home/pi/supercop-20260831` and attributes the remaining KEM/component gap.

The GT `Full_compare` profiler group is rebound from the removed P47 serializer
to `gt864_fr0_equal_modq_asm`; the Official side remains its canonical
serializer plus inline byte verifier.  This preserves the caller-level
re-encryption equality boundary rather than comparing unlike leaf functions.
