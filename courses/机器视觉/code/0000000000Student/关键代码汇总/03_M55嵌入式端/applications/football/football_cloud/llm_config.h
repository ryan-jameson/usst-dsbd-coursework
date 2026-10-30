#ifndef FOOTBALL_LLM_CONFIG_H
#define FOOTBALL_LLM_CONFIG_H

#include "../football_settings/football_settings.h"

const football_settings_t *football_cloud_runtime_config(void);

#define LLM_API_URL                 (football_cloud_runtime_config()->ai_endpoint)
#define LLM_SERVER_AUTH             (football_cloud_runtime_config()->ai_api_key)
#define LLM_MODEL                   (football_cloud_runtime_config()->ai_model)
#define LLM_HEADER_BUFFER_SIZE      1536
#define LLM_RESPONSE_BUFFER_SIZE    4096
#define LLM_ASSISTANT_MAX_TOKENS    120
#define LLM_ASSISTANT_MAX_BYTES     300
#define LLM_ASSISTANT_SYSTEM_PROMPT "你是足球比赛战术分析助手。使用简体中文，在两句话内说明事件影响和建议，不使用Markdown。"

#define TENCENT_ASR_API_URL         "https://asr.tencentcloudapi.com"
#define TENCENT_ASR_HOST            "asr.tencentcloudapi.com"
#define TENCENT_ASR_REGION          "ap-shanghai"
#define TENCENT_ASR_SECRET_ID       "REDACTED_CONFIGURE_LOCALLY"
#define TENCENT_ASR_SECRET_KEY      "REDACTED_CONFIGURE_LOCALLY"
#define TENCENT_ASR_ENGINE_TYPE     "16k_zh"
#define SPEECH_RECORD_SECONDS       4
#define SPEECH_SAMPLE_RATE          16000
#define SPEECH_RESPONSE_BUFFER_SIZE 2048

#define TENCENT_TTS_API_URL         "https://tts.tencentcloudapi.com"
#define TENCENT_TTS_HOST            "tts.tencentcloudapi.com"
#define TENCENT_TTS_VOICE_TYPE      1001
#define TENCENT_TTS_PRIMARY_LANGUAGE 1
#define TENCENT_TTS_SAMPLE_RATE     16000
#define TENCENT_TTS_MAX_TEXT_LEN    300

#endif
