#ifndef CAN_H
#define CAN_H

typedef short *canMessage;

/**
 * Generate a can frame from given parameter
 *
 * @param can_id IDENT
 * @param data DATA
 * @param data_len LEN
 * @return _frame the resulting can frame (_frame is allocated on call of the
 * function so DON'T FORGET TO FREE IT)
 * @return the length of the resulting frame  (-1 on precond. error, -2 on
 * allocation error)
 */
int createCanMessage(int can_id, short *data, int data_len, canMessage *_frame);

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
int decodeCanMessage(canMessage frame_buffer, int f_buff_len, short **_data,
                     int *_data_len, int *_can_id);

/**
 * Convert char array into data parsable into a canMessage
 *
 * @param data the char buffer containing the data (needs to be terminated by
 * '\0')
 * @return _data the short buffer comprensible by createCanMessage (Allocated on
 * call)
 * @returns the length of the resulting buffer
 */
int charToData(char data[], short **_data);

#endif
