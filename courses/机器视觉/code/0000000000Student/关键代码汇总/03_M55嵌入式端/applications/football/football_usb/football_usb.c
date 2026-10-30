#include "football_usb.h"
#include "../football_link/football_link.h"
#include "../football_event/football_event.h"
#include "../football_protocol/football_protocol.h"
#include "../football_settings/football_settings.h"

#include <finsh.h>

#define FOOTBALL_USB_RX_RING_SIZE 8192u
#define FOOTBALL_USB_WORK_STACK   6144u
#define FOOTBALL_USB_WORK_PRIO    18u
#define FOOTBALL_USB_TX_BUFFER_SIZE (sizeof(football_wire_header_t) + FOOTBALL_WIRE_MAX_PAYLOAD)

extern int football_usb_cdc_write(const rt_uint8_t *data, rt_uint32_t length);

static rt_uint8_t g_rx_ring[FOOTBALL_USB_RX_RING_SIZE];
static volatile rt_uint32_t g_rx_head;
static volatile rt_uint32_t g_rx_tail;
static struct rt_semaphore g_rx_sem;
static struct rt_semaphore g_tx_sem;
static football_wire_decoder_t g_decoder;
static rt_thread_t g_worker;
static volatile rt_bool_t g_connected;
static rt_uint32_t g_tx_sequence = 1u;
static rt_uint32_t g_last_sequence;
static rt_uint32_t g_rx_bytes;
static rt_uint32_t g_tx_frames;
static rt_uint32_t g_rx_frames;
static rt_uint32_t g_duplicates;
static rt_uint32_t g_dropped;
static rt_uint32_t g_parse_failures;
static rt_uint32_t g_ack_failures;
static rt_uint32_t g_tx_failures;

static rt_err_t football_usb_write(const rt_uint8_t *data, rt_size_t length)
{
    rt_tick_t deadline = rt_tick_get() + rt_tick_from_millisecond(500);
    while (football_usb_cdc_write(data, (rt_uint32_t)length) != 0)
    {
        if ((rt_int32_t)(deadline - rt_tick_get()) <= 0)
        {
            g_tx_failures++;
            rt_kprintf("fb_usb tx timeout len=%u connected=%d\r\n",
                       (unsigned int)length, g_connected);
            return -RT_ETIMEOUT;
        }
        (void)rt_sem_take(&g_tx_sem, rt_tick_from_millisecond(20));
    }
    return RT_EOK;
}

