#include "football_ui_page_tactics.h"
#include "football_ui_components.h"
#include "../football_comm/football_comm.h"
#include "../football_link/football_link.h"

#ifdef BSP_USING_LVGL
static lv_obj_t *g_mode_label;
static lv_obj_t *g_formation_label;
static lv_obj_t *g_players[22];
static lv_obj_t *g_pitch;
static lv_obj_t *g_status_label;
static lv_obj_t *g_drawings[8];
static lv_point_t g_line_points[8][2];
static rt_uint8_t g_drawing_count;
static rt_bool_t g_local_mode;
static const char *g_formations[] = {"4-3-3", "4-4-2", "3-5-2"};
static rt_uint8_t g_formation;
static rt_int8_t g_undo_player = -1;
static lv_point_t g_undo_position;

static void tactics_layout(void)
{
    static const lv_point_t home[11] = {{225,515},{75,430},{165,450},{285,450},{375,430},{95,330},{225,350},{355,330},{80,210},{225,185},{370,210}};
    static const lv_point_t away[11] = {{225,35},{75,115},{165,95},{285,95},{375,115},{95,220},{225,200},{355,220},{80,335},{225,360},{370,335}};
    rt_uint8_t i;
    for (i = 0u; i < 11u; ++i)
    {
        lv_obj_set_pos(g_players[i], home[i].x, home[i].y);
        lv_obj_set_pos(g_players[i + 11u], away[i].x, away[i].y);
    }
}

static void tactics_set_status(const char *text)
{
    if (g_status_label != RT_NULL) lv_label_set_text(g_status_label, text);
}

static void tactics_player_cb(lv_event_t *event)
{
    lv_event_code_t code = lv_event_get_code(event);
    lv_obj_t *player = lv_event_get_target(event);
    rt_uint8_t index = (rt_uint8_t)(rt_ubase_t)lv_event_get_user_data(event);
    if (g_local_mode == RT_FALSE) return;
    if (code == LV_EVENT_PRESSED)
    {
        g_undo_player = (rt_int8_t)index;
        g_undo_position.x = lv_obj_get_x(player);
        g_undo_position.y = lv_obj_get_y(player);
    }
    else if (code == LV_EVENT_PRESSING)
    {
        lv_point_t vector;
        int32_t x;
        int32_t y;
        lv_indev_t *indev = lv_indev_active();
        if (indev == RT_NULL) return;
        lv_indev_get_vect(indev, &vector);
        x = lv_obj_get_x(player) + vector.x;
        y = lv_obj_get_y(player) + vector.y;
        if (x < 0) x = 0; else if (x > 426) x = 426;
        if (y < 0) y = 0; else if (y > 546) y = 546;
        lv_obj_set_pos(player, x, y);
    }
    else if (code == LV_EVENT_RELEASED)
    {
        football_ui_set_tactic(g_formations[g_formation], RT_TRUE);
        tactics_set_status("Local edit not sent");
    }
}

static void tactics_add_arrow(void)
{
    lv_obj_t *line;
    rt_uint8_t slot;
    if (g_drawing_count >= 8u) { tactics_set_status("Drawing limit 8"); return; }
    slot = g_drawing_count++;
    g_line_points[slot][0].x = 110 + slot * 8; g_line_points[slot][0].y = 430 - slot * 8;
    g_line_points[slot][1].x = 300 + slot * 5; g_line_points[slot][1].y = 180 + slot * 6;
    line = lv_line_create(g_pitch);
    lv_line_set_points(line, g_line_points[slot], 2u);
    lv_obj_set_style_line_width(line, 5, 0);
    lv_obj_set_style_line_color(line, lv_color_hex(0xffd43b), 0);
    g_drawings[slot] = line;
    football_ui_set_tactic(g_formations[g_formation], RT_TRUE);
    tactics_set_status("Arrow added");
}

