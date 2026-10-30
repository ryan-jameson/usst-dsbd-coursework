#include "football_ui.h"
#include "football_event.h"
#include "football_ui_page_tactics.h"
#include "football_ui_page_match.h"
#include "football_ui_page_events.h"
#include "football_ui_page_stats.h"
#include "football_ui_page_ai.h"
#include "football_ui_page_system.h"
#include "../football_cloud/football_cloud.h"
#include "../football_voice/football_voice.h"

#include <finsh.h>
#include <string.h>

#ifdef BSP_USING_LVGL
#include <lvgl.h>
#include <lv_rt_thread_conf.h>

#define FOOTBALL_UI_TIMER_MS 200

static rt_bool_t g_ui_started = RT_FALSE;
static rt_bool_t g_ui_ready = RT_FALSE;
static rt_bool_t g_ui_model_ready = RT_FALSE;
static struct rt_mutex g_ui_model_lock;
static football_ui_snapshot_t g_ui_snapshot;
static lv_obj_t *g_system_panel;

static int football_ui_lower(int ch)
{
    if (ch >= 'A' && ch <= 'Z')
    {
        return ch + ('a' - 'A');
    }
    return ch;
}

static rt_bool_t football_ui_streq_ci(const char *a, const char *b)
{
    if (a == RT_NULL || b == RT_NULL)
    {
        return RT_FALSE;
    }

    while (*a != '\0' && *b != '\0')
    {
        if (football_ui_lower((unsigned char)*a) != football_ui_lower((unsigned char)*b))
        {
            return RT_FALSE;
        }
        a++;
        b++;
    }

    return (*a == '\0' && *b == '\0') ? RT_TRUE : RT_FALSE;
}

static void football_ui_copy(char *dst, rt_size_t dst_size, const char *src)
{
    rt_size_t i = 0;

    if (dst_size == 0)
    {
        return;
    }
    if (src == RT_NULL)
    {
        src = "";
    }

    while (i + 1 < dst_size && src[i] != '\0')
    {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
}

static void football_ui_tactic_from_event(const char *event_name, char *out, rt_size_t out_size)
{
    if (football_ui_streq_ci(event_name, "counter_attack") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Counter Attack");
        return;
    }
    if (football_ui_streq_ci(event_name, "set_piece") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Set Piece");
        return;
    }
    if (football_ui_streq_ci(event_name, "goal") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Goal");
        return;
    }
    if (football_ui_streq_ci(event_name, "pressing") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Pressing");
        return;
    }
    if (football_ui_streq_ci(event_name, "set_piece") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Set Piece");
        return;
    }
    if (football_ui_streq_ci(event_name, "defensive_recover") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "Def. Recover");
        return;
    }
    if (football_ui_streq_ci(event_name, "new_match") == RT_TRUE)
    {
        football_ui_copy(out, out_size, "New Match");
        return;
    }

    football_ui_copy(out, out_size, event_name == RT_NULL || event_name[0] == '\0' ? "Open Play" : event_name);
}

static void football_ui_model_init_once(void)
{
    if (g_ui_model_ready == RT_TRUE)
    {
        return;
    }

    rt_mutex_init(&g_ui_model_lock, "fb_ui", RT_IPC_FLAG_PRIO);
    rt_memset(&g_ui_snapshot, 0, sizeof(g_ui_snapshot));
    football_ui_copy(g_ui_snapshot.current_tactic, sizeof(g_ui_snapshot.current_tactic), "Waiting");
    g_ui_model_ready = RT_TRUE;
}

