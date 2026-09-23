
### M2 Pro, against Official + CryptoExtension (upstream's default build) (ns, median of three sessions)

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official | 4,545 | 5,254 | 4,146 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-8.6%** | **-10.9%** | **-6.6%** |
| 1152 | Official | 7,115 | 6,953 | 5,486 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-9.5%** | **-11.9%** | **-9.6%** |

### M2 Pro, against Official exactly as SUPERCOP has it (portable Keccak) (ns, median of three sessions)

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official | 4,905 | 5,988 | 4,604 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-15.3%** | **-21.8%** | **-15.9%** |
| 1152 | Official | 7,680 | 7,838 | 6,023 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-16.1%** | **-21.8%** | **-17.7%** |

### M2 Pro, Keccak held equal: Official's sponge + GT's permutation (ns, median of three sessions)

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official | 4,380 | 4,979 | 3,988 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-5.2%** | **-5.9%** | **-2.9%** |
| 1152 | Official | 6,858 | 6,571 | 5,265 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-6.1%** | **-6.7%** | **-5.8%** |

### Cortex-A76, against Official as SUPERCOP has it (neither side has FEAT_SHA3) (ns, median of three sessions)

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official | 18,389 | 19,188 | 16,948 |
| | **GT** | **15,216** | **14,811** | **14,205** |
| | | **-17.3%** | **-22.8%** | **-16.2%** |
| 1152 | Official | 28,102 | 24,581 | 21,819 |
| | **GT** | **24,077** | **19,347** | **18,139** |
| | | **-14.3%** | **-21.3%** | **-16.9%** |

### Cortex-A76, Keccak held equal: Official's sponge + GT's scalar permutation (ns, median of three sessions)

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official | 16,897 | 16,710 | 15,457 |
| | **GT** | **15,216** | **14,811** | **14,205** |
| | | **-9.9%** | **-11.4%** | **-8.1%** |
| 1152 | Official | 25,863 | 21,395 | 19,893 |
| | **GT** | **24,077** | **19,347** | **18,139** |
| | | **-6.9%** | **-9.6%** | **-8.8%** |
