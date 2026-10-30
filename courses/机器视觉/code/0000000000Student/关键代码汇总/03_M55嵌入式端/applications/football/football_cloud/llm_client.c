#include <rtthread.h>
#include <string.h>

#ifdef RT_USING_MSH
#include <finsh.h>
#endif

#include "json_util.h"
#include "llm_client.h"
#include "llm_config.h"
#include "tts_client.h"
#include "user_preferences.h"

#if defined(RT_WLAN_MANAGE_ENABLE)
#include <drivers/wlan.h>
#endif

#if defined(RT_USING_NETDEV)
#include <arpa/inet.h>
#include <netdev.h>
#endif

#if defined(PKG_USING_WEBCLIENT)
#include <webclient.h>
#endif

#define LLM_SERVER_AUTH_PLACEHOLDER "PUT_YOUR_AUTH_TOKEN_HERE"
#define LLM_FOCUSTALK_AUTH_PLACEHOLDER "PUT_YOUR_FOCUSTALK_SERVER_AUTH_HERE"
#define LLM_PROMPT_BUFFER_SIZE        768
#define LLM_SYSTEM_PROMPT_BUFFER_SIZE 512
#define LLM_REQUEST_BUFFER_SIZE       1800
#define LLM_SSE_LINE_SIZE             1024
#define LLM_SSE_CHUNK_SIZE            512

typedef struct
{
    char system_prompt[LLM_SYSTEM_PROMPT_BUFFER_SIZE];
    char escaped_system[LLM_SYSTEM_PROMPT_BUFFER_SIZE];
    char escaped_prompt[LLM_PROMPT_BUFFER_SIZE];
    char request[LLM_REQUEST_BUFFER_SIZE];
    char body[LLM_RESPONSE_BUFFER_SIZE];
    char error_message[160];
} llm_chat_workspace_t;

typedef struct
{
    char *reply;
    rt_size_t reply_size;
    rt_size_t reply_len;
    rt_bool_t print_tokens;
} llm_stream_capture_t;

static rt_bool_t llm_network_is_ready(void)
{
#if defined(RT_WLAN_MANAGE_ENABLE)
    if ((rt_wlan_is_connected() != RT_TRUE) || (rt_wlan_is_ready() != RT_TRUE))
    {
        rt_kprintf("llm: Wi-Fi network is not ready.\r\n");
        return RT_FALSE;
    }
#endif

#if defined(RT_USING_NETDEV)
    if ((netdev_default == RT_NULL) ||
        !netdev_is_up(netdev_default) ||
        !netdev_is_link_up(netdev_default))
    {
        rt_kprintf("llm: default network interface is not ready.\r\n");
        return RT_FALSE;
    }
#endif
    return RT_TRUE;
}

static rt_bool_t llm_config_is_valid(void)
{
    if ((LLM_SERVER_AUTH[0] == '\0') ||
        (rt_strcmp(LLM_SERVER_AUTH, LLM_SERVER_AUTH_PLACEHOLDER) == 0) ||
        (rt_strcmp(LLM_SERVER_AUTH, LLM_FOCUSTALK_AUTH_PLACEHOLDER) == 0) ||
        (LLM_API_URL[0] == '\0'))
    {
        rt_kprintf("llm: configure LLM_API_URL and LLM_SERVER_AUTH first.\r\n");
        return RT_FALSE;
    }

    if (rt_strncmp(LLM_API_URL, "https://", 8) != 0)
    {
        rt_kprintf("llm: LLM_API_URL must use HTTPS.\r\n");
        return RT_FALSE;
    }
    return RT_TRUE;
}

static rt_size_t llm_utf8_prefix_len(const char *text, rt_size_t max_bytes)
{
    rt_size_t len = 0U;

    if (text == RT_NULL)
    {
        return 0U;
    }

    while ((text[len] != '\0') && (len < max_bytes))
    {
        unsigned char ch = (unsigned char)text[len];
        rt_size_t step = 1U;
        rt_size_t index;

        if ((ch & 0x80U) == 0U)
        {
            step = 1U;
        }
        else if ((ch & 0xE0U) == 0xC0U)
        {
            step = 2U;
        }
        else if ((ch & 0xF0U) == 0xE0U)
        {
            step = 3U;
        }
        else if ((ch & 0xF8U) == 0xF0U)
        {
            step = 4U;
        }

        if ((len + step) > max_bytes)
        {
            break;
        }

        for (index = 1U; index < step; index++)
        {
            if (text[len + index] == '\0')
            {
                step = 1U;
                break;
            }
        }

        len += step;
    }

    return len;
}

