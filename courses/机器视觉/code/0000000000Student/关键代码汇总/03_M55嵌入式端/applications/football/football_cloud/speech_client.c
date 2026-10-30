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

#if defined(RT_USING_AUDIO)
#include <drivers/audio.h>
#endif

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

#define TENCENT_SECRET_ID_PLACEHOLDER  "REDACTED_CONFIGURE_LOCALLY"
#define TENCENT_SECRET_KEY_PLACEHOLDER "REDACTED_CONFIGURE_LOCALLY"
#define TENCENT_ASR_SERVICE             "asr"
#define TENCENT_ASR_ACTION              "SentenceRecognition"
#define TENCENT_ASR_VERSION             "2019-06-14"
#define SPEECH_CHANNELS            1U
#define SPEECH_SAMPLE_BITS         16U
#define SPEECH_WAV_HEADER_SIZE     44U
#define SPEECH_BYTES_PER_SECOND    ((rt_size_t)SPEECH_SAMPLE_RATE * SPEECH_CHANNELS * \
                                    (SPEECH_SAMPLE_BITS / 8U))
#define SPEECH_PRESS_MAX_SECONDS   8U
#define SPEECH_PRESS_MIN_MS        250U
#define SPEECH_MAX_TEST_SECONDS    8U
#define SPEECH_CAPTURE_IDLE_TIMEOUT_MS 1500U
#define SPEECH_CLI_THREAD_STACK_SIZE   16384U
#define SPEECH_CLI_THREAD_PRIORITY     18U
#define SPEECH_CLI_THREAD_TICK         10U

static volatile rt_bool_t s_press_to_talk_stop = RT_FALSE;
static rt_bool_t s_cloud_time_checked = RT_FALSE;

static int speech_update_rtc_from_timestamp(time_t timestamp)
{
#if defined(RT_USING_RTC)
    if (timestamp < (time_t)1577836800)
    {
        return -RT_EINVAL;
    }
    if (set_timestamp(timestamp) != RT_EOK)
    {
        rt_kprintf("speech: failed to update RTC timestamp.\r\n");
        return -RT_ERROR;
    }
    rt_kprintf("speech: RTC updated to server timestamp %ld; retry transcription.\r\n",
               (long)timestamp);
    return RT_EOK;
#else
    (void)timestamp;
    return -RT_ENOSYS;
#endif
}

static int speech_update_rtc_from_signature_error(const char *body)
{
    const char marker[] = "server time ";
    const char *start;
    char *end;
    long timestamp;

    start = rt_strstr(body, marker);
    if (start == RT_NULL)
    {
        return -RT_ERROR;
    }
    start += sizeof(marker) - 1U;
    timestamp = strtol(start, &end, 10);
    if ((end == start) || (timestamp <= 0L))
    {
        return -RT_ERROR;
    }
    return speech_update_rtc_from_timestamp((time_t)timestamp);
}

int speech_client_sync_time_from_response(const char *body)
{
    int ret;

    if (body == RT_NULL)
    {
        return -RT_EINVAL;
    }

    ret = speech_update_rtc_from_signature_error(body);
    if (ret == RT_EOK)
    {
        s_cloud_time_checked = RT_TRUE;
    }
    return ret;
}

static void speech_put_u16(rt_uint8_t *dst, rt_uint16_t value)
{
    dst[0] = (rt_uint8_t)(value & 0xffU);
    dst[1] = (rt_uint8_t)((value >> 8) & 0xffU);
}

static void speech_put_u32(rt_uint8_t *dst, rt_uint32_t value)
{
    dst[0] = (rt_uint8_t)(value & 0xffU);
    dst[1] = (rt_uint8_t)((value >> 8) & 0xffU);
    dst[2] = (rt_uint8_t)((value >> 16) & 0xffU);
    dst[3] = (rt_uint8_t)((value >> 24) & 0xffU);
}

static void speech_write_wav_header(rt_uint8_t *wav, rt_size_t pcm_size)
{
    rt_memcpy(wav, "RIFF", 4);
    speech_put_u32(wav + 4, (rt_uint32_t)(36U + pcm_size));
    rt_memcpy(wav + 8, "WAVEfmt ", 8);
    speech_put_u32(wav + 16, 16U);
    speech_put_u16(wav + 20, 1U);
    speech_put_u16(wav + 22, SPEECH_CHANNELS);
    speech_put_u32(wav + 24, SPEECH_SAMPLE_RATE);
    speech_put_u32(wav + 28, SPEECH_SAMPLE_RATE * SPEECH_CHANNELS * (SPEECH_SAMPLE_BITS / 8U));
    speech_put_u16(wav + 32, SPEECH_CHANNELS * (SPEECH_SAMPLE_BITS / 8U));
    speech_put_u16(wav + 34, SPEECH_SAMPLE_BITS);
    rt_memcpy(wav + 36, "data", 4);
    speech_put_u32(wav + 40, (rt_uint32_t)pcm_size);
}

