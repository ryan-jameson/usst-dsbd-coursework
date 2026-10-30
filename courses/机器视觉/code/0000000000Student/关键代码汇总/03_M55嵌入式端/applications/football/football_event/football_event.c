#include "football_event.h"

#include <finsh.h>
#include <string.h>

#define FOOTBALL_EVENT_WORKER_STACK 4096
#define FOOTBALL_EVENT_WORKER_PRIO 17
#define FOOTBALL_EVENT_WORKER_TICK 20

typedef struct
{
    rt_bool_t used;
    rt_uint16_t event_id;
    football_event_handler_t handler;
    void *user;
} football_event_subscriber_t;

static rt_mq_t g_event_mq = RT_NULL;
static rt_thread_t g_event_worker = RT_NULL;
static struct rt_mutex g_event_lock;
static rt_bool_t g_event_ready = RT_FALSE;
static football_event_subscriber_t g_event_subscribers[FOOTBALL_EVENT_SUBSCRIBER_MAX];
static football_event_state_t g_event_state;
static volatile rt_uint32_t g_publish_ok;
static volatile rt_uint32_t g_publish_fail;
static volatile rt_uint32_t g_dispatched;
static volatile rt_uint32_t g_handler_calls;
static volatile rt_uint32_t g_subscribe_fail;

static int football_lower(int ch)
{
    if (ch >= 'A' && ch <= 'Z')
    {
        return ch + ('a' - 'A');
    }
    return ch;
}

static rt_bool_t football_streq_ci(const char *a, const char *b)
{
    if (a == RT_NULL || b == RT_NULL)
    {
        return RT_FALSE;
    }

    while (*a != '\0' && *b != '\0')
    {
        if (football_lower((unsigned char)*a) != football_lower((unsigned char)*b))
        {
            return RT_FALSE;
        }
        a++;
        b++;
    }

    return (*a == '\0' && *b == '\0') ? RT_TRUE : RT_FALSE;
}

static void football_event_lock_init_once(void)
{
    if (g_event_ready == RT_TRUE)
    {
        return;
    }

    rt_mutex_init(&g_event_lock, "fb_evt", RT_IPC_FLAG_PRIO);
    rt_memset(g_event_subscribers, 0, sizeof(g_event_subscribers));
    rt_memset(&g_event_state, 0, sizeof(g_event_state));
    g_event_ready = RT_TRUE;
}