static rt_size_t llm_reply_limit(void)
{
    return (LLM_ASSISTANT_MAX_BYTES > 0) ? LLM_ASSISTANT_MAX_BYTES : 1U;
}

static rt_bool_t llm_limit_text_inplace(char *text)
{
    rt_size_t limit = llm_reply_limit();
    rt_size_t keep;

    if (text == RT_NULL)
    {
        return RT_FALSE;
    }

    keep = llm_utf8_prefix_len(text, limit);
    if (text[keep] == '\0')
    {
        return RT_FALSE;
    }

    text[keep] = '\0';
    rt_kprintf("llm: reply truncated to %u bytes for screen/TTS.\r\n",
               (unsigned int)limit);
    return RT_TRUE;
}

#if defined(PKG_USING_WEBCLIENT)
static int llm_read_body(struct webclient_session *session, char *body, rt_size_t body_size)
{
    int content_length;
    int read_len;
    rt_size_t total = 0;

    content_length = webclient_content_length_get(session);
    while (total < (body_size - 1U))
    {
        rt_size_t remain = body_size - total - 1U;
        if ((content_length >= 0) && ((int)remain > (content_length - (int)total)))
        {
            remain = (rt_size_t)(content_length - (int)total);
        }
        if (remain == 0U)
        {
            break;
        }

        read_len = webclient_read(session, body + total, remain);
        if (read_len < 0)
        {
            return -RT_ERROR;
        }
        if (read_len == 0)
        {
            break;
        }
        total += (rt_size_t)read_len;
    }

    body[total] = '\0';
    if ((content_length >= 0) && (total < (rt_size_t)content_length))
    {
        rt_kprintf("llm: response was truncated at %u bytes.\r\n", (unsigned int)total);
    }
    return RT_EOK;
}

