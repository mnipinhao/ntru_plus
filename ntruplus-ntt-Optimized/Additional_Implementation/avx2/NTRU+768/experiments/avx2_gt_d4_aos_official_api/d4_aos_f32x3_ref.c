#include "d4_aos_f32x3_ref.h"
enum { Q=3457 };
static int m(long long x){x%=Q;return (int)(x<0?x+Q:x);} static int pw(int a,int e){int x=1;while(e){if(e&1)x=m((long long)x*a);a=m((long long)a*a);e>>=1;}return x;}
static int p(int b,int r,int j,int c){return 16*(16*r+j/2)+8*b+4*(j&1)+c;} static int br(int j){int x=0;for(int n=0;n<5;n++){x=(x<<1)|(j&1);j>>=1;}return x;}
static void ntt32(int16_t s[3][32][2][4],int inverse){int w=pw(641,3),scale=inverse?pw(32,Q-2):1;if(inverse)w=pw(w,Q-2);for(int r=0;r<3;r++)for(int b=0;b<2;b++)for(int c=0;c<4;c++){int16_t tmp[32];for(int j=0;j<32;j++)tmp[j]=s[r][j][b][c];for(int j=0;j<32;j++)s[r][j][b][c]=tmp[br(j)];for(int len=2;len<=32;len*=2)for(int base=0;base<32;base+=len)for(int j=0;j<len/2;j++){int z=m((long long)s[r][base+j+len/2][b][c]*pw(w,32*j/len));int x=s[r][base+j][b][c];s[r][base+j][b][c]=(int16_t)m(x+z);s[r][base+j+len/2][b][c]=(int16_t)m(x-z);}if(inverse)for(int j=0;j<32;j++)s[r][j][b][c]=(int16_t)m((long long)s[r][j][b][c]*scale);}}
void d4aos_f32x3_ref_forward(d4aos_ntt_poly *out,const d4aos_coeff_poly *in){int16_t s[3][32][2][4];for(int r=0;r<3;r++)for(int j=0;j<32;j++)for(int b=0;b<2;b++)for(int c=0;c<4;c++){int i=(64*r+33*j)%96;int a=in->coeff[4*i+c],h=in->coeff[384+4*i+c];s[r][j][b][c]=(int16_t)m((long long)m(a+(b?723:2735)*h)*pw(b?2:22,i));}ntt32(s,0);for(int R=0;R<3;R++)for(int j=0;j<32;j++)for(int b=0;b<2;b++)for(int c=0;c<4;c++){int x=0;for(int r=0;r<3;r++)x=m(x+(long long)s[r][j][b][c]*pw(pw(641,32),R*r));out->lane[p(b,R,j,c)]=(int16_t)x;}}
void d4aos_f32x3_ref_inverse(d4aos_coeff_poly *out,const d4aos_ntt_poly *in){int16_t s[3][32][2][4];for(int R=0;R<3;R++)for(int j=0;j<32;j++)for(int b=0;b<2;b++)for(int c=0;c<4;c++)s[R][j][b][c]=in->lane[p(b,R,j,c)];ntt32(s,1);for(int r=0;r<3;r++)for(int j=0;j<32;j++)for(int c=0;c<4;c++){int u[2];for(int b=0;b<2;b++){int x=0;for(int R=0;R<3;R++)x=m(x+(long long)s[R][j][b][c]*pw(pw(pw(641,32),Q-2),R*r));u[b]=m((long long)x*pw(3,Q-2)*pw(b?2:22,Q-1-((64*r+33*j)%96)));}int h=m((long long)(u[0]-u[1])*pw(m(2735-723),Q-2)),a=m(u[0]-(long long)2735*h),i=(64*r+33*j)%96;out->coeff[4*i+c]=(int16_t)a;out->coeff[384+4*i+c]=(int16_t)h;}}
void d4aos_f32x3_ref_inverse_checkpoint_stage0(d4aos_f32x3_state *out,const d4aos_f32x3_state *in){for(int r=0;r<3;r++)for(int t=0;t<16;t++)for(int b=0;b<2;b++)for(int c=0;c<4;c++){int x=in->lane[16*(16*r+t)+8*b+c],y=in->lane[16*(16*r+t)+8*b+4+c];out->lane[16*(16*r+t)+8*b+c]=(int16_t)m(x+y);out->lane[16*(16*r+t)+8*b+4+c]=(int16_t)m(x-y);}}

