#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include "signal_processing/pbPlots.h"
#include "signal_processing/supportLib.h"
#include "signal_processing/psk_modulation.h"

#define BUFF_SIZE 16384

double* psk_modulation(int* bits, int n)
{
    double* signal = (double*)malloc(BUFF_SIZE * sizeof(double));

    for(int i = 0; i < n; i++){
        assert(bits[i] == 0 || bits[i] == 1);

        for(int j = i*BUFF_SIZE/n; j < (i+1) * BUFF_SIZE/n; j++){
            signal[j] = (bits[i] == 1 ? bits[i] : -1) * sin(n*2 * M_PI * j / BUFF_SIZE);
        }
    }

    return signal;
}

int test_modulation()
{
    int bits[8] = {1, 0, 1, 1, 0, 1, 0, 0};
    
    double* t = (double *) malloc(BUFF_SIZE * sizeof(double));
    double* signal = psk_modulation(bits, 8);

    // Generate time for psk modulation
    for(int i = 0; i < BUFF_SIZE; i++){
        t[i] = i;
    }

    StringReference error;
    RGBABitmapImageReference *imageRef = CreateRGBABitmapImageReference();

    DrawScatterPlot(imageRef, 1600, 1400, t, BUFF_SIZE, signal, BUFF_SIZE, &error);

    size_t length;
    double *pngData = ConvertToPNG(&length, imageRef->image);
    WriteToFile(pngData, length, "plot.png");

    free(pngData);
    free(t);
    free(signal);
    return 0;
}

#ifdef MAIN_TEST_MODULATION
int main()
{
    test_modulation();
    return 0;
}
#endif