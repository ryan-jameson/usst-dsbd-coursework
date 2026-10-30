#include "football_settings.h"
#include "../football_link/football_link.h"

#include <finsh.h>
#include <stdio.h>
#include <string.h>

#define FOOTBALL_SETTINGS_MAGIC   0x31534246u
#define FOOTBALL_SETTINGS_VERSION 1u
#define FOOTBALL_SETTINGS_PATH    "/flash/football_cloud.cfg"
#define FOOTBALL_SETTINGS_TEST_MODE 1u

#define FOOTBALL_TEST_WIFI_SSID       "REDACTED_CONFIGURE_LOCALLY"
#define FOOTBALL_TEST_WIFI_PASSWORD   "REDACTED_CONFIGURE_LOCALLY"
#define FOOTBALL_TEST_AI_ENDPOINT     "https://api.deepseek.com/chat/completions"
#define FOOTBALL_TEST_AI_MODEL        "deepseek-v4-flash"
#define FOOTBALL_TEST_AI_API_KEY      "REDACTED_CONFIGURE_LOCALLY"
#define FOOTBALL_TEST_TENCENT_ID      "REDACTED_CLOUD_ID"
#define FOOTBALL_TEST_TENCENT_KEY     "kNp6FU8f4gAfFh3RuqjVAf1IXiyHYlpk"

typedef struct football_settings_record
{
    rt_uint32_t magic;
    rt_uint16_t version;
    rt_uint16_t size;
    rt_uint32_t generation;
    football_settings_t values;
    rt_uint32_t crc32;
} football_settings_record_t;

static football_settings_t g_settings;
static football_settings_status_t g_status;
static struct rt_mutex g_lock;
static rt_bool_t g_initialized;

static void settings_copy(char *dst, rt_size_t size, const char *src, rt_size_t length)
{
    if (size == 0u)
    {
        return;
    }
    if (length >= size)
    {
        length = size - 1u;
    }
    if (src != RT_NULL && length != 0u)
    {
        rt_memcpy(dst, src, length);
    }
    dst[length] = '\0';
}

static void settings_load_builtin_test_values(football_settings_t *settings)
{
    rt_memset(settings, 0, sizeof(*settings));
    settings_copy(settings->wifi_ssid, sizeof(settings->wifi_ssid),
                  FOOTBALL_TEST_WIFI_SSID, rt_strlen(FOOTBALL_TEST_WIFI_SSID));
    settings_copy(settings->wifi_password, sizeof(settings->wifi_password),
                  FOOTBALL_TEST_WIFI_PASSWORD, rt_strlen(FOOTBALL_TEST_WIFI_PASSWORD));
    settings_copy(settings->ai_endpoint, sizeof(settings->ai_endpoint),
                  FOOTBALL_TEST_AI_ENDPOINT, rt_strlen(FOOTBALL_TEST_AI_ENDPOINT));
    settings_copy(settings->ai_model, sizeof(settings->ai_model),
                  FOOTBALL_TEST_AI_MODEL, rt_strlen(FOOTBALL_TEST_AI_MODEL));
    settings_copy(settings->ai_api_key, sizeof(settings->ai_api_key),
                  FOOTBALL_TEST_AI_API_KEY, rt_strlen(FOOTBALL_TEST_AI_API_KEY));
    settings_copy(settings->tencent_secret_id, sizeof(settings->tencent_secret_id),
                  FOOTBALL_TEST_TENCENT_ID, rt_strlen(FOOTBALL_TEST_TENCENT_ID));
    settings_copy(settings->tencent_secret_key, sizeof(settings->tencent_secret_key),
                  FOOTBALL_TEST_TENCENT_KEY, rt_strlen(FOOTBALL_TEST_TENCENT_KEY));
}

static rt_bool_t settings_json_string(const char *json, rt_size_t length,
                                      const char *key, char *output, rt_size_t size)
{
    char pattern[48];
    const char *position;
    const char *end = json + length;
    rt_size_t used = 0u;
    rt_snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    position = strstr(json, pattern);
    if (position == RT_NULL || position >= end)
    {
        return RT_FALSE;
    }
    position += rt_strlen(pattern);
    while (position < end && (*position == ' ' || *position == '\t' || *position == ':'))
    {
        position++;
    }
    if (position >= end || *position++ != '"')
    {
        return RT_FALSE;
    }
    while (position < end && *position != '"')
    {
        char value = *position++;
        if (value == '\\' && position < end)
        {
            value = *position++;
        }
        if (used + 1u >= size)
        {
            return RT_FALSE;
        }
        output[used++] = value;
    }
    if (position >= end)
    {
        return RT_FALSE;
    }
    output[used] = '\0';
    return RT_TRUE;
}

