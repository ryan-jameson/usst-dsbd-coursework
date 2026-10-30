#include "football_protocol.h"

#include <stdlib.h>
#include <string.h>

static void football_copy(char *dst, rt_size_t dst_size, const char *src)
{
    rt_size_t i = 0;

    if (dst_size == 0)
    {
        return;
    }
    if (src == RT_NULL)
    {
        src = "";
    }

    while (i + 1 < dst_size && src[i] != '\0')
    {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
}

static char *football_trim(char *text)
{
    char *end;

    if (text == RT_NULL)
    {
        return "";
    }

    while (*text == ' ' || *text == '\t' || *text == '\r' || *text == '\n')
    {
        text++;
    }

    end = text + strlen(text);
    while (end > text)
    {
        char c = *(end - 1);
        if (c != ' ' && c != '\t' && c != '\r' && c != '\n')
        {
            break;
        }
        end--;
    }
    *end = '\0';

    return text;
}

static int football_lower(int ch)
{
    if (ch >= 'A' && ch <= 'Z')
    {
        return ch + ('a' - 'A');
    }
    return ch;
}

static rt_bool_t football_streq_ci(const char *a, const char *b)
{
    if (a == RT_NULL || b == RT_NULL)
    {
        return RT_FALSE;
    }

    while (*a != '\0' && *b != '\0')
    {
        if (football_lower((unsigned char)*a) != football_lower((unsigned char)*b))
        {
            return RT_FALSE;
        }
        a++;
        b++;
    }

    return (*a == '\0' && *b == '\0') ? RT_TRUE : RT_FALSE;
}

static const char *football_find_json_value(const char *json, const char *key)
{
    char pattern[40];
    const char *pos;

    rt_snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    pos = strstr(json, pattern);
    if (pos == RT_NULL)
    {
        return RT_NULL;
    }

    pos = strchr(pos + strlen(pattern), ':');
    if (pos == RT_NULL)
    {
        return RT_NULL;
    }

    pos++;
    while (*pos == ' ' || *pos == '\t')
    {
        pos++;
    }

    return pos;
}

static rt_bool_t football_json_get_string(const char *json, const char *key, char *out, rt_size_t out_size)
{
    const char *pos = football_find_json_value(json, key);
    rt_size_t used = 0;

    if (pos == RT_NULL || out_size == 0)
    {
        return RT_FALSE;
    }

    out[0] = '\0';
    if (*pos == '"')
    {
        pos++;
        while (*pos != '\0' && *pos != '"' && used + 1 < out_size)
        {
            if (*pos == '\\' && *(pos + 1) != '\0')
            {
                pos++;
            }
            out[used++] = *pos++;
        }
        out[used] = '\0';
        return RT_TRUE;
    }

    while (*pos != '\0' && *pos != ',' && *pos != '}' && used + 1 < out_size)
    {
        out[used++] = *pos++;
    }
    out[used] = '\0';
    football_copy(out, out_size, football_trim(out));

    return RT_TRUE;
}

static rt_bool_t football_json_get_u32(const char *json, const char *key, rt_uint32_t *out)
{
    char value[24];

    if (football_json_get_string(json, key, value, sizeof(value)) == RT_FALSE)
    {
        return RT_FALSE;
    }

    *out = (rt_uint32_t)strtoul(value, RT_NULL, 10);
    return RT_TRUE;
}

static rt_bool_t football_json_get_i32(const char *json, const char *key, rt_int32_t *out)
{
    char value[24];

    if (football_json_get_string(json, key, value, sizeof(value)) == RT_FALSE)
    {
        return RT_FALSE;
    }

    *out = (rt_int32_t)strtol(value, RT_NULL, 10);
    return RT_TRUE;
}

static rt_bool_t football_json_get_float(const char *json, const char *key, float *out)
{
    char value[24];

    if (football_json_get_string(json, key, value, sizeof(value)) == RT_FALSE)
    {
        return RT_FALSE;
    }

    *out = (float)atof(value);
    return RT_TRUE;
}

static rt_uint32_t football_confidence_milli(float confidence)
{
    if (confidence <= 0.0f)
    {
        return 0;
    }
    if (confidence >= 1.0f)
    {
        return 1000;
    }
    return (rt_uint32_t)(confidence * 1000.0f + 0.5f);
}

static rt_uint16_t football_confidence_permille(float confidence)
{
    rt_uint32_t permille = football_confidence_milli(confidence);

    return (rt_uint16_t)(permille > 1000u ? 1000u : permille);
}

static rt_uint8_t football_clamp_u8(rt_int32_t value, rt_uint8_t max_value)
{
    if (value <= 0)
    {
        return 0;
    }
    if (value >= (rt_int32_t)max_value)
    {
        return max_value;
    }
    return (rt_uint8_t)value;
}

static rt_int16_t football_clamp_i16(rt_int32_t value)
{
    if (value > 32767)
    {
        return 32767;
    }
    if (value < -32768)
    {
        return -32768;
    }
    return (rt_int16_t)value;
}

static void football_tactic_from_event(const char *event_name, char *out, rt_size_t out_size)
{
    if (football_streq_ci(event_name, "counter_attack") == RT_TRUE)
    {
        football_copy(out, out_size, "Counter Attack");
        return;
    }
    if (football_streq_ci(event_name, "set_piece") == RT_TRUE)
    {
        football_copy(out, out_size, "Set Piece");
        return;
    }
    if (football_streq_ci(event_name, "goal") == RT_TRUE)
    {
        football_copy(out, out_size, "Goal");
        return;
    }
    if (football_streq_ci(event_name, "new_match") == RT_TRUE)
    {
        football_copy(out, out_size, "New Match");
        return;
    }

    football_copy(out, out_size, event_name == RT_NULL || event_name[0] == '\0' ? "Open Play" : event_name);
}

void football_protocol_init_message(football_message_t *message)
{
    if (message == RT_NULL)
    {
        return;
    }

    rt_memset(message, 0, sizeof(*message));
    message->protocol_version = FOOTBALL_PROTOCOL_VERSION;
    football_copy(message->event_type, sizeof(message->event_type), "football_event");
}

rt_err_t football_protocol_parse_json(const char *utf8_json, football_message_t *message)
{
    rt_uint32_t version;

    if (utf8_json == RT_NULL || message == RT_NULL)
    {
        return -RT_EINVAL;
    }

    football_protocol_init_message(message);

    if (football_json_get_u32(utf8_json, "protocol_version", &version) == RT_FALSE)
    {
        return -RT_EINVAL;
    }
    message->protocol_version = (rt_uint16_t)version;

    if (football_json_get_u32(utf8_json, "message_id", &message->message_id) == RT_FALSE ||
        football_json_get_string(utf8_json, "event_type", message->event_type, sizeof(message->event_type)) == RT_FALSE ||
        football_json_get_u32(utf8_json, "timestamp", &message->timestamp) == RT_FALSE ||
        football_json_get_string(utf8_json, "event", message->event, sizeof(message->event)) == RT_FALSE ||
        football_json_get_string(utf8_json, "team", message->team, sizeof(message->team)) == RT_FALSE ||
        football_json_get_float(utf8_json, "confidence", &message->confidence) == RT_FALSE ||
        football_json_get_i32(utf8_json, "danger", &message->danger) == RT_FALSE ||
        football_json_get_i32(utf8_json, "ball_x", &message->ball_x) == RT_FALSE ||
        football_json_get_i32(utf8_json, "ball_y", &message->ball_y) == RT_FALSE ||
        football_json_get_string(utf8_json, "checksum", message->checksum, sizeof(message->checksum)) == RT_FALSE)
    {
        return -RT_EINVAL;
    }
    (void)football_json_get_string(utf8_json, "commentary", message->commentary,
                                   sizeof(message->commentary));

    if (message->protocol_version != FOOTBALL_PROTOCOL_VERSION)
    {
        return -RT_EINVAL;
    }

    return RT_EOK;
}

rt_err_t football_protocol_format_json(const football_message_t *message, char *out, rt_size_t out_size)
{
    rt_uint32_t conf;
    int written;

    if (message == RT_NULL || out == RT_NULL || out_size == 0)
    {
        return -RT_EINVAL;
    }

    conf = football_confidence_milli(message->confidence);
    written = rt_snprintf(out,
                          out_size,
                          "{\"protocol_version\":%u,\"message_id\":%u,\"event_type\":\"%s\",\"timestamp\":%u,\"event\":\"%s\",\"team\":\"%s\",\"confidence\":%u.%03u,\"danger\":%d,\"ball_x\":%d,\"ball_y\":%d,\"checksum\":\"%s\",\"commentary\":\"%s\"}",
                          (unsigned int)message->protocol_version,
                          (unsigned int)message->message_id,
                          message->event_type,
                          (unsigned int)message->timestamp,
                          message->event,
                          message->team,
                          (unsigned int)(conf / 1000u),
                          (unsigned int)(conf % 1000u),
                          (int)message->danger,
                          (int)message->ball_x,
                          (int)message->ball_y,
                          message->checksum,
                          message->commentary);
    if (written < 0 || written >= (int)out_size)
    {
        return -RT_ERROR;
    }

    return RT_EOK;
}

rt_bool_t football_protocol_is_event(const football_message_t *message, const char *event_name)
{
    if (message == RT_NULL)
    {
        return RT_FALSE;
    }

    return football_streq_ci(message->event, event_name);
}

void football_shared_data_init(volatile FootballSharedData *shared)
{
    if (shared == RT_NULL)
    {
        return;
    }

    if (shared->magic == FOOTBALL_SHARED_MAGIC &&
        shared->version == FOOTBALL_SHARED_VERSION &&
        shared->struct_size == sizeof(FootballSharedData))
    {
        return;
    }

    rt_memset((void *)shared, 0, sizeof(FootballSharedData));
    shared->magic = FOOTBALL_SHARED_MAGIC;
    shared->version = FOOTBALL_SHARED_VERSION;
    shared->struct_size = sizeof(FootballSharedData);
    shared->possession.home_permille = 500u;
    shared->possession.away_permille = 500u;
    football_copy((char *)shared->current_tactic.tactic_name,
                  sizeof(shared->current_tactic.tactic_name),
                  "Waiting");
}

rt_err_t football_message_to_shared_event(const football_message_t *message,
                                          rt_uint16_t event_id,
                                          FootballSharedEvent *shared_event)
{
    if (message == RT_NULL || shared_event == RT_NULL)
    {
        return -RT_EINVAL;
    }

    rt_memset(shared_event, 0, sizeof(*shared_event));
    shared_event->message_id = message->message_id;
    shared_event->event_id = event_id;
    shared_event->danger = football_clamp_u8(message->danger, 5u);
    shared_event->timestamp_ms = message->timestamp;
    football_copy(shared_event->event_name, sizeof(shared_event->event_name), message->event);
    football_copy(shared_event->team, sizeof(shared_event->team), message->team);
    shared_event->confidence_permille = football_confidence_permille(message->confidence);
    shared_event->ball_x = football_clamp_i16(message->ball_x);
    shared_event->ball_y = football_clamp_i16(message->ball_y);

    return RT_EOK;
}

rt_err_t football_shared_event_to_message(const FootballSharedEvent *shared_event,
                                          football_message_t *message)
{
    if (shared_event == RT_NULL || message == RT_NULL)
    {
        return -RT_EINVAL;
    }

    football_protocol_init_message(message);
    message->message_id = shared_event->message_id;
    message->timestamp = shared_event->timestamp_ms;
    football_copy(message->event, sizeof(message->event), shared_event->event_name);
    football_copy(message->team, sizeof(message->team), shared_event->team);
    message->confidence = (float)shared_event->confidence_permille / 1000.0f;
    message->danger = shared_event->danger;
    message->ball_x = shared_event->ball_x;
    message->ball_y = shared_event->ball_y;
    football_copy(message->checksum, sizeof(message->checksum), "");

    return RT_EOK;
}

rt_err_t football_shared_data_write_event(volatile FootballSharedData *shared,
                                          const football_message_t *message,
                                          rt_uint16_t event_id)
{
    FootballSharedEvent shared_event;
    rt_base_t level;
    rt_uint32_t seq;
    rt_uint8_t index;

    if (shared == RT_NULL || message == RT_NULL)
    {
        return -RT_EINVAL;
    }
    if (football_message_to_shared_event(message, event_id, &shared_event) != RT_EOK)
    {
        return -RT_ERROR;
    }

    football_shared_data_init(shared);

    level = rt_hw_interrupt_disable();

    seq = shared->m33_write_seq;
    if ((seq & 1u) == 0u)
    {
        seq++;
    }
    shared->m33_write_seq = seq;

    shared->current_event = shared_event;
    football_tactic_from_event(message->event,
                               (char *)shared->current_tactic.tactic_name,
                               sizeof(shared->current_tactic.tactic_name));
    shared->match_time_ms = message->timestamp;
    shared->danger_level = (rt_uint8_t)shared_event.danger;
    shared->match_period = 1u;

    if (football_streq_ci(message->team, "home") == RT_TRUE)
    {
        shared->possession.home_permille = 600u;
        shared->possession.away_permille = 400u;
    }
    else if (football_streq_ci(message->team, "away") == RT_TRUE)
    {
        shared->possession.home_permille = 400u;
        shared->possession.away_permille = 600u;
    }
    else
    {
        shared->possession.home_permille = 500u;
        shared->possession.away_permille = 500u;
    }

    index = shared->recent_write_index % FOOTBALL_RECENT_EVENT_MAX;
    shared->recent_events[index] = shared_event;
    shared->recent_write_index = (rt_uint8_t)((index + 1u) % FOOTBALL_RECENT_EVENT_MAX);
    if (shared->recent_count < FOOTBALL_RECENT_EVENT_MAX)
    {
        shared->recent_count++;
    }

    shared->ui_status.refresh_required = 1u;
    shared->feature_flags = 1u;
    shared->checksum = 0u;

    shared->m33_write_seq = seq + 1u;

    rt_hw_interrupt_enable(level);

    return RT_EOK;
}

rt_bool_t football_shared_data_try_read(volatile FootballSharedData *shared,
                                        FootballSharedData *snapshot)
{
    rt_uint32_t seq_a;
    rt_uint32_t seq_b;

    if (shared == RT_NULL || snapshot == RT_NULL)
    {
        return RT_FALSE;
    }
    if (shared->magic != FOOTBALL_SHARED_MAGIC ||
        shared->version != FOOTBALL_SHARED_VERSION ||
        shared->struct_size != sizeof(FootballSharedData))
    {
        return RT_FALSE;
    }

    seq_a = shared->m33_write_seq;
    if ((seq_a & 1u) != 0u)
    {
        return RT_FALSE;
    }

    *snapshot = *shared;

    seq_b = shared->m33_write_seq;
    if (seq_a != seq_b || (seq_b & 1u) != 0u)
    {
        return RT_FALSE;
    }

    return RT_TRUE;
}