#if defined(RT_USING_AUDIO)
static int speech_configure_and_open_mic(rt_device_t *mic_out)
{
    struct rt_audio_caps caps;
    rt_device_t mic;

    mic = rt_device_find("mic0");
    if (mic == RT_NULL)
    {
        rt_kprintf("speech: microphone device mic0 is not available.\r\n");
        return -RT_ERROR;
    }

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_INPUT;
    caps.sub_type = AUDIO_DSP_PARAM;
    caps.udata.config.samplerate = SPEECH_SAMPLE_RATE;
    caps.udata.config.channels = SPEECH_CHANNELS;
    caps.udata.config.samplebits = SPEECH_SAMPLE_BITS;
    if (rt_device_control(mic, AUDIO_CTL_CONFIGURE, &caps) != RT_EOK)
    {
        rt_kprintf("speech: failed to configure mic0.\r\n");
        return -RT_ERROR;
    }

    if (rt_device_open(mic, RT_DEVICE_OFLAG_RDONLY) != RT_EOK)
    {
        rt_kprintf("speech: failed to open mic0.\r\n");
        return -RT_ERROR;
    }

    *mic_out = mic;
    return RT_EOK;
}

static int speech_record_pcm(rt_uint8_t *pcm, rt_size_t pcm_size)
{
    rt_device_t mic;
    rt_size_t received = 0;
    rt_size_t progress_size = SPEECH_BYTES_PER_SECOND;
    rt_tick_t last_data_tick;
    rt_ssize_t size;

    if (speech_configure_and_open_mic(&mic) != RT_EOK)
    {
        return -RT_ERROR;
    }

    last_data_tick = rt_tick_get();
    while (received < pcm_size)
    {
        size = rt_device_read(mic, 0, pcm + received, pcm_size - received);
        if (size <= 0)
        {
            if ((rt_tick_get() - last_data_tick) >=
                rt_tick_from_millisecond(SPEECH_CAPTURE_IDLE_TIMEOUT_MS))
            {
                rt_kprintf("speech: microphone capture stalled after %u bytes.\r\n",
                           (unsigned int)received);
                rt_device_close(mic);
                return -RT_ETIMEOUT;
            }
            rt_thread_mdelay(10);
            continue;
        }
        received += (rt_size_t)size;
        last_data_tick = rt_tick_get();
        if (received >= progress_size)
        {
            progress_size += SPEECH_BYTES_PER_SECOND;
        }
    }
    rt_device_close(mic);
    return RT_EOK;
}

static int speech_record_pcm_press_to_talk(rt_uint8_t *pcm, rt_size_t max_size,
                                           rt_size_t *captured_size)
{
    const rt_size_t min_size = (SPEECH_BYTES_PER_SECOND * SPEECH_PRESS_MIN_MS) / 1000U;
    rt_device_t mic;
    rt_size_t received = 0;
    rt_tick_t last_data_tick;
    rt_ssize_t size;

    if (speech_configure_and_open_mic(&mic) != RT_EOK)
    {
        return -RT_ERROR;
    }

    last_data_tick = rt_tick_get();
    while (received < max_size)
    {
        size = rt_device_read(mic, 0, pcm + received, max_size - received);
        if (size <= 0)
        {
            if ((rt_tick_get() - last_data_tick) >=
                rt_tick_from_millisecond(SPEECH_CAPTURE_IDLE_TIMEOUT_MS))
            {
                rt_kprintf("speech: microphone capture stalled after %u bytes.\r\n",
                           (unsigned int)received);
                rt_device_close(mic);
                return -RT_ETIMEOUT;
            }
            rt_thread_mdelay(10);
            continue;
        }
        received += (rt_size_t)size;
        last_data_tick = rt_tick_get();
        if (s_press_to_talk_stop && (received >= min_size))
        {
            break;
        }
    }
    rt_device_close(mic);
    *captured_size = received;
    return (received > 0U) ? RT_EOK : -RT_ERROR;
}
#endif /* RT_USING_AUDIO */

#if defined(PKG_USING_WEBCLIENT) && defined(RT_USING_AUDIO) && defined(PKG_USING_MBEDTLS)
static int speech_sha256(const char *data, rt_size_t size, unsigned char output[32])
{
    return (mbedtls_sha256_ret((const unsigned char *)data, size, output, 0) == 0) ?
           RT_EOK : -RT_ERROR;
}

