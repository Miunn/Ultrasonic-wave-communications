#ifndef DEF_PSK_MODULATION
#define DEF_PSK_MODULATION

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#ifndef  M_PI
#define  M_PI  3.1415926535897932384626433
#endif

#define BUFF_SIZE 16384

double* psk_modulation(int* bits, int n);

#endif