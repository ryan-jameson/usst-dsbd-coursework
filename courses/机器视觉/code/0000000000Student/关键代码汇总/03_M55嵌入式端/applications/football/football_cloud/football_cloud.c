#include "football_cloud.h"
#include "../football_settings/football_settings.h"
#include "llm_client.h"
#include "speech_client.h"
#include "tts_client.h"
#include "user_preferences.h"

#include <drivers/wlan.h>
#include <finsh.h>
#include <time.h>

static football_settings_t g_runtime_config;
static football_cloud_status_t g_cloud_status;
static struct rt_mutex g_cloud_lock;
static rt_thread_t g_cloud_thread;
static rt_bool_t g_cloud_running;
static volatile rt_uint32_t g_cancelled_request;

const football_settings_t *football_cloud_runtime_config(void)
{
    football_settings_get(&g_runtime_config);
    return &g_runtime_config;
}

static rt_bool_t football_cloud_time_valid(void)
{
    time_t now = time(RT_NULL);
    return now > (time_t)1704067200 ? RT_TRUE : RT_FALSE;
}

static rt_err_t football_cloud_begin(rt_uint32_t request_id, rt_bool_t needs_ai,
                                     rt_bool_t needs_tencent)
{
    football_settings_status_t settings;
    football_settings_get_status(&settings);
    if (rt_wlan_is_connected() != RT_TRUE || rt_wlan_is_ready() != RT_TRUE)
    {
        return -RT_ERROR;
    }
    if ((needs_ai == RT_TRUE && settings.ai_configured == RT_FALSE) ||
        (needs_tencent == RT_TRUE && settings.tencent_configured == RT_FALSE))
    {
        return -RT_EINVAL;
    }
    if (needs_tencent == RT_TRUE && football_cloud_time_valid() == RT_FALSE)
    {
        return -RT_ETIMEOUT;
    }
    rt_mutex_take(&g_cloud_lock, RT_WAITING_FOREVER);
    if (g_cloud_status.active_request != 0u)
    {
        rt_mutex_release(&g_cloud_lock);
        return -RT_EBUSY;
    }
    g_cloud_status.active_request = request_id == 0u ? 1u : request_id;
    g_cloud_status.state = FOOTBALL_CLOUD_BUSY;
    g_cancelled_request = 0u;
    rt_mutex_release(&g_cloud_lock);
    return RT_EOK;
}

static rt_err_t football_cloud_finish(rt_uint32_t request_id, rt_err_t result)
{
    rt_mutex_take(&g_cloud_lock, RT_WAITING_FOREVER);
    if (g_cancelled_request == request_id)
    {
        result = -RT_EINTR;
    }
    g_cloud_status.active_request = 0u;
    g_cloud_status.last_error = result;
    if (result == RT_EOK)
    {
        g_cloud_status.completed_requests++;
        g_cloud_status.state = FOOTBALL_CLOUD_READY;
    }
    else
    {
        g_cloud_status.failed_requests++;
        g_cloud_status.state = FOOTBALL_CLOUD_ERROR;
    }
    rt_mutex_release(&g_cloud_lock);
    return result;
}

rt_err_t football_cloud_chat(rt_uint32_t request_id, const char *prompt,
                             char *reply, rt_size_t reply_size)
{
    rt_err_t result = football_cloud_begin(request_id, RT_TRUE, RT_FALSE);
    if (result == RT_EOK)
    {
        result = llm_client_chat(prompt, reply, reply_size);
        result = football_cloud_finish(request_id, result);
    }
    return result;
}

rt_err_t football_cloud_transcribe(rt_uint32_t request_id, rt_uint32_t seconds,
                                   char *text, rt_size_t text_size)
{
    rt_err_t result = football_cloud_begin(request_id, RT_FALSE, RT_TRUE);
    if (result == RT_EOK)
    {
        result = speech_client_transcribe_seconds(text, text_size, seconds);
        result = football_cloud_finish(request_id, result);
    }
    return result;
}

rt_err_t football_cloud_speak(rt_uint32_t request_id, const char *text)
{
    rt_err_t result = football_cloud_begin(request_id, RT_FALSE, RT_TRUE);
    if (result == RT_EOK)
    {
        /* The voice scheduler already owns a worker thread.  Keep this call
         * synchronous so COMPLETE means that playback actually finished. */
        result = tts_client_speak(text);
        result = football_cloud_finish(request_id, result);
    }
    return result;
}