static int speech_hmac_sha256(const unsigned char *key, rt_size_t key_size,
                              const char *data, rt_size_t data_size,
                              unsigned char output[32])
{
    const mbedtls_md_info_t *md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);

    if (md_info == RT_NULL)
    {
        return -RT_ERROR;
    }
    return (mbedtls_md_hmac(md_info, key, key_size,
                            (const unsigned char *)data, data_size, output) == 0) ?
           RT_EOK : -RT_ERROR;
}

static void speech_hex(const unsigned char *input, rt_size_t size, char *output)
{
    static const char hex[] = "0123456789abcdef";
    rt_size_t index;

    for (index = 0; index < size; index++)
    {
        output[index * 2U] = hex[input[index] >> 4];
        output[index * 2U + 1U] = hex[input[index] & 0x0fU];
    }
    output[size * 2U] = '\0';
}

static int speech_build_authorization(const char *payload, rt_size_t payload_size,
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

    if (speech_sha256(payload, payload_size, digest) != RT_EOK)
    {
        return -RT_ERROR;
    }
    speech_hex(digest, sizeof(digest), canonical_hash);

    size = rt_snprintf(canonical_request, sizeof(canonical_request),
        "POST\n/\n\ncontent-type:application/json; charset=utf-8\n"
        "host:%s\n\ncontent-type;host\n%s",
        TENCENT_ASR_HOST, canonical_hash);
    if ((size <= 0) || (size >= (int)sizeof(canonical_request)) ||
        (speech_sha256(canonical_request, (rt_size_t)size, digest) != RT_EOK))
    {
        return -RT_ERROR;
    }
    speech_hex(digest, sizeof(digest), canonical_hash);

    size = rt_snprintf(credential_scope, sizeof(credential_scope),
                       "%s/%s/tc3_request", date, TENCENT_ASR_SERVICE);
    if ((size <= 0) || (size >= (int)sizeof(credential_scope)))
    {
        return -RT_ERROR;
    }
    size = rt_snprintf(string_to_sign, sizeof(string_to_sign),
                       "TC3-HMAC-SHA256\n%ld\n%s\n%s",
                       (long)timestamp, credential_scope, canonical_hash);
    if ((size <= 0) || (size >= (int)sizeof(string_to_sign)))
    {
        return -RT_ERROR;
    }

    size = rt_snprintf(secret_date_input, sizeof(secret_date_input),
                       "TC3%s", TENCENT_ASR_SECRET_KEY);
    if ((size <= 0) || (size >= (int)sizeof(secret_date_input)) ||
        (speech_hmac_sha256((const unsigned char *)secret_date_input, (rt_size_t)size,
                            date, rt_strlen(date), secret_date) != RT_EOK) ||
        (speech_hmac_sha256(secret_date, sizeof(secret_date),
                            TENCENT_ASR_SERVICE, rt_strlen(TENCENT_ASR_SERVICE),
                            secret_service) != RT_EOK) ||
        (speech_hmac_sha256(secret_service, sizeof(secret_service),
                            "tc3_request", rt_strlen("tc3_request"),
                            secret_signing) != RT_EOK) ||
        (speech_hmac_sha256(secret_signing, sizeof(secret_signing),
                            string_to_sign, rt_strlen(string_to_sign),
                            signature_bytes) != RT_EOK))
    {
        return -RT_ERROR;
    }
    speech_hex(signature_bytes, sizeof(signature_bytes), signature);

    size = rt_snprintf(authorization, authorization_size,
        "TC3-HMAC-SHA256 Credential=%s/%s, SignedHeaders=content-type;host, Signature=%s",
        TENCENT_ASR_SECRET_ID, credential_scope, signature);
    return ((size > 0) && (size < (int)authorization_size)) ? RT_EOK : -RT_ENOMEM;
}

static int speech_read_body(struct webclient_session *session, char *body, rt_size_t body_size)
{
    rt_size_t total = 0;
    int size;
    int content_length = webclient_content_length_get(session);

    while (total < (body_size - 1U))
    {
        rt_size_t remain = body_size - total - 1U;
        if ((content_length >= 0) && ((int)remain > (content_length - (int)total)))
        {
            remain = (rt_size_t)(content_length - (int)total);
        }
        if (remain == 0U)
        {
            break;
        }
        size = webclient_read(session, body + total, remain);
        if (size <= 0)
        {
            break;
        }
        total += (rt_size_t)size;
    }
    body[total] = '\0';
    return (total > 0U) ? RT_EOK : -RT_ERROR;
}

