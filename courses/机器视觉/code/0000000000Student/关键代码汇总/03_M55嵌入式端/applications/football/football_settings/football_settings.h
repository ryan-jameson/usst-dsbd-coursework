#ifndef FOOTBALL_SETTINGS_H
#define FOOTBALL_SETTINGS_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct football_settings
{
    char wifi_ssid[33];
    char wifi_password[65];
    char ai_endpoint[96];
    char ai_model[48];
    char ai_api_key[160];
    char tencent_secret_id[96];
    char tencent_secret_key[128];
} football_settings_t;

typedef struct football_settings_status
{
    rt_bool_t loaded;
    rt_bool_t persisted;
    rt_bool_t wifi_configured;
    rt_bool_t ai_configured;
    rt_bool_t tencent_configured;
    rt_uint32_t generation;
    rt_err_t last_error;
} football_settings_status_t;

rt_err_t football_settings_init(void);
rt_err_t football_settings_apply_json(rt_uint8_t message_type,
                                      const char *json,
                                      rt_size_t length);
rt_err_t football_settings_save(void);
rt_err_t football_settings_clear(void);
void football_settings_get(football_settings_t *settings);
void football_settings_get_status(football_settings_status_t *status);

#ifdef __cplusplus
}
#endif
#endif
