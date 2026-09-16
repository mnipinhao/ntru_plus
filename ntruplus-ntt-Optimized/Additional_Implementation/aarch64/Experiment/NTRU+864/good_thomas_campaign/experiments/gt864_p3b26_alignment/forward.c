/* P3B26 diagnostic: common input reset is inside every timed boundary.
 * The KEM input contract is [-3,4]; never feed transformed output back as input.
 * Include the unchanged PMU/RNG support from the staged KEM harness.
 */
#define main kem_harness_main
#include "harness.c"
#undef main
typedef void (*ntt_gt)(int16_t *,const int16_t *);
typedef void (*ntt_sc)(int16_t *);
typedef void (*pack_fn)(uint8_t *,const int16_t *);
static int16_t source[864] __attribute__((aligned(16)));
static int16_t work[864] __attribute__((aligned(16)));
static int16_t output[864] __attribute__((aligned(16)));
static void *libs[3];
static ntt_gt forward_gt[2];
static ntt_sc forward_sc;
static pack_fn pack[3];
static void transform(int v) {
    memcpy(work,source,sizeof work);
    if(v==2)forward_sc(work);
    else if(v<2)forward_gt[v](output,work);
    else __asm__ volatile("" : : "r"(work) : "memory");
    sink+=(v==2||v==3)?(uint16_t)work[0]:(uint16_t)output[0];
}
int main(int argc,char **argv) {
    const char *names[]={"gt","t1","sc","reset_only"};
    for(int v=0;v<3;v++) {
        char name[32];snprintf(name,sizeof name,"./%s.so",names[v]);
        libs[v]=dlopen(name,RTLD_NOW|RTLD_LOCAL);if(!libs[v]){puts(dlerror());return 2;}
        if(v==2)forward_sc=(ntt_sc)dlsym(libs[v],"poly_ntt");
        else forward_gt[v]=(ntt_gt)dlsym(libs[v],"gt_d1_poly_ntt");
        pack[v]=(pack_fn)dlsym(libs[v],v==2?"poly_tobytes":"p3b12_candidate_tobytes");
        if(!pack[v] || (v==2?!forward_sc:!forward_gt[v]))return 2;
    }
    int16_t oracle[864];uint8_t expected[1296],actual[1296];
    for(int t=0;t<64;t++) {
        for(int k=0;k<864;k++) {uint8_t b;randombytes(&b,1);source[k]=t==0?-3:t==1?4:(b&7)-3;}
        for(int v=0;v<3;v++) {
            transform(v);const int16_t *out=v==2?work:output;
            pack[v](actual,out);
            if(v==0){memcpy(oracle,out,sizeof oracle);memcpy(expected,actual,sizeof expected);}
            else if(memcmp(expected,actual,sizeof expected)||(v==1&&memcmp(oracle,out,sizeof oracle))) {
                fprintf(stderr,"forward mismatch case=%d variant=%d\n",t,v);return 4;
            }
        }
    }
    puts("forward_correctness=pass cases=64 T0_T1_bitexact=pass SUPERCOP_wire_equivalence=pass");
    fd=counter(PERF_COUNT_HW_CPU_CYCLES,-1);
    int c1=counter(PERF_COUNT_HW_INSTRUCTIONS,fd),c2=counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);
    if(fd<0||c1<0||c2<0)return 2;
    ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
    int reverse=argc>1?atoi(argv[1]):0;
    for(int s=0;s<61;s++)for(int p=0;p<4;p++) {
        int v=reverse?3-p:p;for(int k=0;k<32;k++)transform(v);
        struct counts x=readpmu();for(int k=0;k<400;k++)transform(v);struct counts y=readpmu();
        printf("forward,%s,%.3f,%.3f,%.3f\n",names[v],(y.v[0]-x.v[0])/400.,(y.v[1]-x.v[1])/400.,(y.v[2]-x.v[2])/400.);
    }
    return 0;
}
