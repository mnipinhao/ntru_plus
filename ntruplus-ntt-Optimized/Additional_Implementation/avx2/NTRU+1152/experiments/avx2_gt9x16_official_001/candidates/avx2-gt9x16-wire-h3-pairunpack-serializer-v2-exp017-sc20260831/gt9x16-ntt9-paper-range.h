#ifndef NTRUPLUS1152_EXP001_NTT9_PAPER_RANGE_H
#define NTRUPLUS1152_EXP001_NTT9_PAPER_RANGE_H

#include <stdint.h>

#define NTRUPLUS1152_EXP001_PAPER_INPUT_MIN (-1795)
#define NTRUPLUS1152_EXP001_PAPER_INPUT_MAX (1780)
#define NTRUPLUS1152_EXP001_PAPER_R1_FINAL_MIN (-13128)
#define NTRUPLUS1152_EXP001_PAPER_R1_FINAL_MAX (13128)
#define NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MIN (-13128)
#define NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MAX (13128)

static const int16_t ntruplus1152_exp001_paper_distance8_zeta[9][1] = {
  {-147},
  {-886},
  {1033},
  {-460},
  {708},
  {-248},
  {682},
  {1265},
  {1510},
};
static const int16_t ntruplus1152_exp001_paper_distance4_zeta[9][2] = {
  {-147, 366},
  {1033, 1520},
  {-886, 1571},
  {1510, -867},
  {1265, -257},
  {682, 1124},
  {708, 1},
  {-460, 722},
  {-248, -723},
};
static const int16_t ntruplus1152_exp001_paper_distance2_zeta[9][4] = {
  {-147, 366, -109, 1118},
  {-886, 1571, -704, 624},
  {1033, 1520, 813, 1715},
  {-248, -723, 357, -395},
  {-460, 722, 1164, -1346},
  {708, 1, -1521, -1716},
  {1265, -257, 256, -1484},
  {1510, -867, 1590, 1262},
  {682, 1124, 1611, 222},
};
static const int16_t ntruplus1152_exp001_paper_distance1_zeta[9][8] = {
  {-147, 366, -109, 1118, 1339, -794, 1181, 446},
  {1033, 1520, 813, 1715, -1202, 594, -1197, 511},
  {-886, 1571, -704, 624, -137, 200, 16, -957},
  {682, 1124, 1611, 222, 1713, 603, -1058, -1105},
  {1510, -867, 1590, 1262, -820, -216, 121, 757},
  {1265, -257, 256, -1484, -893, -387, 937, 348},
  {-460, 722, 1164, -1346, 639, 455, -655, 502},
  {-248, -723, 357, -395, 1577, 95, 699, -541},
  {708, 1, -1521, -1716, 1241, -550, -44, 39},
};


#endif
