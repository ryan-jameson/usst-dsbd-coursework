#include <rtthread.h>
#include <rtdevice.h>
#include <stdlib.h>
#include <time.h>

#ifdef RT_USING_MSH
#include <finsh.h>
#endif

#include "json_util.h"
#include "llm_config.h"
#include "speech_client.h"
#include "tts_client.h"
#include "user_preferences.h"

#if defined(RT_USING_RTC)
#include <drivers/rtc.h>
#endif

#if defined(RT_WLAN_MANAGE_ENABLE)
#include <drivers/wlan.h>
#endif

#if defined(PKG_USING_WEBCLIENT)
#include <webclient.h>
#endif

#if defined(PKG_USING_MBEDTLS)
#include <mbedtls/base64.h>
#include <mbedtls/md.h>
#include <mbedtls/sha256.h>
#endif

#define TTS_SERVICE      "tts"
#define TTS_ACTION       "TextToVoice"
#define TTS_VERSION      "2019-08-23"
#define TTS_HEADER_SIZE  1536
#define TTS_REQUEST_SIZE 640
#define TTS_PCM_CHUNK    2048u
#define TTS_AUDIO_DEVICE "sound0"
#define TTS_FORCE_VOLUME_X100 1000
#define TTS_CLI_THREAD_STACK_SIZE   16384u
#define TTS_CLI_THREAD_PRIORITY     18u
#define TTS_CLI_THREAD_TICK         10u

static volatile rt_bool_t s_tts_cli_busy = RT_FALSE;
static volatile rt_bool_t s_tts_cli_pending = RT_FALSE;
static rt_mutex_t s_tts_cli_lock = RT_NULL;
static char s_tts_cli_text[TENCENT_TTS_MAX_TEXT_LEN + 1];
static char s_tts_cli_pending_text[TENCENT_TTS_MAX_TEXT_LEN + 1];

static int tts_cli_lock_take(void)
{
    if (s_tts_cli_lock == RT_NULL)
    {
        s_tts_cli_lock = rt_mutex_create("ttslock", RT_IPC_FLAG_PRIO);
        if (s_tts_cli_lock == RT_NULL)
        {
            rt_kprintf("tts: unable to create TTS lock.\r\n");
            return -RT_ENOMEM;
        }
    }

    return rt_mutex_take(s_tts_cli_lock, RT_WAITING_FOREVER);
}

static void tts_cli_lock_release(void)
{
    if (s_tts_cli_lock != RT_NULL)
    {
        rt_mutex_release(s_tts_cli_lock);
    }
}

#if defined(PKG_USING_WEBCLIENT) && defined(PKG_USING_MBEDTLS)
static int tts_sha256(const char *data, rt_size_t size, unsigned char output[32])
{
    return (mbedtls_sha256_ret((const unsigned char *)data, size, output, 0) == 0) ? RT_EOK : -RT_ERROR;
}

static int tts_hmac_sha256(const unsigned char *key, rt_size_t key_size,
                            const char *data, rt_size_t data_size,
                            unsigned char output[32])
{
    const mbedtls_md_info_t *md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    if (md_info == RT_NULL) return -RT_ERROR;
    return (mbedtls_md_hmac(md_info, key, key_size,
                            (const unsigned char *)data, data_size, output) == 0) ? RT_EOK : -RT_ERROR;
}

static void tts_hex(const unsigned char *input, rt_size_t size, char *output)
{
    static const char hex[] = "0123456789abcdef";
    rt_size_t i;
    for (i = 0; i < size; i++)
    {
        output[i * 2U] = hex[input[i] >> 4];
        output[i * 2U + 1U] = hex[input[i] & 0x0fU];
    }
    output[size * 2U] = '\0';
}

