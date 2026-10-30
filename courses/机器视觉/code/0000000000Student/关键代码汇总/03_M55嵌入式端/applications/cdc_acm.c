#include "usbd_core.h"
#include "usbd_cdc_acm.h"
#include <rtthread.h>
#include <finsh.h>

#define CDC_IN_EP  0x81
#define CDC_OUT_EP 0x02
#define CDC_INT_EP 0x83

#define USBD_VID           0xFFFF
#define USBD_PID           0xFFFF
#define USBD_MAX_POWER     100
#define USBD_LANGID_STRING 1033

#define USB_CONFIG_SIZE (9 + CDC_ACM_DESCRIPTOR_LEN)

#ifdef CONFIG_USB_HS
#define CDC_MAX_MPS 512
#else
#define CDC_MAX_MPS 64
#endif

/* Complete each USB packet so FBP1 framing can handle arbitrary packet boundaries. */
#define FOOTBALL_CDC_RX_TRANSFER_SIZE CDC_MAX_MPS

static const uint8_t device_descriptor[] = {
    USB_DEVICE_DESCRIPTOR_INIT(USB_2_0, 0xEF, 0x02, 0x01, USBD_VID, USBD_PID, 0x0100, 0x01)
};

static const uint8_t config_descriptor[] = {
    USB_CONFIG_DESCRIPTOR_INIT(USB_CONFIG_SIZE, 0x02, 0x01, USB_CONFIG_BUS_POWERED, USBD_MAX_POWER),
    CDC_ACM_DESCRIPTOR_INIT(0x00, CDC_INT_EP, CDC_OUT_EP, CDC_IN_EP, CDC_MAX_MPS, 0x02)
};

static const uint8_t device_quality_descriptor[] = {
    0x0a, USB_DESCRIPTOR_TYPE_DEVICE_QUALIFIER, 0x00, 0x02, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00,
};

static const char *string_descriptors[] = {
    (const char[]){ 0x09, 0x04 },
    "CherryUSB",
    "Football Tactics Console",
    "20260715",
};

static const uint8_t *device_descriptor_callback(uint8_t speed)
{
    return device_descriptor;
}

static const uint8_t *config_descriptor_callback(uint8_t speed)
{
    return config_descriptor;
}

static const uint8_t *device_quality_descriptor_callback(uint8_t speed)
{
    return device_quality_descriptor;
}

static const char *string_descriptor_callback(uint8_t speed, uint8_t index)
{
    if (index > 3) {
        return NULL;
    }
    return string_descriptors[index];
}

const struct usb_descriptor cdc_descriptor = {
    .device_descriptor_callback = device_descriptor_callback,
    .config_descriptor_callback = config_descriptor_callback,
    .device_quality_descriptor_callback = device_quality_descriptor_callback,
    .string_descriptor_callback = string_descriptor_callback
};

USB_NOCACHE_RAM_SECTION USB_MEM_ALIGNX uint8_t read_buffer[16 * 1024];
USB_NOCACHE_RAM_SECTION USB_MEM_ALIGNX uint8_t write_buffer[16 * 1024];

volatile bool ep_tx_busy_flag = false;
static rt_uint32_t g_reset_events;
static rt_uint32_t g_connected_events;
static rt_uint32_t g_disconnected_events;
static rt_uint32_t g_configured_events;
static rt_uint32_t g_out_callbacks;
static rt_uint32_t g_out_bytes;
static rt_uint32_t g_read_start_failures;
static rt_uint32_t g_write_start_failures;
static rt_uint32_t g_dtr_changes;
static rt_uint32_t g_rts_changes;
static int g_last_read_result;
static int g_last_write_result;
static bool g_dtr;
static bool g_rts;

extern int football_usb_rx_isr(const uint8_t *data, uint32_t length);
extern void football_usb_link_state(uint8_t connected);
extern void football_usb_tx_complete(void);

static void football_cdc_start_read(uint8_t busid)
{
    g_last_read_result = usbd_ep_start_read(busid, CDC_OUT_EP, read_buffer,
                                            FOOTBALL_CDC_RX_TRANSFER_SIZE);
    if (g_last_read_result != 0)
    {
        g_read_start_failures++;
    }
}

