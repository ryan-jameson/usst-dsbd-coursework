#include "user_preferences.h"

#include <stdlib.h>
#include <string.h>

#ifdef BSP_USING_SDCARD
#include <fcntl.h>
#include <unistd.h>
#endif

#include "llm_config.h"

#define USER_PREFS_MAGIC "focus_talk_user_prefs_v1"
#define USER_PREFS_FILE_BUFFER_SIZE 1024U
#define USER_PREFS_SAVE_BUFFER_SIZE 1024U

static user_preferences_t s_user_preferences;
static rt_mutex_t s_user_preferences_lock = RT_NULL;
static rt_bool_t s_user_preferences_ready = RT_FALSE;

static int user_preferences_lock_take(void)
{
    if (s_user_preferences_lock == RT_NULL)
    {
        s_user_preferences_lock = rt_mutex_create("usrpref", RT_IPC_FLAG_PRIO);
        if (s_user_preferences_lock == RT_NULL)
        {
            return -RT_ENOMEM;
        }
    }

    return rt_mutex_take(s_user_preferences_lock, RT_WAITING_FOREVER);
}

static void user_preferences_lock_release(void)
{
    if (s_user_preferences_lock != RT_NULL)
    {
        rt_mutex_release(s_user_preferences_lock);
    }
}

static int user_preferences_clamp_int(int value, int min_value, int max_value)
{
    if (value < min_value)
    {
        return min_value;
    }
    if (value > max_value)
    {
        return max_value;
    }
    return value;
}

static rt_bool_t user_preferences_text_has_line_break(const char *text)
{
    if (text == RT_NULL)
    {
        return RT_FALSE;
    }

    while (*text != '\0')
    {
        if ((*text == '\r') || (*text == '\n'))
        {
            return RT_TRUE;
        }
        text++;
    }

    return RT_FALSE;
}

static rt_bool_t user_preferences_music_name_is_mp3(const char *name)
{
    rt_size_t len;
    const char *ext;

    if (name == RT_NULL)
    {
        return RT_FALSE;
    }
    len = rt_strlen(name);
    if (len < 5U)
    {
        return RT_FALSE;
    }

    ext = name + len - 4U;
    return ((ext[0] == '.') &&
            ((ext[1] == 'm') || (ext[1] == 'M')) &&
            ((ext[2] == 'p') || (ext[2] == 'P')) &&
            (ext[3] == '3')) ? RT_TRUE : RT_FALSE;
}

static rt_bool_t user_preferences_music_path_allowed(const char *path)
{
    const char prefix[] = "/sdcard/";
    const char *p;

    if ((path == RT_NULL) || (path[0] == '\0'))
    {
        return RT_TRUE;
    }
    if ((rt_strncmp(path, prefix, sizeof(prefix) - 1U) != 0) ||
        user_preferences_text_has_line_break(path) ||
        !user_preferences_music_name_is_mp3(path))
    {
        return RT_FALSE;
    }

    p = path;
    while ((p[0] != '\0') && (p[1] != '\0'))
    {
        if ((p[0] == '.') && (p[1] == '.'))
        {
            return RT_FALSE;
        }
        p++;
    }

    return RT_TRUE;
}

static rt_bool_t user_preferences_emotion_allowed(const char *emotion)
{
    static const char *const allowed[] = {
        "neutral",
        "happy",
        "sad",
        "angry",
        "fear",
        "sajiao",
        "disgusted",
        "amaze",
        "peaceful",
    };
    rt_size_t i;

    if (emotion == RT_NULL)
    {
        return RT_FALSE;
    }

    for (i = 0U; i < (sizeof(allowed) / sizeof(allowed[0])); i++)
    {
        if (rt_strcmp(emotion, allowed[i]) == 0)
        {
            return RT_TRUE;
        }
    }

    return RT_FALSE;
}

