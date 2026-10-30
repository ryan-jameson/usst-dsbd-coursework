#include "football_voice.h"
#include "football_prompt_data.h"
#include "../football_cloud/football_cloud.h"
#include "../football_event/football_event.h"

#include <drivers/audio.h>
#include <finsh.h>
#include <rtdevice.h>

#define FOOTBALL_VOICE_QUEUE_CAPACITY 12u
#define FOOTBALL_VOICE_DEDUP_CAPACITY 16u
#define FOOTBALL_VOICE_WORK_STACK 12288u
#define FOOTBALL_VOICE_DIAG_REV "20260716-audio-3"

typedef struct football_voice_item
{
    football_message_t message;
    rt_uint8_t priority;
    football_prompt_id_t prompt;
} football_voice_item_t;

static football_voice_item_t g_queue[FOOTBALL_VOICE_QUEUE_CAPACITY];
static rt_uint16_t g_queue_count;
static rt_uint32_t g_recent_ids[FOOTBALL_VOICE_DEDUP_CAPACITY];
static rt_uint8_t g_recent_index;
static struct rt_mutex g_voice_lock;
static struct rt_semaphore g_voice_sem;
static rt_thread_t g_voice_thread;
static football_voice_status_t g_voice_status;
static volatile rt_bool_t g_voice_cancel;
static rt_uint32_t g_manual_request = 0x80000000u;

static rt_bool_t voice_equal(const char *left, const char *right)
{
    while (*left != '\0' && *right != '\0')
    {
        int a = (*left >= 'A' && *left <= 'Z') ? *left + ('a' - 'A') : *left;
        int b = (*right >= 'A' && *right <= 'Z') ? *right + ('a' - 'A') : *right;
        if (a != b) return RT_FALSE;
        left++;
        right++;
    }
    return (*left == '\0' && *right == '\0') ? RT_TRUE : RT_FALSE;
}

static rt_bool_t voice_classify(const football_message_t *message,
                                rt_uint8_t *priority,
                                football_prompt_id_t *prompt)
{
    const char *event = message->event;
    if (voice_equal(event, "new_frame") == RT_TRUE || event[0] == '\0') return RT_FALSE;
    if (voice_equal(event, "goal") == RT_TRUE)
    {
        *priority = 0u; *prompt = FOOTBALL_PROMPT_GOAL;
    }
    else if (voice_equal(event, "red_card") == RT_TRUE)
    {
        *priority = 0u; *prompt = FOOTBALL_PROMPT_RED_CARD;
    }
    else if (voice_equal(event, "penalty") == RT_TRUE || voice_equal(event, "penalty_result") == RT_TRUE)
    {
        *priority = 0u; *prompt = FOOTBALL_PROMPT_PENALTY;
    }
    else if (voice_equal(event, "new_match") == RT_TRUE ||
             voice_equal(event, "match_end") == RT_TRUE)
    {
        *priority = 0u; *prompt = FOOTBALL_PROMPT_MATCH;
    }
    else if (voice_equal(event, "counter_attack") == RT_TRUE ||
             voice_equal(event, "wide_attack") == RT_TRUE ||
             voice_equal(event, "central_penetration") == RT_TRUE ||
             voice_equal(event, "high_press") == RT_TRUE ||
             voice_equal(event, "transition_defense") == RT_TRUE ||
             voice_equal(event, "attacking_phase") == RT_TRUE ||
             voice_equal(event, "pass_into_penalty_area") == RT_TRUE ||
             voice_equal(event, "shot_on_target") == RT_TRUE ||
             voice_equal(event, "goalkeeper_save") == RT_TRUE ||
             voice_equal(event, "shot") == RT_TRUE ||
             voice_equal(event, "save") == RT_TRUE)
    {
        *priority = 2u; *prompt = FOOTBALL_PROMPT_DANGER;
    }
    else if (voice_equal(event, "pressing") == RT_TRUE)
    {
        *priority = 2u; *prompt = FOOTBALL_PROMPT_DANGER;
    }
    else if (voice_equal(event, "set_piece") == RT_TRUE)
    {
        *priority = 2u; *prompt = FOOTBALL_PROMPT_DANGER;
    }
    else if (voice_equal(event, "defensive_recover") == RT_TRUE ||
             voice_equal(event, "defensive_block") == RT_TRUE ||
             voice_equal(event, "build_up") == RT_TRUE ||
             voice_equal(event, "foul_committed") == RT_TRUE ||
             voice_equal(event, "free_kick_restart") == RT_TRUE ||
             voice_equal(event, "ball_out_touchline") == RT_TRUE ||
             voice_equal(event, "throw_in_restart") == RT_TRUE)
    {
        *priority = 3u; *prompt = FOOTBALL_PROMPT_MATCH;
    }
    else if (message->danger >= 4)
    {
        *priority = 2u; *prompt = FOOTBALL_PROMPT_DANGER;
    }
    else
    {
        *priority = 3u; *prompt = FOOTBALL_PROMPT_MATCH;
    }
    return RT_TRUE;
}

