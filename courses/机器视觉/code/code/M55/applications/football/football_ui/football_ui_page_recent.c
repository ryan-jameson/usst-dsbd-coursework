#include "football_ui_page_recent.h"
#include "football_ui_components.h"

#ifdef BSP_USING_LVGL

static lv_obj_t *g_header_label;
static lv_obj_t *g_recent_labels[FOOTBALL_RECENT_EVENT_MAX];

void football_ui_page_recent_create(lv_obj_t *parent)
{
    rt_uint32_t i;

    football_ui_components_prepare_page(parent);
    g_header_label = football_ui_components_label(parent, "Recent Events", 10, 0xf7fbff);

    for (i = 0; i < FOOTBALL_RECENT_EVENT_MAX; i++)
    {
        g_recent_labels[i] = football_ui_components_label(parent, "-", 44 + (int32_t)(i * 28u), 0xffffff);
    }
}

void football_ui_page_recent_update(const football_ui_snapshot_t *snapshot)
{
    rt_uint32_t i;

    if (snapshot == RT_NULL || g_header_label == RT_NULL)
    {
        return;
    }

    lv_label_set_text_fmt(g_header_label, "Recent Events: %u", (unsigned int)snapshot->recent_count);

    for (i = 0; i < FOOTBALL_RECENT_EVENT_MAX; i++)
    {
        rt_uint32_t src;
        const FootballSharedEvent *event;

        if (i >= snapshot->recent_count)
        {
            lv_label_set_text(g_recent_labels[i], "-");
            continue;
        }

        src = (snapshot->recent_write_index + FOOTBALL_RECENT_EVENT_MAX - 1u - i) % FOOTBALL_RECENT_EVENT_MAX;
        event = &snapshot->recent_events[src];
        lv_label_set_text_fmt(g_recent_labels[i],
                              "#%u %s %s D%u T%u",
                              (unsigned int)event->message_id,
                              event->team[0] == '\0' ? "-" : event->team,
                              event->event_name[0] == '\0' ? "-" : event->event_name,
                              (unsigned int)event->danger,
                              (unsigned int)event->timestamp_ms);
    }
}

#endif