static void settings_refresh_status(void)
{
    g_status.wifi_configured = g_settings.wifi_ssid[0] != '\0';
    g_status.ai_configured = g_settings.ai_endpoint[0] != '\0' &&
                             g_settings.ai_model[0] != '\0' &&
                             g_settings.ai_api_key[0] != '\0';
    g_status.tencent_configured = g_settings.tencent_secret_id[0] != '\0' &&
                                  g_settings.tencent_secret_key[0] != '\0';
}

rt_err_t football_settings_save(void)
{
    football_settings_record_t record;
    FILE *file;
    rt_err_t result = RT_EOK;
    if (g_initialized == RT_FALSE)
    {
        return -RT_EINVAL;
    }
    if (FOOTBALL_SETTINGS_TEST_MODE != 0u)
    {
        g_status.persisted = RT_FALSE;
        g_status.last_error = RT_EOK;
        return RT_EOK;
    }
    rt_mutex_take(&g_lock, RT_WAITING_FOREVER);
    rt_memset(&record, 0, sizeof(record));
    record.magic = FOOTBALL_SETTINGS_MAGIC;
    record.version = FOOTBALL_SETTINGS_VERSION;
    record.size = sizeof(record);
    record.generation = ++g_status.generation;
    record.values = g_settings;
    record.crc32 = football_crc32(&record, sizeof(record) - sizeof(record.crc32), 0u);
    file = fopen(FOOTBALL_SETTINGS_PATH, "wb");
    if (file == RT_NULL || fwrite(&record, 1u, sizeof(record), file) != sizeof(record))
    {
        result = -RT_ERROR;
    }
    if (file != RT_NULL)
    {
        fclose(file);
    }
    g_status.persisted = (result == RT_EOK) ? RT_TRUE : RT_FALSE;
    g_status.last_error = result;
    rt_memset(&record, 0, sizeof(record));
    rt_mutex_release(&g_lock);
    return result;
}

rt_err_t football_settings_init(void)
{
    football_settings_record_t record;
    FILE *file;
    rt_uint32_t crc;
    if (g_initialized == RT_TRUE)
    {
        return RT_EOK;
    }
    rt_memset(&g_settings, 0, sizeof(g_settings));
    rt_memset(&g_status, 0, sizeof(g_status));
    settings_load_builtin_test_values(&g_settings);
    g_status.loaded = RT_TRUE;
    rt_mutex_init(&g_lock, "fb_cfg", RT_IPC_FLAG_PRIO);
    g_initialized = RT_TRUE;
    if (FOOTBALL_SETTINGS_TEST_MODE == 0u)
    {
        file = fopen(FOOTBALL_SETTINGS_PATH, "rb");
        if (file != RT_NULL && fread(&record, 1u, sizeof(record), file) == sizeof(record))
        {
            crc = football_crc32(&record, sizeof(record) - sizeof(record.crc32), 0u);
            if (record.magic == FOOTBALL_SETTINGS_MAGIC &&
                record.version == FOOTBALL_SETTINGS_VERSION &&
                record.size == sizeof(record) && record.crc32 == crc)
            {
                g_settings = record.values;
                g_status.generation = record.generation;
                g_status.loaded = RT_TRUE;
                g_status.persisted = RT_TRUE;
            }
            else
            {
                g_status.last_error = -RT_EINVAL;
            }
        }
        if (file != RT_NULL)
        {
            fclose(file);
        }
    }
    rt_memset(&record, 0, sizeof(record));
    settings_refresh_status();
    return RT_EOK;
}

