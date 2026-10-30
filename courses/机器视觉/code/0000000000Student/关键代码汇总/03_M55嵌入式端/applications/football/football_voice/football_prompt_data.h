#ifndef FOOTBALL_PROMPT_DATA_H
#define FOOTBALL_PROMPT_DATA_H

#include <rtthread.h>

typedef enum football_prompt_id
{
    FOOTBALL_PROMPT_GOAL = 0,
    FOOTBALL_PROMPT_RED_CARD,
    FOOTBALL_PROMPT_PENALTY,
    FOOTBALL_PROMPT_DANGER,
    FOOTBALL_PROMPT_MATCH,
    FOOTBALL_PROMPT_PRESSING,
    FOOTBALL_PROMPT_DEFENSIVE_RECOVER
} football_prompt_id_t;

rt_err_t football_prompt_get(football_prompt_id_t id,
                             const rt_uint8_t **pcm,
                             rt_size_t *length);

#endif
