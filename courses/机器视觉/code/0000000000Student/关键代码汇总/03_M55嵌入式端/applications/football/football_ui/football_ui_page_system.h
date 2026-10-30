#ifndef FOOTBALL_UI_PAGE_SYSTEM_H
#define FOOTBALL_UI_PAGE_SYSTEM_H

#include "football_ui.h"

#ifdef BSP_USING_LVGL
#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

void football_ui_page_system_create(lv_obj_t *parent);
void football_ui_page_system_update(const football_ui_snapshot_t *snapshot);
void football_ui_system_toggle(lv_event_t *event);

#ifdef __cplusplus
}
#endif
#endif

#endif