static void football_ui_apply_message(const FootballEvent *event, const football_message_t *message)
{
    FootballSharedEvent shared_event;
    rt_uint8_t index;

    if (football_message_to_shared_event(message, event->event_id, &shared_event) != RT_EOK)
    {
        return;
    }

    football_ui_model_init_once();
    rt_mutex_take(&g_ui_model_lock, RT_WAITING_FOREVER);

    g_ui_snapshot.total_messages++;
    if (football_ui_streq_ci(message->event, "counter_attack") == RT_TRUE)
    {
        g_ui_snapshot.counter_attack_messages++;
    }
    if (football_ui_streq_ci(message->event, "set_piece") == RT_TRUE)
    {
        g_ui_snapshot.set_piece_messages++;
    }
    if (football_ui_streq_ci(message->event, "goal") == RT_TRUE)
    {
        g_ui_snapshot.goal_messages++;
        if (football_ui_streq_ci(message->team, "home") == RT_TRUE)
            g_ui_snapshot.home_score++;
        else if (football_ui_streq_ci(message->team, "away") == RT_TRUE)
            g_ui_snapshot.away_score++;
    }
    if (message->danger >= 4)
    {
        g_ui_snapshot.high_danger_messages++;
    }
    if (football_ui_streq_ci(message->team, "home") == RT_TRUE)
    {
        g_ui_snapshot.home_messages++;
    }
    if (football_ui_streq_ci(message->team, "away") == RT_TRUE)
    {
        g_ui_snapshot.away_messages++;
    }

    g_ui_snapshot.last_message = *message;
    football_ui_tactic_from_event(message->event,
                                  g_ui_snapshot.current_tactic,
                                  sizeof(g_ui_snapshot.current_tactic));

    index = g_ui_snapshot.recent_write_index % FOOTBALL_RECENT_EVENT_MAX;
    g_ui_snapshot.recent_events[index] = shared_event;
    g_ui_snapshot.recent_write_index = (rt_uint8_t)((index + 1u) % FOOTBALL_RECENT_EVENT_MAX);
    if (g_ui_snapshot.recent_count < FOOTBALL_RECENT_EVENT_MAX)
    {
        g_ui_snapshot.recent_count++;
    }

    g_ui_snapshot.shared_seq = event->message_id;
    g_ui_snapshot.link_status = 1u;
    g_ui_snapshot.last_update_tick = rt_tick_get();
    g_ui_snapshot.danger_level = (rt_uint8_t)((message->danger < 0) ? 0 :
                                  (message->danger > 5 ? 5 : message->danger));
    g_ui_snapshot.match_minute = (rt_uint16_t)(message->timestamp / 60000u);
    g_ui_snapshot.match_second = (rt_uint16_t)((message->timestamp / 1000u) % 60u);

    rt_mutex_release(&g_ui_model_lock);
}

void football_ui_set_tactic(const char *formation, rt_bool_t dirty)
{
    RT_UNUSED(dirty);
    football_ui_model_init_once();
    rt_mutex_take(&g_ui_model_lock, RT_WAITING_FOREVER);
    football_ui_copy(g_ui_snapshot.current_tactic,
                     sizeof(g_ui_snapshot.current_tactic), formation);
    rt_mutex_release(&g_ui_model_lock);
}

static void football_ui_event_handler(const FootballEvent *event, void *user)
{
    football_message_t message;

    RT_UNUSED(user);

    if (event == RT_NULL ||
        event->payload_type != FOOTBALL_EVENT_PAYLOAD_FOOTBALL_MESSAGE ||
        event->payload_size != sizeof(message))
    {
        return;
    }

    rt_memcpy(&message, event->payload, sizeof(message));
    football_ui_apply_message(event, &message);
}

void football_ui_get_snapshot(football_ui_snapshot_t *snapshot)
{
    if (snapshot == RT_NULL)
    {
        return;
    }

    football_ui_model_init_once();
    rt_mutex_take(&g_ui_model_lock, RT_WAITING_FOREVER);
    *snapshot = g_ui_snapshot;
    rt_mutex_release(&g_ui_model_lock);
}

