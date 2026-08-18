# Compact DFT3 paired benchmark

CPU 3, same binary, 10,001 paired/interleaved samples. Two retained runs:

| Measurement | Run 1 median/p10/p90 | Run 2 median/p10/p90 |
| --- | --- | --- |
| Y1 NTT32 | 482/462/500 | 522/510/542 |
| Y1 + materialized DFT3 | 560/538/578 | 606/596/624 |
| paired Y1 DFT3 delta | 78/62/94 | 84/66/104 |
| Y2 NTT32 | 478/458/492 | 516/506/532 |
| Y2 + materialized DFT3 | 564/540/580 | 608/598/624 |
| paired Y2 DFT3 delta | 86/74/98 | 92/78/106 |

Both median deltas are within the <=100 TSC strong-result band. The delta includes 48
input loads and 48 probe stores; terminal integration is expected to remove the latter.
PMU values remain unclaimed because host permissions reject reliable paired PMU access.
