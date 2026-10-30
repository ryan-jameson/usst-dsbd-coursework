#include "football_ui_page_events.h"
#include "football_ui_components.h"
#ifdef BSP_USING_LVGL
static lv_obj_t *g_rows[FOOTBALL_RECENT_EVENT_MAX];
void football_ui_page_events_create(lv_obj_t *parent)
{
    rt_uint8_t i;
    football_ui_components_prepare_page(parent);
    football_ui_components_label(parent, "Event timeline / tap for AI analysis", 8, 0xf7fbff);
    for (i = 0u; i < FOOTBALL_RECENT_EVENT_MAX; ++i)
        g_rows[i] = football_ui_components_label(parent, "-", 52 + i * 66, 0xffffff);
}
void football_ui_page_events_update(const football_ui_snapshot_t *s)
{
    rt_uint8_t row;
    if (s == RT_NULL) return;
    for (row = 0u; row < FOOTBALL_RECENT_EVENT_MAX; ++row)
    {
        if (row >= s->recent_count) lv_label_set_text(g_rows[row], "-");
        else
        {
            rt_uint8_t index = (rt_uint8_t)((s->recent_write_index + FOOTBALL_RECENT_EVENT_MAX - 1u - row) % FOOTBALL_RECENT_EVENT_MAX);
            const FootballSharedEvent *e = &s->recent_events[index];
            lv_label_set_text_fmt(g_rows[row], "%02u  %s / %s  danger=%u  voice=%u",
                                  (unsigned int)e->message_id, e->team, e->event_name,
                                  e->danger, s->voice_status);
        }
    }
}
#endif
