SECTIONS
{
  .text.gt033b.hot : ALIGN(64)
  {
    *(.text.ntruplus768_unpack_m_avx2)
    *(.text.ntruplus768_unpack_m_body_avx2)
    *(.text.ntruplus768_pack_m_lazy10788_avx2)
    *(.text.ntruplus768_pack_m_highrange12699_avx2)
    build/ntt.o(.text)
    build/ntt_m.o(.text)
    build/basemul.o(.text)
    *(.text.gt033b_encap)
  }
}
INSERT BEFORE .text;
