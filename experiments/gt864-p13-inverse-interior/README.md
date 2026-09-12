# P13 — Inverse interior campaign

P13 begins from the P12 profile, which localized `+4493` retired instructions
and `+171` branches to GT Inverse-to-ternary versus selected Official
Inverse+Crepmod3.  P11 already rejected terminal routing-only rewrites.

P13-A instead changes the fixed wrapper scratch-clear granularity while keeping
the exact 256-byte initialization and 1792-byte post-operation wipe.  See
`iteration.yml` for the complete falsifiable hypothesis.  Production remains
unchanged until exact native/KAT/malformed and paired Pi 5 component/full-Decaps
gates pass.
