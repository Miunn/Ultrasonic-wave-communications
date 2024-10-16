#include "can/can.h"
#include <stdio.h>
#include <stdlib.h>

void printCanMessage(canMessage message, int len) {
  printf("[ ");
  for (int i = 0; i < len; i++) {
    printf("%d ", message[i]);
  }
  printf("]\n");
}

int createCanMessage(int can_id, short *data, int data_len,
                     canMessage *_frame) {
  // preconditions ----------------------------
  if (data_len > 64) {
    return -1;
  }
  // allocations ------------------------------
  short *preframe = (short *)calloc(sizeof(short), (43 + data_len));
  *_frame = (canMessage)calloc(sizeof(short), (43 + data_len + data_len / 3));
  if (*_frame == NULL || preframe == NULL) {
    return -2;
  }
  // Start bit b0 ------------------------------
  (preframe)[0] = 1;
  // IDENT [b1 to b12] -------------------------
  for (int i = 1; i < 13; i++) {
    if (((short)can_id) & (1 << (i - 1))) {
      (preframe)[i] = 1;
    } else {
      (preframe)[i] = 0;
    }
  }
  // COMMAND [b13 to b18] ----------------------
  // DATA [b19 to ...] -------------------------
  int ptr = 19;
  int i = 0;
  for (i = 0; i < data_len; i++) {
    (preframe)[ptr + i] = data[i];
  }
  ptr += i;
  // CRC [len 16] ------------------------------
  ptr += 16;
  // ACK [len 2] -------------------------------
  ptr += 2;
  // EOF [len 7] -------------------------------
  ptr += 7;
  // stuffing ----------------------------------
  puts("now the fun part");
  int offset = 0;
  int rep_counter = 0;
  short last = -1;
  for (int i = 0; i < ptr; i++) {
    (*_frame)[i + offset] = preframe[i];
    if (last != preframe[i]) {
      rep_counter = 0;
      last = preframe[i];
    }
    rep_counter++;
    if (rep_counter == 5) {
      last = (last + 1) % 2;
      (*_frame)[i + (++offset)] = last;
      rep_counter = 1;
      ptr++;
    }
  }
  free(preframe);
  return ptr;
}

int decodeCanMessage(canMessage frame_buffer, int f_buff_len, short **_data,
                     int *_data_len, int *_can_id) {
  // Allocations
  short *after_buff = (short *)calloc(sizeof(short), f_buff_len);
  int r_length = f_buff_len;
  // TODO seeking end of frame

  // TODO Frame Integrity (removal of bit stuffing)
  for (int i = 0; i < f_buff_len;) {
  }
  // TODO Frame Verification

  // TODO getting IDENT

  // TODO getting DATA
  *_data = (short *)calloc(sizeof(short), f_buff_len - 43);

  free(after_buff);
  return 1;
}

#ifdef MAIN_TEST_CAN

#include <assert.h>

int main() {
  short data[] = {1, 0, 0, 1, 1};
  canMessage frame;
  // printf("so far so good\n");
  int n = createCanMessage(0x123, data, 5, &frame);
  printf("%d\n", n);
  assert(n >= 0);
  printCanMessage(frame, n);
  return 0;
}

#endif