rt_err_t football_settings_apply_json(rt_uint8_t message_type,
                                      const char *json,
                                      rt_size_t length)
{
    football_settings_t updated;
    char value[160];
    if (json == RT_NULL || length == 0u || length > FOOTBALL_WIRE_MAX_PAYLOAD)
    {
        return -RT_EINVAL;
    }
    football_settings_init();
    if (FOOTBALL_SETTINGS_TEST_MODE != 0u)
    {
        return RT_EOK;
    }
    rt_mutex_take(&g_lock, RT_WAITING_FOREVER);
    updated = g_settings;
    if (message_type == FOOTBALL_MSG_WIFI_CONFIG)
    {
        if (settings_json_string(json, length, "ssid", value, sizeof(value)) == RT_FALSE)
        {
            rt_mutex_release(&g_lock);
            return -RT_EINVAL;
        }
        settings_copy(updated.wifi_ssid, sizeof(updated.wifi_ssid), value, rt_strlen(value));
        if (settings_json_string(json, length, "password", value, sizeof(value)) == RT_TRUE)
        {
            settings_copy(updated.wifi_password, sizeof(updated.wifi_password), value, rt_strlen(value));
        }
    }
    else if (message_type == FOOTBALL_MSG_CLOUD_CONFIG)
    {
        if (settings_json_string(json, length, "endpoint", value, sizeof(value)) == RT_TRUE)
            settings_copy(updated.ai_endpoint, sizeof(updated.ai_endpoint), value, rt_strlen(value));
        if (settings_json_string(json, length, "model", value, sizeof(value)) == RT_TRUE)
            settings_copy(updated.ai_model, sizeof(updated.ai_model), value, rt_strlen(value));
        if (settings_json_string(json, length, "api_key", value, sizeof(value)) == RT_TRUE)
            settings_copy(updated.ai_api_key, sizeof(updated.ai_api_key), value, rt_strlen(value));
        if (settings_json_string(json, length, "secret_id", value, sizeof(value)) == RT_TRUE)
            settings_copy(updated.tencent_secret_id, sizeof(updated.tencent_secret_id), value, rt_strlen(value));
        if (settings_json_string(json, length, "secret_key", value, sizeof(value)) == RT_TRUE)
            settings_copy(updated.tencent_secret_key, sizeof(updated.tencent_secret_key), value, rt_strlen(value));
    }
    else
    {
        rt_mutex_release(&g_lock);
        return -RT_ENOSYS;
    }
    rt_memset(value, 0, sizeof(value));
    g_settings = updated;
    settings_refresh_status();
    rt_mutex_release(&g_lock);
    rt_memset(&updated, 0, sizeof(updated));
    return football_settings_save();
}

rt_err_t football_settings_clear(void)
{
    football_settings_init();
    rt_mutex_take(&g_lock, RT_WAITING_FOREVER);
    if (FOOTBALL_SETTINGS_TEST_MODE != 0u)
    {
        settings_load_builtin_test_values(&g_settings);
    }
    else
    {
        rt_memset(&g_settings, 0, sizeof(g_settings));
        settings_copy(g_settings.ai_endpoint, sizeof(g_settings.ai_endpoint),
                      "https://api.deepseek.com/chat/completions", 41u);
        settings_copy(g_settings.ai_model, sizeof(g_settings.ai_model),
                      "deepseek-v4-flash", 17u);
    }
    settings_refresh_status();
    rt_mutex_release(&g_lock);
    if (FOOTBALL_SETTINGS_TEST_MODE == 0u)
    {
        (void)remove(FOOTBALL_SETTINGS_PATH);
    }
    g_status.persisted = RT_FALSE;
    g_status.generation++;
    return RT_EOK;
}

void football_settings_get(football_settings_t *settings)
{
    if (settings == RT_NULL)
    {
        return;
    }
    football_settings_init();
    rt_mutex_take(&g_lock, RT_WAITING_FOREVER);
    *settings = g_settings;
    rt_mutex_release(&g_lock);
}

void football_settings_get_status(football_settings_status_t *status)
{
    if (status == RT_NULL)
    {
        return;
    }
    football_settings_init();
    rt_mutex_take(&g_lock, RT_WAITING_FOREVER);
    *status = g_status;
    rt_mutex_release(&g_lock);
}

static int football_config_cmd(int argc, char **argv)
{
    football_settings_status_t status;
    if (argc >= 2 && rt_strcmp(argv[1], "clear") == 0)
    {
        rt_kprintf("config clear=%d\r\n", football_settings_clear());
    }
    football_settings_get_status(&status);
    rt_kprintf("config loaded=%d persisted=%d wifi=%d ai=%d tencent=%d generation=%u error=%d\r\n",
               status.loaded, status.persisted, status.wifi_configured,
               status.ai_configured, status.tencent_configured,
               (unsigned int)status.generation, status.last_error);
    return 0;
}
MSH_CMD_EXPORT_ALIAS(football_config_cmd, football_config, football redacted settings status or clear);

static int football_settings_auto_init(void)
{
    return football_settings_init();
}
INIT_ENV_EXPORT(football_settings_auto_init);