int speech_client_sync_time(void)
{
    static const char probe_payload[] = "{}";
    struct webclient_session *session = RT_NULL;
    char authorization[384];
    char date[11];
    char body[SPEECH_RESPONSE_BUFFER_SIZE];
    time_t timestamp;
    struct tm *utc_time;
    int status;
    int ret = -RT_ERROR;

    if (s_cloud_time_checked)
    {
        return RT_EOK;
    }
#if defined(RT_WLAN_MANAGE_ENABLE)
    if ((rt_wlan_is_connected() != RT_TRUE) || (rt_wlan_is_ready() != RT_TRUE))
    {
        return -RT_ERROR;
    }
#endif
    timestamp = time(RT_NULL);
    utc_time = gmtime(&timestamp);
    if ((utc_time == RT_NULL) ||
        (strftime(date, sizeof(date), "%Y-%m-%d", utc_time) != 10U) ||
        (speech_build_authorization(probe_payload, sizeof(probe_payload) - 1U,
                                    timestamp, date, authorization,
                                    sizeof(authorization)) != RT_EOK))
    {
        return -RT_ERROR;
    }
    session = webclient_session_create(LLM_HEADER_BUFFER_SIZE);
    if (session == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    if (webclient_header_fields_add(session, "Content-Length: %u\r\n",
                                    (unsigned int)(sizeof(probe_payload) - 1U)) < 0 ||
        webclient_header_fields_add(session, "Content-Type: application/json; charset=utf-8\r\n") < 0 ||
        webclient_header_fields_add(session, "Host: %s\r\n", TENCENT_ASR_HOST) < 0 ||
        webclient_header_fields_add(session, "X-TC-Action: " TENCENT_ASR_ACTION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Version: " TENCENT_ASR_VERSION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Region: %s\r\n", TENCENT_ASR_REGION) < 0 ||
        webclient_header_fields_add(session, "X-TC-Timestamp: %ld\r\n", (long)timestamp) < 0 ||
        webclient_header_fields_add(session, "Authorization: %s\r\n", authorization) < 0)
    {
        goto __exit;
    }
    status = webclient_post(session, TENCENT_ASR_API_URL,
                            probe_payload, sizeof(probe_payload) - 1U);
    if ((status < 200) || (status >= 300) ||
        (speech_read_body(session, body, sizeof(body)) != RT_EOK))
    {
        goto __exit;
    }
    if (speech_client_sync_time_from_response(body) == RT_EOK)
    {
        s_cloud_time_checked = RT_TRUE;
        ret = RT_EOK;
        goto __exit;
    }
    if (rt_strstr(body, "SignatureExpire") == RT_NULL)
    {
        s_cloud_time_checked = RT_TRUE;
        ret = RT_EOK;
    }

__exit:
    if (session != RT_NULL)
    {
        webclient_close(session);
    }
    return ret;
}

static int speech_client_transcribe_capture(char *text, rt_size_t text_size,
                                            rt_uint32_t seconds, rt_bool_t press_to_talk)
{
    struct webclient_session *session = RT_NULL;
    char authorization[384];
    char date[11];
    char body[SPEECH_RESPONSE_BUFFER_SIZE];
    char audio_key[48];
    char *encoded_audio = RT_NULL;
    char *request = RT_NULL;
    rt_uint8_t *wav = RT_NULL;
    rt_size_t max_pcm_size;
    rt_size_t pcm_size;
    rt_size_t wav_size;
    rt_size_t encoded_size;
    rt_size_t request_capacity;
    rt_size_t request_size;
    size_t encoded_written = 0;
    time_t timestamp;
    struct tm *utc_time;
    int status;
    int ret = -RT_ERROR;

    if ((text == RT_NULL) || (text_size == 0U))
    {
        return -RT_EINVAL;
    }
    text[0] = '\0';
    if ((TENCENT_ASR_API_URL[0] == '\0') ||
        (TENCENT_ASR_SECRET_ID[0] == '\0') ||
        (TENCENT_ASR_SECRET_KEY[0] == '\0') ||
        (rt_strcmp(TENCENT_ASR_SECRET_ID, TENCENT_SECRET_ID_PLACEHOLDER) == 0) ||
        (rt_strcmp(TENCENT_ASR_SECRET_KEY, TENCENT_SECRET_KEY_PLACEHOLDER) == 0))
    {
        rt_kprintf("speech: configure Tencent ASR SecretId and SecretKey first.\r\n");
        return -RT_ENOSYS;
    }
    if (rt_strncmp(TENCENT_ASR_API_URL, "https://", 8) != 0)
    {
        return -RT_EINVAL;
    }
#if defined(RT_WLAN_MANAGE_ENABLE)
    if ((rt_wlan_is_connected() != RT_TRUE) || (rt_wlan_is_ready() != RT_TRUE))
    {
        rt_kprintf("speech: Wi-Fi is not connected or ready.\r\n");
        return -RT_ERROR;
    }
#endif
    if (speech_client_sync_time() != RT_EOK)
    {
        rt_kprintf("speech: unable to confirm cloud time before recording.\r\n");
        return -RT_ERROR;
    }

    timestamp = time(RT_NULL);
    if (timestamp < (time_t)1577836800)
    {
        rt_kprintf("speech: set or synchronize RTC time before Tencent ASR authentication.\r\n");
        return -RT_ERROR;
    }
    utc_time = gmtime(&timestamp);
    if ((utc_time == RT_NULL) ||
        (strftime(date, sizeof(date), "%Y-%m-%d", utc_time) != 10U))
    {
        return -RT_ERROR;
    }

    max_pcm_size = SPEECH_BYTES_PER_SECOND *
                   (press_to_talk ? SPEECH_PRESS_MAX_SECONDS : seconds);
    wav = (rt_uint8_t *)rt_malloc(SPEECH_WAV_HEADER_SIZE + max_pcm_size);
    if (wav == RT_NULL)
    {
        rt_kprintf("speech: insufficient memory for audio buffer.\r\n");
        return -RT_ENOMEM;
    }
    if (press_to_talk)
    {
        if (speech_record_pcm_press_to_talk(wav + SPEECH_WAV_HEADER_SIZE,
                                            max_pcm_size, &pcm_size) != RT_EOK)
        {
            goto __exit;
        }
    }
    else
    {
        pcm_size = max_pcm_size;
        if (speech_record_pcm(wav + SPEECH_WAV_HEADER_SIZE, pcm_size) != RT_EOK)
        {
            goto __exit;
        }
    }
    wav_size = SPEECH_WAV_HEADER_SIZE + pcm_size;
    speech_write_wav_header(wav, pcm_size);

    encoded_size = ((wav_size + 2U) / 3U) * 4U + 1U;
    encoded_audio = (char *)rt_malloc(encoded_size);
    if (encoded_audio == RT_NULL ||
        mbedtls_base64_encode((unsigned char *)encoded_audio, encoded_size,
                              &encoded_written, wav, wav_size) != 0)
    {
        rt_kprintf("speech: failed to encode captured audio.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }
    encoded_audio[encoded_written] = '\0';
    rt_snprintf(audio_key, sizeof(audio_key), "m55-%ld-%u",
                (long)timestamp, (unsigned int)rt_tick_get());

    request_capacity = (rt_size_t)encoded_written + 320U;
    request = (char *)rt_malloc(request_capacity);
    if (request == RT_NULL)
    {
        rt_kprintf("speech: insufficient memory for ASR request payload.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }
    status = rt_snprintf(request, request_capacity,
        "{\"ProjectId\":0,\"SubServiceType\":2,\"EngSerViceType\":\"%s\","
        "\"SourceType\":1,\"VoiceFormat\":\"wav\",\"UsrAudioKey\":\"%s\","
        "\"Data\":\"%s\",\"DataLen\":%u}",
        TENCENT_ASR_ENGINE_TYPE, audio_key, encoded_audio,
        (unsigned int)wav_size);
    if ((status <= 0) || (status >= (int)request_capacity))
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }
    request_size = (rt_size_t)status;

    if (speech_build_authorization(request, request_size, timestamp, date,
                                   authorization, sizeof(authorization)) != RT_EOK)
    {
        rt_kprintf("speech: failed to create Tencent ASR authorization.\r\n");
        goto __exit;
    }

    session = webclient_session_create(LLM_HEADER_BUFFER_SIZE);
    if (session == RT_NULL)
    {
        rt_kprintf("speech: failed to create HTTP session.\r\n");
        ret = -RT_ENOMEM;
        goto __exit;
    }
    if (webclient_header_fields_add(session, "Content-Length: %u\r\n", (unsigned int)request_size) < 0 ||
        webclient_header_fields_add(session, "Content-Type: application/json; charset=utf-8\r\n") < 0 ||
        webclient_header_fields_add(session, "Host: %s\r\n", TENCENT_ASR_HOST) < 0 ||
        webclient_header_fields_add(session, "X-TC-Action: " TENCENT_ASR_ACTION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Version: " TENCENT_ASR_VERSION "\r\n") < 0 ||
        webclient_header_fields_add(session, "X-TC-Region: %s\r\n", TENCENT_ASR_REGION) < 0 ||
        webclient_header_fields_add(session, "X-TC-Timestamp: %ld\r\n", (long)timestamp) < 0 ||
        webclient_header_fields_add(session, "Authorization: %s\r\n", authorization) < 0)
    {
        ret = -RT_ENOMEM;
        goto __exit;
    }

    status = webclient_post(session, TENCENT_ASR_API_URL, request, request_size);
    if ((status < 200) || (status >= 300))
    {
        rt_kprintf("speech: transcription HTTP status %d.\r\n", status);
        if (speech_read_body(session, body, sizeof(body)) == RT_EOK)
        {
            rt_kprintf("speech: HTTP response: %s\r\n", body);
        }
        goto __exit;
    }
    if (speech_read_body(session, body, sizeof(body)) != RT_EOK)
    {
        rt_kprintf("speech: Tencent ASR response body is empty.\r\n");
        goto __exit;
    }
    if (json_util_get_string(body, "Result", text, text_size) != RT_EOK)
    {
        rt_kprintf("speech: Tencent ASR response has no Result field: %s\r\n", body);
        speech_update_rtc_from_signature_error(body);
        goto __exit;
    }
    ret = RT_EOK;

__exit:
    if (session != RT_NULL)
    {
        webclient_close(session);
    }
    if (request != RT_NULL)
    {
        rt_free(request);
    }
    if (encoded_audio != RT_NULL)
    {
        rt_free(encoded_audio);
    }
    if (wav != RT_NULL)
    {
        rt_free(wav);
    }
    return ret;
}

int speech_client_transcribe(char *text, rt_size_t text_size)
{
    return speech_client_transcribe_seconds(text, text_size, SPEECH_RECORD_SECONDS);
}

int speech_client_transcribe_seconds(char *text, rt_size_t text_size, rt_uint32_t seconds)
{
    if ((seconds == 0U) || (seconds > SPEECH_MAX_TEST_SECONDS))
    {
        rt_kprintf("speech: recording seconds must be between 1 and %u.\r\n",
                   (unsigned int)SPEECH_MAX_TEST_SECONDS);
        return -RT_EINVAL;
    }
    return speech_client_transcribe_capture(text, text_size, seconds, RT_FALSE);
}

void speech_client_press_to_talk_begin(void)
{
    s_press_to_talk_stop = RT_FALSE;
}

void speech_client_press_to_talk_end(void)
{
    s_press_to_talk_stop = RT_TRUE;
}

int speech_client_transcribe_press_to_talk(char *text, rt_size_t text_size)
{
    return speech_client_transcribe_capture(text, text_size, 0U, RT_TRUE);
}
#else
int speech_client_sync_time(void)
{
    return -RT_ENOSYS;
}

int speech_client_sync_time_from_response(const char *body)
{
    (void)body;
    return -RT_ENOSYS;
}

int speech_client_transcribe(char *text, rt_size_t text_size)
{
    (void)text;
    (void)text_size;
    rt_kprintf("speech: enable audio recording and WebClient first.\r\n");
    return -RT_ERROR;
}

int speech_client_transcribe_seconds(char *text, rt_size_t text_size, rt_uint32_t seconds)
{
    (void)seconds;
    return speech_client_transcribe(text, text_size);
}

void speech_client_press_to_talk_begin(void)
{
}

void speech_client_press_to_talk_end(void)
{
}

int speech_client_transcribe_press_to_talk(char *text, rt_size_t text_size)
{
    return speech_client_transcribe(text, text_size);
}
#endif /* PKG_USING_WEBCLIENT && RT_USING_AUDIO && PKG_USING_MBEDTLS */

#ifdef RT_USING_MSH
typedef enum
{
    SPEECH_CLI_JOB_TRANSCRIBE = 0,
    SPEECH_CLI_JOB_SYNC
} speech_cli_job_t;

typedef struct
{
    speech_cli_job_t job;
    rt_uint32_t seconds;
} speech_cli_request_t;

static volatile rt_bool_t s_cli_job_running = RT_FALSE;
static speech_cli_request_t s_cli_request;

static void speech_cli_worker_entry(void *parameter)
{
    speech_cli_request_t request = s_cli_request;
    char text[256];
    rt_base_t level;
    int ret;

    (void)parameter;
    if (request.job == SPEECH_CLI_JOB_SYNC)
    {
        ret = speech_client_sync_time();
        rt_kprintf("asr: cloud time synchronization %s.\r\n",
                   (ret == RT_EOK) ? "complete" : "failed");
    }
    else
    {
        ret = speech_client_transcribe_seconds(text, sizeof(text), request.seconds);
        if (ret == RT_EOK)
        {
            rt_kprintf("speech: %s\r\n", text);
        }
        else
        {
            rt_kprintf("speech: transcription failed; review the preceding stage message.\r\n");
        }
    }

    level = rt_hw_interrupt_disable();
    s_cli_job_running = RT_FALSE;
    rt_hw_interrupt_enable(level);
}

static int speech_cli_start(speech_cli_job_t job, rt_uint32_t seconds)
{
    rt_thread_t worker;
    rt_base_t level;
    int ret;

    level = rt_hw_interrupt_disable();
    if (s_cli_job_running)
    {
        rt_hw_interrupt_enable(level);
        rt_kprintf("speech: another ASR task is already running.\r\n");
        return -RT_ERROR;
    }
    s_cli_job_running = RT_TRUE;
    s_cli_request.job = job;
    s_cli_request.seconds = seconds;
    rt_hw_interrupt_enable(level);

    worker = rt_thread_create("asrwork", speech_cli_worker_entry, RT_NULL,
                              SPEECH_CLI_THREAD_STACK_SIZE,
                              SPEECH_CLI_THREAD_PRIORITY,
                              SPEECH_CLI_THREAD_TICK);
    if (worker == RT_NULL)
    {
        level = rt_hw_interrupt_disable();
        s_cli_job_running = RT_FALSE;
        rt_hw_interrupt_enable(level);
        rt_kprintf("speech: unable to create ASR worker thread.\r\n");
        return -RT_ENOMEM;
    }
    rt_kprintf("speech: ASR worker started with %u-byte stack.\r\n",
               (unsigned int)SPEECH_CLI_THREAD_STACK_SIZE);
    ret = rt_thread_startup(worker);
    if (ret != RT_EOK)
    {
        level = rt_hw_interrupt_disable();
        s_cli_job_running = RT_FALSE;
        rt_hw_interrupt_enable(level);
        rt_thread_delete(worker);
        rt_kprintf("speech: failed to start ASR worker thread.\r\n");
    }
    return ret;
}

static int voice_test(int argc, char **argv)
{
    rt_uint32_t seconds = SPEECH_RECORD_SECONDS;

    if (argc > 1)
    {
        seconds = (rt_uint32_t)atoi(argv[1]);
    }
    if ((seconds == 0U) || (seconds > SPEECH_MAX_TEST_SECONDS))
    {
        rt_kprintf("Usage: voice_test [seconds:1-%u]\r\n",
                   (unsigned int)SPEECH_MAX_TEST_SECONDS);
        return -RT_EINVAL;
    }
    return speech_cli_start(SPEECH_CLI_JOB_TRANSCRIBE, seconds);
}

#if defined(RT_USING_AUDIO)
static int mic_test(int argc, char **argv)
{
    rt_uint8_t *pcm;
    rt_uint32_t seconds = 1U;
    rt_size_t pcm_size;
    rt_size_t index;
    rt_uint64_t sum = 0;
    rt_uint16_t peak = 0;
    rt_int16_t sample;
    rt_uint16_t level;

    if (argc > 1)
    {
        seconds = (rt_uint32_t)atoi(argv[1]);
    }
    if ((seconds == 0U) || (seconds > SPEECH_MAX_TEST_SECONDS))
    {
        rt_kprintf("Usage: mic_test [seconds:1-%u]\r\n", (unsigned int)SPEECH_MAX_TEST_SECONDS);
        return -RT_EINVAL;
    }
    pcm_size = SPEECH_BYTES_PER_SECOND * seconds;
    pcm = (rt_uint8_t *)rt_malloc(pcm_size);
    if (pcm == RT_NULL)
    {
        rt_kprintf("mic: insufficient memory.\r\n");
        return -RT_ENOMEM;
    }
    rt_kprintf("mic: recording %u second(s) from mic0...\r\n", (unsigned int)seconds);
    if (speech_record_pcm(pcm, pcm_size) == RT_EOK)
    {
        for (index = 0; index < pcm_size; index += 2U)
        {
            sample = (rt_int16_t)((rt_uint16_t)pcm[index] | ((rt_uint16_t)pcm[index + 1U] << 8));
            level = (sample < 0) ? (rt_uint16_t)(-sample) : (rt_uint16_t)sample;
            sum += level;
            if (level > peak)
            {
                peak = level;
            }
        }
        rt_kprintf("mic: captured %u bytes, average=%u, peak=%u.\r\n",
                   (unsigned int)pcm_size,
                   (unsigned int)(sum / (pcm_size / 2U)),
                   (unsigned int)peak);
        rt_free(pcm);
        return RT_EOK;
    }
    rt_free(pcm);
    return -RT_ERROR;
}

static int asr_check(int argc, char **argv)
{
    rt_device_t mic;
    time_t timestamp;
    rt_bool_t ready = RT_TRUE;

    (void)argc;
    (void)argv;
    mic = rt_device_find("mic0");
    rt_kprintf("asr: mic0 %s.\r\n", (mic != RT_NULL) ? "available" : "missing");
    if (mic == RT_NULL)
    {
        ready = RT_FALSE;
    }
#if defined(RT_WLAN_MANAGE_ENABLE)
    rt_kprintf("asr: Wi-Fi connected=%d ready=%d.\r\n",
               (int)rt_wlan_is_connected(), (int)rt_wlan_is_ready());
    if ((rt_wlan_is_connected() != RT_TRUE) || (rt_wlan_is_ready() != RT_TRUE))
    {
        ready = RT_FALSE;
    }
#endif
    timestamp = time(RT_NULL);
    rt_kprintf("asr: unix time=%ld (%s).\r\n", (long)timestamp,
               (timestamp >= (time_t)1577836800) ?
               "set; verify current UTC time before signing" : "RTC not synchronized");
    if (timestamp < (time_t)1577836800)
    {
        ready = RT_FALSE;
    }
    rt_kprintf("asr: use asr_sync or begin speech once to synchronize RTC through Tencent.\r\n");
    rt_kprintf("asr: URL=%s region=%s engine=%s credentials=%s.\r\n",
               TENCENT_ASR_API_URL, TENCENT_ASR_REGION, TENCENT_ASR_ENGINE_TYPE,
               ((rt_strcmp(TENCENT_ASR_SECRET_ID, TENCENT_SECRET_ID_PLACEHOLDER) != 0) &&
                (rt_strcmp(TENCENT_ASR_SECRET_KEY, TENCENT_SECRET_KEY_PLACEHOLDER) != 0)) ?
               "configured" : "missing");
    if ((rt_strcmp(TENCENT_ASR_SECRET_ID, TENCENT_SECRET_ID_PLACEHOLDER) == 0) ||
        (rt_strcmp(TENCENT_ASR_SECRET_KEY, TENCENT_SECRET_KEY_PLACEHOLDER) == 0))
    {
        ready = RT_FALSE;
    }
    rt_kprintf("asr: readiness=%s.\r\n",
               ready ? (s_cloud_time_checked ? "ready; cloud time confirmed" :
                        "basic checks passed; cloud time sync pending") : "not ready");
    return ready ? RT_EOK : -RT_ERROR;
}

static int asr_time(int argc, char **argv)
{
    char *end;
    long timestamp;

    if (argc != 2)
    {
        rt_kprintf("Usage: asr_time <unix_timestamp>\r\n");
        return -RT_EINVAL;
    }
    timestamp = strtol(argv[1], &end, 10);
    if ((*end != '\0') || (timestamp <= 0L))
    {
        rt_kprintf("Usage: asr_time <unix_timestamp>\r\n");
        return -RT_EINVAL;
    }
    return speech_update_rtc_from_timestamp((time_t)timestamp);
}

static int asr_sync(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    return speech_cli_start(SPEECH_CLI_JOB_SYNC, 0U);
}

static int mic_gain(int argc, char **argv)
{
    struct rt_audio_caps caps;
    rt_device_t mic;
    int gain;

    mic = rt_device_find("mic0");
    if (mic == RT_NULL)
    {
        rt_kprintf("mic: device mic0 is not available.\r\n");
        return -RT_ERROR;
    }

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_MIXER;
    caps.sub_type = AUDIO_MIXER_VOLUME;
    if (argc > 1)
    {
        gain = atoi(argv[1]);
        if ((gain < AUDIO_VOLUME_MIN) || (gain > AUDIO_VOLUME_MAX))
        {
            rt_kprintf("Usage: mic_gain [0-100]\r\n");
            return -RT_EINVAL;
        }
        caps.udata.value = (rt_uint32_t)gain;
        if (rt_device_control(mic, AUDIO_CTL_CONFIGURE, &caps) != RT_EOK)
        {
            rt_kprintf("mic: failed to set gain.\r\n");
            return -RT_ERROR;
        }
    }
    if (rt_device_control(mic, AUDIO_CTL_GETCAPS, &caps) != RT_EOK)
    {
        rt_kprintf("mic: failed to read gain.\r\n");
        return -RT_ERROR;
    }
    rt_kprintf("mic: gain=%u.\r\n", (unsigned int)caps.udata.value);
    return RT_EOK;
}

MSH_CMD_EXPORT(mic_test, Capture microphone audio and print signal level: mic_test [seconds]);
MSH_CMD_EXPORT(mic_gain, Read or set microphone gain: mic_gain [0-100]);
MSH_CMD_EXPORT(asr_check, Print microphone network time and ASR configuration readiness);
MSH_CMD_EXPORT(asr_time, Set RTC from Tencent server time: asr_time <unix_timestamp>);
MSH_CMD_EXPORT(asr_sync, Synchronize RTC through Tencent ASR before recording);
#endif
MSH_CMD_EXPORT(voice_test, Record speech and submit STT: voice_test [seconds]);
#endif
