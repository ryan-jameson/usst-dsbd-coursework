#include "football_ui_page_ai.h"
#include "football_ui_components.h"
#include "../football_voice/football_voice.h"
#ifdef BSP_USING_LVGL
static lv_obj_t *g_status;
static lv_obj_t *g_result;
static void ai_worker(void *parameter) { RT_UNUSED(parameter); (void)football_voice_manual_assistant(); }
static void ai_record_cb(lv_event_t *event)
{
    rt_thread_t thread;
    RT_UNUSED(event);
    thread = rt_thread_create("fb_ask", ai_worker, RT_NULL, 6144u, 23u, 20u);
    if (thread != RT_NULL) rt_thread_startup(thread);
}
static void ai_cancel_cb(lv_event_t *event) { RT_UNUSED(event); football_voice_cancel(); }
void football_ui_page_ai_create(lv_obj_t *parent)
{
    lv_obj_t *button;
    lv_obj_t *label;
    football_ui_components_prepare_page(parent);
    g_status = football_ui_components_label(parent, "Voice assistant: idle", 24, 0xf7fbff);
    button = lv_button_create(parent); lv_obj_set_size(button, 190, 64); lv_obj_align(button, LV_ALIGN_TOP_LEFT, 20, 100);
    label = lv_label_create(button); lv_label_set_text(label, "Record / Ask"); lv_obj_center(label);
    lv_obj_add_event_cb(button, ai_record_cb, LV_EVENT_CLICKED, RT_NULL);
    button = lv_button_create(parent); lv_obj_set_size(button, 190, 64); lv_obj_align(button, LV_ALIGN_TOP_RIGHT, -20, 100);
    label = lv_label_create(button); lv_label_set_text(label, "Cancel / Stop"); lv_obj_center(label);
    lv_obj_add_event_cb(button, ai_cancel_cb, LV_EVENT_CLICKED, RT_NULL);
    g_result = football_ui_components_label(parent, "ASR and AI results appear here after service completion.", 210, 0xb7d3c4);
}
void football_ui_page_ai_update(const football_ui_snapshot_t *s)
{
    if (s == RT_NULL || g_status == RT_NULL) return;
    lv_label_set_text_fmt(g_status, "Voice=%u  WiFi=%s  Cloud=%u", s->voice_status,
                          s->wifi_status ? "ready" : "offline", s->cloud_status);
    if (s->ai_text[0] != '\0') lv_label_set_text(g_result, s->ai_text);
}
#endif
