#ifdef MAIN_C

#include <stdio.h>

int main(void) { printf("Hello world !\n"); }

#endif

#ifdef MAIN_ALL

#include <stdio.h>
#include "signal_processing/psk_modulation.h"

int main(void)
{
    test_modulation();
    return 0;
}

#endif