/* Native natural-J input -> bit-reversed CT state -> exact canonical L0/L1/L2. */
void d4aos_f32x3_ref_inverse_ntt32_checkpoints(
    d4aos_f32x3_state *after_l0,
    d4aos_f32x3_state *after_l1,
    d4aos_f32x3_state *after_l2,
    d4aos_f32x3_state *after_l3,
    d4aos_f32x3_state *after_l4,
    const d4aos_f32x3_state *in)
{
    int16_t state[3][32][2][4];
    const int inverse_root32 = pw(pw(641, 3), Q - 2);
    d4aos_f32x3_state *checkpoints[5] = {
        after_l0, after_l1, after_l2, after_l3, after_l4
    };

    for (int row = 0; row < 3; ++row) {
        for (int j = 0; j < 32; ++j) {
            const int source_j = br(j);
            for (int branch = 0; branch < 2; ++branch) {
                for (int coeff = 0; coeff < 4; ++coeff) {
                    state[row][j][branch][coeff] =
                        in->lane[p(branch, row, source_j, coeff)];
                }
            }
        }
    }

    for (int layer = 0; layer < 5; ++layer) {
        const int length = 1 << (layer + 1);
        const int half = length / 2;

        for (int row = 0; row < 3; ++row) {
            for (int base = 0; base < 32; base += length) {
                for (int j = 0; j < half; ++j) {
                    const int factor = pw(inverse_root32, 32 * j / length);

                    for (int branch = 0; branch < 2; ++branch) {
                        for (int coeff = 0; coeff < 4; ++coeff) {
                            const int left = state[row][base + j][branch][coeff];
                            const int right = m((long long)
                                state[row][base + j + half][branch][coeff] * factor);
                            state[row][base + j][branch][coeff] =
                                (int16_t)m(left + right);
                            state[row][base + j + half][branch][coeff] =
                                (int16_t)m(left - right);
                        }
                    }
                }
            }
        }

        for (int row = 0; row < 3; ++row) {
            for (int j = 0; j < 32; ++j) {
                for (int branch = 0; branch < 2; ++branch) {
                    for (int coeff = 0; coeff < 4; ++coeff) {
                        checkpoints[layer]->lane[p(branch, row, j, coeff)] =
                            state[row][j][branch][coeff];
                    }
                }
            }
        }
    }
}

/* Exact post-L4 state to compact inverse-DFT3 canonical verification boundary. */
void d4aos_f32x3_ref_inverse_dft3_barrett(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *post_l4)
{
    const int omega_montgomery = -886;
    const int omega_qinv = 13706;
    const int barrett_v = 19412;

    for (int block = 0; block < 16; ++block) {
        for (int lane = 0; lane < 16; ++lane) {
            const int y0 = post_l4->lane[16 * block + lane];
            const int y1 = post_l4->lane[16 * (16 + block) + lane];
            const int y2 = post_l4->lane[16 * (32 + block) + lane];
            const int delta = y2 - y1;
            const int16_t low = (int16_t)(delta * omega_qinv);
            const int omega_term = (delta * omega_montgomery >> 16) -
                ((int)low * Q >> 16);
            const int raw[3] = {
                y0 + y1 + y2,
                y0 - y1 + omega_term,
                y0 - y2 - omega_term
            };

            for (int row = 0; row < 3; ++row) {
                const int quotient = (raw[row] * barrett_v >> 16) >> 10;
                out->lane[16 * (16 * row + block) + lane] =
                    (int16_t)(raw[row] - quotient * Q);
            }
        }
    }
}

/* Compact post-DFT3 [0,q] state to canonical natural coefficients. */
void d4aos_f32x3_ref_inverse_terminal(
    d4aos_coeff_poly *out,
    const d4aos_f32x3_state *post_dft3)
{
    const int twist_base[2] = {22, 2};
    const int crt_alpha[2] = {2735, 723};
    const int inverse96 = pw(96, Q - 2);
    const int delta_inverse = pw(m(crt_alpha[0] - crt_alpha[1]), Q - 2);

    const int dft_slot_to_row[3] = {0, 2, 1};

    for (int dft_slot = 0; dft_slot < 3; ++dft_slot) {
        const int row = dft_slot_to_row[dft_slot];
        for (int block = 0; block < 16; ++block) {
            for (int packed_u = 0; packed_u < 2; ++packed_u) {
                const int natural_index =
                    (64 * row + 33 * (2 * block + packed_u)) % 96;

                for (int coefficient = 0; coefficient < 4; ++coefficient) {
                    int branch_value[2];

                    for (int branch = 0; branch < 2; ++branch) {
                        const int lane = 8 * branch + 4 * packed_u + coefficient;
                        const int value = post_dft3->lane[
                            16 * (16 * dft_slot + block) + lane];
                        const int untwist = pw(
                            twist_base[branch], Q - 1 - natural_index);
                        branch_value[branch] = m(
                            (long long)value * inverse96 * untwist);
                    }

                    const int high = m((long long)
                        (branch_value[0] - branch_value[1]) * delta_inverse);
                    const int low = m(
                        branch_value[0] - (long long)crt_alpha[0] * high);
                    out->coeff[4 * natural_index + coefficient] = (int16_t)low;
                    out->coeff[384 + 4 * natural_index + coefficient] = (int16_t)high;
                }
            }
        }
    }
}
