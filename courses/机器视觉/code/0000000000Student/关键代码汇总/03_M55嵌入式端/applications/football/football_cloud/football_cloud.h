#ifndef FOOTBALL_CLOUD_H
#define FOOTBALL_CLOUD_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum football_cloud_state
{
    FOOTBALL_CLOUD_OFFLINE = 0,
    FOOTBALL_CLOUD_WAIT_CONFIG,
    FOOTBALL_CLOUD_CONNECTING,
    FOOTBALL_CLOUD_WAIT_TIME,
    FOOTBALL_CLOUD_READY,
    FOOTBALL_CLOUD_BUSY,
    FOOTBALL_CLOUD_ERROR
} football_cloud_state_t;

typedef struct football_cloud_status
{
    football_cloud_state_t state;
    rt_bool_t wifi_ready;
    rt_bool_t rtc_ready;
    rt_bool_t ai_configured;
    rt_bool_t tencent_configured;
    rt_uint32_t active_request;
    rt_uint32_t completed_requests;
    rt_uint32_t failed_requests;
    rt_err_t last_error;
} football_cloud_status_t;

rt_err_t football_cloud_start(void);
rt_err_t football_cloud_chat(rt_uint32_t request_id, const char *prompt,
                             char *reply, rt_size_t reply_size);
rt_err_t football_cloud_transcribe(rt_uint32_t request_id, rt_uint32_t seconds,
                                   char *text, rt_size_t text_size);
rt_err_t football_cloud_speak(rt_uint32_t request_id, const char *text);
void football_cloud_cancel(rt_uint32_t request_id);
void football_cloud_get_status(football_cloud_status_t *status);

#ifdef __cplusplus
}
#endif
#endif
