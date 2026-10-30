#ifndef FOOTBALL_VOICE_H
#define FOOTBALL_VOICE_H

#include "../football_protocol/football_protocol.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum football_voice_state
{
    FOOTBALL_VOICE_IDLE = 0,
    FOOTBALL_VOICE_LOCAL_PENDING,
    FOOTBALL_VOICE_LOCAL_PLAYING,
    FOOTBALL_VOICE_CLOUD_PENDING,
    FOOTBALL_VOICE_CLOUD_SPEAKING,
    FOOTBALL_VOICE_COMPLETE,
    FOOTBALL_VOICE_FAILED,
    FOOTBALL_VOICE_CANCELLED
} football_voice_state_t;

typedef struct football_voice_status
{
    football_voice_state_t state;
    rt_uint32_t active_message_id;
    rt_uint16_t queue_depth;
    rt_uint32_t local_played;
    rt_uint32_t cloud_played;
    rt_uint32_t deduplicated;
    rt_uint32_t dropped;
    rt_err_t last_error;
} football_voice_status_t;

rt_err_t football_voice_start(void);
rt_err_t football_voice_enqueue(const football_message_t *message);
rt_err_t football_voice_manual_assistant(void);
void football_voice_cancel(void);
void football_voice_get_status(football_voice_status_t *status);

#ifdef __cplusplus
}
#endif
#endif
