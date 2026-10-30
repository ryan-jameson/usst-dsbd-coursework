#ifndef FOOTBALL_STORAGE_H
#define FOOTBALL_STORAGE_H

#include "football_protocol.h"

#ifdef __cplusplus
extern "C" {
#endif

rt_err_t football_storage_append(const football_message_t *message);
void football_storage_status(void);

#ifdef __cplusplus
}
#endif

#endif
