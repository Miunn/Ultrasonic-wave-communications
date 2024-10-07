#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include "signal_processing/pbPlots.h"
#include "signal_processing/supportLib.h"
#include "signal_processing/psk_modulation.h"

#define BUFF_SIZE 16384
#define PTS_BITS 1000
#define FREQ 5

double* psk_modulation(int* bits, int n)
{
    double* signal = (double*)malloc(n*PTS_BITS * sizeof(double));

    for(int i = 0; i < n; i++){
        assert(bits[i] == 0 || bits[i] == 1);

        for(int j = i * PTS_BITS; j < (i+1) * PTS_BITS; j++){
            signal[j] = (bits[i] == 1 ? bits[i] : -1) * sin(FREQ*2 * M_PI * j / (float)PTS_BITS);
        }
    }

    return signal;
}

short* decision(double* signal, int n)
{
    short* bits = (short*)malloc(n / PTS_BITS * sizeof(short));

    for(int i = 0; i < n; i++){
        bits[i] = signal[i] > 0 ? 1 : 0;
    }

    return bits;
}

double *bpsk_demodulation(double* modulated, int n, int freq)
{
    double* demodulated = (double*)malloc(n * sizeof(double));

    for(int i = 0; i < n; i++){
        demodulated[i] = modulated[i] * sin(freq * 2 * M_PI * i / (float)PTS_BITS);
    }

    return demodulated;
}

int test_modulation()
{
    int bits[8] = {1, 0, 1, 1, 0, 1, 0, 0};
    
    double* t = (double *) malloc(8 * PTS_BITS * sizeof(double));
    double* signal = psk_modulation(bits, 8);

    // Generate time for psk modulation
    for(int i = 0; i < 8 * PTS_BITS; i++){
        t[i] = i;
    }

    StringReference error;
    RGBABitmapImageReference *imageRef = CreateRGBABitmapImageReference();

    DrawScatterPlot(imageRef, 1600, 1400, t, 8 * PTS_BITS, signal, 8 * PTS_BITS, &error);

    size_t length;
    double *pngData = ConvertToPNG(&length, imageRef->image);
    WriteToFile(pngData, length, "modulated.png");

    double* demodulated = bpsk_demodulation(signal, 8 * PTS_BITS, FREQ);

    RGBABitmapImageReference *imageRef2 = CreateRGBABitmapImageReference();
    DrawScatterPlot(imageRef2, 1600, 1400, t, 8 * PTS_BITS, demodulated, 8 * PTS_BITS, &error);

    pngData = ConvertToPNG(&length, imageRef2->image);
    WriteToFile(pngData, length, "demodulated.png");

    free(pngData);
    free(t);
    free(signal);
    free(demodulated);
    return 0;
}

#ifdef MAIN_TEST_MODULATION
int main()
{
    test_modulation();
    return 0;
}
#endif