#ifndef __LLM_CLIENT_H__
#define __LLM_CLIENT_H__

#include <rtthread.h>

typedef void (*llm_token_callback)(const char *token, void *user_data);

int llm_client_chat(const char *prompt, char *reply, rt_size_t reply_size);
int llm_client_chat_stream(const char *prompt,
                            llm_token_callback on_token,
                            void *user_data);
int llm_client_chat_test(void);

#endif /* __LLM_CLIENT_H__ */
