#include "football_ui_components.h"

#ifdef BSP_USING_LVGL

lv_obj_t *football_ui_components_label(lv_obj_t *parent,
                                       const char *text,
                                       int32_t y,
                                       uint32_t color)
{
    lv_obj_t *label = lv_label_create(parent);

    lv_obj_set_width(label, lv_pct(94));
    lv_label_set_long_mode(label, LV_LABEL_LONG_WRAP);
    lv_label_set_text(label, text);
    lv_obj_set_style_text_color(label, lv_color_hex(color), 0);
    lv_obj_align(label, LV_ALIGN_TOP_LEFT, 12, y);

    return label;
}

void football_ui_components_prepare_page(lv_obj_t *page)
{
    lv_obj_set_style_bg_color(page, lv_color_hex(0x071b14), 0);
    lv_obj_set_style_bg_opa(page, LV_OPA_COVER, 0);
    lv_obj_set_style_pad_all(page, 8, 0);
}

#endif
