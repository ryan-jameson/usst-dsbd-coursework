#include "football_link.h"
#include <rthw.h>
#include "cybsp.h"

#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
#define FOOTBALL_CACHE_CLEAN(addr, size) SCB_CleanDCache_by_Addr((void *)(addr), (int32_t)(size))
#define FOOTBALL_CACHE_INVALIDATE(addr, size) SCB_InvalidateDCache_by_Addr((void *)(addr), (int32_t)(size))
#else
#define FOOTBALL_CACHE_CLEAN(addr, size) ((void)0)
#define FOOTBALL_CACHE_INVALIDATE(addr, size) ((void)0)
#endif

static const rt_uint8_t g_wire_magic[4] = {'F', 'B', 'P', '1'};
extern rt_uint8_t __football_shared_start__;

static void football_copy_from_volatile(void *dst, const volatile void *src, rt_size_t length)
{
    rt_uint8_t *out = (rt_uint8_t *)dst;
    const volatile rt_uint8_t *in = (const volatile rt_uint8_t *)src;
    while (length-- != 0u)
    {
        *out++ = *in++;
    }
}

static void football_copy_to_volatile(volatile void *dst, const void *src, rt_size_t length)
{
    volatile rt_uint8_t *out = (volatile rt_uint8_t *)dst;
    const rt_uint8_t *in = (const rt_uint8_t *)src;
    while (length-- != 0u)
    {
        *out++ = *in++;
    }
}

static rt_bool_t football_has_magic(const rt_uint8_t *data)
{
    return (data[0] == g_wire_magic[0] && data[1] == g_wire_magic[1] &&
            data[2] == g_wire_magic[2] && data[3] == g_wire_magic[3]) ? RT_TRUE : RT_FALSE;
}

static void football_decoder_discard(football_wire_decoder_t *decoder, rt_size_t count)
{
    rt_size_t i;
    if (count >= decoder->used)
    {
        decoder->discarded_bytes += decoder->used;
        decoder->used = 0u;
        return;
    }
    for (i = 0u; i < decoder->used - count; ++i)
    {
        decoder->buffer[i] = decoder->buffer[i + count];
    }
    decoder->used -= count;
    decoder->discarded_bytes += count;
}

void football_wire_decoder_init(football_wire_decoder_t *decoder)
{
    if (decoder != RT_NULL)
    {
        rt_memset(decoder, 0, sizeof(*decoder));
    }
}

rt_uint32_t football_crc32(const void *data, rt_size_t length, rt_uint32_t seed)
{
    const rt_uint8_t *bytes = (const rt_uint8_t *)data;
    rt_uint32_t crc = seed ^ 0xffffffffu;
    rt_size_t i;
    rt_uint8_t bit;
    for (i = 0u; i < length; ++i)
    {
        crc ^= bytes[i];
        for (bit = 0u; bit < 8u; ++bit)
        {
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
        }
    }
    return crc ^ 0xffffffffu;
}

rt_uint32_t football_wire_crc(const football_wire_header_t *header, const rt_uint8_t *payload)
{
    football_wire_header_t copy;
    rt_uint32_t crc;
    if (header == RT_NULL)
    {
        return 0u;
    }
    copy = *header;
    copy.crc32 = 0u;
    crc = football_crc32(&copy, sizeof(copy), 0u);
    if (payload != RT_NULL && header->payload_length != 0u)
    {
        crc = football_crc32(payload, header->payload_length, crc);
    }
    return crc;
}

rt_err_t football_wire_encode(const football_wire_header_t *header,
                              const rt_uint8_t *payload,
                              rt_uint8_t *output,
                              rt_size_t output_size,
                              rt_size_t *written)
{
    football_wire_header_t copy;
    rt_size_t total;
    if (header == RT_NULL || output == RT_NULL || written == RT_NULL)
    {
        return -RT_EINVAL;
    }
    if (header->payload_length > FOOTBALL_WIRE_MAX_PAYLOAD ||
        (header->payload_length != 0u && payload == RT_NULL))
    {
        return -RT_EINVAL;
    }
    total = sizeof(copy) + header->payload_length;
    if (output_size < total)
    {
        return -RT_EFULL;
    }
    copy = *header;
    rt_memcpy(copy.magic, g_wire_magic, sizeof(copy.magic));
    copy.version = FOOTBALL_WIRE_VERSION;
    copy.crc32 = football_wire_crc(&copy, payload);
    rt_memcpy(output, &copy, sizeof(copy));
    if (copy.payload_length != 0u)
    {
        rt_memcpy(output + sizeof(copy), payload, copy.payload_length);
    }
    *written = total;
    return RT_EOK;
}