static void tactics_add_zone(void)
{
    lv_obj_t *zone;
    rt_uint8_t slot;
    if (g_drawing_count >= 8u) { tactics_set_status("Drawing limit 8"); return; }
    slot = g_drawing_count++;
    zone = lv_obj_create(g_pitch);
    lv_obj_set_size(zone, 105, 72);
    lv_obj_set_pos(zone, 170 + (slot % 2u) * 45, 245 + (slot % 3u) * 28);
    lv_obj_set_style_bg_color(zone, lv_color_hex(0xff8a3d), 0);
    lv_obj_set_style_bg_opa(zone, LV_OPA_40, 0);
    lv_obj_set_style_border_color(zone, lv_color_hex(0xffd4ad), 0);
    g_drawings[slot] = zone;
    football_ui_set_tactic(g_formations[g_formation], RT_TRUE);
    tactics_set_status("Zone added");
}

static void tactics_clear_drawings(void)
{
    while (g_drawing_count != 0u)
    {
        g_drawing_count--;
        if (g_drawings[g_drawing_count] != RT_NULL)
        {
            lv_obj_delete(g_drawings[g_drawing_count]);
            g_drawings[g_drawing_count] = RT_NULL;
        }
    }
}

static void tactics_send(void)
{
    char json[FOOTBALL_SHARED_ENTRY_PAYLOAD];
    rt_size_t used;
    rt_uint8_t i;
    int written = rt_snprintf(json, sizeof(json),
                              "{\"formation\":\"%s\",\"drawings\":%u,\"players\":[",
                              g_formations[g_formation], g_drawing_count);
    if (written < 0 || (rt_size_t)written >= sizeof(json)) return;
    used = (rt_size_t)written;
    for (i = 0u; i < 22u; ++i)
    {
        written = rt_snprintf(json + used, sizeof(json) - used, "%s[%d,%d]",
                              i == 0u ? "" : ",", lv_obj_get_x(g_players[i]),
                              lv_obj_get_y(g_players[i]));
        if (written < 0 || (rt_size_t)written >= sizeof(json) - used)
        {
            tactics_set_status("Tactic too large");
            return;
        }
        used += (rt_size_t)written;
    }
    written = rt_snprintf(json + used, sizeof(json) - used, "]}");
    if (written < 0 || (rt_size_t)written >= sizeof(json) - used) return;
    used += (rt_size_t)written;
    if (football_comm_publish_to_m33(FOOTBALL_MSG_TACTICS_OPERATION, 0u,
                                     (rt_uint32_t)rt_tick_get(), json, used) == RT_EOK)
    {
        football_ui_set_tactic(g_formations[g_formation], RT_FALSE);
        tactics_set_status("Sent to PC");
    }
    else tactics_set_status("Send queue busy");
}

static void tactics_tool_cb(lv_event_t *event)
{
    const char *action = (const char *)lv_event_get_user_data(event);
    if (g_local_mode == RT_FALSE) { tactics_set_status("Switch to LOCAL EDIT"); return; }
    if (rt_strcmp(action, "Arrow") == 0) tactics_add_arrow();
    else if (rt_strcmp(action, "Zone") == 0) tactics_add_zone();
    else if (rt_strcmp(action, "Undo") == 0)
    {
        if (g_drawing_count != 0u)
        {
            g_drawing_count--;
            lv_obj_delete(g_drawings[g_drawing_count]);
            g_drawings[g_drawing_count] = RT_NULL;
        }
        else if (g_undo_player >= 0)
        {
            lv_obj_set_pos(g_players[(rt_uint8_t)g_undo_player],
                           g_undo_position.x, g_undo_position.y);
            g_undo_player = -1;
        }
        tactics_set_status("Undo complete");
    }
    else if (rt_strcmp(action, "Clear") == 0) { tactics_clear_drawings(); tactics_set_status("Drawings cleared"); }
    else if (rt_strcmp(action, "Reset") == 0) { tactics_clear_drawings(); tactics_layout(); tactics_set_status("Formation reset"); }
    else if (rt_strcmp(action, "Send") == 0) tactics_send();
}

