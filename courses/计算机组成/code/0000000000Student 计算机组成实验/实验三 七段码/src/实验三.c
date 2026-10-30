#include <stdint.h>
#include <stdio.h>
#include <string.h>
#if defined(D_NEXYS_A7)
   #include <bsp_printf.h>
   #include <bsp_mem_map.h>
   #include <bsp_version.h>
#else
   PRE_COMPILED_MSG("no platform was defined")
#endif
#include <psp_api.h>

#define GPIO_SWs    0x80001400
#define GPIO_LEDs   0x80001404
#define GPIO_INOUT  0x80001408


// for延时参数，3s
#define DELAY 100000
#define delay 300000//while输出延时，3s
// 宏定义
#define READ_GPIO(dir) (*(volatile unsigned *)dir)
#define WRITE_GPIO(dir, value) { (*(volatile unsigned *)dir) = (value); }

// SEG 寄存器地址
#define REG1 ((volatile uint32_t *)0x80001038)
#define REG2  ((volatile uint32_t *)0x8000103C)

// 共阳极段码表
const uint8_t seg_code[10] = {
    0x81, // 0
    0xCF, // 1
    0x92, // 2
    0x86, // 3
    0xCC, // 4
    0xA4, // 5
    0xA0, // 6
    0x8F, // 7
    0x80, // 8
    0x84  // 9
};

// 构造32位寄存器值（每个字节对应一个数码管）
uint32_t build_register_value(int digit, int position) {
    uint32_t value = 0;
    value = (seg_code[digit]) << (position);
    return value;
}
// 构造32位寄存器值（对应前4个数码管）
uint32_t reg2_value(int digit) {
    uint32_t valuer2 = 0,value1=0xFF<<16,value2=0xFF<<8,value3=0xFF<<0;
    if(digit>=100000) value1=build_register_value(digit/100000,16);
    if(digit>=10000) value2=build_register_value((digit/10000)%10,8);
    if(digit>=1000) value3=build_register_value((digit%10000)/1000,0);
    valuer2= (0xFF<<24)|value1|value2|value3;
    return valuer2;
}
// 构造32位寄存器值（对应后4个数码管）
uint32_t reg1_value(int digit) {
    uint32_t valuer1 =0, value4=0xFF<<24,value5=0xFF<<16,value6=0xFF<<8;
    if(digit>=100) value4=build_register_value((digit%1000)/100,24);
    if(digit>=10) value5=build_register_value((digit%100)/10,16);
    if(1) value6=build_register_value(digit%10,8);
    
    valuer1=value4|value5|value6|(0xFF<<0);
    return valuer1;
}


// 全局变量
int counting=0;

int main(void) {
    // 初始化 UART
    uartInit();
    // 设置 GPIO 方向：低16位输出（LED），高16位输入（开关）
    WRITE_GPIO(GPIO_INOUT, 0xFFFF);
    int En_Value=0xFFFF,display_value=0x00000000;
    WRITE_GPIO(GPIO_INOUT, En_Value);

    while (1) {
        
        counting++;
        display_value = READ_GPIO(GPIO_SWs) >> 16;
        // 更新 LED
        WRITE_GPIO(GPIO_LEDs, display_value);
        
        *REG1 = reg1_value(display_value);
        *REG2 =reg2_value(display_value);
        
        // 串口输出十进制和二进制
        char binary_str[17];
        for (int i = 0; i < 16; i++) {
            binary_str[i] = (display_value & (1 << (15 - i))) ? '1' : '0';
        }
        binary_str[16] = '\0';
        if(counting==delay){
            printfNexys("Decimal: %d\n", display_value);
            printfNexys("Binary: %s\n", binary_str);
            counting=0; 
        }
    }
    return 0;
}