static int tts_build_authorization(const char *payload, rt_size_t payload_size,
                                    time_t timestamp, const char *date,
                                    char *authorization, rt_size_t authorization_size)
{
    char canonical_request[512];
    char canonical_hash[65];
    char credential_scope[64];
    char string_to_sign[256];
    char secret_date_input[96];
    char signature[65];
    unsigned char digest[32];
    unsigned char secret_date[32];
    unsigned char secret_service[32];
    unsigned char secret_signing[32];
    unsigned char signature_bytes[32];
    int size;

    if (tts_sha256(payload, payload_size, digest) != RT_EOK) return -RT_ERROR;
    tts_hex(digest, sizeof(digest), canonical_hash);

    size = rt_snprintf(canonical_request, sizeof(canonical_request),
        "POST\n/\n\ncontent-type:application/json; charset=utf-8\n"
        "host:%s\n\ncontent-type;host\n%s",
        TENCENT_TTS_HOST, canonical_hash);
    if ((size <= 0) || (size >= (int)sizeof(canonical_request)) ||
        (tts_sha256(canonical_request, (rt_size_t)size, digest) != RT_EOK))
        return -RT_ERROR;
    tts_hex(digest, sizeof(digest), canonical_hash);

    size = rt_snprintf(credential_scope, sizeof(credential_scope),
                       "%s/%s/tc3_request", date, TTS_SERVICE);
    if ((size <= 0) || (size >= (int)sizeof(credential_scope))) return -RT_ERROR;

    size = rt_snprintf(string_to_sign, sizeof(string_to_sign),
                       "TC3-HMAC-SHA256\n%ld\n%s\n%s",
                       (long)timestamp, credential_scope, canonical_hash);
    if ((size <= 0) || (size >= (int)sizeof(string_to_sign))) return -RT_ERROR;

    size = rt_snprintf(secret_date_input, sizeof(secret_date_input),
                       "TC3%s", TENCENT_ASR_SECRET_KEY);
    if ((size <= 0) || (size >= (int)sizeof(secret_date_input)) ||
        (tts_hmac_sha256((const unsigned char *)secret_date_input, (rt_size_t)size,
                          date, rt_strlen(date), secret_date) != RT_EOK) ||
        (tts_hmac_sha256(secret_date, sizeof(secret_date),
                          TTS_SERVICE, rt_strlen(TTS_SERVICE), secret_service) != RT_EOK) ||
        (tts_hmac_sha256(secret_service, sizeof(secret_service),
                          "tc3_request", rt_strlen("tc3_request"), secret_signing) != RT_EOK) ||
        (tts_hmac_sha256(secret_signing, sizeof(secret_signing),
                          string_to_sign, rt_strlen(string_to_sign), signature_bytes) != RT_EOK))
        return -RT_ERROR;
    tts_hex(signature_bytes, sizeof(signature_bytes), signature);

    size = rt_snprintf(authorization, authorization_size,
        "TC3-HMAC-SHA256 Credential=%s/%s, SignedHeaders=content-type;host, Signature=%s",
        TENCENT_ASR_SECRET_ID, credential_scope, signature);
    return ((size > 0) && (size < (int)authorization_size)) ? RT_EOK : -RT_ENOMEM;
}

static int tts_read_body(struct webclient_session *session, char *body, rt_size_t body_size)
{
    rt_size_t total = 0;
    int size;
    int content_length = webclient_content_length_get(session);

    while (total < (body_size - 1U))
    {
        rt_size_t remain = body_size - total - 1U;
        if ((content_length >= 0) && ((int)remain > (content_length - (int)total)))
            remain = (rt_size_t)(content_length - (int)total);
        if (remain == 0U) break;
        size = webclient_read(session, body + total, remain);
        if (size <= 0) break;
        total += (rt_size_t)size;
    }
    body[total] = '\0';
    return (total > 0U) ? RT_EOK : -RT_ERROR;
}

