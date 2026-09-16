#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void tbl_empty(uint64_t),tbl2_throughput(uint64_t),tbl3_throughput(uint64_t),tbl2_latency(uint64_t),tbl3_latency(uint64_t);
int main(int argc,char**argv){
 if(argc!=3)return 2;uint64_t n=strtoull(argv[2],0,0);
 void(*f)(uint64_t)=!strcmp(argv[1],"empty")?tbl_empty:!strcmp(argv[1],"tbl2t")?tbl2_throughput:!strcmp(argv[1],"tbl3t")?tbl3_throughput:!strcmp(argv[1],"tbl2l")?tbl2_latency:tbl3_latency;
 f(1000);f(n);return 0;
}
