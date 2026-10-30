#if defined(D_NEXYS_A7)
   #include <bsp_printf.h>
   #include <bsp_mem_map.h>
   #include <bsp_version.h>
#else
   PRE_COMPILED_MSG("no platform was defined")
#endif
#include <psp_api.h>

// GPIO 寄存器地址
#define GPIO_SWs    0x80001400
#define GPIO_LEDs   0x80001404
#define GPIO_INOUT  0x80001408

// 延时参数（根据系统时钟调整）
#define DELAY 50000000  // 约 1 秒延时（假设 100 MHz 时钟）

// 宏定义
#define READ_GPIO(dir) (*(volatile unsigned *)dir)
#define WRITE_GPIO(dir, value) { (*(volatile unsigned *)dir) = (value); }

int main (void)
{  

   int En_Value = 0xFFFF;  // 设置低16位为输出（LED），高16位为输入（开关）
   int switches_value;

    // 初始化 GPIO 方向
   WRITE_GPIO(GPIO_INOUT, En_Value);
   // Initialize UART
   uartInit();
   printfNexys("Hello World!");
   while (1) {
     switches_value = READ_GPIO(GPIO_SWs);
     switches_value = switches_value >> 16;
     WRITE_GPIO(GPIO_LEDs, switches_value);
     // 4. 解析并输出点亮的 LED 编号
     printfNexys("LEDs currently ON: ");
     for (int i = 0; i < 16; i++) {
         if ((switches_value >> i) & 0x1) {
             printfNexys("LED%d\t ", i);
         }
     }
     printfNexys("\n\n");
	 for (unsigned int i=0; i < DELAY; i++) ;  // delay between printf's
   }
}