static int tts_play_pcm(const rt_uint8_t *pcm, rt_size_t pcm_size)
{
    rt_device_t snd;
    struct rt_audio_caps caps;
    rt_size_t written = 0;
    rt_size_t chunk;
    rt_size_t chunk_samples;
    rt_uint32_t chunk_delay;
    rt_size_t total_samples;
    rt_ssize_t write_size;

    snd = rt_device_find(TTS_AUDIO_DEVICE);
    if (snd == RT_NULL)
    {
        rt_kprintf("tts: sound0 device not found.\r\n");
        return -RT_ERROR;
    }

    if (rt_device_open(snd, RT_DEVICE_OFLAG_WRONLY) != RT_EOK)
    {
        rt_kprintf("tts: failed to open sound0.\r\n");
        return -RT_ERROR;
    }

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_OUTPUT;
    caps.sub_type = AUDIO_DSP_PARAM;
    caps.udata.config.samplerate = TENCENT_TTS_SAMPLE_RATE;
    caps.udata.config.channels = 1;
    caps.udata.config.samplebits = 16;
    if (rt_device_control(snd, AUDIO_CTL_CONFIGURE, &caps) != RT_EOK)
    {
        rt_kprintf("tts: failed to configure sound0 replay.\r\n");
        rt_device_close(snd);
        return -RT_ERROR;
    }

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_MIXER;
    caps.sub_type = AUDIO_MIXER_VOLUME;
    caps.udata.value = AUDIO_VOLUME_MAX;
    if (rt_device_control(snd, AUDIO_CTL_CONFIGURE, &caps) != RT_EOK)
    {
        rt_kprintf("tts: failed to set sound0 volume.\r\n");
        rt_device_close(snd);
        return -RT_ERROR;
    }
    rt_kprintf("tts: volume_set=%u\r\n", (unsigned int)AUDIO_VOLUME_MAX);

    rt_kprintf("tts: playing %u bytes PCM...\r\n", (unsigned int)pcm_size);
    while (written < pcm_size)
    {
        chunk = pcm_size - written;
        if (chunk > TTS_PCM_CHUNK) chunk = TTS_PCM_CHUNK;
        write_size = rt_device_write(snd, 0, pcm + written, chunk);
        if (write_size <= 0)
        {
            rt_kprintf("tts: audio write failed at %u/%u bytes.\r\n",
                       (unsigned int)written, (unsigned int)pcm_size);
            rt_device_close(snd);
            return -RT_ERROR;
        }
        if ((rt_size_t)write_size < chunk)
        {
            chunk = (rt_size_t)write_size;
        }
        written += chunk;
        chunk_samples = chunk / 2U;
        chunk_delay = (rt_uint32_t)(chunk_samples * 1000U / TENCENT_TTS_SAMPLE_RATE);
        rt_thread_mdelay(chunk_delay + 5U);
    }

    total_samples = pcm_size / 2U;
    rt_thread_mdelay(250U);

    rt_kprintf("tts: playback queued %u samples; closing audio device...\r\n",
               (unsigned int)total_samples);
    rt_device_close(snd);
    rt_kprintf("tts: audio device closed.\r\n");
    return RT_EOK;
}

static char *tts_extract_audio_field(char *body, rt_size_t *audio_len)
{
    const char marker[] = "\"Audio\":\"";
    char *start = rt_strstr(body, marker);
    char *end;
    if (start == RT_NULL) return RT_NULL;
    start += sizeof(marker) - 1U;
    end = rt_strstr(start, "\",\"RequestId\"");
    if (end == RT_NULL)
    {
        end = start + rt_strlen(start);
        while ((end > start) && (end[-1] == '\"')) end--;
    }
    *audio_len = (rt_size_t)(end - start);
    return start;
}

static rt_bool_t tts_log_cloud_error(const char *body)
{
    char code[96];
    char message[192];
    rt_bool_t has_error = RT_FALSE;

    if (body == RT_NULL)
    {
        return RT_FALSE;
    }

    code[0] = '\0';
    message[0] = '\0';
    if (json_util_get_path_string(body, "Response.Error.Code",
                                  code, sizeof(code)) == RT_EOK)
    {
        has_error = RT_TRUE;
    }
    if (json_util_get_path_string(body, "Response.Error.Message",
                                  message, sizeof(message)) == RT_EOK)
    {
        has_error = RT_TRUE;
    }

    if (has_error)
    {
        rt_kprintf("tts: Tencent cloud error code=%s\r\n",
                   code[0] ? code : "(none)");
        rt_kprintf("tts: Tencent cloud error message=%s\r\n",
                   message[0] ? message : "(none)");
        rt_kprintf("tts: request used Tencent ASR SecretId/SecretKey with TTS service signing.\r\n");
    }

    return has_error;
}