static const char *voice_scene_name(const char *event)
{
    if (voice_equal(event, "build_up") == RT_TRUE) return "阵地组织";
    if (voice_equal(event, "wide_attack") == RT_TRUE) return "边路进攻";
    if (voice_equal(event, "central_penetration") == RT_TRUE) return "中路渗透";
    if (voice_equal(event, "counter_attack") == RT_TRUE) return "快速反击";
    if (voice_equal(event, "high_press") == RT_TRUE) return "高位压迫";
    if (voice_equal(event, "set_piece") == RT_TRUE) return "定位球";
    if (voice_equal(event, "shot") == RT_TRUE) return "射门威胁";
    if (voice_equal(event, "goal") == RT_TRUE) return "进球事件";
    if (voice_equal(event, "defensive_block") == RT_TRUE) return "防守阵型";
    if (voice_equal(event, "transition_defense") == RT_TRUE) return "攻防转换防守";
    if (voice_equal(event, "foul_committed") == RT_TRUE) return "犯规停表";
    if (voice_equal(event, "free_kick_restart") == RT_TRUE) return "任意球重启";
    if (voice_equal(event, "ball_out_touchline") == RT_TRUE) return "边线出界";
    if (voice_equal(event, "throw_in_restart") == RT_TRUE) return "界外球重启";
    if (voice_equal(event, "attacking_phase") == RT_TRUE) return "持续进攻";
    if (voice_equal(event, "pass_into_penalty_area") == RT_TRUE) return "禁区传球";
    if (voice_equal(event, "shot_on_target") == RT_TRUE) return "射正威胁";
    if (voice_equal(event, "goalkeeper_save") == RT_TRUE) return "门将扑救";
    return "比赛局面";
}

static const char *voice_ball_zone(const football_message_t *message)
{
    if (message->ball_x < 0) return "未知区域";
    if (message->ball_x < 284) return "左侧区域";
    if (message->ball_x < 568) return "中路区域";
    return "右侧区域";
}

static const char *voice_team_name(const char *team)
{
    if (voice_equal(team, "home") == RT_TRUE) return "阿根廷";
    if (voice_equal(team, "away") == RT_TRUE) return "法国";
    return team;
}

static void voice_build_summary(const football_message_t *message, char *summary,
                                rt_size_t summary_size)
{
    rt_size_t length;
    if (message->commentary[0] != '\0')
    {
        length = rt_strlen(message->commentary);
        if (length >= summary_size) length = summary_size - 1u;
        rt_memcpy(summary, message->commentary, length);
        summary[length] = '\0';
        return;
    }
    rt_snprintf(summary, summary_size, "已观测到%s，%s，危险等级%d/5，球在%s。",
                voice_scene_name(message->event), voice_team_name(message->team),
                message->danger, voice_ball_zone(message));
}

static rt_bool_t voice_seen(rt_uint32_t message_id)
{
    rt_uint8_t i;
    if (message_id == 0u) return RT_FALSE;
    for (i = 0u; i < FOOTBALL_VOICE_DEDUP_CAPACITY; ++i)
        if (g_recent_ids[i] == message_id) return RT_TRUE;
    g_recent_ids[g_recent_index] = message_id;
    g_recent_index = (g_recent_index + 1u) % FOOTBALL_VOICE_DEDUP_CAPACITY;
    return RT_FALSE;
}

