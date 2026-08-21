SECTIONS
{
  .text.gt033b.factorial.hot : ALIGN(64)
  {
    *(.text.gt033b_factorial_encap)
    *(.text.ntruplus768_unpack_m_avx2)
    *(.text.ntruplus768_unpack_m_body_avx2)
    *ntt.o(.text)
    *ntt_m.o(.text)
    *(.text.ntruplus768_pack_m_lazy10788_avx2)
    *(.text.ntruplus768_pack_m_highrange12699_avx2)
    *basemul.o(.text)
  }
}
INSERT BEFORE .text;