static int tts_format_x100(int value, char *buffer, rt_size_t buffer_size)
{
    int sign = 1;
    int whole;
    int frac;

    if ((buffer == RT_NULL) || (buffer_size == 0U))
    {
        return -RT_EINVAL;
    }

    if (value < 0)
    {
        sign = -1;
        value = -value;
    }

    whole = value / 100;
    frac = value % 100;
    if (frac == 0)
    {
        return rt_snprintf(buffer, buffer_size, "%s%d",
                           (sign < 0) ? "-" : "",
                           whole);
    }
    if ((frac % 10) == 0)
    {
        return rt_snprintf(buffer, buffer_size, "%s%d.%d",
                           (sign < 0) ? "-" : "",
                           whole, frac / 10);
    }
    return rt_snprintf(buffer, buffer_size, "%s%d.%02d",
                       (sign < 0) ? "-" : "",
                       whole, frac);
}

static int tts_client_speak_once(const char *text, rt_bool_t *retry_after_time_sync)
{
    struct webclient_session *session = RT_NULL;
    char escaped_text[TENCENT_TTS_MAX_TEXT_LEN * 2 + 4];
    char request[TTS_REQUEST_SIZE];
    char authorization[384];
    char date[11];
    char *body = RT_NULL;
    char session_id[48];
    char speed_value[16];
    char volume_value[16];
    const user_preferences_t *prefs = user_preferences_get();
    rt_uint8_t *pcm = RT_NULL;
    rt_size_t body_size;
    int content_length;
    int request_len;
    time_t timestamp;
    struct tm *utc_time;
    int status;
    int ret = -RT_ERROR;
    size_t decoded_len;
    char *audio_ptr;
    rt_size_t audio_len;

    if (retry_after_time_sync != RT_NULL)
    {
        *retry_after_time_sync = RT_FALSE;
    }

    if ((text == RT_NULL) || (text[0] == '\0')) return -RT_EINVAL;

#if defined(RT_WLAN_MANAGE_ENABLE)
    if ((rt_wlan_is_connected() != RT_TRUE) || (rt_wlan_is_ready() != RT_TRUE))
    {
        rt_kprintf("tts: Wi-Fi not ready.\r\n");
        return -RT_ERROR;
    }
#endif

    timestamp = time(RT_NULL);
    if (timestamp < (time_t)1577836800)
    {
        rt_kprintf("tts: RTC time not set; run asr_sync first.\r\n");
        return -RT_ERROR;
    }

    utc_time = gmtime(&timestamp);
    if ((utc_time == RT_NULL) ||
        (strftime(date, sizeof(date), "%Y-%m-%d", utc_time) != 10U))
        return -RT_ERROR;

    if (json_util_escape(text, escaped_text, sizeof(escaped_text)) != RT_EOK)
    {
        rt_kprintf("tts: text too long.\r\n");
        return -RT_ENOMEM;
    }

    rt_snprintf(session_id, sizeof(session_id), "m55-%ld-%u",
                (long)timestamp, (unsigned int)rt_tick_get());
    if ((tts_format_x100(prefs->tts_speed_x100, speed_value, sizeof(speed_value)) <= 0) ||
        (tts_format_x100(TTS_FORCE_VOLUME_X100, volume_value, sizeof(volume_value)) <= 0))
    {
        return -RT_ERROR;
    }
    request_len = rt_snprintf(request, sizeof(request),
        "{\"Text\":\"%s\",\"SessionId\":\"%s\",\"VoiceType\":%d,"
        "\"PrimaryLanguage\":%d,\"SampleRate\":%d,\"Codec\":\"pcm\","
        "\"Speed\":%s,\"Volume\":%s}",
        escaped_text, session_id, USER_PREFS_TTS_SAFE_VOICE_TYPE,
        (int)TENCENT_TTS_PRIMARY_LANGUAGE, (int)TENCENT_TTS_SAMPLE_RATE,
        speed_value, volume_value);
    if ((request_len <= 0) || (request_len >= (int)sizeof(request)))
        return -RT_ENOMEM;

    if (tts_build_authorization(request, (rt_size_t)request_len, timestamp, date,
                                 authorization, sizeof(authorization)) != RT_EOK)
    {
        rt_kprintf("tts: signature build failed.\r\n");
        return -RT_ERROR;
    }

    session = webclient_session_create(TTS_HEADER_SIZE);
    if (session == RT_NULL) return -RT_ENOMEM;

    if (webclient_header_fields_add(session, "Content-Length: %d\r\n", request_len) < 0 ||
        webclient_header_fields_add(session, "Content-Type: application/json; charset=utf-8\r\n") < 0 ||
        webclient_header_fields_add(session, "Host: %s\r\n", TENCENT_TTS_HOST) < 0 ||
        webclient_header_fields_add(session, "X-TC-Action: " TTS_ACTION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Version: " TTS_VERSION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Timestamp: %ld\r\n", (long)timestamp) < 0 ||
        webclient_header_fields_add(session, "Authorization: %s\r\n", authorization) < 0)
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }

    rt_kprintf("tts: requesting synthesis for %u chars...\r\n",
               (unsigned int)rt_strlen(text));
    rt_kprintf("tts: request volume=%s hardware=%u\r\n", volume_value,
               (unsigned int)AUDIO_VOLUME_MAX);
    status = webclient_post(session, TENCENT_TTS_API_URL, request, (rt_size_t)request_len);

    if ((status < 200) || (status >= 300))
    {
        rt_kprintf("tts: HTTP %d.\r\n", status);
    }

    content_length = webclient_content_length_get(session);
    if (content_length <= 0)
    {
        rt_kprintf("tts: empty response.\r\n");
        goto __exit;
    }

    body_size = (rt_size_t)content_length + 1U;
    body = (char *)rt_malloc(body_size);
    if (body == RT_NULL)
    {
        rt_kprintf("tts: insufficient memory for response (%u bytes).\r\n",
                   (unsigned int)body_size);
        goto __exit;
    }

    if (tts_read_body(session, body, body_size) != RT_EOK)
    {
        rt_kprintf("tts: failed to read response body.\r\n");
        goto __exit;
    }

    audio_ptr = tts_extract_audio_field(body, &audio_len);
    if (audio_ptr == RT_NULL || audio_len == 0U)
    {
        if (tts_log_cloud_error(body))
        {
            if ((retry_after_time_sync != RT_NULL) &&
                (speech_client_sync_time_from_response(body) == RT_EOK))
            {
                *retry_after_time_sync = RT_TRUE;
            }
        }
        else
        {
            rt_kprintf("tts: no Audio field in response.\r\n");
        }
        rt_kprintf("tts: response[%u]: %.200s\r\n",
                   (unsigned int)rt_strlen(body),
                   (body[0] != '\0') ? body : "(empty)");
        goto __exit;
    }

    rt_kprintf("tts: Audio field is %u base64 chars.\r\n", (unsigned int)audio_len);

    pcm = (rt_uint8_t *)rt_malloc(body_size);
    if ((pcm == RT_NULL) ||
        (mbedtls_base64_decode(pcm, body_size, &decoded_len,
                               (const unsigned char *)audio_ptr,
                               audio_len) != 0))
    {
        rt_kprintf("tts: base64 decode failed.\r\n");
        goto __exit;
    }

    rt_kprintf("tts: decoded %u bytes PCM.\r\n", (unsigned int)decoded_len);
    if (session != RT_NULL)
    {
        webclient_close(session);
        session = RT_NULL;
        rt_kprintf("tts: network session closed before playback.\r\n");
    }
    if (body != RT_NULL)
    {
        rt_free(body);
        body = RT_NULL;
    }

    ret = tts_play_pcm(pcm, (rt_size_t)decoded_len);