rt_err_t football_wire_decoder_feed(football_wire_decoder_t *decoder,
                                    const rt_uint8_t *data,
                                    rt_size_t length,
                                    football_wire_frame_handler_t handler,
                                    void *user)
{
    rt_size_t offset = 0u;
    if (decoder == RT_NULL || (length != 0u && data == RT_NULL))
    {
        return -RT_EINVAL;
    }
    while (offset < length)
    {
        rt_size_t space = sizeof(decoder->buffer) - decoder->used;
        rt_size_t chunk = length - offset;
        if (space == 0u)
        {
            football_decoder_discard(decoder, 1u);
            space = 1u;
        }
        if (chunk > space)
        {
            chunk = space;
        }
        rt_memcpy(decoder->buffer + decoder->used, data + offset, chunk);
        decoder->used += chunk;
        offset += chunk;

        while (decoder->used >= 4u)
        {
            football_wire_header_t header;
            rt_size_t total;
            if (football_has_magic(decoder->buffer) == RT_FALSE)
            {
                football_decoder_discard(decoder, 1u);
                continue;
            }
            if (decoder->used < sizeof(header))
            {
                break;
            }
            rt_memcpy(&header, decoder->buffer, sizeof(header));
            if (header.payload_length > FOOTBALL_WIRE_MAX_PAYLOAD)
            {
                decoder->length_errors++;
                football_decoder_discard(decoder, 1u);
                continue;
            }
            total = sizeof(header) + header.payload_length;
            if (decoder->used < total)
            {
                break;
            }
            if (header.version != FOOTBALL_WIRE_VERSION)
            {
                decoder->version_errors++;
                football_decoder_discard(decoder, total);
                continue;
            }
            if (football_wire_crc(&header, decoder->buffer + sizeof(header)) != header.crc32)
            {
                decoder->crc_errors++;
                football_decoder_discard(decoder, 1u);
                continue;
            }
            if (handler != RT_NULL)
            {
                rt_err_t result = handler(&header, decoder->buffer + sizeof(header), user);
                if (result != RT_EOK)
                {
                    football_decoder_discard(decoder, total);
                    return result;
                }
            }
            football_decoder_discard(decoder, total);
        }
    }
    return RT_EOK;
}

void football_shared_region_reset(volatile football_shared_region_t *region,
                                  rt_uint32_t m33_boot_id)
{
    volatile rt_uint8_t *bytes;
    rt_size_t i;
    if (region == RT_NULL)
    {
        return;
    }
    bytes = (volatile rt_uint8_t *)region;
    for (i = 0u; i < sizeof(*region); ++i)
    {
        bytes[i] = 0u;
    }
    region->magic = FOOTBALL_LINK_SHARED_MAGIC;
    region->abi_version = FOOTBALL_SHARED_ABI_VERSION;
    region->header_size = (rt_uint16_t)(sizeof(*region) -
        sizeof(region->m33_to_m55) - sizeof(region->m55_to_m33));
    region->region_size = sizeof(*region);
    region->m33_boot_id = (m33_boot_id == 0u) ? 1u : m33_boot_id;
    region->reset_count = 1u;
    FOOTBALL_CACHE_CLEAN((void *)region, sizeof(*region));
    rt_hw_dmb();
}

volatile football_shared_region_t *football_shared_region_get(void)
{
    return (volatile football_shared_region_t *)&__football_shared_start__;
}