static void user_preferences_set_defaults(user_preferences_t *prefs)
{
    if (prefs == RT_NULL)
    {
        return;
    }

    prefs->brightness_percent = 80;
    prefs->volume_percent = 95;
    prefs->tts_voice_type = USER_PREFS_TTS_SAFE_VOICE_TYPE;
    prefs->tts_speed_x100 = 0;
    prefs->tts_volume_x100 = 0;
    rt_strncpy(prefs->tts_emotion_category, "neutral", sizeof(prefs->tts_emotion_category) - 1U);
    prefs->tts_emotion_category[sizeof(prefs->tts_emotion_category) - 1U] = '\0';
    prefs->tts_emotion_intensity = 100;
    prefs->tts_segment_rate = 0;
    prefs->ai_reply_length = USER_PREF_AI_LENGTH_NORMAL;
    prefs->ai_reply_style = USER_PREF_AI_STYLE_DIRECT;
    prefs->ai_read_aloud = RT_TRUE;
    prefs->work_minutes = 25;
    prefs->break_minutes = 5;
    prefs->favorite_music_name[0] = '\0';
    prefs->favorite_music_path[0] = '\0';
}

static void user_preferences_clamp(user_preferences_t *prefs)
{
    if (prefs == RT_NULL)
    {
        return;
    }

    prefs->brightness_percent = user_preferences_clamp_int(prefs->brightness_percent, 5, 100);
    prefs->volume_percent = user_preferences_clamp_int(prefs->volume_percent, 0, 100);
    prefs->tts_voice_type = USER_PREFS_TTS_SAFE_VOICE_TYPE;
    prefs->tts_speed_x100 = user_preferences_clamp_int(prefs->tts_speed_x100, -200, 600);
    prefs->tts_volume_x100 = user_preferences_clamp_int(prefs->tts_volume_x100, -1000, 1000);
    prefs->tts_emotion_category[sizeof(prefs->tts_emotion_category) - 1U] = '\0';
    if (!user_preferences_emotion_allowed(prefs->tts_emotion_category))
    {
        rt_strncpy(prefs->tts_emotion_category, "neutral", sizeof(prefs->tts_emotion_category) - 1U);
        prefs->tts_emotion_category[sizeof(prefs->tts_emotion_category) - 1U] = '\0';
    }
    rt_strncpy(prefs->tts_emotion_category, "neutral", sizeof(prefs->tts_emotion_category) - 1U);
    prefs->tts_emotion_category[sizeof(prefs->tts_emotion_category) - 1U] = '\0';
    prefs->tts_emotion_intensity = user_preferences_clamp_int(prefs->tts_emotion_intensity, 50, 200);
    prefs->tts_segment_rate = 0;
    prefs->ai_reply_length = user_preferences_clamp_int(prefs->ai_reply_length, 0, USER_PREF_AI_LENGTH_COUNT - 1);
    prefs->ai_reply_style = user_preferences_clamp_int(prefs->ai_reply_style, 0, USER_PREF_AI_STYLE_COUNT - 1);
    prefs->ai_read_aloud = prefs->ai_read_aloud ? RT_TRUE : RT_FALSE;
    prefs->work_minutes = user_preferences_clamp_int(prefs->work_minutes, 1, 180);
    prefs->break_minutes = user_preferences_clamp_int(prefs->break_minutes, 1, 60);
    prefs->favorite_music_name[sizeof(prefs->favorite_music_name) - 1U] = '\0';
    prefs->favorite_music_path[sizeof(prefs->favorite_music_path) - 1U] = '\0';
    if (user_preferences_text_has_line_break(prefs->favorite_music_name))
    {
        prefs->favorite_music_name[0] = '\0';
    }
    if (!user_preferences_music_path_allowed(prefs->favorite_music_path))
    {
        prefs->favorite_music_path[0] = '\0';
    }
}

static void user_preferences_assign_string(char *dst, rt_size_t dst_size, const char *value)
{
    if ((dst == RT_NULL) || (dst_size == 0U))
    {
        return;
    }

    if (value == RT_NULL)
    {
        dst[0] = '\0';
        return;
    }

    rt_strncpy(dst, value, dst_size - 1U);
    dst[dst_size - 1U] = '\0';
}