__exit:
    if (pcm != RT_NULL) rt_free(pcm);
    if (body != RT_NULL) rt_free(body);
    if (session != RT_NULL) webclient_close(session);
    return ret;
}

int tts_client_speak(const char *text)
{
    rt_bool_t retry_after_time_sync = RT_FALSE;
    int ret;

    ret = tts_client_speak_once(text, &retry_after_time_sync);
    if ((ret != RT_EOK) && retry_after_time_sync)
    {
        rt_kprintf("tts: SignatureExpire corrected RTC; retrying once with synchronized RTC.\r\n");
        ret = tts_client_speak_once(text, RT_NULL);
    }
    return ret;
}

#else
int tts_client_speak(const char *text)
{
    (void)text;
    rt_kprintf("tts: enable WebClient and mbedTLS first.\r\n");
    return -RT_ENOSYS;
}
#endif

static void tts_cli_worker_entry(void *parameter)
{
    int ret;

    (void)parameter;
    while (1)
    {
        ret = tts_client_speak(s_tts_cli_text);
        if (ret != RT_EOK && ret != -RT_ENOSYS)
        {
            rt_kprintf("tts: synthesis failed.\r\n");
        }

        if (tts_cli_lock_take() != RT_EOK)
        {
            s_tts_cli_busy = RT_FALSE;
            return;
        }

        if (s_tts_cli_pending)
        {
            rt_strncpy(s_tts_cli_text, s_tts_cli_pending_text, sizeof(s_tts_cli_text) - 1U);
            s_tts_cli_text[sizeof(s_tts_cli_text) - 1U] = '\0';
            s_tts_cli_pending = RT_FALSE;
            s_tts_cli_pending_text[0] = '\0';
            tts_cli_lock_release();
            rt_kprintf("tts: starting queued synthesis task.\r\n");
            continue;
        }

        s_tts_cli_busy = RT_FALSE;
        tts_cli_lock_release();
        rt_kprintf("tts: TTS worker finished.\r\n");
        break;
    }
}

