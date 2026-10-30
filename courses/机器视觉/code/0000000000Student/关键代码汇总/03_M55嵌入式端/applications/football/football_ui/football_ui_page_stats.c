#include "football_ui_page_stats.h"
#include "football_ui_components.h"

#ifdef BSP_USING_LVGL

static lv_obj_t *g_total_label;
static lv_obj_t *g_attack_label;
static lv_obj_t *g_goal_label;
static lv_obj_t *g_team_label;

void football_ui_page_stats_create(lv_obj_t *parent)
{
    football_ui_components_prepare_page(parent);
    g_total_label = football_ui_components_label(parent, "Match Stats", 10, 0xf7fbff);
    g_attack_label = football_ui_components_label(parent, "Counter Attack: 0  Set Piece: 0", 58, 0x7ef29a);
    g_goal_label = football_ui_components_label(parent, "Goals: 0  High Danger: 0", 106, 0xffffff);
    g_team_label = football_ui_components_label(parent, "Home: 0  Away: 0", 154, 0xb7d3c4);
}

void football_ui_page_stats_update(const football_ui_snapshot_t *snapshot)
{
    if (snapshot == RT_NULL || g_total_label == RT_NULL)
    {
        return;
    }

    lv_label_set_text_fmt(g_total_label,
                          "Match Stats: total=%u",
                          (unsigned int)snapshot->total_messages);
    lv_label_set_text_fmt(g_attack_label,
                          "Counter Attack: %u  Set Piece: %u",
                          (unsigned int)snapshot->counter_attack_messages,
                          (unsigned int)snapshot->set_piece_messages);
    lv_label_set_text_fmt(g_goal_label,
                          "Goals: %u  High Danger: %u",
                          (unsigned int)snapshot->goal_messages,
                          (unsigned int)snapshot->high_danger_messages);
    lv_label_set_text_fmt(g_team_label,
                          "Home: %u  Away: %u",
                          (unsigned int)snapshot->home_messages,
                          (unsigned int)snapshot->away_messages);
}

#endif