static void user_preferences_parse_line(user_preferences_t *prefs, char *line)
{
    char *eq;
    char *value;
    char *end;

    if ((prefs == RT_NULL) || (line == RT_NULL))
    {
        return;
    }

    eq = strchr(line, '=');
    if (eq == RT_NULL)
    {
        return;
    }

    *eq = '\0';
    value = eq + 1;
    end = value;
    while (*end != '\0')
    {
        if ((*end == '\r') || (*end == '\n'))
        {
            *end = '\0';
            break;
        }
        end++;
    }

    if (rt_strcmp(line, "magic") == 0)
    {
        return;
    }
    if (rt_strcmp(line, "brightness") == 0)
    {
        prefs->brightness_percent = atoi(value);
    }
    else if (rt_strcmp(line, "volume") == 0)
    {
        prefs->volume_percent = atoi(value);
    }
    else if (rt_strcmp(line, "voice") == 0)
    {
        prefs->tts_voice_type = atoi(value);
    }
    else if (rt_strcmp(line, "tts_speed_x100") == 0)
    {
        prefs->tts_speed_x100 = atoi(value);
    }
    else if (rt_strcmp(line, "tts_volume_x100") == 0)
    {
        prefs->tts_volume_x100 = atoi(value);
    }
    else if (rt_strcmp(line, "tts_emotion") == 0)
    {
        user_preferences_assign_string(prefs->tts_emotion_category,
                                       sizeof(prefs->tts_emotion_category),
                                       value);
    }
    else if (rt_strcmp(line, "tts_emotion_intensity") == 0)
    {
        prefs->tts_emotion_intensity = atoi(value);
    }
    else if (rt_strcmp(line, "tts_segment_rate") == 0)
    {
        prefs->tts_segment_rate = atoi(value);
    }
    else if (rt_strcmp(line, "ai_reply_length") == 0)
    {
        prefs->ai_reply_length = atoi(value);
    }
    else if (rt_strcmp(line, "ai_reply_style") == 0)
    {
        prefs->ai_reply_style = atoi(value);
    }
    else if (rt_strcmp(line, "ai_read_aloud") == 0)
    {
        prefs->ai_read_aloud = (atoi(value) != 0) ? RT_TRUE : RT_FALSE;
    }
    else if (rt_strcmp(line, "work_minutes") == 0)
    {
        prefs->work_minutes = atoi(value);
    }
    else if (rt_strcmp(line, "break_minutes") == 0)
    {
        prefs->break_minutes = atoi(value);
    }
    else if (rt_strcmp(line, "favorite_music_name") == 0)
    {
        user_preferences_assign_string(prefs->favorite_music_name,
                                       sizeof(prefs->favorite_music_name),
                                       value);
    }
    else if (rt_strcmp(line, "favorite_music_path") == 0)
    {
        user_preferences_assign_string(prefs->favorite_music_path,
                                       sizeof(prefs->favorite_music_path),
                                       value);
    }
}

static void user_preferences_parse_buffer(user_preferences_t *prefs, char *buffer)
{
    char *line;
    char *next;

    if ((prefs == RT_NULL) || (buffer == RT_NULL))
    {
        return;
    }

    line = buffer;
    while (*line != '\0')
    {
        next = strchr(line, '\n');
        if (next != RT_NULL)
        {
            *next = '\0';
            next++;
        }
        user_preferences_parse_line(prefs, line);
        if (next == RT_NULL)
        {
            break;
        }
        line = next;
    }
}

void user_preferences_init(void)
{
    if (user_preferences_lock_take() != RT_EOK)
    {
        return;
    }

    if (!s_user_preferences_ready)
    {
        user_preferences_set_defaults(&s_user_preferences);
        s_user_preferences_ready = RT_TRUE;
    }

    user_preferences_lock_release();
    (void)user_preferences_load();
}

int user_preferences_load(void)
{
    user_preferences_t prefs;
#ifdef BSP_USING_SDCARD
    char buffer[USER_PREFS_FILE_BUFFER_SIZE];
    int fd;
    int size;
#endif
    int ret;

    user_preferences_set_defaults(&prefs);

#ifdef BSP_USING_SDCARD
    fd = open(USER_PREFS_PATH, O_RDONLY, 0);
    if (fd >= 0)
    {
        size = read(fd, buffer, sizeof(buffer) - 1U);
        close(fd);
        if (size > 0)
        {
            buffer[size] = '\0';
            if (strstr(buffer, USER_PREFS_MAGIC) != RT_NULL)
            {
                user_preferences_parse_buffer(&prefs, buffer);
            }
        }
    }
#else
    ret = user_preferences_update(&prefs);
    return (ret == RT_EOK) ? -RT_ENOSYS : ret;
#endif

    user_preferences_clamp(&prefs);
    ret = user_preferences_update(&prefs);
    return ret;
}

