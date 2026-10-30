#ifndef __TTS_CLIENT_H__
#define __TTS_CLIENT_H__

#include <rtthread.h>

int tts_client_speak(const char *text);
int tts_client_speak_async(const char *text);

#endif /* __TTS_CLIENT_H__ */
