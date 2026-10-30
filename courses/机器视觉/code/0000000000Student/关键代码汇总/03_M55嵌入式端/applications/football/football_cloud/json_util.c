#include "json_util.h"
#include <string.h>

static int json_put_byte(char *dst, rt_size_t dst_size, rt_size_t *pos, char value)
{
    if ((*pos + 1U) >= dst_size)
    {
        return -RT_ENOMEM;
    }

    dst[*pos] = value;
    (*pos)++;
    dst[*pos] = '\0';
    return RT_EOK;
}

static int json_put_utf8(char *dst, rt_size_t dst_size, rt_size_t *pos, rt_uint32_t value)
{
    if (value < 0x80U)
    {
        return json_put_byte(dst, dst_size, pos, (char)value);
    }
    if (value < 0x800U)
    {
        if (json_put_byte(dst, dst_size, pos, (char)(0xC0U | (value >> 6))) != RT_EOK ||
            json_put_byte(dst, dst_size, pos, (char)(0x80U | (value & 0x3FU))) != RT_EOK)
        {
            return -RT_ENOMEM;
        }
        return RT_EOK;
    }

    if (json_put_byte(dst, dst_size, pos, (char)(0xE0U | (value >> 12))) != RT_EOK ||
        json_put_byte(dst, dst_size, pos, (char)(0x80U | ((value >> 6) & 0x3FU))) != RT_EOK ||
        json_put_byte(dst, dst_size, pos, (char)(0x80U | (value & 0x3FU))) != RT_EOK)
    {
        return -RT_ENOMEM;
    }
    return RT_EOK;
}

static int json_hex_value(char value)
{
    if ((value >= '0') && (value <= '9'))
    {
        return value - '0';
    }
    if ((value >= 'a') && (value <= 'f'))
    {
        return value - 'a' + 10;
    }
    if ((value >= 'A') && (value <= 'F'))
    {
        return value - 'A' + 10;
    }
    return -1;
}

int json_util_escape(const char *src, char *dst, rt_size_t dst_size)
{
    static const char hex[] = "0123456789abcdef";
    rt_size_t pos = 0;
    unsigned char value;

    if ((src == RT_NULL) || (dst == RT_NULL) || (dst_size == 0U))
    {
        return -RT_EINVAL;
    }

    dst[0] = '\0';
    while (*src != '\0')
    {
        value = (unsigned char)*src++;
        switch (value)
        {
        case '\"':
        case '\\':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, (char)value) != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        case '\b':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, 'b') != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        case '\f':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, 'f') != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        case '\n':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, 'n') != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        case '\r':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, 'r') != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        case '\t':
            if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                json_put_byte(dst, dst_size, &pos, 't') != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        default:
            if (value < 0x20U)
            {
                if (json_put_byte(dst, dst_size, &pos, '\\') != RT_EOK ||
                    json_put_byte(dst, dst_size, &pos, 'u') != RT_EOK ||
                    json_put_byte(dst, dst_size, &pos, '0') != RT_EOK ||
                    json_put_byte(dst, dst_size, &pos, '0') != RT_EOK ||
                    json_put_byte(dst, dst_size, &pos, hex[value >> 4]) != RT_EOK ||
                    json_put_byte(dst, dst_size, &pos, hex[value & 0x0FU]) != RT_EOK)
                {
                    return -RT_ENOMEM;
                }
            }
            else if (json_put_byte(dst, dst_size, &pos, (char)value) != RT_EOK)
            {
                return -RT_ENOMEM;
            }
            break;
        }
    }

    return RT_EOK;
}

