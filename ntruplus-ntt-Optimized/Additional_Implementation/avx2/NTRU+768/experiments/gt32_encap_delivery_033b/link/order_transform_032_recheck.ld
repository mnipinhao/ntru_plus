SECTIONS
{
  .text.gt033b.recheck032.hot : ALIGN(64)
  {
    *(.text.gt32_032_encap_control_normal)
    *(.text.gt32_032_encap_candidate_normal)
    *(.text.gt32_032_encap_candidate_reversed)
    *(.text.gt32_032_encap_control_reversed)
    *(.text.ntruplus768_unpack_m_avx2)
    *(.text.ntruplus768_unpack_m_body_avx2)
    build/factorial/common/ntt.o(.text)
    build/factorial/common/ntt_m.o(.text)
    *(.text.ntruplus768_pack_m_lazy10788_avx2)
    *(.text.ntruplus768_pack_m_highrange12699_avx2)
    build/recheck032/basemul.o(.text)
  }
}
INSERT BEFORE .text;
