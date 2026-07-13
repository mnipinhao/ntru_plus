/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)@PAGE
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, C_SYM(sym)@PAGEOFF
#else
#define C_SYM(sym) sym
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, :lo12:C_SYM(sym)
#endif

#endif