int user_preferences_save(void)
{
#ifdef BSP_USING_SDCARD
    const user_preferences_t *prefs;
    char buffer[USER_PREFS_SAVE_BUFFER_SIZE];
    int fd;
    int len;
    int ret = RT_EOK;

    if (!s_user_preferences_ready)
    {
        user_preferences_init();
    }
    prefs = user_preferences_get();
    len = rt_snprintf(buffer, sizeof(buffer),
                      "magic=%s\n"
                      "brightness=%d\n"
                      "volume=%d\n"
                      "voice=%d\n"
                      "tts_speed_x100=%d\n"
                      "tts_volume_x100=%d\n"
                      "tts_emotion=%s\n"
                      "tts_emotion_intensity=%d\n"
                      "tts_segment_rate=%d\n"
                      "ai_reply_length=%d\n"
                      "ai_reply_style=%d\n"
                      "ai_read_aloud=%d\n"
                      "work_minutes=%d\n"
                      "break_minutes=%d\n"
                      "favorite_music_name=%s\n"
                      "favorite_music_path=%s\n",
                      USER_PREFS_MAGIC,
                      prefs->brightness_percent,
                      prefs->volume_percent,
                      prefs->tts_voice_type,
                      prefs->tts_speed_x100,
                      prefs->tts_volume_x100,
                      prefs->tts_emotion_category,
                      prefs->tts_emotion_intensity,
                      prefs->tts_segment_rate,
                      prefs->ai_reply_length,
                      prefs->ai_reply_style,
                      prefs->ai_read_aloud ? 1 : 0,
                      prefs->work_minutes,
                      prefs->break_minutes,
                      prefs->favorite_music_name,
                      prefs->favorite_music_path);
    if ((len <= 0) || (len >= (int)sizeof(buffer)))
    {
        return -RT_ENOMEM;
    }

    fd = open(USER_PREFS_PATH, O_WRONLY | O_CREAT | O_TRUNC, 0);
    if (fd < 0)
    {
        return -RT_ERROR;
    }

    if (write(fd, buffer, (rt_size_t)len) != len)
    {
        ret = -RT_ERROR;
    }
    close(fd);
    return ret;
#else
    return -RT_ENOSYS;
#endif
}

const user_preferences_t *user_preferences_get(void)
{
    if (!s_user_preferences_ready)
    {
        user_preferences_init();
    }
    return &s_user_preferences;
}

int user_preferences_update(const user_preferences_t *prefs)
{
    if (prefs == RT_NULL)
    {
        return -RT_EINVAL;
    }

    if (user_preferences_lock_take() != RT_EOK)
    {
        return -RT_ENOMEM;
    }

    s_user_preferences = *prefs;
    user_preferences_clamp(&s_user_preferences);
    s_user_preferences_ready = RT_TRUE;
    user_preferences_lock_release();
    return RT_EOK;
}

int user_preferences_build_system_prompt(char *buffer, rt_size_t buffer_size)
{
    const user_preferences_t *prefs;
    const char *length_text;
    const char *style_text;
    int len;

    if ((buffer == RT_NULL) || (buffer_size == 0U))
    {
        return -RT_EINVAL;
    }

    prefs = user_preferences_get();
    if (prefs->ai_reply_length == USER_PREF_AI_LENGTH_SHORT)
    {
        length_text = "Keep the answer within 30 Chinese characters.";
    }
    else if (prefs->ai_reply_length == USER_PREF_AI_LENGTH_DETAILED)
    {
        length_text = "Use up to three short Chinese sentences when useful.";
    }
    else
    {
        length_text = "Use one or two short Chinese sentences.";
    }

    if (prefs->ai_reply_style == USER_PREF_AI_STYLE_GENTLE)
    {
        style_text = "Use a calm and gentle tone.";
    }
    else if (prefs->ai_reply_style == USER_PREF_AI_STYLE_ENCOURAGING)
    {
        style_text = "Use a concise encouraging tone.";
    }
    else
    {
        style_text = "Use a direct and practical tone.";
    }

    len = rt_snprintf(buffer, buffer_size, "%s %s %s",
                      LLM_ASSISTANT_SYSTEM_PROMPT,
                      length_text,
                      style_text);
    return ((len > 0) && (len < (int)buffer_size)) ? RT_EOK : -RT_ENOMEM;
}
