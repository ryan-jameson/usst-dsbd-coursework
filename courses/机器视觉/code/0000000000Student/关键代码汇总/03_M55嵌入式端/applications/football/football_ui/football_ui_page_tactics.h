#ifndef FOOTBALL_UI_PAGE_TACTICS_H
#define FOOTBALL_UI_PAGE_TACTICS_H
#include "football_ui.h"
#ifdef BSP_USING_LVGL
#include <lvgl.h>
void football_ui_page_tactics_create(lv_obj_t *parent);
void football_ui_page_tactics_update(const football_ui_snapshot_t *snapshot);
#endif
#endif