int tts_client_speak_async(const char *text)
{
    rt_thread_t worker;
    int ret;

    if ((text == RT_NULL) || (text[0] == '\0'))
    {
        return -RT_EINVAL;
    }

    ret = tts_cli_lock_take();
    if (ret != RT_EOK)
    {
        return ret;
    }

    if (s_tts_cli_busy)
    {
        rt_strncpy(s_tts_cli_pending_text, text, sizeof(s_tts_cli_pending_text) - 1U);
        s_tts_cli_pending_text[sizeof(s_tts_cli_pending_text) - 1U] = '\0';
        s_tts_cli_pending = RT_TRUE;
        tts_cli_lock_release();
        rt_kprintf("tts: another synthesis task is running; queued latest text.\r\n");
        return RT_EOK;
    }

    rt_strncpy(s_tts_cli_text, text, sizeof(s_tts_cli_text) - 1U);
    s_tts_cli_text[sizeof(s_tts_cli_text) - 1U] = '\0';
    s_tts_cli_pending = RT_FALSE;
    s_tts_cli_pending_text[0] = '\0';
    s_tts_cli_busy = RT_TRUE;
    tts_cli_lock_release();

    worker = rt_thread_create("ttswork", tts_cli_worker_entry, RT_NULL,
                              TTS_CLI_THREAD_STACK_SIZE,
                              TTS_CLI_THREAD_PRIORITY,
                              TTS_CLI_THREAD_TICK);
    if (worker == RT_NULL)
    {
        if (tts_cli_lock_take() == RT_EOK)
        {
            s_tts_cli_busy = RT_FALSE;
            tts_cli_lock_release();
        }
        rt_kprintf("tts: unable to create TTS worker thread.\r\n");
        return -RT_ENOMEM;
    }

    rt_kprintf("tts: TTS worker started with %u-byte stack.\r\n",
               (unsigned int)TTS_CLI_THREAD_STACK_SIZE);

    if (rt_thread_startup(worker) != RT_EOK)
    {
        if (tts_cli_lock_take() == RT_EOK)
        {
            s_tts_cli_busy = RT_FALSE;
            tts_cli_lock_release();
        }
        rt_thread_delete(worker);
        rt_kprintf("tts: failed to start TTS worker thread.\r\n");
        return -RT_ERROR;
    }

    return RT_EOK;
}

#ifdef RT_USING_MSH
static int tts_test(int argc, char **argv)
{
    char text[TENCENT_TTS_MAX_TEXT_LEN + 1] = {0};
    int i;
    rt_size_t used = 0;
    int written;

    if (argc < 2)
    {
        rt_kprintf("Usage: tts_test <text>\r\n");
        return -RT_EINVAL;
    }

    for (i = 1; i < argc; i++)
    {
        written = rt_snprintf(text + used, sizeof(text) - used,
                              "%s%s", (i == 1) ? "" : " ", argv[i]);
        if ((written < 0) || ((rt_size_t)written >= (sizeof(text) - used)))
            break;
        used += (rt_size_t)written;
    }

    return tts_client_speak_async(text);
}
MSH_CMD_EXPORT(tts_test, Synthesize speech from text: tts_test <text>);
#endif
