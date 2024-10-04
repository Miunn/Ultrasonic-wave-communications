#include "can/can.h"
#include <stdlib.h>

int createCanMessage(int can_id, short *data, int data_len, short **_frame) {
  *_frame = (short *)calloc(sizeof(short), (34 + data_len));
  if (*_frame == NULL) {
    return -1;
  }
  *_frame[0] = 1; // Start bit
  for (int i = 1; i < 13; i++) {
    *_frame[i] = can_id & 1 >> i;
  }
  return (34 + data_len);
}

int decodeCanMessage(short *frame_buffer, int f_buff_len, short **_data,
                     int *_data_len, int *_can_id) {
  return 1;
}

#define MAIN_TEST_CAN
#ifdef MAIN_TEST_CAN

#include <assert.h>
#include <stdio.h>

int main() {
  short data[] = {1, 2, 3, 4};
  short *frame;
  printf("so far so good\n");
  int n = createCanMessage(123, data, 4, &frame);
  printf("%d\n", n);
  assert(n >= 0);
  printf("[ ");
  for (int i = 0; i < n; i++) {
    printf("%d ", frame[i]);
  }
  printf("]\n");
  return 0;
}

#endif
