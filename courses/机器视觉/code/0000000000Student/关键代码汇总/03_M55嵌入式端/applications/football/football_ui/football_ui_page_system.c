#include "football_ui_page_system.h"
#include "football_ui_components.h"

#ifdef BSP_USING_LVGL

static lv_obj_t *g_link_label;
static lv_obj_t *g_shared_label;
static lv_obj_t *g_status_label;
static lv_obj_t *g_message_label;

void football_ui_system_toggle(lv_event_t *event)
{
    lv_obj_t *panel = (lv_obj_t *)lv_event_get_user_data(event);
    if (panel == RT_NULL) return;
    if (lv_obj_has_flag(panel, LV_OBJ_FLAG_HIDDEN)) lv_obj_remove_flag(panel, LV_OBJ_FLAG_HIDDEN);
    else lv_obj_add_flag(panel, LV_OBJ_FLAG_HIDDEN);
}

void football_ui_page_system_create(lv_obj_t *parent)
{
    football_ui_components_prepare_page(parent);
    g_link_label = football_ui_components_label(parent, "System Status", 10, 0xf7fbff);
    g_shared_label = football_ui_components_label(parent, "Shared Seq: 0", 58, 0x7ef29a);
    g_status_label = football_ui_components_label(parent, "SD: idle  Audio: idle", 106, 0xffffff);
    g_message_label = football_ui_components_label(parent, "Last Message: 0", 154, 0xb7d3c4);
}

void football_ui_page_system_update(const football_ui_snapshot_t *snapshot)
{
    if (snapshot == RT_NULL || g_link_label == RT_NULL)
    {
        return;
    }

    lv_label_set_text_fmt(g_link_label,
                          "System: USB/IPC=%s page=%u",
                          snapshot->link_status == 0u ? "waiting" : "active",
                          (unsigned int)snapshot->active_page);
    lv_label_set_text_fmt(g_shared_label,
                          "Shared Seq: %u  Tick: %u",
                          (unsigned int)snapshot->shared_seq,
                          (unsigned int)snapshot->last_update_tick);
    lv_label_set_text_fmt(g_status_label,
                          "M33 SD: %s  Audio: %s  WiFi: %s Cloud:%u",
                          snapshot->sd_status == 0u ? "idle" : "active",
                          snapshot->audio_status == 0u ? "idle" : "busy",
                          snapshot->wifi_status == 0u ? "offline" : "ready",
                          snapshot->cloud_status);
    lv_label_set_text_fmt(g_message_label,
                          "Last Message: %u  Event: %s",
                          (unsigned int)snapshot->last_message.message_id,
                          snapshot->last_message.event[0] == '\0' ? "-" : snapshot->last_message.event);
}

#endif
