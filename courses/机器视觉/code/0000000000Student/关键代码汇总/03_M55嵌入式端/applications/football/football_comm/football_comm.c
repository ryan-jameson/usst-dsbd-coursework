#include "football_comm.h"
#include "football_event.h"
#include "../football_link/football_link.h"
#include "../football_settings/football_settings.h"

#include <finsh.h>
#include <rtdevice.h>

#include "../../libraries/HAL_Drivers/drv_ipc.h"

#define FOOTBALL_COMM_RX_STACK 4096
#define FOOTBALL_COMM_RX_PRIORITY 21
#define FOOTBALL_COMM_RX_TICK 20

static rt_thread_t g_comm_thread = RT_NULL;
static volatile rt_bool_t g_comm_running = RT_FALSE;
static rt_uint32_t g_rx_messages;
static rt_uint32_t g_bad_magic;
static rt_uint32_t g_ipc_reads;
static rt_uint32_t g_last_m33_seq;
static rt_uint32_t g_publish_fail;
static rt_uint32_t g_tx_messages;
static volatile football_shared_region_t *g_shared;
static rt_uint32_t g_m55_boot_id;

rt_err_t football_comm_publish_to_m33(rt_uint8_t type, rt_uint16_t flags,
                                      rt_uint32_t sequence,
                                      const void *payload, rt_size_t length)
{
    rt_err_t result;
    if (g_shared == RT_NULL || football_shared_region_valid(g_shared) == RT_FALSE)
    {
        return -RT_ERROR;
    }
    result = football_shared_ring_push(&g_shared->m55_to_m33, type, flags,
                                       sequence, (rt_uint32_t)rt_tick_get(), 1u,
                                       payload, length);
    if (result == RT_EOK)
    {
        g_tx_messages++;
    }
    else
    {
        g_publish_fail++;
    }
    return result;
}

static void football_comm_drain_shared_memory(void)
{
    football_shared_entry_t shared_event;
    football_message_t message;
    FootballEvent event;

    if (g_shared == RT_NULL || football_shared_region_valid(g_shared) == RT_FALSE)
    {
        g_bad_magic++;
        return;
    }
    while (football_shared_ring_pop(&g_shared->m33_to_m55, &shared_event) == RT_EOK)
    {
        if (shared_event.type == FOOTBALL_MSG_WIFI_CONFIG ||
            shared_event.type == FOOTBALL_MSG_CLOUD_CONFIG)
        {
            char json[FOOTBALL_SHARED_ENTRY_PAYLOAD + 1u];
            rt_memcpy(json, shared_event.payload, shared_event.payload_length);
            json[shared_event.payload_length] = '\0';
            if (football_settings_apply_json((rt_uint8_t)shared_event.type, json,
                                             shared_event.payload_length) != RT_EOK)
            {
                g_publish_fail++;
            }
            else
            {
                g_rx_messages++;
            }
            rt_memset(json, 0, sizeof(json));
            continue;
        }
        if (shared_event.type == FOOTBALL_MSG_CONFIG_CLEAR)
        {
            if (football_settings_clear() != RT_EOK)
            {
                g_publish_fail++;
            }
            else
            {
                g_rx_messages++;
            }
            continue;
        }
        if (shared_event.type != FOOTBALL_MSG_MATCH_EVENT ||
            shared_event.payload_length != sizeof(message))
        {
            g_publish_fail++;
            continue;
        }
        rt_memcpy(&message, shared_event.payload, sizeof(message));
        if (football_event_build_from_message(&message, FOOTBALL_EVENT_SOURCE_COMM, &event) != RT_EOK)
        {
            g_publish_fail++;
            continue;
        }
        event.event_id = shared_event.flags;
        if (football_event_publish(&event) != RT_EOK)
        {
            g_publish_fail++;
            continue;
        }
        g_last_m33_seq = shared_event.sequence;
        g_rx_messages++;
    }
}

static void football_comm_rx_entry(void *parameter)
{
    rt_device_t ipc;
    edge_rc_frame_t frame;

    RT_UNUSED(parameter);

    ipc = rt_device_find(EDGE_IPC_DEVICE_NAME);
    if (ipc != RT_NULL)
    {
        rt_device_open(ipc, RT_DEVICE_FLAG_RDWR | RT_DEVICE_FLAG_INT_RX);
    }

    while (g_comm_running == RT_TRUE)
    {
        if (football_shared_region_valid(g_shared) == RT_TRUE && g_shared->m55_boot_id != g_m55_boot_id)
        {
            g_shared->m55_boot_id = g_m55_boot_id;
        }
        if (football_shared_region_valid(g_shared) == RT_TRUE)
        {
            g_shared->m55_heartbeat++;
        }
        if (ipc != RT_NULL)
        {
            while (rt_device_read(ipc, 0, &frame, 1) == 1)
            {
                g_ipc_reads++;
                football_comm_drain_shared_memory();
            }
        }

        football_comm_drain_shared_memory();
        rt_thread_mdelay(100);
    }

    g_comm_thread = RT_NULL;
}

rt_err_t football_comm_start(void)
{
    if (g_comm_running == RT_TRUE)
    {
        return RT_EOK;
    }

    g_shared = football_shared_region_get();
    g_m55_boot_id = (rt_uint32_t)rt_tick_get();
    if (g_m55_boot_id == 0u)
    {
        g_m55_boot_id = 1u;
    }
    if (football_shared_region_valid(g_shared) == RT_TRUE)
    {
        g_shared->m55_boot_id = g_m55_boot_id;
    }
    g_comm_running = RT_TRUE;
    g_comm_thread = rt_thread_create("fb_comm",
                                     football_comm_rx_entry,
                                     RT_NULL,
                                     FOOTBALL_COMM_RX_STACK,
                                     FOOTBALL_COMM_RX_PRIORITY,
                                     FOOTBALL_COMM_RX_TICK);
    if (g_comm_thread == RT_NULL)
    {
        g_comm_running = RT_FALSE;
        return -RT_ENOMEM;
    }

    rt_thread_startup(g_comm_thread);
    return RT_EOK;
}

void football_comm_status(void)
{
    rt_kprintf("comm shared-ring rx running=%d messages=%u tx=%u invalid_region=%u ipc_reads=%u last_seq=%u publish_fail=%u boot=%u\r\n",
               g_comm_running,
               (unsigned int)g_rx_messages,
               (unsigned int)g_tx_messages,
               (unsigned int)g_bad_magic,
               (unsigned int)g_ipc_reads,
               (unsigned int)g_last_m33_seq,
               (unsigned int)g_publish_fail,
               (unsigned int)g_m55_boot_id);
}

static int football_m55(int argc, char **argv)
{
    RT_UNUSED(argc);
    RT_UNUSED(argv);

    football_comm_status();
    football_event_status();
    return 0;
}
MSH_CMD_EXPORT(football_m55, AI football M55 receiver status);

static int football_comm_auto_init(void)
{
    return football_comm_start();
}
INIT_APP_EXPORT(football_comm_auto_init);
