#!/bin/bash
# usage: gtsrc.sh TREE  -> line 1: sources (paths), line 2: CFLAGS, both from the tree's Makefile
G=$1
case $(basename $G) in
*768*)  V=$(printf 'v:\n\t@echo $(KEM_SOURCES)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v);;
*864*)  V=$(printf 'v:\n\t@echo $(KEM_OBJECTS)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - BUILD_DIR=@ v)
        L=""; for o in $(echo "$V" | sed -n 1p); do b=${o#@/}; b=${b%.o}; [ -f $G/$b.c ] && L="$L $b.c" || L="$L $b.S"; done
        V="$L"$'\n'"$(echo "$V" | sed -n 2p)";;
*)      V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v);;
esac
SS=""; for s in $(echo "$V" | sed -n 1p); do [ $s = randombytes.c ] || SS="$SS $G/$s"; done
echo $SS; echo "$V" | sed -n 2p