static rt_err_t voice_play_prompt(football_prompt_id_t prompt, rt_bool_t diagnostics)
{
    const rt_uint8_t *pcm;
    rt_size_t length;
    rt_size_t offset = 0u;
    rt_device_t sound;
    struct rt_audio_caps caps;
    int stream = AUDIO_STREAM_REPLAY;
    rt_err_t result;
    rt_uint32_t volume = 0u;

    result = football_prompt_get(prompt, &pcm, &length);
    if (result != RT_EOK)
    {
        if (diagnostics == RT_TRUE) rt_kprintf("fb_audio prompt_get=%d\r\n", result);
        return result;
    }

    if (diagnostics == RT_TRUE)
        rt_kprintf("fb_audio diag=%s prompt=%d bytes=%u\r\n",
                   FOOTBALL_VOICE_DIAG_REV, prompt, (unsigned int)length);

    sound = rt_device_find("sound0");
    if (sound == RT_NULL)
    {
        if (diagnostics == RT_TRUE) rt_kprintf("fb_audio find=-1\r\n");
        return -RT_ERROR;
    }

    result = rt_device_open(sound, RT_DEVICE_OFLAG_WRONLY);
    if (diagnostics == RT_TRUE) rt_kprintf("fb_audio open=%d\r\n", result);
    if (result != RT_EOK) return result;

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_OUTPUT;
    caps.sub_type = AUDIO_DSP_PARAM;
    caps.udata.config.samplerate = 16000;
    caps.udata.config.channels = 1;
    caps.udata.config.samplebits = 16;
    result = rt_device_control(sound, AUDIO_CTL_CONFIGURE, &caps);
    if (diagnostics == RT_TRUE) rt_kprintf("fb_audio config=%d\r\n", result);
    if (result != RT_EOK)
    {
        rt_device_close(sound);
        return result;
    }

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_MIXER;
    caps.sub_type = AUDIO_MIXER_VOLUME;
    result = rt_device_control(sound, AUDIO_CTL_GETCAPS, &caps);
    if (result == RT_EOK) volume = caps.udata.value;
    rt_kprintf("fb_audio volume_get=%d volume=%u\r\n", result, (unsigned int)volume);

    rt_memset(&caps, 0, sizeof(caps));
    caps.main_type = AUDIO_TYPE_MIXER;
    caps.sub_type = AUDIO_MIXER_VOLUME;
    caps.udata.value = AUDIO_VOLUME_MAX;
    result = rt_device_control(sound, AUDIO_CTL_CONFIGURE, &caps);
    rt_kprintf("fb_audio volume_set=%d volume=%u\r\n", result, (unsigned int)AUDIO_VOLUME_MAX);
    if (result != RT_EOK)
    {
        rt_device_close(sound);
        return result;
    }

    result = rt_device_control(sound, AUDIO_CTL_START, &stream);
    if (diagnostics == RT_TRUE) rt_kprintf("fb_audio start=%d\r\n", result);
    if (result != RT_EOK)
    {
        rt_device_close(sound);
        return result;
    }
    while (offset < length && g_voice_cancel == RT_FALSE)
    {
        rt_size_t chunk = length - offset;
        rt_ssize_t written;
        if (chunk > 1024u) chunk = 1024u;
        written = rt_device_write(sound, 0, pcm + offset, chunk);
        if (written <= 0)
        {
            result = (written < 0) ? (rt_err_t)written : -RT_ERROR;
            if (diagnostics == RT_TRUE)
                rt_kprintf("fb_audio write=%d offset=%u\r\n", (int)written, (unsigned int)offset);
            (void)rt_device_control(sound, AUDIO_CTL_STOP, &stream);
            rt_device_close(sound);
            return result;
        }
        offset += (rt_size_t)written;
        rt_thread_mdelay((rt_uint32_t)written * 1000u / 32000u + 2u);
    }
    result = rt_device_control(sound, AUDIO_CTL_STOP, &stream);
    if (diagnostics == RT_TRUE)
        rt_kprintf("fb_audio sent=%u stop=%d close=%d\r\n", (unsigned int)offset,
                   result, rt_device_close(sound));
    else (void)rt_device_close(sound);
    if (g_voice_cancel == RT_TRUE) return -RT_EINTR;
    return result;
}

