#ifndef __SPEECH_CLIENT_H__
#define __SPEECH_CLIENT_H__

#include <rtthread.h>

int speech_client_transcribe(char *text, rt_size_t text_size);
int speech_client_transcribe_seconds(char *text, rt_size_t text_size, rt_uint32_t seconds);
int speech_client_transcribe_press_to_talk(char *text, rt_size_t text_size);
int speech_client_sync_time(void);
int speech_client_sync_time_from_response(const char *body);
void speech_client_press_to_talk_begin(void);
void speech_client_press_to_talk_end(void);

#endif /* __SPEECH_CLIENT_H__ */
