#ifndef FOOTBALL_EVENT_H
#define FOOTBALL_EVENT_H

#include "football_protocol.h"

#ifdef __cplusplus
extern "C" {
#endif

#define FOOTBALL_EVENT_PAYLOAD_MAX                 384u
#define FOOTBALL_EVENT_SUBSCRIBER_MAX              16u
#define FOOTBALL_EVENT_QUEUE_DEPTH                 16u

#define FOOTBALL_EVENT_ANY                         0xffffu

#define EVENT_NONE                                 0x0000u
#define EVENT_NEW_MATCH                            0x0100u
#define EVENT_NEW_FRAME                            0x0101u
#define EVENT_COUNTER_ATTACK                       0x0102u
#define EVENT_SET_PIECE                            0x0103u
#define EVENT_GOAL                                 0x0104u
#define EVENT_PRESSING                             0x0105u
#define EVENT_DEFENSIVE_RECOVER                    0x0106u
#define EVENT_BUILD_UP                              0x0107u
#define EVENT_WIDE_ATTACK                           0x0108u
#define EVENT_CENTRAL_PENETRATION                   0x0109u
#define EVENT_HIGH_PRESS                            0x010au
#define EVENT_SHOT                                  0x010bu
#define EVENT_DEFENSIVE_BLOCK                       0x010cu
#define EVENT_TRANSITION_DEFENSE                    0x010du
#define EVENT_FOUL_COMMITTED                        0x010eu
#define EVENT_FREE_KICK_RESTART                     0x010fu
#define EVENT_BALL_OUT_TOUCHLINE                    0x0110u
#define EVENT_THROW_IN_RESTART                      0x0111u
#define EVENT_ATTACKING_PHASE                       0x0112u
#define EVENT_PASS_INTO_PENALTY_AREA                0x0113u
#define EVENT_SHOT_ON_TARGET                        0x0114u
#define EVENT_GOALKEEPER_SAVE                       0x0115u
#define EVENT_UI_REFRESH                           0x0200u
#define EVENT_SAVE_SD                              0x0300u
#define EVENT_PLAY_AUDIO                           0x0400u
#define EVENT_SYSTEM_STATUS                        0x0500u
#define EVENT_EXTENSION_BASE                       0x8000u

#define FOOTBALL_EVENT_SOURCE_UNKNOWN              0u
#define FOOTBALL_EVENT_SOURCE_COMM                 1u
#define FOOTBALL_EVENT_SOURCE_STORAGE              2u
#define FOOTBALL_EVENT_SOURCE_UI                   3u
#define FOOTBALL_EVENT_SOURCE_SYSTEM               4u

#define FOOTBALL_EVENT_TARGET_ALL                  0xffffu

#define FOOTBALL_EVENT_PAYLOAD_NONE                0u
#define FOOTBALL_EVENT_PAYLOAD_FOOTBALL_MESSAGE    1u

typedef struct FootballEvent
{
    rt_uint16_t protocol_version;
    rt_uint16_t event_id;
    rt_uint32_t message_id;
    rt_uint32_t timestamp_ms;
    rt_uint16_t source;
    rt_uint16_t target;
    rt_uint16_t payload_type;
    rt_uint16_t payload_size;
    rt_uint32_t flags;
    rt_uint32_t checksum;
    rt_uint8_t payload[FOOTBALL_EVENT_PAYLOAD_MAX];
} FootballEvent;

typedef void (*football_event_handler_t)(const FootballEvent *event, void *user);

typedef struct
{
    rt_uint32_t total_messages;
    rt_uint32_t counter_attack_messages;
    rt_uint32_t high_danger_messages;
    rt_uint32_t home_messages;
    rt_uint32_t away_messages;
    rt_uint32_t last_update_tick;
    football_message_t last_message;
} football_event_state_t;

rt_err_t football_event_bus_init(void);
rt_err_t football_event_publish(const FootballEvent *event);
rt_err_t football_event_subscribe(rt_uint16_t event_id,
                                  football_event_handler_t handler,
                                  void *user);
rt_err_t football_event_unsubscribe(rt_uint16_t event_id,
                                    football_event_handler_t handler,
                                    void *user);
rt_err_t football_event_build_from_message(const football_message_t *message,
                                           rt_uint16_t source,
                                           FootballEvent *event);
rt_uint16_t football_event_id_from_message(const football_message_t *message);

void football_event_apply(const football_message_t *message);
void football_event_apply_sync(const football_message_t *message);
void football_event_get_state(football_event_state_t *state);
void football_event_reset(void);
void football_event_status(void);

#ifdef __cplusplus
}
#endif

#endif
