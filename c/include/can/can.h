#ifndef CAN_H
#define CAN_H

/**
 * Generate a can frame from given parameter
 *
 * @param can_id IDENT
 * @param data DATA
 * @param data_len LEN
 * @return _frame the resulting can frame
 * @return the length of the resulting frame  (-1 on error)
 */
int createCanMessage(int can_id, char *data, int data_len, char *_frame);

/**
 * Decode the can passed by refernce
 *
 * @param frame_buffer the buffer that contains the frame can
 * @param f_buff_len the length of the frame buffer
 *
 * @return _data the data field of the can frame
 * @return _data_len the lenght of the data field
 * @return _can_id the IDENT of the message
 * @returns 0 on success, 1 on error
 */
int decodeCanMessage(char *frame_buffer, int f_buff_len, char *_data,
                     int *_data_len, int *_can_id);

#endif
