#ifndef FOOTBALL_UI_PAGE_EVENTS_H
#define FOOTBALL_UI_PAGE_EVENTS_H
#include "football_ui.h"
#ifdef BSP_USING_LVGL
#include <lvgl.h>
void football_ui_page_events_create(lv_obj_t *parent);
void football_ui_page_events_update(const football_ui_snapshot_t *snapshot);
#endif
#endif