static void tactics_tool_button(lv_obj_t *parent, const char *text, int32_t x)
{
    lv_obj_t *button = lv_button_create(parent);
    lv_obj_t *label;
    lv_obj_set_size(button, 68, 31);
    lv_obj_set_pos(button, x, 620);
    label = lv_label_create(button);
    lv_label_set_text(label, text);
    lv_obj_center(label);
    lv_obj_add_event_cb(button, tactics_tool_cb, LV_EVENT_CLICKED, (void *)text);
}

static void tactics_mode_cb(lv_event_t *event)
{
    RT_UNUSED(event);
    g_local_mode = !g_local_mode;
    lv_label_set_text(g_mode_label, g_local_mode ? "LOCAL EDIT" : "LIVE PC");
    tactics_set_status(g_local_mode ? "Drag players or add drawings" : "Following PC tactics");
}

static void tactics_formation_cb(lv_event_t *event)
{
    RT_UNUSED(event);
    g_formation = (g_formation + 1u) % 3u;
    football_ui_set_tactic(g_formations[g_formation], RT_TRUE);
    lv_label_set_text(g_formation_label, g_formations[g_formation]);
}

void football_ui_page_tactics_create(lv_obj_t *parent)
{
    lv_obj_t *pitch;
    lv_obj_t *button;
    rt_uint8_t i;
    football_ui_components_prepare_page(parent);
    button = lv_button_create(parent);
    lv_obj_set_size(button, 120, 34); lv_obj_align(button, LV_ALIGN_TOP_LEFT, 8, 4);
    g_mode_label = lv_label_create(button); lv_label_set_text(g_mode_label, "LIVE PC"); lv_obj_center(g_mode_label);
    lv_obj_add_event_cb(button, tactics_mode_cb, LV_EVENT_CLICKED, RT_NULL);
    button = lv_button_create(parent);
    lv_obj_set_size(button, 100, 34); lv_obj_align(button, LV_ALIGN_TOP_MID, 0, 4);
    g_formation_label = lv_label_create(button); lv_label_set_text(g_formation_label, "4-3-3"); lv_obj_center(g_formation_label);
    lv_obj_add_event_cb(button, tactics_formation_cb, LV_EVENT_CLICKED, RT_NULL);
    pitch = lv_obj_create(parent);
    g_pitch = pitch;
    lv_obj_set_size(pitch, 450, 570); lv_obj_align(pitch, LV_ALIGN_TOP_MID, 0, 46);
    lv_obj_set_style_bg_color(pitch, lv_color_hex(0x176b3a), 0);
    lv_obj_set_style_border_color(pitch, lv_color_hex(0xeaf7ee), 0);
    lv_obj_set_style_border_width(pitch, 2, 0);
    for (i = 0u; i < 22u; ++i)
    {
        g_players[i] = lv_obj_create(pitch);
        lv_obj_remove_style_all(g_players[i]);
        lv_obj_set_size(g_players[i], 24, 24);
        lv_obj_set_style_radius(g_players[i], LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_opa(g_players[i], LV_OPA_COVER, 0);
        lv_obj_set_style_bg_color(g_players[i], lv_color_hex(i < 11u ? 0x22aaff : 0xff5b4d), 0);
        lv_obj_add_flag(g_players[i], LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_event_cb(g_players[i], tactics_player_cb, LV_EVENT_ALL,
                            (void *)(rt_ubase_t)i);
    }
    tactics_layout();
    tactics_tool_button(parent, "Arrow", 8);
    tactics_tool_button(parent, "Zone", 80);
    tactics_tool_button(parent, "Undo", 152);
    tactics_tool_button(parent, "Clear", 224);
    tactics_tool_button(parent, "Reset", 296);
    tactics_tool_button(parent, "Send", 368);
    g_status_label = football_ui_components_label(parent, "Following PC tactics", 655, 0xb7d3c4);
}

void football_ui_page_tactics_update(const football_ui_snapshot_t *snapshot)
{
    if (snapshot == RT_NULL || g_formation_label == RT_NULL) return;
    if (g_local_mode == RT_FALSE && snapshot->current_tactic[0] != '\0')
        lv_label_set_text(g_formation_label, snapshot->current_tactic);
}
#endif