rt_uint16_t football_event_id_from_message(const football_message_t *message)
{
    if (message == RT_NULL)
    {
        return EVENT_NONE;
    }

    if (football_streq_ci(message->event, "new_match") == RT_TRUE)
    {
        return EVENT_NEW_MATCH;
    }
    if (football_streq_ci(message->event, "counter_attack") == RT_TRUE)
    {
        return EVENT_COUNTER_ATTACK;
    }
    if (football_streq_ci(message->event, "set_piece") == RT_TRUE)
    {
        return EVENT_SET_PIECE;
    }
    if (football_streq_ci(message->event, "goal") == RT_TRUE)
    {
        return EVENT_GOAL;
    }
    if (football_streq_ci(message->event, "pressing") == RT_TRUE)
    {
        return EVENT_PRESSING;
    }
    if (football_streq_ci(message->event, "defensive_recover") == RT_TRUE)
    {
        return EVENT_DEFENSIVE_RECOVER;
    }
    if (football_streq_ci(message->event, "build_up") == RT_TRUE)
    {
        return EVENT_BUILD_UP;
    }
    if (football_streq_ci(message->event, "wide_attack") == RT_TRUE)
    {
        return EVENT_WIDE_ATTACK;
    }
    if (football_streq_ci(message->event, "central_penetration") == RT_TRUE)
    {
        return EVENT_CENTRAL_PENETRATION;
    }
    if (football_streq_ci(message->event, "high_press") == RT_TRUE)
    {
        return EVENT_HIGH_PRESS;
    }
    if (football_streq_ci(message->event, "shot") == RT_TRUE)
    {
        return EVENT_SHOT;
    }
    if (football_streq_ci(message->event, "defensive_block") == RT_TRUE)
    {
        return EVENT_DEFENSIVE_BLOCK;
    }
    if (football_streq_ci(message->event, "transition_defense") == RT_TRUE)
    {
        return EVENT_TRANSITION_DEFENSE;
    }
    if (football_streq_ci(message->event, "foul_committed") == RT_TRUE)
    {
        return EVENT_FOUL_COMMITTED;
    }
    if (football_streq_ci(message->event, "free_kick_restart") == RT_TRUE)
    {
        return EVENT_FREE_KICK_RESTART;
    }
    if (football_streq_ci(message->event, "ball_out_touchline") == RT_TRUE)
    {
        return EVENT_BALL_OUT_TOUCHLINE;
    }
    if (football_streq_ci(message->event, "throw_in_restart") == RT_TRUE)
    {
        return EVENT_THROW_IN_RESTART;
    }
    if (football_streq_ci(message->event, "attacking_phase") == RT_TRUE)
    {
        return EVENT_ATTACKING_PHASE;
    }
    if (football_streq_ci(message->event, "pass_into_penalty_area") == RT_TRUE)
    {
        return EVENT_PASS_INTO_PENALTY_AREA;
    }
    if (football_streq_ci(message->event, "shot_on_target") == RT_TRUE)
    {
        return EVENT_SHOT_ON_TARGET;
    }
    if (football_streq_ci(message->event, "goalkeeper_save") == RT_TRUE)
    {
        return EVENT_GOALKEEPER_SAVE;
    }
    if (football_streq_ci(message->event, "ui_refresh") == RT_TRUE)
    {
        return EVENT_UI_REFRESH;
    }
    if (football_streq_ci(message->event, "save_sd") == RT_TRUE)
    {
        return EVENT_SAVE_SD;
    }
    if (football_streq_ci(message->event, "play_audio") == RT_TRUE)
    {
        return EVENT_PLAY_AUDIO;
    }

    return EVENT_NEW_FRAME;
}

rt_err_t football_event_build_from_message(const football_message_t *message,
                                           rt_uint16_t source,
                                           FootballEvent *event)
{
    if (message == RT_NULL || event == RT_NULL)
    {
        return -RT_EINVAL;
    }
    if (sizeof(*message) > FOOTBALL_EVENT_PAYLOAD_MAX)
    {
        return -RT_EFULL;
    }

    rt_memset(event, 0, sizeof(*event));
    event->protocol_version = message->protocol_version;
    event->event_id = football_event_id_from_message(message);
    event->message_id = message->message_id;
    event->timestamp_ms = message->timestamp;
    event->source = source;
    event->target = FOOTBALL_EVENT_TARGET_ALL;
    event->payload_type = FOOTBALL_EVENT_PAYLOAD_FOOTBALL_MESSAGE;
    event->payload_size = sizeof(*message);
    rt_memcpy(event->payload, message, sizeof(*message));

    return RT_EOK;
}

static rt_bool_t football_event_match_subscriber(rt_uint16_t subscribed_id, rt_uint16_t event_id)
{
    return (subscribed_id == FOOTBALL_EVENT_ANY || subscribed_id == event_id) ? RT_TRUE : RT_FALSE;
}

static void football_event_reduce_state(const FootballEvent *event)
{
    football_message_t message;

    if (event->payload_type != FOOTBALL_EVENT_PAYLOAD_FOOTBALL_MESSAGE ||
        event->payload_size != sizeof(message))
    {
        return;
    }

    rt_memcpy(&message, event->payload, sizeof(message));

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    g_event_state.total_messages++;
    if (football_protocol_is_event(&message, "counter_attack") == RT_TRUE)
    {
        g_event_state.counter_attack_messages++;
    }
    if (message.danger >= 4)
    {
        g_event_state.high_danger_messages++;
    }
    if (football_streq_ci(message.team, "home") == RT_TRUE)
    {
        g_event_state.home_messages++;
    }
    if (football_streq_ci(message.team, "away") == RT_TRUE)
    {
        g_event_state.away_messages++;
    }
    g_event_state.last_update_tick = rt_tick_get();
    g_event_state.last_message = message;
    rt_mutex_release(&g_event_lock);
}

