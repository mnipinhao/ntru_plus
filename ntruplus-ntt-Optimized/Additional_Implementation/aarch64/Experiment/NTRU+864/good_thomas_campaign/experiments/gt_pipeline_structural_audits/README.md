# M5A-E2E-AUDIT0: GT pipeline structural audits

This directory turns six optimization ideas into rerunnable evidence audits:

1. GT axis order;
2. twist absorption;
3. inverse backward liveness;
4. weighted BaseMul specialization;
5. layout/serializer co-design;
6. reduction placement.

The audit locks two pipelines separately. CF4 is the current executable
complete polynomial multiplication, while CF5-A is only a passing Forward
producer/consumer gate. Evidence from one is never used to claim that the other
is already an end-to-end binary.

Run:

```sh
make check
make report
```

`make check` fails only when frozen evidence is missing or has drifted. An
individual research question may legitimately remain `open` or `partial`.
`make report` regenerates `audit-results.json` and `AUDIT_REPORT.md`.

No Production or SUPERCOP source is linked or modified by this experiment.
