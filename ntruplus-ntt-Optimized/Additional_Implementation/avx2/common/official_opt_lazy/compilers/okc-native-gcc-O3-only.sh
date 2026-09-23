#!/bin/sh
# SUPERCOP okc-amd64 restricted to one entry: line 2 (the -O3 gcc entry) of the campaign default list.
echo 'gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'