rt_err_t football_usb_send_frame(rt_uint8_t type,
                                 rt_uint16_t flags,
                                 rt_uint32_t sequence,
                                 rt_uint32_t acknowledgement,
                                 const void *payload,
                                 rt_size_t length)
{
    football_wire_header_t header;
    rt_uint8_t *output;
    rt_size_t written;
    rt_err_t result;
    if (length > FOOTBALL_WIRE_MAX_PAYLOAD)
    {
        return -RT_EINVAL;
    }
    output = (rt_uint8_t *)rt_malloc(FOOTBALL_USB_TX_BUFFER_SIZE);
    if (output == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    rt_memset(&header, 0, sizeof(header));
    header.type = type;
    header.flags = flags;
    header.sequence = sequence;
    header.acknowledgement = acknowledgement;
    header.payload_length = (rt_uint32_t)length;
    result = football_wire_encode(&header, (const rt_uint8_t *)payload,
                                  output, FOOTBALL_USB_TX_BUFFER_SIZE, &written);
    if (result == RT_EOK)
    {
        result = football_usb_write(output, written);
        if (result == RT_EOK)
        {
            g_tx_frames++;
        }
    }
    if (result != RT_EOK)
    {
        rt_kprintf("fb_usb tx type=%u seq=%u ack=%u result=%d\r\n",
                   (unsigned int)type, (unsigned int)sequence,
                   (unsigned int)acknowledgement, result);
    }
    rt_free(output);
    return result;
}

static rt_err_t football_usb_ack(rt_uint32_t sequence, const char *status)
{
    return football_usb_send_frame(FOOTBALL_MSG_ACK, 0u, g_tx_sequence++, sequence,
                                   status, rt_strlen(status));
}

static rt_err_t football_usb_handle_frame(const football_wire_header_t *header,
                                          const rt_uint8_t *payload,
                                          void *user)
{
    rt_err_t result = RT_EOK;
    rt_err_t ack_result;
    football_message_t event_msg;
    rt_bool_t has_match_event = RT_FALSE;

    RT_UNUSED(user);
    g_rx_frames++;
    rt_kprintf("fb_usb rx seq=%u type=%u len=%u\r\n",
               (unsigned int)header->sequence, (unsigned int)header->type,
               (unsigned int)header->payload_length);
    if (header->sequence == g_last_sequence && header->sequence != 0u)
    {
        g_duplicates++;
        ack_result = football_usb_ack(header->sequence, "{\"status\":\"duplicate\"}");
        if (ack_result != RT_EOK)
        {
            g_ack_failures++;
        }
        rt_kprintf("fb_usb ack seq=%u result=%d duplicate=1\r\n",
                   (unsigned int)header->sequence, ack_result);
        return ack_result;
    }
    if (header->payload_length > FOOTBALL_WIRE_MAX_PAYLOAD)
    {
        return -RT_EINVAL;
    }
    if (header->type == FOOTBALL_MSG_MATCH_EVENT ||
        header->type == FOOTBALL_MSG_WIFI_CONFIG ||
        header->type == FOOTBALL_MSG_CLOUD_CONFIG)
    {
        char *json = (char *)rt_malloc(header->payload_length + 1u);
        if (json == RT_NULL)
        {
            result = -RT_ENOMEM;
        }
        else
        {
            rt_memcpy(json, payload, header->payload_length);
            json[header->payload_length] = '\0';
            if (header->type == FOOTBALL_MSG_MATCH_EVENT)
            {
                if (football_protocol_parse_json(json, &event_msg) == RT_EOK)
                {
                    has_match_event = RT_TRUE;
                }
                else
                {
                    result = -RT_ERROR;
                }
            }
            else
            {
                result = football_settings_apply_json(header->type, json,
                                                      header->payload_length);
            }
            rt_free(json);
        }
    }
    else if (header->type == FOOTBALL_MSG_CONFIG_CLEAR)
    {
        result = football_settings_clear();
    }
    else if (header->type != FOOTBALL_MSG_HELLO &&
             header->type != FOOTBALL_MSG_HEARTBEAT &&
             header->type != FOOTBALL_MSG_MATCH_STATE &&
             header->type != FOOTBALL_MSG_TACTICS_SNAPSHOT &&
             header->type != FOOTBALL_MSG_TACTICS_OPERATION &&
             header->type != FOOTBALL_MSG_VOICE_CONTROL &&
             header->type != FOOTBALL_MSG_CONFIG_STATUS)
    {
        result = -RT_ENOSYS;
    }
    if (result == RT_EOK)
    {
        g_last_sequence = header->sequence;
    }
    else
    {
        g_parse_failures++;
    }
    rt_kprintf("fb_usb parse seq=%u result=%d event=%d\r\n",
               (unsigned int)header->sequence, result, has_match_event);

    /* Send ACK/ERROR immediately, before event dispatch */
    if (result == RT_EOK)
    {
        ack_result = football_usb_ack(header->sequence, "{\"status\":\"accepted\"}");
    }
    else
    {
        ack_result = football_usb_send_frame(FOOTBALL_MSG_ERROR, (rt_uint16_t)(-result),
                                             g_tx_sequence++, header->sequence,
                                             "{\"status\":\"rejected\"}", 21u);
    }
    if (ack_result != RT_EOK)
    {
        g_ack_failures++;
    }
    rt_kprintf("fb_usb ack seq=%u result=%d\r\n",
               (unsigned int)header->sequence, ack_result);

    /* Dispatch match event synchronously after ACK sent */
    if (has_match_event)
    {
        football_event_apply_sync(&event_msg);
    }

    return result;
}

static rt_size_t football_usb_drain(rt_uint8_t *output, rt_size_t capacity)
{
    rt_base_t level = rt_hw_interrupt_disable();
    rt_size_t used = 0u;
    while (used < capacity && g_rx_tail != g_rx_head)
    {
        output[used++] = g_rx_ring[g_rx_tail];
        g_rx_tail = (g_rx_tail + 1u) % FOOTBALL_USB_RX_RING_SIZE;
    }
    rt_hw_interrupt_enable(level);
    return used;
}

static void football_usb_worker(void *parameter)
{
    rt_uint8_t chunk[256];
    RT_UNUSED(parameter);
    while (1)
    {
        rt_size_t length;
        (void)rt_sem_take(&g_rx_sem, rt_tick_from_millisecond(100));
        while ((length = football_usb_drain(chunk, sizeof(chunk))) != 0u)
        {
            (void)football_wire_decoder_feed(&g_decoder, chunk, length,
                                             football_usb_handle_frame, RT_NULL);
        }
    }
}

int football_usb_rx_isr(const rt_uint8_t *data, rt_uint32_t length)
{
    rt_uint32_t i;
    rt_base_t level;
    if (data == RT_NULL)
    {
        return -1;
    }
    level = rt_hw_interrupt_disable();
    for (i = 0u; i < length; ++i)
    {
        rt_uint32_t next = (g_rx_head + 1u) % FOOTBALL_USB_RX_RING_SIZE;
        if (next == g_rx_tail)
        {
            g_dropped += length - i;
            break;
        }
        g_rx_ring[g_rx_head] = data[i];
        g_rx_head = next;
        g_rx_bytes++;
    }
    rt_hw_interrupt_enable(level);
    rt_sem_release(&g_rx_sem);
    return 0;
}

void football_usb_link_state(rt_uint8_t connected)
{
    g_connected = connected ? RT_TRUE : RT_FALSE;
}

void football_usb_tx_complete(void)
{
    rt_sem_release(&g_tx_sem);
}

void football_usb_status(void)
{
    rt_kprintf("usb connected=%d rx_bytes=%u rx_frames=%u tx_frames=%u duplicate=%u dropped=%u crc=%u length=%u parse_fail=%u ack_fail=%u tx_fail=%u\r\n",
               g_connected, (unsigned int)g_rx_bytes, (unsigned int)g_rx_frames,
               (unsigned int)g_tx_frames, (unsigned int)g_duplicates,
               (unsigned int)g_dropped, (unsigned int)g_decoder.crc_errors,
               (unsigned int)g_decoder.length_errors, (unsigned int)g_parse_failures,
               (unsigned int)g_ack_failures, (unsigned int)g_tx_failures);
}

static int football_usb_cmd(int argc, char **argv)
{
    RT_UNUSED(argc);
    RT_UNUSED(argv);
    football_usb_status();
    return 0;
}
MSH_CMD_EXPORT_ALIAS(football_usb_cmd, football_usb, football USB protocol status);

static int football_usb_init(void)
{
    football_wire_decoder_init(&g_decoder);
    rt_sem_init(&g_rx_sem, "fb_rx", 0u, RT_IPC_FLAG_PRIO);
    rt_sem_init(&g_tx_sem, "fb_tx", 0u, RT_IPC_FLAG_PRIO);
    g_worker = rt_thread_create("fb_usb", football_usb_worker, RT_NULL,
                                FOOTBALL_USB_WORK_STACK, FOOTBALL_USB_WORK_PRIO, 10u);
    if (g_worker == RT_NULL)
    {
        return -RT_ENOMEM;
    }
    rt_thread_startup(g_worker);
    return RT_EOK;
}
INIT_APP_EXPORT(football_usb_init);
