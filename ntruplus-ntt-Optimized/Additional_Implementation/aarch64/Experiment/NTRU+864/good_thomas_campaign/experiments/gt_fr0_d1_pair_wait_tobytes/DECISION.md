# D1-P3B15 decision

Decision: **reject generated pair-wait; retain P3B6 ToBytes.**

The experiment validates the user's request to try the saturated allocation.
It is byte-correct and only 5.033 cycles slower, but GCC emits 67 non-ABI
vector stack accesses and retires 113 extra instructions per polynomial.

Reopen pair-wait only with a schedule whose frontier is at most 26, or with a
symbolic/manual allocation that proves fewer spill instructions before Pi 5.
Do not promote or integrate into full KEM.
