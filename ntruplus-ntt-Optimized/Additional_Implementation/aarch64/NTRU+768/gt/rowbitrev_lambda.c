#include <stdint.h>

#include "ntt.h"

const int16_t gt_rowbitrev_lambda[2][96] = {
#include "rowbitrev_lambda.inc"
};
