#ifndef FOOTBALL_PROTOCOL_H
#define FOOTBALL_PROTOCOL_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FOOTBALL_PROTOCOL_VERSION       1u
#define FOOTBALL_SHARED_MAGIC           0x46424353u
#define FOOTBALL_SHARED_VERSION         FOOTBALL_PROTOCOL_VERSION
#define FOOTBALL_RECENT_EVENT_MAX       8u
#define FOOTBALL_TACTIC_TEXT_MAX        32u
#define FOOTBALL_EVENT_TEXT_MAX         32u
#define FOOTBALL_EXT_BYTES              256u
#define FOOTBALL_EVENT_NAME_MAX         32u
#define FOOTBALL_TEAM_MAX               16u
#define FOOTBALL_EVENT_TYPE_MAX         24u
#define FOOTBALL_CHECKSUM_MAX           24u
#define FOOTBALL_COMMENTARY_MAX         193u
#define FOOTBALL_JSON_MAX               512u

/* Wire format: one UTF-8 JSON object per line. */
typedef struct
{
    rt_uint16_t protocol_version;
    rt_uint32_t message_id;
    char event_type[FOOTBALL_EVENT_TYPE_MAX];
    rt_uint32_t timestamp;
    char event[FOOTBALL_EVENT_NAME_MAX];
    char team[FOOTBALL_TEAM_MAX];
    float confidence;
    rt_int32_t danger;
    rt_int32_t ball_x;
    rt_int32_t ball_y;
    char checksum[FOOTBALL_CHECKSUM_MAX];
    char commentary[FOOTBALL_COMMENTARY_MAX];
} football_message_t;

typedef struct FootballSharedEvent
{
    rt_uint32_t message_id;
    rt_uint16_t event_id;
    rt_uint16_t danger;
    rt_uint32_t timestamp_ms;
    char event_name[FOOTBALL_EVENT_TEXT_MAX];
    char team[FOOTBALL_TEAM_MAX];
    rt_uint16_t confidence_permille;
    rt_int16_t ball_x;
    rt_int16_t ball_y;
} FootballSharedEvent;

typedef struct FootballSharedTactic
{
    char tactic_name[FOOTBALL_TACTIC_TEXT_MAX];
    rt_uint8_t formation_home;
    rt_uint8_t formation_away;
    rt_uint8_t phase;
    rt_uint8_t reserved0;
} FootballSharedTactic;

typedef struct FootballPossession
{
    rt_uint16_t home_permille;
    rt_uint16_t away_permille;
} FootballPossession;

typedef struct FootballUiStatus
{
    rt_uint8_t active_page;
    rt_uint8_t refresh_required;
    rt_uint8_t audio_busy;
    rt_uint8_t link_status;
    rt_uint32_t last_ui_tick;
} FootballUiStatus;

typedef struct FootballSharedData
{
    rt_uint32_t magic;
    rt_uint16_t version;
    rt_uint16_t struct_size;
    volatile rt_uint32_t m33_write_seq;
    volatile rt_uint32_t m55_write_seq;

    FootballSharedEvent current_event;
    FootballSharedTactic current_tactic;
    rt_uint32_t match_time_ms;
    rt_uint8_t danger_level;
    rt_uint8_t match_period;
    rt_uint16_t reserved_flags;
    FootballPossession possession;

    FootballSharedEvent recent_events[FOOTBALL_RECENT_EVENT_MAX];
    rt_uint8_t recent_write_index;
    rt_uint8_t recent_count;
    rt_uint16_t recent_reserved;

    FootballUiStatus ui_status;

    rt_uint32_t feature_flags;
    rt_uint32_t checksum;
    rt_uint8_t extension_bytes[FOOTBALL_EXT_BYTES];
} FootballSharedData;

void football_protocol_init_message(football_message_t *message);
rt_err_t football_protocol_parse_json(const char *utf8_json, football_message_t *message);
rt_err_t football_protocol_format_json(const football_message_t *message, char *out, rt_size_t out_size);
rt_bool_t football_protocol_is_event(const football_message_t *message, const char *event_name);
void football_shared_data_init(volatile FootballSharedData *shared);
rt_err_t football_message_to_shared_event(const football_message_t *message,
                                          rt_uint16_t event_id,
                                          FootballSharedEvent *shared_event);
rt_err_t football_shared_event_to_message(const FootballSharedEvent *shared_event,
                                          football_message_t *message);
rt_err_t football_shared_data_write_event(volatile FootballSharedData *shared,
                                          const football_message_t *message,
                                          rt_uint16_t event_id);
rt_bool_t football_shared_data_try_read(volatile FootballSharedData *shared,
                                        FootballSharedData *snapshot);

#ifdef __cplusplus
}
#endif

#endif
