# D1-P3B13 decision

Decision at this static gate: **the conservative allocation gate did not
authorize implementation.**  The user explicitly requested the saturated
case be tested anyway; P3B15 supersedes this static decision with real object
and Pi 5 evidence.

P3B15 is correct but emits 67 non-ABI vector stack accesses and runs 5.033
cycles slower than P3B6.  The static result remains useful as the reason for
that spill pressure; it was not a mathematical impossibility result.
