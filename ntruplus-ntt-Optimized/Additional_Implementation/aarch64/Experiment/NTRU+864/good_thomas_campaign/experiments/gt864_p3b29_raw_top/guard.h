#include <sys/mman.h>
/* Full kernel at both exact allocation edges, disjoint and exact alias.
 * Compare modular coefficients, not old integer representatives.
 */
static void guard_check(void) {
    size_t page=(size_t)sysconf(_SC_PAGESIZE);
    uint8_t *a=mmap(0,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    uint8_t *b=mmap(0,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(a==MAP_FAILED||b==MAP_FAILED||mprotect(a+page,page,PROT_READ|PROT_WRITE)||mprotect(b+page,page,PROT_READ|PROT_WRITE))exit(9);
    int16_t expected[864];
    for(int edge=0;edge<2;edge++)for(int alias=0;alias<2;alias++)for(int t=0;t<64;t++) {
        int16_t *in=(int16_t*)(a+page+(edge?page-1728:0));
        int16_t *out=alias?in:(int16_t*)(b+page+(edge?page-1728:0));
        for(int i=0;i<864;i++) {uint8_t x;randombytes(&x,1);in[i]=t==0?-3:t==1?4:(x&7)-3;}
        forward_gt[0](expected,in);forward_gt[1](out,in);
        for(int i=0;i<864;i++)if(((int)out[i]-expected[i])%3457){fprintf(stderr,"guard modular mismatch\n");exit(9);}
    }
    munmap(a,3*page);munmap(b,3*page);
    puts("guard_correctness=pass cases=256 both_edges=pass disjoint_and_exact_alias=pass");
}