static void football_event_dispatch(const FootballEvent *event)
{
    football_event_subscriber_t subscribers[FOOTBALL_EVENT_SUBSCRIBER_MAX];
    rt_uint32_t count = 0;
    rt_uint32_t i;

    football_event_lock_init_once();
    football_event_reduce_state(event);

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    for (i = 0; i < FOOTBALL_EVENT_SUBSCRIBER_MAX; i++)
    {
        if (g_event_subscribers[i].used == RT_TRUE &&
            football_event_match_subscriber(g_event_subscribers[i].event_id, event->event_id) == RT_TRUE)
        {
            subscribers[count++] = g_event_subscribers[i];
        }
    }
    rt_mutex_release(&g_event_lock);

    for (i = 0; i < count; i++)
    {
        subscribers[i].handler(event, subscribers[i].user);
        g_handler_calls++;
    }
}

static void football_event_worker_entry(void *parameter)
{
    FootballEvent event;

    RT_UNUSED(parameter);

    while (1)
    {
        if (rt_mq_recv(g_event_mq, &event, sizeof(event), RT_WAITING_FOREVER) != RT_EOK)
        {
            continue;
        }

        g_dispatched++;
        football_event_dispatch(&event);
    }
}

rt_err_t football_event_bus_init(void)
{
    football_event_lock_init_once();

    if (g_event_mq == RT_NULL)
    {
        g_event_mq = rt_mq_create("fb_bus",
                                  sizeof(FootballEvent),
                                  FOOTBALL_EVENT_QUEUE_DEPTH,
                                  RT_IPC_FLAG_PRIO);
        if (g_event_mq == RT_NULL)
        {
            return -RT_ENOMEM;
        }
    }

    if (g_event_worker == RT_NULL)
    {
        g_event_worker = rt_thread_create("fb_evtb",
                                          football_event_worker_entry,
                                          RT_NULL,
                                          FOOTBALL_EVENT_WORKER_STACK,
                                          FOOTBALL_EVENT_WORKER_PRIO,
                                          FOOTBALL_EVENT_WORKER_TICK);
        if (g_event_worker == RT_NULL)
        {
            return -RT_ENOMEM;
        }
        rt_thread_startup(g_event_worker);
    }

    return RT_EOK;
}

rt_err_t football_event_publish(const FootballEvent *event)
{
    rt_err_t ret;

    if (event == RT_NULL || event->payload_size > FOOTBALL_EVENT_PAYLOAD_MAX)
    {
        g_publish_fail++;
        return -RT_EINVAL;
    }

    ret = football_event_bus_init();
    if (ret != RT_EOK)
    {
        g_publish_fail++;
        return ret;
    }

    ret = rt_mq_send(g_event_mq, event, sizeof(*event));
    if (ret == RT_EOK)
    {
        g_publish_ok++;
    }
    else
    {
        g_publish_fail++;
    }

    return ret;
}

rt_err_t football_event_subscribe(rt_uint16_t event_id,
                                  football_event_handler_t handler,
                                  void *user)
{
    rt_uint32_t i;
    rt_int32_t free_index = -1;

    if (handler == RT_NULL)
    {
        g_subscribe_fail++;
        return -RT_EINVAL;
    }

    if (football_event_bus_init() != RT_EOK)
    {
        g_subscribe_fail++;
        return -RT_ERROR;
    }

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    for (i = 0; i < FOOTBALL_EVENT_SUBSCRIBER_MAX; i++)
    {
        if (g_event_subscribers[i].used == RT_TRUE)
        {
            if (g_event_subscribers[i].event_id == event_id &&
                g_event_subscribers[i].handler == handler &&
                g_event_subscribers[i].user == user)
            {
                rt_mutex_release(&g_event_lock);
                return RT_EOK;
            }
            continue;
        }
        if (free_index < 0)
        {
            free_index = (rt_int32_t)i;
        }
    }

    if (free_index < 0)
    {
        rt_mutex_release(&g_event_lock);
        g_subscribe_fail++;
        return -RT_EFULL;
    }

    g_event_subscribers[free_index].used = RT_TRUE;
    g_event_subscribers[free_index].event_id = event_id;
    g_event_subscribers[free_index].handler = handler;
    g_event_subscribers[free_index].user = user;
    rt_mutex_release(&g_event_lock);

    return RT_EOK;
}

