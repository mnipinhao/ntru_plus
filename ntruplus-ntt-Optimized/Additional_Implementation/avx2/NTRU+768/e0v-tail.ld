SECTIONS
{
  .e0v_tail ALIGN(0x1000) : { KEEP(*(.e0v_tail)) }
}
INSERT AFTER .bss;
