#ifndef __JSON_UTIL_H__
#define __JSON_UTIL_H__

#include <rtthread.h>

int json_util_escape(const char *src, char *dst, rt_size_t dst_size);
int json_util_get_string(const char *json, const char *key, char *dst, rt_size_t dst_size);
int json_util_get_path_string(const char *json, const char *path,
                               char *dst, rt_size_t dst_size);

#endif /* __JSON_UTIL_H__ */
