#ifndef FOOTBALL_UI_PAGE_RECENT_H
#define FOOTBALL_UI_PAGE_RECENT_H

#include "football_ui.h"

#ifdef BSP_USING_LVGL
#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

void football_ui_page_recent_create(lv_obj_t *parent);
void football_ui_page_recent_update(const football_ui_snapshot_t *snapshot);

#ifdef __cplusplus
}
#endif
#endif

#endif
