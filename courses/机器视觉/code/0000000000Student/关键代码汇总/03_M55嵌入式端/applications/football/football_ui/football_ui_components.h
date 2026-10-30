#ifndef FOOTBALL_UI_COMPONENTS_H
#define FOOTBALL_UI_COMPONENTS_H

#include "football_ui.h"

#ifdef BSP_USING_LVGL
#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

lv_obj_t *football_ui_components_label(lv_obj_t *parent,
                                       const char *text,
                                       int32_t y,
                                       uint32_t color);
void football_ui_components_prepare_page(lv_obj_t *page);

#ifdef __cplusplus
}
#endif
#endif

#endif
