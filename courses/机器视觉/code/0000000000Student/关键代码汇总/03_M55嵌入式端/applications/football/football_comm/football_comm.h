#ifndef FOOTBALL_COMM_H
#define FOOTBALL_COMM_H

#include "football_protocol.h"

#ifdef __cplusplus
extern "C" {
#endif

rt_err_t football_comm_start(void);
rt_err_t football_comm_publish_to_m33(rt_uint8_t type, rt_uint16_t flags,
                                      rt_uint32_t sequence,
                                      const void *payload, rt_size_t length);
void football_comm_status(void);

#ifdef __cplusplus
}
#endif

#endif
