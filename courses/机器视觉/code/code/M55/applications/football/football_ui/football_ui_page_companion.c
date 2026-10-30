#include "football_ui_page_companion.h"
#include "football_ui_components.h"

#ifdef BSP_USING_LVGL

static lv_obj_t *g_title_label;
static lv_obj_t *g_tactic_label;
static lv_obj_t *g_danger_label;
static lv_obj_t *g_time_label;

void football_ui_page_companion_create(lv_obj_t *parent)
{
    football_ui_components_prepare_page(parent);
    g_title_label = football_ui_components_label(parent, "Football Companion", 10, 0xf7fbff);
    g_tactic_label = football_ui_components_label(parent, "Tactic: Waiting", 54, 0x7ef29a);
    g_danger_label = football_ui_components_label(parent, "Danger: 0", 98, 0xffffff);
    g_time_label = football_ui_components_label(parent, "Match Time: 00:00", 142, 0xb7d3c4);
}

void football_ui_page_companion_update(const football_ui_snapshot_t *snapshot)
{
    rt_uint32_t seconds;

    if (snapshot == RT_NULL || g_title_label == RT_NULL)
    {
        return;
    }

    seconds = snapshot->last_message.timestamp / 1000u;
    lv_label_set_text(g_title_label, "Football Companion");
    lv_label_set_text_fmt(g_tactic_label,
                          "Tactic: %s",
                          snapshot->current_tactic[0] == '\0' ? "Waiting" : snapshot->current_tactic);
    lv_label_set_text_fmt(g_danger_label,
                          "Danger: %d  Team: %s",
                          (int)snapshot->last_message.danger,
                          snapshot->last_message.team[0] == '\0' ? "-" : snapshot->last_message.team);
    lv_label_set_text_fmt(g_time_label,
                          "Match Time: %02u:%02u  Ball: (%d,%d)",
                          (unsigned int)(seconds / 60u),
                          (unsigned int)(seconds % 60u),
                          (int)snapshot->last_message.ball_x,
                          (int)snapshot->last_message.ball_y);
}

#endif
