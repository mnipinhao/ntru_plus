#define ntruplus768_exp001_pack_identity14 ntruplus768_exp001_pack_triad_m
#define main shared_domain_checks
#include "test_pack_identity14.c"
#undef main

int main(void){
    _Alignas(32) int16_t input[768]={0};
    uint8_t output[1152];
    check(input,output);
    for(int i=0;i<768;i++)for(int sign=-1;sign<=1;sign+=2){
        input[i]=(int16_t)sign;check(input,output);input[i]=0;
    }
    for(int i=0;i<768;i++)input[i]=(int16_t)(i%2?32767:-32768);
    check(input,output);
    if(shared_domain_checks())return 1;
    puts("PASS mask/store ASM: inherited exhaustive test plus 1536 signed impulses, zero and alternating boundary");
    return 0;
}