int football_usb_cdc_write(const uint8_t *data, uint32_t length)
{
    if (data == NULL || length == 0 || length > sizeof(write_buffer) || ep_tx_busy_flag) {
        return -1;
    }
    memcpy(write_buffer, data, length);
    ep_tx_busy_flag = true;
    g_last_write_result = usbd_ep_start_write(0, CDC_IN_EP, write_buffer, length);
    if (g_last_write_result != 0)
    {
        ep_tx_busy_flag = false;
        g_write_start_failures++;
    }
    return g_last_write_result;
}

static void usbd_event_handler(uint8_t busid, uint8_t event)
{
    switch (event) {
        case USBD_EVENT_RESET:
            g_reset_events++;
            ep_tx_busy_flag = false;
            football_usb_link_state(0);
            break;
        case USBD_EVENT_CONNECTED:
            g_connected_events++;
            football_usb_link_state(1);
            break;
        case USBD_EVENT_DISCONNECTED:
            g_disconnected_events++;
            football_usb_link_state(0);
            break;
        case USBD_EVENT_CONFIGURED:
            g_configured_events++;
            ep_tx_busy_flag = false;
            football_usb_link_state(1);
            football_cdc_start_read(busid);
            break;
        default:
            break;
    }
}

void usbd_cdc_acm_bulk_out(uint8_t busid, uint8_t ep, uint32_t nbytes)
{
    g_out_callbacks++;
    g_out_bytes += nbytes;
    if (nbytes != 0) {
        (void)football_usb_rx_isr(read_buffer, nbytes);
    }
    football_cdc_start_read(busid);
}

void usbd_cdc_acm_bulk_in(uint8_t busid, uint8_t ep, uint32_t nbytes)
{
    if ((nbytes % usbd_get_ep_mps(busid, ep)) == 0 && nbytes) {
        usbd_ep_start_write(busid, CDC_IN_EP, NULL, 0);
    } else {
        ep_tx_busy_flag = false;
        football_usb_tx_complete();
    }
}

struct usbd_endpoint cdc_out_ep = {
    .ep_addr = CDC_OUT_EP,
    .ep_cb = usbd_cdc_acm_bulk_out
};

struct usbd_endpoint cdc_in_ep = {
    .ep_addr = CDC_IN_EP,
    .ep_cb = usbd_cdc_acm_bulk_in
};

static struct usbd_interface intf0;
static struct usbd_interface intf1;

static int football_cdc_cmd(int argc, char **argv)
{
    RT_UNUSED(argc);
    RT_UNUSED(argv);
    rt_kprintf("cdc reset=%u connected=%u disconnected=%u configured=%u out_calls=%u out_bytes=%u read_fail=%u write_fail=%u dtr=%d rts=%d dtr_changes=%u rts_changes=%u last_read=%d last_write=%d tx_busy=%d\r\n",
               (unsigned int)g_reset_events, (unsigned int)g_connected_events,
               (unsigned int)g_disconnected_events, (unsigned int)g_configured_events,
               (unsigned int)g_out_callbacks, (unsigned int)g_out_bytes,
               (unsigned int)g_read_start_failures, (unsigned int)g_write_start_failures,
               g_dtr, g_rts, (unsigned int)g_dtr_changes, (unsigned int)g_rts_changes,
               g_last_read_result, g_last_write_result, ep_tx_busy_flag);
    return 0;
}
MSH_CMD_EXPORT_ALIAS(football_cdc_cmd, football_cdc, football USB CDC status);

void usbd_cdc_acm_set_dtr(uint8_t busid, uint8_t intf, bool dtr)
{
    RT_UNUSED(busid);
    RT_UNUSED(intf);
    g_dtr = dtr;
    g_dtr_changes++;
}

void usbd_cdc_acm_set_rts(uint8_t busid, uint8_t intf, bool rts)
{
    RT_UNUSED(busid);
    RT_UNUSED(intf);
    g_rts = rts;
    g_rts_changes++;
}

static int cherryusb_device_cdc_acm_init(void)
{
    usbd_desc_register(0, &cdc_descriptor);
    usbd_add_interface(0, usbd_cdc_acm_init_intf(0, &intf0));
    usbd_add_interface(0, usbd_cdc_acm_init_intf(0, &intf1));
    usbd_add_endpoint(0, &cdc_out_ep);
    usbd_add_endpoint(0, &cdc_in_ep);
    usbd_initialize(0, USBHS_BASE, usbd_event_handler);
    return 0;
}
INIT_APP_EXPORT(cherryusb_device_cdc_acm_init);
