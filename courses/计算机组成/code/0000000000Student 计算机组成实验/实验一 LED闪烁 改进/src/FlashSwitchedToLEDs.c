
// GPIO 寄存器地址
#define GPIO_SWs    0x80001400
#define GPIO_LEDs   0x80001404
#define GPIO_INOUT  0x80001408

// 延时参数（根据系统时钟调整）
#define DELAY 5000000  // 约 1 秒延时（假设 100 MHz 时钟）

// 宏定义
#define READ_GPIO(dir) (*(volatile unsigned *)dir)
#define WRITE_GPIO(dir, value) { (*(volatile unsigned *)dir) = (value); }

int main(void)
{
    int En_Value = 0xFFFF;  // 设置低16位为输出（LED），高16位为输入（开关）
    int switches_value;

    // 初始化 GPIO 方向
    WRITE_GPIO(GPIO_INOUT, En_Value);

    while (1)
    {
        // 1. 读取开关值
        switches_value = READ_GPIO(GPIO_SWs);
        switches_value = switches_value >> 16;  // 高16位为开关输入

        // 2. 显示开关值到 LED
        WRITE_GPIO(GPIO_LEDs, switches_value);

        // 3. 延时，LED 亮起
        for (unsigned int i = 0; i < DELAY; i++);

        // 4. 关闭 LED
        WRITE_GPIO(GPIO_LEDs, 0x0000);

        // 5. 再次延时，LED 熄灭
        for (unsigned int i = 0; i < DELAY; i++);
    }

    return 0;
}