rt_err_t football_event_unsubscribe(rt_uint16_t event_id,
                                    football_event_handler_t handler,
                                    void *user)
{
    rt_uint32_t i;

    if (handler == RT_NULL)
    {
        return -RT_EINVAL;
    }

    football_event_lock_init_once();

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    for (i = 0; i < FOOTBALL_EVENT_SUBSCRIBER_MAX; i++)
    {
        if (g_event_subscribers[i].used == RT_TRUE &&
            g_event_subscribers[i].event_id == event_id &&
            g_event_subscribers[i].handler == handler &&
            g_event_subscribers[i].user == user)
        {
            rt_memset(&g_event_subscribers[i], 0, sizeof(g_event_subscribers[i]));
            rt_mutex_release(&g_event_lock);
            return RT_EOK;
        }
    }
    rt_mutex_release(&g_event_lock);

    return -RT_ERROR;
}

void football_event_apply(const football_message_t *message)
{
    FootballEvent event;

    if (football_event_build_from_message(message, FOOTBALL_EVENT_SOURCE_COMM, &event) != RT_EOK)
    {
        return;
    }

    (void)football_event_publish(&event);
}

void football_event_apply_sync(const football_message_t *message)
{
    FootballEvent event;

    if (football_event_build_from_message(message, FOOTBALL_EVENT_SOURCE_COMM, &event) != RT_EOK)
    {
        return;
    }

    football_event_dispatch(&event);
}

void football_event_get_state(football_event_state_t *state)
{
    if (state == RT_NULL)
    {
        return;
    }

    football_event_lock_init_once();

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    *state = g_event_state;
    rt_mutex_release(&g_event_lock);
}

void football_event_reset(void)
{
    football_event_lock_init_once();

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    rt_memset(&g_event_state, 0, sizeof(g_event_state));
    rt_mutex_release(&g_event_lock);
}

void football_event_status(void)
{
    football_event_state_t state;
    rt_uint32_t subscriber_count = 0;
    rt_uint32_t i;

    football_event_get_state(&state);

    rt_mutex_take(&g_event_lock, RT_WAITING_FOREVER);
    for (i = 0; i < FOOTBALL_EVENT_SUBSCRIBER_MAX; i++)
    {
        if (g_event_subscribers[i].used == RT_TRUE)
        {
            subscriber_count++;
        }
    }
    rt_mutex_release(&g_event_lock);

    rt_kprintf("event_bus started=%d subscribers=%u publish_ok=%u publish_fail=%u dispatched=%u handler_calls=%u subscribe_fail=%u\r\n",
               g_event_mq != RT_NULL,
               (unsigned int)subscriber_count,
               (unsigned int)g_publish_ok,
               (unsigned int)g_publish_fail,
               (unsigned int)g_dispatched,
               (unsigned int)g_handler_calls,
               (unsigned int)g_subscribe_fail);
    rt_kprintf("event_state total=%u counter_attack=%u high_danger=%u home=%u away=%u last_id=%u\r\n",
               (unsigned int)state.total_messages,
               (unsigned int)state.counter_attack_messages,
               (unsigned int)state.high_danger_messages,
               (unsigned int)state.home_messages,
               (unsigned int)state.away_messages,
               (unsigned int)state.last_message.message_id);
}

static int football_event(int argc, char **argv)
{
    if (argc >= 2 && rt_strcmp(argv[1], "reset") == 0)
    {
        football_event_reset();
        return 0;
    }

    football_event_status();
    return 0;
}
MSH_CMD_EXPORT(football_event, AI football event bus status);

static int football_event_auto_init(void)
{
    return football_event_bus_init();
}
INIT_APP_EXPORT(football_event_auto_init);
