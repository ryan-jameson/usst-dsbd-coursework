#ifndef FOOTBALL_USB_H
#define FOOTBALL_USB_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

int football_usb_rx_isr(const rt_uint8_t *data, rt_uint32_t length);
void football_usb_link_state(rt_uint8_t connected);
void football_usb_tx_complete(void);
rt_err_t football_usb_send_frame(rt_uint8_t type,
                                 rt_uint16_t flags,
                                 rt_uint32_t sequence,
                                 rt_uint32_t acknowledgement,
                                 const void *payload,
                                 rt_size_t length);
void football_usb_status(void);

#ifdef __cplusplus
}
#endif
#endif
