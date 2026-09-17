SECTIONS
{
  .e0v_tail ALIGN(0x1000) : { KEEP(*(.e0v_tail)) }
  .ql2_tail ALIGN(0x1000) : {
    KEEP(*(.ql2_tail.1_ntt))
    KEEP(*(.ql2_tail.2_b3))
    KEEP(*(.ql2_tail.3_pack))
  }
  .rhash_tail ALIGN(0x1000) : { KEEP(*(.rhash_tail)) }
}
INSERT AFTER .bss;