static void football_ui_init_page(void)
{
    lv_obj_t *screen;
    lv_obj_t *tabview;
    lv_obj_t *tab_tactics;
    lv_obj_t *tab_match;
    lv_obj_t *tab_events;
    lv_obj_t *tab_stats;
    lv_obj_t *tab_ai;
    lv_obj_t *status_button;

    if (g_ui_ready == RT_TRUE)
    {
        return;
    }

    screen = lv_screen_active();
    lv_obj_clean(screen);
    lv_obj_set_style_bg_color(screen, lv_color_hex(0x071b14), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);

    status_button = lv_button_create(screen);
    lv_obj_set_size(status_button, 70, 30);
    lv_obj_align(status_button, LV_ALIGN_TOP_RIGHT, -4, 2);
    lv_obj_t *status_label = lv_label_create(status_button);
    lv_label_set_text(status_label, "SYS");
    lv_obj_center(status_label);

    tabview = lv_tabview_create(screen);
    lv_obj_set_size(tabview, lv_pct(100), 766);
    lv_obj_align(tabview, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_tabview_set_tab_bar_position(tabview, LV_DIR_TOP);
    lv_tabview_set_tab_bar_size(tabview, 42);
    lv_obj_remove_flag(lv_tabview_get_content(tabview), LV_OBJ_FLAG_SCROLLABLE);

    tab_tactics = lv_tabview_add_tab(tabview, "Tactics");
    tab_match = lv_tabview_add_tab(tabview, "Match");
    tab_events = lv_tabview_add_tab(tabview, "Events");
    tab_stats = lv_tabview_add_tab(tabview, "Stats");
    tab_ai = lv_tabview_add_tab(tabview, "AI");

    football_ui_page_tactics_create(tab_tactics);
    football_ui_page_match_create(tab_match);
    football_ui_page_events_create(tab_events);
    football_ui_page_stats_create(tab_stats);
    football_ui_page_ai_create(tab_ai);
    g_system_panel = lv_obj_create(screen);
    lv_obj_set_size(g_system_panel, 460, 620);
    lv_obj_align(g_system_panel, LV_ALIGN_CENTER, 0, 20);
    football_ui_page_system_create(g_system_panel);
    lv_obj_add_flag(g_system_panel, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_event_cb(status_button, football_ui_system_toggle, LV_EVENT_CLICKED, g_system_panel);

    g_ui_ready = RT_TRUE;
}

void football_ui_refresh(void)
{
    football_ui_snapshot_t snapshot;
    football_cloud_status_t cloud;
    football_voice_status_t voice;

    if (g_ui_ready == RT_FALSE)
    {
        return;
    }

    football_ui_get_snapshot(&snapshot);
    football_cloud_get_status(&cloud);
    football_voice_get_status(&voice);
    snapshot.wifi_status = cloud.wifi_ready;
    snapshot.cloud_status = (rt_uint8_t)cloud.state;
    snapshot.voice_status = (rt_uint8_t)voice.state;
    snapshot.audio_status = (voice.state == FOOTBALL_VOICE_LOCAL_PLAYING ||
                             voice.state == FOOTBALL_VOICE_CLOUD_SPEAKING) ? 1u : 0u;
    football_ui_page_tactics_update(&snapshot);
    football_ui_page_match_update(&snapshot);
    football_ui_page_events_update(&snapshot);
    football_ui_page_stats_update(&snapshot);
    football_ui_page_ai_update(&snapshot);
    football_ui_page_system_update(&snapshot);
}

static void football_ui_timer(lv_timer_t *timer)
{
    RT_UNUSED(timer);
    football_ui_refresh();
}

void lv_user_gui_init(void)
{
    football_ui_init_page();
    lv_timer_create(football_ui_timer, FOOTBALL_UI_TIMER_MS, RT_NULL);
}

rt_err_t football_ui_start(void)
{
    rt_err_t ret;

    football_ui_model_init_once();
    if (g_ui_started == RT_TRUE)
    {
        return RT_EOK;
    }
    ret = football_event_subscribe(FOOTBALL_EVENT_ANY, football_ui_event_handler, RT_NULL);
    if (ret != RT_EOK)
    {
        return ret;
    }

    g_ui_started = RT_TRUE;
    return lvgl_thread_init();
}

static int football_lvgl_start(void)
{
    return football_ui_start();
}
MSH_CMD_EXPORT(football_lvgl_start, start AI football LVGL UI);

static int football_ui_auto_init(void)
{
    return football_ui_start();
}
INIT_APP_EXPORT(football_ui_auto_init);

#else

rt_err_t football_ui_start(void)
{
    return -RT_ENOSYS;
}

void football_ui_refresh(void)
{
}

void football_ui_get_snapshot(football_ui_snapshot_t *snapshot)
{
    if (snapshot != RT_NULL)
    {
        rt_memset(snapshot, 0, sizeof(*snapshot));
    }
}

#endif

static int football_ui(int argc, char **argv)
{
    RT_UNUSED(argc);
    RT_UNUSED(argv);

    rt_kprintf("football_ui start=%d\r\n", football_ui_start());
    return 0;
}
MSH_CMD_EXPORT(football_ui, AI football UI status/start);
