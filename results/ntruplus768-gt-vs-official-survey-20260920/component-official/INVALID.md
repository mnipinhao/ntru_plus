# Invalid component campaign

This attempted `derived-component-768` run is not a valid Official component
result.  The component harness names GT-specific frontend, M/P, J1, inverse,
and Q24 operations that do not exist in the Official implementation, so the
runner correctly rejected the output as missing all required operation labels.

Official-vs-GT matched evidence in this survey comes from the same-ELF caller
harness and the operation-region PMU campaign.  The `data` and `run.out` files
are retained only to make the failed attempt auditable; they must not be used
as performance evidence.
