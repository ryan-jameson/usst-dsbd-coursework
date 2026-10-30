#ifndef FOOTBALL_LINK_H
#define FOOTBALL_LINK_H

#include <rtthread.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FOOTBALL_WIRE_MAGIC_U32       0x31504246u
#define FOOTBALL_WIRE_VERSION         1u
#define FOOTBALL_WIRE_MAX_PAYLOAD     4096u
#define FOOTBALL_WIRE_BUFFER_SIZE     (FOOTBALL_WIRE_MAX_PAYLOAD + 64u)

#define FOOTBALL_LINK_SHARED_MAGIC    0x52425346u
#define FOOTBALL_SHARED_ABI_VERSION   1u
#define FOOTBALL_SHARED_ENTRY_PAYLOAD 512u
#define FOOTBALL_SHARED_RING_CAPACITY 64u

typedef enum
{
    FOOTBALL_MSG_HELLO = 0x01,
    FOOTBALL_MSG_HEARTBEAT = 0x02,
    FOOTBALL_MSG_ACK = 0x03,
    FOOTBALL_MSG_ERROR = 0x04,
    FOOTBALL_MSG_MATCH_STATE = 0x10,
    FOOTBALL_MSG_MATCH_EVENT = 0x11,
    FOOTBALL_MSG_TACTICS_SNAPSHOT = 0x20,
    FOOTBALL_MSG_TACTICS_OPERATION = 0x21,
    FOOTBALL_MSG_VOICE_CONTROL = 0x30,
    FOOTBALL_MSG_VOICE_STATUS = 0x31,
    FOOTBALL_MSG_DEVICE_STATUS = 0x40,
    FOOTBALL_MSG_LOG_STATUS = 0x41,
    FOOTBALL_MSG_WIFI_CONFIG = 0x50,
    FOOTBALL_MSG_CLOUD_CONFIG = 0x51,
    FOOTBALL_MSG_CONFIG_STATUS = 0x52,
    FOOTBALL_MSG_CONFIG_CLEAR = 0x53
} football_message_type_t;

typedef enum
{
    FOOTBALL_LINK_OK = 0,
    FOOTBALL_LINK_ERR_MAGIC = 1,
    FOOTBALL_LINK_ERR_VERSION = 2,
    FOOTBALL_LINK_ERR_LENGTH = 3,
    FOOTBALL_LINK_ERR_CRC = 4,
    FOOTBALL_LINK_ERR_QUEUE_FULL = 5,
    FOOTBALL_LINK_ERR_PEER_RESET = 6
} football_link_error_t;

typedef struct football_wire_header
{
    rt_uint8_t magic[4];
    rt_uint8_t version;
    rt_uint8_t type;
    rt_uint16_t flags;
    rt_uint32_t sequence;
    rt_uint32_t acknowledgement;
    rt_uint32_t payload_length;
    rt_uint32_t crc32;
} football_wire_header_t;

typedef struct football_wire_frame
{
    football_wire_header_t header;
    rt_uint8_t payload[FOOTBALL_WIRE_MAX_PAYLOAD];
} football_wire_frame_t;

typedef rt_err_t (*football_wire_frame_handler_t)(const football_wire_header_t *header,
                                                   const rt_uint8_t *payload,
                                                   void *user);

typedef struct football_wire_decoder
{
    rt_uint8_t buffer[FOOTBALL_WIRE_BUFFER_SIZE];
    rt_size_t used;
    rt_uint32_t discarded_bytes;
    rt_uint32_t crc_errors;
    rt_uint32_t length_errors;
    rt_uint32_t version_errors;
} football_wire_decoder_t;

typedef struct football_shared_entry
{
    rt_uint16_t type;
    rt_uint16_t flags;
    rt_uint32_t sequence;
    rt_uint32_t timestamp_ms;
    rt_uint16_t payload_length;
    rt_uint16_t priority;
    rt_uint32_t crc32;
    rt_uint8_t payload[FOOTBALL_SHARED_ENTRY_PAYLOAD];
} football_shared_entry_t;

typedef struct football_shared_ring
{
    volatile rt_uint32_t producer;
    volatile rt_uint32_t consumer;
    volatile rt_uint32_t dropped;
    volatile rt_uint32_t corrupt;
    football_shared_entry_t entries[FOOTBALL_SHARED_RING_CAPACITY];
} football_shared_ring_t;

typedef struct football_shared_region
{
    rt_uint32_t magic;
    rt_uint16_t abi_version;
    rt_uint16_t header_size;
    rt_uint32_t region_size;
    volatile rt_uint32_t m33_boot_id;
    volatile rt_uint32_t m55_boot_id;
    volatile rt_uint32_t m33_heartbeat;
    volatile rt_uint32_t m55_heartbeat;
    volatile rt_uint32_t reset_count;
    volatile rt_uint32_t flags;
    football_shared_ring_t m33_to_m55;
    football_shared_ring_t m55_to_m33;
} football_shared_region_t;

typedef char football_wire_header_must_be_24_bytes[(sizeof(football_wire_header_t) == 24u) ? 1 : -1];

void football_wire_decoder_init(football_wire_decoder_t *decoder);
rt_uint32_t football_crc32(const void *data, rt_size_t length, rt_uint32_t seed);
rt_uint32_t football_wire_crc(const football_wire_header_t *header, const rt_uint8_t *payload);
rt_err_t football_wire_encode(const football_wire_header_t *header,
                              const rt_uint8_t *payload,
                              rt_uint8_t *output,
                              rt_size_t output_size,
                              rt_size_t *written);
rt_err_t football_wire_decoder_feed(football_wire_decoder_t *decoder,
                                    const rt_uint8_t *data,
                                    rt_size_t length,
                                    football_wire_frame_handler_t handler,
                                    void *user);

void football_shared_region_reset(volatile football_shared_region_t *region,
                                  rt_uint32_t m33_boot_id);
rt_bool_t football_shared_region_valid(const volatile football_shared_region_t *region);
volatile football_shared_region_t *football_shared_region_get(void);
rt_err_t football_shared_ring_push(volatile football_shared_ring_t *ring,
                                   rt_uint16_t type,
                                   rt_uint16_t flags,
                                   rt_uint32_t sequence,
                                   rt_uint32_t timestamp_ms,
                                   rt_uint16_t priority,
                                   const void *payload,
                                   rt_size_t length);
rt_err_t football_shared_ring_pop(volatile football_shared_ring_t *ring,
                                  football_shared_entry_t *entry);

#ifdef __cplusplus
}
#endif
#endif