rt_bool_t football_shared_region_valid(const volatile football_shared_region_t *region)
{
    if (region == RT_NULL)
    {
        return RT_FALSE;
    }
    FOOTBALL_CACHE_INVALIDATE((void *)region,
                              sizeof(region->magic) +
                              sizeof(region->abi_version) +
                              sizeof(region->header_size) +
                              sizeof(region->region_size));
    rt_hw_dmb();
    return (region->magic == FOOTBALL_LINK_SHARED_MAGIC &&
            region->abi_version == FOOTBALL_SHARED_ABI_VERSION &&
            region->region_size == sizeof(*region)) ? RT_TRUE : RT_FALSE;
}

rt_err_t football_shared_ring_push(volatile football_shared_ring_t *ring,
                                   rt_uint16_t type,
                                   rt_uint16_t flags,
                                   rt_uint32_t sequence,
                                   rt_uint32_t timestamp_ms,
                                   rt_uint16_t priority,
                                   const void *payload,
                                   rt_size_t length)
{
    rt_uint32_t producer;
    rt_uint32_t next;
    volatile football_shared_entry_t *entry;
    football_shared_entry_t local;
    if (ring == RT_NULL || length > FOOTBALL_SHARED_ENTRY_PAYLOAD ||
        (length != 0u && payload == RT_NULL))
    {
        return -RT_EINVAL;
    }
    producer = ring->producer;
    next = (producer + 1u) % FOOTBALL_SHARED_RING_CAPACITY;
    if (next == ring->consumer)
    {
        ring->dropped++;
        return -RT_EFULL;
    }
    rt_memset(&local, 0, sizeof(local));
    local.type = type;
    local.flags = flags;
    local.sequence = sequence;
    local.timestamp_ms = timestamp_ms;
    local.payload_length = (rt_uint16_t)length;
    local.priority = priority;
    if (length != 0u)
    {
        rt_memcpy(local.payload, payload, length);
    }
    local.crc32 = football_crc32(&local, sizeof(local) - sizeof(local.payload) + length, 0u);
    entry = &ring->entries[producer];
    football_copy_to_volatile(entry, &local, sizeof(local));
    FOOTBALL_CACHE_CLEAN((void *)entry, sizeof(*entry));
    rt_hw_dmb();
    ring->producer = next;
    FOOTBALL_CACHE_CLEAN((void *)&ring->producer, sizeof(ring->producer));
    return RT_EOK;
}

rt_err_t football_shared_ring_pop(volatile football_shared_ring_t *ring,
                                  football_shared_entry_t *entry)
{
    rt_uint32_t consumer;
    rt_uint32_t expected;
    if (ring == RT_NULL || entry == RT_NULL)
    {
        return -RT_EINVAL;
    }
    FOOTBALL_CACHE_INVALIDATE((void *)ring, sizeof(ring->producer) + sizeof(ring->consumer));
    consumer = ring->consumer;
    if (consumer == ring->producer)
    {
        return -RT_EEMPTY;
    }
    FOOTBALL_CACHE_INVALIDATE((void *)&ring->entries[consumer], sizeof(*entry));
    football_copy_from_volatile(entry, &ring->entries[consumer], sizeof(*entry));
    if (entry->payload_length > FOOTBALL_SHARED_ENTRY_PAYLOAD)
    {
        ring->corrupt++;
        ring->consumer = (consumer + 1u) % FOOTBALL_SHARED_RING_CAPACITY;
        return -RT_EINVAL;
    }
    expected = entry->crc32;
    entry->crc32 = 0u;
    if (football_crc32(entry, sizeof(*entry) - sizeof(entry->payload) + entry->payload_length, 0u) != expected)
    {
        ring->corrupt++;
        ring->consumer = (consumer + 1u) % FOOTBALL_SHARED_RING_CAPACITY;
        return -RT_EINVAL;
    }
    entry->crc32 = expected;
    rt_hw_dmb();
    ring->consumer = (consumer + 1u) % FOOTBALL_SHARED_RING_CAPACITY;
    FOOTBALL_CACHE_CLEAN((void *)&ring->consumer, sizeof(ring->consumer));
    return RT_EOK;
}