static rt_bool_t voice_take(football_voice_item_t *item)
{
    rt_uint16_t i;
    if (g_queue_count == 0u) return RT_FALSE;
    *item = g_queue[0];
    for (i = 1u; i < g_queue_count; ++i) g_queue[i - 1u] = g_queue[i];
    g_queue_count--;
    g_voice_status.queue_depth = g_queue_count;
    return RT_TRUE;
}

static void voice_worker(void *parameter)
{
    football_voice_item_t item;
    char summary[FOOTBALL_COMMENTARY_MAX];

    RT_UNUSED(parameter);
    while (1)
    {
        rt_sem_take(&g_voice_sem, RT_WAITING_FOREVER);
        while (1)
        {
            rt_mutex_take(&g_voice_lock, RT_WAITING_FOREVER);
            if (voice_take(&item) == RT_FALSE)
            {
                g_voice_status.state = FOOTBALL_VOICE_IDLE;
                rt_mutex_release(&g_voice_lock);
                break;
            }
            g_voice_cancel = RT_FALSE;
            g_voice_status.active_message_id = item.message.message_id;
            g_voice_status.state = FOOTBALL_VOICE_LOCAL_PLAYING;
            rt_mutex_release(&g_voice_lock);

            voice_build_summary(&item.message, summary, sizeof(summary));
            rt_kprintf("fb_voice summary id=%u %s\r\n",
                       (unsigned int)item.message.message_id, summary);
            g_voice_status.state = FOOTBALL_VOICE_CLOUD_SPEAKING;
            rt_kprintf("fb_voice tts id=%u begin\r\n", (unsigned int)item.message.message_id);
            g_voice_status.last_error = football_cloud_speak(item.message.message_id, summary);
            rt_kprintf("fb_voice tts id=%u result=%d\r\n",
                       (unsigned int)item.message.message_id, g_voice_status.last_error);
            if (g_voice_status.last_error == RT_EOK)
            {
                g_voice_status.cloud_played++;
                g_voice_status.state = FOOTBALL_VOICE_COMPLETE;
            }
            else
            {
                g_voice_status.state = g_voice_cancel ? FOOTBALL_VOICE_CANCELLED : FOOTBALL_VOICE_FAILED;
            }
            rt_memset(summary, 0, sizeof(summary));
        }
    }
}

rt_err_t football_voice_enqueue(const football_message_t *message)
{
    football_voice_item_t item;
    rt_uint16_t position;
    if (message == RT_NULL || voice_classify(message, &item.priority, &item.prompt) == RT_FALSE)
        return -RT_EINVAL;
    item.message = *message;
    rt_mutex_take(&g_voice_lock, RT_WAITING_FOREVER);
    if (voice_seen(message->message_id) == RT_TRUE)
    {
        g_voice_status.deduplicated++;
        rt_mutex_release(&g_voice_lock);
        return RT_EOK;
    }
    if (g_queue_count >= FOOTBALL_VOICE_QUEUE_CAPACITY)
    {
        if (item.priority != 0u)
        {
            g_voice_status.dropped++;
            rt_mutex_release(&g_voice_lock);
            return -RT_EFULL;
        }
        g_queue_count--;
        g_voice_status.dropped++;
    }
    position = g_queue_count;
    while (position > 0u && g_queue[position - 1u].priority > item.priority)
    {
        g_queue[position] = g_queue[position - 1u];
        position--;
    }
    g_queue[position] = item;
    g_queue_count++;
    g_voice_status.queue_depth = g_queue_count;
    g_voice_status.state = FOOTBALL_VOICE_LOCAL_PENDING;
    if (item.priority == 0u) g_voice_cancel = RT_TRUE;
    rt_mutex_release(&g_voice_lock);
    rt_kprintf("fb_voice enqueue id=%u event=%s priority=%u queue=%u\r\n",
               (unsigned int)message->message_id, message->event, item.priority,
               (unsigned int)g_queue_count);
    rt_sem_release(&g_voice_sem);
    return RT_EOK;
}

