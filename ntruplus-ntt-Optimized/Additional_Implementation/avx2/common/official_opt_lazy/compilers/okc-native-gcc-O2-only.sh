#!/bin/sh
# SUPERCOP okc-amd64 restricted to one entry: line 4 (the -O2 gcc entry) of the campaign default list.
echo 'gcc -march=native -mtune=native -O2 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'
