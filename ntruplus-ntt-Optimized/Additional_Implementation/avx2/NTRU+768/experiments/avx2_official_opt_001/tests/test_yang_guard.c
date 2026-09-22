#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "poly.h"
void ntruplus768_officialopt_invntt_yang_factored(poly *);
int main(void) {
    long page=sysconf(_SC_PAGESIZE);
    unsigned char *m=mmap(0,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(m==MAP_FAILED || mprotect(m+page,page,PROT_READ|PROT_WRITE)) return 2;
    for(int side=0;side<2;side++) {
        poly *p=(poly *)(m+page+(side?page-sizeof(poly):0));
        for(int trial=0;trial<64;trial++) {
            memset(m+page,0xa5,page);
            for(int i=0;i<768;i++)p->coeffs[i]=((trial>>(i/128))&1)?7644:-7644;
            poly ref=*p;poly_invntt_scale(&ref);
            ntruplus768_officialopt_invntt_yang_factored(p);
            for(int i=0;i<768;i++) if((ref.coeffs[i]-p->coeffs[i])%3457) return 3;
            for(long i=0;i<page;i++) {
                unsigned char *x=m+page+i;
                if((x<(unsigned char*)p || x>=(unsigned char*)(p+1)) && *x!=0xa5)return 4;
            }
        }
    }
    munmap(m,3*page);puts("128 guard-page/canary signed-corner cases pass");return 0;
}