static void football_voice_event(const FootballEvent *event, void *user)
{
    football_message_t message;
    RT_UNUSED(user);
    if (event == RT_NULL || event->event_id == EVENT_NEW_FRAME ||
        event->payload_type != FOOTBALL_EVENT_PAYLOAD_FOOTBALL_MESSAGE ||
        event->payload_size != sizeof(message)) return;
    rt_memcpy(&message, event->payload, sizeof(message));
    rt_kprintf("fb_voice event id=%u event=%s danger=%u\r\n",
               (unsigned int)message.message_id, message.event, message.danger);
    (void)football_voice_enqueue(&message);
}

rt_err_t football_voice_manual_assistant(void)
{
    char text[512];
    char reply[512];
    rt_uint32_t request = ++g_manual_request;
    rt_err_t result = football_cloud_transcribe(request, 4u, text, sizeof(text));
    if (result == RT_EOK) result = football_cloud_chat(request, text, reply, sizeof(reply));
    if (result == RT_EOK) result = football_cloud_speak(request, reply);
    rt_memset(text, 0, sizeof(text));
    rt_memset(reply, 0, sizeof(reply));
    return result;
}

void football_voice_cancel(void)
{
    g_voice_cancel = RT_TRUE;
    football_cloud_cancel(g_voice_status.active_message_id);
}

void football_voice_get_status(football_voice_status_t *status)
{
    if (status == RT_NULL) return;
    rt_mutex_take(&g_voice_lock, RT_WAITING_FOREVER);
    *status = g_voice_status;
    rt_mutex_release(&g_voice_lock);
}

rt_err_t football_voice_start(void)
{
    if (g_voice_thread != RT_NULL) return RT_EOK;
    rt_mutex_init(&g_voice_lock, "fb_voice", RT_IPC_FLAG_PRIO);
    rt_sem_init(&g_voice_sem, "fb_vq", 0u, RT_IPC_FLAG_PRIO);
    g_voice_thread = rt_thread_create("fb_voice", voice_worker, RT_NULL,
                                      FOOTBALL_VOICE_WORK_STACK, 22u, 20u);
    if (g_voice_thread == RT_NULL) return -RT_ENOMEM;
    rt_thread_startup(g_voice_thread);
    return football_event_subscribe(FOOTBALL_EVENT_ANY, football_voice_event, RT_NULL);
}

static int football_voice_cmd(int argc, char **argv)
{
    football_voice_status_t status;
    if (argc >= 2 && rt_strcmp(argv[1], "cancel") == 0) football_voice_cancel();
    else if (argc >= 2 && rt_strcmp(argv[1], "ask") == 0)
        rt_kprintf("voice ask=%d\r\n", football_voice_manual_assistant());
    else if (argc >= 2 && rt_strcmp(argv[1], "test") == 0)
    {
        rt_kprintf("sound0 present=%d\r\n", rt_device_find("sound0") != RT_NULL);
        rt_kprintf("voice local prompt=%d\r\n", voice_play_prompt(FOOTBALL_PROMPT_DANGER, RT_TRUE));
    }
    else if (argc >= 2 && rt_strcmp(argv[1], "help") == 0)
    {
        rt_kprintf("Usage: football_voice [test|ask|cancel]\r\n");
    }
    football_voice_get_status(&status);
    rt_kprintf("voice state=%d active=%u queue=%u local=%u cloud=%u dedup=%u dropped=%u error=%d\r\n",
               status.state, (unsigned int)status.active_message_id, status.queue_depth,
               (unsigned int)status.local_played, (unsigned int)status.cloud_played,
               (unsigned int)status.deduplicated, (unsigned int)status.dropped,
               status.last_error);
    return 0;
}
MSH_CMD_EXPORT_ALIAS(football_voice_cmd, football_voice, football voice status test ask or cancel);

static int football_voice_auto_init(void)
{
    return football_voice_start();
}
INIT_APP_EXPORT(football_voice_auto_init);