void football_cloud_cancel(rt_uint32_t request_id)
{
    g_cancelled_request = request_id;
}

void football_cloud_get_status(football_cloud_status_t *status)
{
    if (status == RT_NULL)
    {
        return;
    }
    rt_mutex_take(&g_cloud_lock, RT_WAITING_FOREVER);
    *status = g_cloud_status;
    rt_mutex_release(&g_cloud_lock);
}

static void football_cloud_monitor(void *parameter)
{
    static const rt_uint32_t delays[] = {1000u, 2000u, 5000u, 10000u, 30000u};
    rt_uint32_t attempt = 0u;
    RT_UNUSED(parameter);
    user_preferences_init();
    while (g_cloud_running == RT_TRUE)
    {
        football_settings_t settings;
        football_settings_status_t status;
        football_settings_get(&settings);
        football_settings_get_status(&status);
        rt_mutex_take(&g_cloud_lock, RT_WAITING_FOREVER);
        g_cloud_status.ai_configured = status.ai_configured;
        g_cloud_status.tencent_configured = status.tencent_configured;
        g_cloud_status.wifi_ready = rt_wlan_is_ready();
        g_cloud_status.rtc_ready = football_cloud_time_valid();
        if (status.wifi_configured == RT_FALSE)
            g_cloud_status.state = FOOTBALL_CLOUD_WAIT_CONFIG;
        else if (g_cloud_status.wifi_ready == RT_FALSE)
            g_cloud_status.state = FOOTBALL_CLOUD_CONNECTING;
        else if (g_cloud_status.rtc_ready == RT_FALSE)
            g_cloud_status.state = FOOTBALL_CLOUD_WAIT_TIME;
        else if (g_cloud_status.active_request == 0u)
            g_cloud_status.state = FOOTBALL_CLOUD_READY;
        rt_mutex_release(&g_cloud_lock);

        if (status.wifi_configured == RT_TRUE && rt_wlan_is_connected() != RT_TRUE)
        {
            (void)rt_wlan_connect(settings.wifi_ssid, settings.wifi_password);
            rt_thread_mdelay(delays[attempt]);
            if (attempt + 1u < sizeof(delays) / sizeof(delays[0])) attempt++;
        }
        else
        {
            attempt = 0u;
            if (rt_wlan_is_ready() == RT_TRUE && football_cloud_time_valid() == RT_FALSE)
            {
                (void)speech_client_sync_time();
            }
            rt_thread_mdelay(1000u);
        }
        rt_memset(&settings, 0, sizeof(settings));
    }
}

rt_err_t football_cloud_start(void)
{
    if (g_cloud_running == RT_TRUE)
    {
        return RT_EOK;
    }
    football_settings_init();
    rt_memset(&g_cloud_status, 0, sizeof(g_cloud_status));
    rt_mutex_init(&g_cloud_lock, "fb_cloud", RT_IPC_FLAG_PRIO);
    g_cloud_running = RT_TRUE;
    g_cloud_thread = rt_thread_create("fb_cloud", football_cloud_monitor, RT_NULL,
                                      4096u, 24u, 20u);
    if (g_cloud_thread == RT_NULL)
    {
        g_cloud_running = RT_FALSE;
        return -RT_ENOMEM;
    }
    rt_thread_startup(g_cloud_thread);
    return RT_EOK;
}

static int football_cloud_cmd(int argc, char **argv)
{
    football_cloud_status_t status;
    RT_UNUSED(argc);
    RT_UNUSED(argv);
    football_cloud_get_status(&status);
    rt_kprintf("cloud state=%d wifi=%d rtc=%d ai=%d tencent=%d active=%u done=%u failed=%u error=%d\r\n",
               status.state, status.wifi_ready, status.rtc_ready,
               status.ai_configured, status.tencent_configured,
               (unsigned int)status.active_request,
               (unsigned int)status.completed_requests,
               (unsigned int)status.failed_requests, status.last_error);
    return 0;
}
MSH_CMD_EXPORT_ALIAS(football_cloud_cmd, football_cloud, football cloud redacted status);

static int football_cloud_auto_init(void)
{
    return football_cloud_start();
}
INIT_APP_EXPORT(football_cloud_auto_init);
