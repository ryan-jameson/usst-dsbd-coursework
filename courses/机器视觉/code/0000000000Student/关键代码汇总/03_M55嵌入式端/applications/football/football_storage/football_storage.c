#include "football_storage.h"

#include <finsh.h>

rt_err_t football_storage_append(const football_message_t *message)
{
    RT_UNUSED(message);
    return -RT_ENOSYS;
}

void football_storage_status(void)
{
    rt_kprintf("football_storage not used on M55; M33 owns SD event JSON log\r\n");
}

static int football_storage(int argc, char **argv)
{
    RT_UNUSED(argc);
    RT_UNUSED(argv);

    football_storage_status();
    return 0;
}
MSH_CMD_EXPORT(football_storage, AI football M55 storage stub);
