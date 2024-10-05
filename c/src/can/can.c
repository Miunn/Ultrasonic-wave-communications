#include "can/can.h"

int createCanMessage(int can_id, char *data, int data_len, char *_frame) {
  return -1;
}

int decodeCanMessage(char *frame_buffer, int f_buff_len, char *_data,
                     int *_data_len, int *_can_id) {
  return 1;
}
