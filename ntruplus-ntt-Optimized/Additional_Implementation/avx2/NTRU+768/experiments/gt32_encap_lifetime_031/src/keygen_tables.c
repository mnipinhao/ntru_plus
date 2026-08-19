/*
 * basemul.s contains the unselected key-generation entry in the same object
 * as the M entry used by this gate.  Satisfy its table relocations without
 * linking the unrelated BaseInv implementation.
 */
#include "basemul.h"
#include "baseinv_tables.inc"