static const char *json_parse_string(const char *src, char *dst, rt_size_t dst_size)
{
    rt_size_t pos = 0;
    rt_uint32_t unicode;
    int value;
    int index;

    if (*src != '\"')
    {
        return RT_NULL;
    }

    dst[0] = '\0';
    src++;
    while ((*src != '\0') && (*src != '\"'))
    {
        if (*src != '\\')
        {
            if (json_put_byte(dst, dst_size, &pos, *src++) != RT_EOK)
            {
                return RT_NULL;
            }
            continue;
        }

        src++;
        switch (*src)
        {
        case '\"':
        case '\\':
        case '/':
            if (json_put_byte(dst, dst_size, &pos, *src++) != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 'b':
            src++;
            if (json_put_byte(dst, dst_size, &pos, '\b') != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 'f':
            src++;
            if (json_put_byte(dst, dst_size, &pos, '\f') != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 'n':
            src++;
            if (json_put_byte(dst, dst_size, &pos, '\n') != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 'r':
            src++;
            if (json_put_byte(dst, dst_size, &pos, '\r') != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 't':
            src++;
            if (json_put_byte(dst, dst_size, &pos, '\t') != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        case 'u':
            unicode = 0;
            src++;
            for (index = 0; index < 4; index++)
            {
                value = json_hex_value(*src++);
                if (value < 0)
                {
                    return RT_NULL;
                }
                unicode = (unicode << 4) | (rt_uint32_t)value;
            }
            if (json_put_utf8(dst, dst_size, &pos, unicode) != RT_EOK)
            {
                return RT_NULL;
            }
            break;
        default:
            return RT_NULL;
        }
    }

    return (*src == '\"') ? (src + 1) : RT_NULL;
}

int json_util_get_string(const char *json, const char *key, char *dst, rt_size_t dst_size)
{
    char parsed_key[48];
    const char *next;
    const char *cursor;

    if ((json == RT_NULL) || (key == RT_NULL) || (dst == RT_NULL) || (dst_size == 0U))
    {
        return -RT_EINVAL;
    }

    cursor = json;
    while (*cursor != '\0')
    {
        if (*cursor != '\"')
        {
            cursor++;
            continue;
        }

        next = json_parse_string(cursor, parsed_key, sizeof(parsed_key));
        if (next == RT_NULL)
        {
            return -RT_ERROR;
        }

        cursor = next;
        while ((*cursor == ' ') || (*cursor == '\t') || (*cursor == '\r') || (*cursor == '\n'))
        {
            cursor++;
        }
        if ((*cursor != ':') || (rt_strcmp(parsed_key, key) != 0))
        {
            continue;
        }

        cursor++;
        while ((*cursor == ' ') || (*cursor == '\t') || (*cursor == '\r') || (*cursor == '\n'))
        {
            cursor++;
        }
        if (json_parse_string(cursor, dst, dst_size) == RT_NULL)
        {
            return -RT_ERROR;
        }
        return RT_EOK;
    }

    return -RT_ERROR;
}

static const char *json_skip_whitespace(const char *cursor)
{
    while ((*cursor == ' ') || (*cursor == '\t') ||
           (*cursor == '\r') || (*cursor == '\n'))
    {
        cursor++;
    }
    return cursor;
}

static const char *json_seek_to_key(const char *cursor, const char *key,
                                     rt_size_t key_len)
{
    char parsed_key[48];
    const char *next;

    while (*cursor != '\0')
    {
        if (*cursor != '\"')
        {
            cursor++;
            continue;
        }
        next = json_parse_string(cursor, parsed_key, sizeof(parsed_key));
        if (next == RT_NULL)
        {
            return RT_NULL;
        }
        cursor = json_skip_whitespace(next);
        if ((*cursor == ':') &&
            (rt_strlen(parsed_key) == key_len) &&
            (rt_strncmp(parsed_key, key, key_len) == 0))
        {
            return cursor + 1;
        }
    }
    return RT_NULL;
}

static const char *json_skip_value(const char *cursor)
{
    int depth;

    cursor = json_skip_whitespace(cursor);
    if (*cursor == '\0')
    {
        return RT_NULL;
    }

    if (*cursor == '\"')
    {
        char dummy[4];
        return json_parse_string(cursor, dummy, sizeof(dummy));
    }
    if (*cursor == '{')
    {
        depth = 1;
        cursor++;
        while ((*cursor != '\0') && (depth > 0))
        {
            if (*cursor == '{') depth++;
            else if (*cursor == '}') depth--;
            cursor++;
        }
        return (*cursor == '\0') ? RT_NULL : cursor;
    }
    if (*cursor == '[')
    {
        depth = 1;
        cursor++;
        while ((*cursor != '\0') && (depth > 0))
        {
            if (*cursor == '[') depth++;
            else if (*cursor == ']') depth--;
            cursor++;
        }
        return (*cursor == '\0') ? RT_NULL : cursor;
    }
    while ((*cursor != '\0') && (*cursor != ',') &&
           (*cursor != '}') && (*cursor != ']'))
    {
        cursor++;
    }
    return cursor;
}

static const char *json_enter_array_index(const char *cursor, int target_idx)
{
    int idx = 0;

    cursor = json_skip_whitespace(cursor);
    if ((cursor == RT_NULL) || (*cursor != '['))
    {
        return RT_NULL;
    }
    cursor++;

    while ((cursor != RT_NULL) && (idx <= target_idx))
    {
        cursor = json_skip_whitespace(cursor);
        if ((cursor == RT_NULL) || (*cursor == '\0'))
        {
            return RT_NULL;
        }
        if (*cursor == ']')
        {
            return RT_NULL;
        }
        if (idx == target_idx)
        {
            return cursor;
        }
        cursor = json_skip_value(cursor);
        if (cursor == RT_NULL)
        {
            return RT_NULL;
        }
        cursor = json_skip_whitespace(cursor);
        if ((cursor != RT_NULL) && (*cursor == ','))
        {
            cursor++;
        }
        idx++;
    }
    return RT_NULL;
}

int json_util_get_path_string(const char *json, const char *path,
                               char *dst, rt_size_t dst_size)
{
    const char *cursor;
    char segment[48];
    rt_size_t seg_len;
    int arr_idx;
    const char *dot;

    if ((json == RT_NULL) || (path == RT_NULL) ||
        (dst == RT_NULL) || (dst_size == 0U))
    {
        return -RT_EINVAL;
    }

    dst[0] = '\0';
    cursor = json;

    while (*path != '\0')
    {
        dot = strchr(path, '.');
        if (dot != RT_NULL)
        {
            seg_len = (rt_size_t)(dot - path);
        }
        else
        {
            seg_len = rt_strlen(path);
        }
        if ((seg_len == 0U) || (seg_len >= sizeof(segment)))
        {
            return -RT_ERROR;
        }
        rt_memcpy(segment, path, seg_len);
        segment[seg_len] = '\0';

        arr_idx = -1;
        if ((seg_len >= 3U) && (segment[seg_len - 1U] == ']'))
        {
            char *bracket = strchr(segment, '[');
            if ((bracket != RT_NULL) &&
                (segment[seg_len - 1U] == ']'))
            {
                *bracket = '\0';
                arr_idx = 0;
                bracket++;
                while (*bracket >= '0' && *bracket <= '9')
                {
                    arr_idx = arr_idx * 10 + (int)(*bracket - '0');
                    bracket++;
                }
                seg_len = rt_strlen(segment);
            }
        }

        if (dot == RT_NULL)
        {
            cursor = json_seek_to_key(cursor, segment, seg_len);
            if (cursor == RT_NULL)
            {
                return -RT_ERROR;
            }
            cursor = json_skip_whitespace(cursor);
            if (json_parse_string(cursor, dst, dst_size) == RT_NULL)
            {
                return -RT_ERROR;
            }
            return RT_EOK;
        }

        cursor = json_seek_to_key(cursor, segment, seg_len);
        if (cursor == RT_NULL)
        {
            return -RT_ERROR;
        }
        cursor = json_skip_whitespace(cursor);

        if (arr_idx >= 0)
        {
            cursor = json_enter_array_index(cursor, arr_idx);
            if (cursor == RT_NULL)
            {
                return -RT_ERROR;
            }
        }
        path = dot + 1;
    }

    return -RT_ERROR;
}
