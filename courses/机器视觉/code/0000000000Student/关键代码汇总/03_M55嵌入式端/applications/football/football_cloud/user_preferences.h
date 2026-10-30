#ifndef APPLICATIONS_USER_PREFERENCES_H
#define APPLICATIONS_USER_PREFERENCES_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

#define USER_PREFS_PATH "/flash/football_user_prefs.cfg"
#define USER_PREFS_TTS_SAFE_VOICE_TYPE 502003
#define USER_PREFS_TTS_EMOTION_SIZE 16U
#define USER_PREFS_MUSIC_NAME_SIZE 64U
#define USER_PREFS_MUSIC_PATH_SIZE 112U
#define USER_PREFS_PROMPT_SIZE 512U

typedef enum
{
    USER_PREF_AI_LENGTH_SHORT = 0,
    USER_PREF_AI_LENGTH_NORMAL,
    USER_PREF_AI_LENGTH_DETAILED,
    USER_PREF_AI_LENGTH_COUNT
} user_pref_ai_length_t;

typedef enum
{
    USER_PREF_AI_STYLE_DIRECT = 0,
    USER_PREF_AI_STYLE_GENTLE,
    USER_PREF_AI_STYLE_ENCOURAGING,
    USER_PREF_AI_STYLE_COUNT
} user_pref_ai_style_t;

typedef struct
{
    int brightness_percent;
    int volume_percent;
    int tts_voice_type;
    int tts_speed_x100;
    int tts_volume_x100;
    char tts_emotion_category[USER_PREFS_TTS_EMOTION_SIZE];
    int tts_emotion_intensity;
    int tts_segment_rate;
    int ai_reply_length;
    int ai_reply_style;
    rt_bool_t ai_read_aloud;
    int work_minutes;
    int break_minutes;
    char favorite_music_name[USER_PREFS_MUSIC_NAME_SIZE];
    char favorite_music_path[USER_PREFS_MUSIC_PATH_SIZE];
} user_preferences_t;

void user_preferences_init(void);
int user_preferences_load(void);
int user_preferences_save(void);
const user_preferences_t *user_preferences_get(void);
int user_preferences_update(const user_preferences_t *prefs);
int user_preferences_build_system_prompt(char *buffer, rt_size_t buffer_size);

#ifdef __cplusplus
}
#endif

#endif /* APPLICATIONS_USER_PREFERENCES_H */