int llm_client_chat(const char *prompt, char *reply, rt_size_t reply_size)
{
    struct webclient_session *session = RT_NULL;
    llm_chat_workspace_t *workspace;
    int request_len;
    int status;
    int ret = -RT_ERROR;

    if ((prompt == RT_NULL) || (prompt[0] == '\0') || (reply == RT_NULL) || (reply_size == 0U))
    {
        return -RT_EINVAL;
    }
    reply[0] = '\0';

    if ((llm_network_is_ready() != RT_TRUE) || (llm_config_is_valid() != RT_TRUE))
    {
        return -RT_ERROR;
    }
    workspace = rt_malloc(sizeof(*workspace));
    if (workspace == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    rt_memset(workspace, 0, sizeof(*workspace));
    if (user_preferences_build_system_prompt(workspace->system_prompt,
                                             sizeof(workspace->system_prompt)) != RT_EOK)
    {
        rt_kprintf("llm: runtime system prompt is too long.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }
    if (json_util_escape(workspace->system_prompt, workspace->escaped_system,
                         sizeof(workspace->escaped_system)) != RT_EOK)
    {
        rt_kprintf("llm: system prompt is too long.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }
    if (json_util_escape(prompt, workspace->escaped_prompt,
                         sizeof(workspace->escaped_prompt)) != RT_EOK)
    {
        rt_kprintf("llm: prompt is too long.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }

    request_len = rt_snprintf(workspace->request, sizeof(workspace->request),
        "{\"model\":\"%s\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},"
        "{\"role\":\"user\",\"content\":\"%s\"}],\"max_tokens\":%d}",
        LLM_MODEL, workspace->escaped_system, workspace->escaped_prompt,
        (int)LLM_ASSISTANT_MAX_TOKENS);
    if ((request_len <= 0) || (request_len >= (int)sizeof(workspace->request)))
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }

    session = webclient_session_create(LLM_HEADER_BUFFER_SIZE);
    if (session == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    if (webclient_header_fields_add(session, "Content-Length: %d\r\n", request_len) < 0 ||
        webclient_header_fields_add(session, "Content-Type: application/json\r\n") < 0 ||
        webclient_header_fields_add(session, "Authorization: Bearer %s\r\n", LLM_SERVER_AUTH) < 0)
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }

    status = webclient_post(session, LLM_API_URL, workspace->request, (rt_size_t)request_len);
    if (status < 0)
    {
        rt_kprintf("llm: HTTPS request failed(%d).\r\n", status);
        goto __exit;
    }
    if (llm_read_body(session, workspace->body, sizeof(workspace->body)) != RT_EOK)
    {
        goto __exit;
    }
    if ((status < 200) || (status >= 300))
    {
        if (json_util_get_string(workspace->body, "message", workspace->error_message,
                                 sizeof(workspace->error_message)) == RT_EOK)
        {
            rt_kprintf("llm: HTTP %d: %s\r\n", status, workspace->error_message);
        }
        else
        {
            rt_kprintf("llm: HTTP error %d.\r\n", status);
        }
        goto __exit;
    }
    if ((json_util_get_path_string(workspace->body, "choices[0].message.content", reply, reply_size) != RT_EOK) &&
        (json_util_get_string(workspace->body, "content", reply, reply_size) != RT_EOK))
    {
        rt_kprintf("llm: response does not contain a text content field.\r\n");
        goto __exit;
    }
    llm_limit_text_inplace(reply);
    ret = RT_EOK;

__exit:
    if (session != RT_NULL)
    {
        webclient_close(session);
    }
    rt_free(workspace);
    return ret;
}

int llm_client_chat_stream(const char *prompt,
                            llm_token_callback on_token,
                            void *user_data)
{
    struct webclient_session *session = RT_NULL;
    char system_prompt[LLM_SYSTEM_PROMPT_BUFFER_SIZE];
    char escaped_system[LLM_SYSTEM_PROMPT_BUFFER_SIZE];
    char escaped_prompt[LLM_PROMPT_BUFFER_SIZE];
    char request[LLM_REQUEST_BUFFER_SIZE];
    char line_buf[LLM_SSE_LINE_SIZE];
    char token[256];
    char limited_token[256];
    char error_message[160];
    char body[512];
    char ch;
    rt_size_t delivered_len = 0U;
    int request_len;
    int line_pos;
    int status;
    int ret = -RT_ERROR;

    if ((prompt == RT_NULL) || (prompt[0] == '\0') || (on_token == RT_NULL))
    {
        return -RT_EINVAL;
    }

    if ((llm_network_is_ready() != RT_TRUE) || (llm_config_is_valid() != RT_TRUE))
    {
        return -RT_ERROR;
    }
    if (user_preferences_build_system_prompt(system_prompt, sizeof(system_prompt)) != RT_EOK)
    {
        rt_kprintf("llm: runtime system prompt is too long.\r\n");
        return -RT_ENOMEM;
    }
    if (json_util_escape(system_prompt, escaped_system, sizeof(escaped_system)) != RT_EOK)
    {
        rt_kprintf("llm: system prompt is too long.\r\n");
        return -RT_ENOMEM;
    }
    if (json_util_escape(prompt, escaped_prompt, sizeof(escaped_prompt)) != RT_EOK)
    {
        rt_kprintf("llm: prompt is too long.\r\n");
        return -RT_ENOMEM;
    }

    request_len = rt_snprintf(request, sizeof(request),
        "{\"model\":\"%s\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},"
        "{\"role\":\"user\",\"content\":\"%s\"}],\"max_tokens\":%d,\"stream\":true}",
        LLM_MODEL, escaped_system, escaped_prompt, (int)LLM_ASSISTANT_MAX_TOKENS);
    if ((request_len <= 0) || (request_len >= (int)sizeof(request)))
    {
        return -RT_ENOMEM;
    }

    session = webclient_session_create(LLM_HEADER_BUFFER_SIZE);
    if (session == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    webclient_set_timeout(session, 30000);
    if (webclient_header_fields_add(session, "Content-Length: %d\r\n", request_len) < 0 ||
        webclient_header_fields_add(session, "Content-Type: application/json\r\n") < 0 ||
        webclient_header_fields_add(session, "Authorization: Bearer %s\r\n", LLM_SERVER_AUTH) < 0)
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }

    status = webclient_post(session, LLM_API_URL, request, (rt_size_t)request_len);
    if (status < 0)
    {
        rt_kprintf("llm: HTTPS request failed(%d).\r\n", status);
        goto __exit;
    }
    if ((status < 200) || (status >= 300))
    {
        if (llm_read_body(session, body, sizeof(body)) == RT_EOK)
        {
            if (json_util_get_string(body, "error", error_message,
                                      sizeof(error_message)) == RT_EOK)
            {
                rt_kprintf("llm: HTTP %d error: %s\r\n", status, error_message);
            }
            else
            {
                rt_kprintf("llm: HTTP error %d.\r\n", status);
            }
        }
        else
        {
            rt_kprintf("llm: HTTP error %d.\r\n", status);
        }
        goto __exit;
    }

    line_pos = 0;
    ret = RT_EOK;

    {
        char chunk_buf[LLM_SSE_CHUNK_SIZE];
        int chunk_off = 0;
        int chunk_len = 0;

        while (1)
        {
            if (chunk_off >= chunk_len)
            {
                chunk_len = webclient_read(session, chunk_buf, sizeof(chunk_buf));
                if (chunk_len < 0)
                {
                    ret = -RT_ERROR;
                    break;
                }
                if (chunk_len == 0)
                {
                    break;
                }
                chunk_off = 0;
            }

            ch = chunk_buf[chunk_off++];

            if (ch == '\n')
            {
                if (line_pos > 0 && line_buf[line_pos - 1] == '\r')
                {
                    line_pos--;
                }
                line_buf[line_pos] = '\0';

                if (rt_strncmp(line_buf, "data: ", 6) == 0)
                {
                    const char *data = line_buf + 6;
                    if (rt_strcmp(data, "[DONE]") == 0)
                    {
                        break;
                    }
                    if (((json_util_get_path_string(data, "choices[0].delta.content",
                              token, sizeof(token)) == RT_EOK) ||
                         (json_util_get_string(data, "c", token, sizeof(token)) == RT_EOK)) &&
                        token[0] != '\0')
                    {
                        rt_size_t limit = llm_reply_limit();
                        rt_size_t remain;
                        rt_size_t token_len;
                        rt_size_t keep;

                        if (delivered_len >= limit)
                        {
                            rt_kprintf("llm: stream reply truncated to %u bytes for screen/TTS.\r\n",
                                       (unsigned int)limit);
                            goto __exit;
                        }

                        remain = limit - delivered_len;
                        token_len = rt_strlen(token);
                        keep = llm_utf8_prefix_len(token, remain);
                        if (keep > 0U)
                        {
                            rt_memcpy(limited_token, token, keep);
                            limited_token[keep] = '\0';
                            delivered_len += keep;
                            on_token(limited_token, user_data);
                        }

                        if ((keep < token_len) || (delivered_len >= limit))
                        {
                            rt_kprintf("llm: stream reply truncated to %u bytes for screen/TTS.\r\n",
                                       (unsigned int)limit);
                            goto __exit;
                        }
                    }
                }
                line_pos = 0;
            }
            else if (line_pos < (int)(sizeof(line_buf) - 1))
            {
                line_buf[line_pos++] = ch;
            }
        }
    }

__exit:
    webclient_close(session);
    return ret;
}
#else
int llm_client_chat(const char *prompt, char *reply, rt_size_t reply_size)
{
    (void)prompt;
    (void)reply;
    (void)reply_size;
    rt_kprintf("llm: enable WebClient with TLS support first.\r\n");
    return -RT_ERROR;
}

int llm_client_chat_stream(const char *prompt,
                            llm_token_callback on_token,
                            void *user_data)
{
    (void)prompt;
    (void)on_token;
    (void)user_data;
    rt_kprintf("llm: enable WebClient with TLS support first.\r\n");
    return -RT_ERROR;
}
#endif /* PKG_USING_WEBCLIENT */

int llm_client_chat_test(void)
{
    char reply[512];
    int ret;

    ret = llm_client_chat("Please reply with one short greeting.", reply, sizeof(reply));
    if (ret == RT_EOK)
    {
        rt_kprintf("llm: %s\r\n", reply);
    }
    return ret;
}

static void llm_test_token_callback(const char *token, void *user_data)
{
    llm_stream_capture_t *capture = (llm_stream_capture_t *)user_data;
    rt_size_t len;
    rt_size_t remain;

    if (token == RT_NULL)
    {
        return;
    }

    if ((capture == RT_NULL) || (capture->print_tokens == RT_TRUE))
    {
        rt_kprintf("%s", token);
    }

    if ((capture == RT_NULL) || (capture->reply == RT_NULL) ||
        (capture->reply_size == 0U) ||
        (capture->reply_len >= capture->reply_size - 1U))
    {
        return;
    }

    len = rt_strlen(token);
    remain = capture->reply_size - 1U - capture->reply_len;
    if (len > remain)
    {
        len = remain;
    }
    rt_memcpy(capture->reply + capture->reply_len, token, len);
    capture->reply_len += len;
    capture->reply[capture->reply_len] = '\0';
}

int llm_client_chat_test_stream(void)
{
    char reply[512] = {0};
    llm_stream_capture_t capture;
    int ret;

    capture.reply = reply;
    capture.reply_size = sizeof(reply);
    capture.reply_len = 0U;
    capture.print_tokens = RT_TRUE;

    rt_kprintf("llm test (stream): ");
    ret = llm_client_chat_stream("Please reply with one short greeting.",
                                  llm_test_token_callback, &capture);
    rt_kprintf("\r\n");
    if ((ret == RT_EOK) && (reply[0] != '\0'))
    {
        tts_client_speak_async(reply);
    }
    return ret;
}

static void llm_test(void)
{
    (void)llm_client_chat_test();
}

static void llm_test_stream_cmd(void)
{
    (void)llm_client_chat_test_stream();
}

#ifdef RT_USING_MSH
static int llm_chat(int argc, char **argv)
{
    char prompt[LLM_PROMPT_BUFFER_SIZE];
    char reply[512];
    rt_size_t used = 0;
    int index;
    int written;

    if (argc < 2)
    {
        rt_kprintf("Usage: llm_chat <message>\r\n");
        return -RT_EINVAL;
    }

    prompt[0] = '\0';
    for (index = 1; index < argc; index++)
    {
        written = rt_snprintf(prompt + used, sizeof(prompt) - used, "%s%s",
                              (index == 1) ? "" : " ", argv[index]);
        if ((written < 0) || ((rt_size_t)written >= (sizeof(prompt) - used)))
        {
            rt_kprintf("llm: message is too long.\r\n");
            return -RT_ENOMEM;
        }
        used += (rt_size_t)written;
    }

    if (llm_client_chat(prompt, reply, sizeof(reply)) == RT_EOK)
    {
        rt_kprintf("AI: %s\r\n", reply);
        tts_client_speak_async(reply);
        return RT_EOK;
    }
    return -RT_ERROR;
}

static int llm_chat_stream_cmd(int argc, char **argv)
{
    char prompt[LLM_PROMPT_BUFFER_SIZE];
    char reply[512] = {0};
    llm_stream_capture_t capture;
    rt_size_t used = 0;
    int ret;
    int index;
    int written;

    if (argc < 2)
    {
        rt_kprintf("Usage: llm_chat_stream <message>\r\n");
        return -RT_EINVAL;
    }

    prompt[0] = '\0';
    for (index = 1; index < argc; index++)
    {
        written = rt_snprintf(prompt + used, sizeof(prompt) - used, "%s%s",
                              (index == 1) ? "" : " ", argv[index]);
        if ((written < 0) || ((rt_size_t)written >= (sizeof(prompt) - used)))
        {
            rt_kprintf("llm: message is too long.\r\n");
            return -RT_ENOMEM;
        }
        used += (rt_size_t)written;
    }

    capture.reply = reply;
    capture.reply_size = sizeof(reply);
    capture.reply_len = 0U;
    capture.print_tokens = RT_TRUE;

    rt_kprintf("AI: ");
    ret = llm_client_chat_stream(prompt, llm_test_token_callback, &capture);
    rt_kprintf("\r\n");
    if ((ret == RT_EOK) && (reply[0] != '\0'))
    {
        tts_client_speak_async(reply);
    }
    return ret;
}

MSH_CMD_EXPORT(llm_test, Send a test Chat Completions request);
MSH_CMD_EXPORT(llm_test_stream_cmd, Send a test streaming Chat Completions request);
MSH_CMD_EXPORT(llm_chat, Send text to the configured chat model);
MSH_CMD_EXPORT(llm_chat_stream_cmd, Send text with streaming output);
#endif
