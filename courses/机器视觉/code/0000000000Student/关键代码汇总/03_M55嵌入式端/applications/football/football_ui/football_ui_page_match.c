#include "football_ui_page_match.h"
#include "football_ui_components.h"
#ifdef BSP_USING_LVGL
static lv_obj_t *g_score;
static lv_obj_t *g_clock;
static lv_obj_t *g_state;
static lv_obj_t *g_event;
static lv_obj_t *g_ai;
void football_ui_page_match_create(lv_obj_t *parent)
{
    football_ui_components_prepare_page(parent);
    g_score = football_ui_components_label(parent, "HOME 0 : 0 AWAY", 22, 0xffffff);
    lv_obj_set_style_text_font(g_score, &lv_font_montserrat_24, 0);
    g_clock = football_ui_components_label(parent, "00:00", 78, 0x7ef29a);
    g_state = football_ui_components_label(parent, "Possession -- | Danger 0 | 4-3-3", 132, 0xb7d3c4);
    g_event = football_ui_components_label(parent, "Current event: waiting", 210, 0xffffff);
    g_ai = football_ui_components_label(parent, "AI: waiting for an event", 300, 0xf6d365);
}
void football_ui_page_match_update(const football_ui_snapshot_t *s)
{
    if (s == RT_NULL || g_score == RT_NULL) return;
    lv_label_set_text_fmt(g_score, "HOME %u : %u AWAY", s->home_score, s->away_score);
    lv_label_set_text_fmt(g_clock, "%02u:%02u", s->match_minute, s->match_second);
    lv_label_set_text_fmt(g_state, "Possession %u%% | Danger %u | %s", s->possession_home, s->danger_level, s->current_tactic);
    lv_label_set_text_fmt(g_event, "Current event: %s / %s", s->last_message.event, s->last_message.team);
    lv_label_set_text_fmt(g_ai, "AI/Voice state: %u", s->voice_status);
}
#endif
