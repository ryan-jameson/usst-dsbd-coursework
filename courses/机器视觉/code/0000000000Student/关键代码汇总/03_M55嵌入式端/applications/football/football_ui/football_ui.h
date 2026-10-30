#ifndef FOOTBALL_UI_H
#define FOOTBALL_UI_H

#include "football_protocol.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    rt_uint32_t total_messages;
    rt_uint32_t counter_attack_messages;
    rt_uint32_t set_piece_messages;
    rt_uint32_t goal_messages;
    rt_uint32_t high_danger_messages;
    rt_uint32_t home_messages;
    rt_uint32_t away_messages;
    rt_uint32_t shared_seq;
    rt_uint32_t last_update_tick;
    rt_uint8_t link_status;
    rt_uint8_t sd_status;
    rt_uint8_t audio_status;
    rt_uint8_t active_page;
    rt_uint8_t home_score;
    rt_uint8_t away_score;
    rt_uint8_t match_phase;
    rt_uint8_t possession_home;
    rt_uint8_t danger_level;
    rt_uint8_t wifi_status;
    rt_uint8_t cloud_status;
    rt_uint8_t voice_status;
    rt_uint16_t match_minute;
    rt_uint16_t match_second;
    char current_tactic[FOOTBALL_TACTIC_TEXT_MAX];
    char ai_text[160];
    football_message_t last_message;
    FootballSharedEvent recent_events[FOOTBALL_RECENT_EVENT_MAX];
    rt_uint8_t recent_count;
    rt_uint8_t recent_write_index;
} football_ui_snapshot_t;

rt_err_t football_ui_start(void);
void football_ui_refresh(void);
void football_ui_get_snapshot(football_ui_snapshot_t *snapshot);
void football_ui_set_tactic(const char *formation, rt_bool_t dirty);

#ifdef __cplusplus
}
#endif

#endif
