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

#define GPIO2_BTNs  0x80001800//按钮地址
#define GPIO2_INOUT 0x80001808

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
// 构造个-千位数据
uint32_t r1_value(int digit) {
    uint32_t valuer2 =0, value1=0xFF<<24,value2=0xFF<<16,value3=0xFF<<8,value4=0xFF<<0;
    if(1) value4=build_register_value(digit%10,0);
    if(digit>=10) value3=build_register_value((digit%100)/10,8);
    if(digit>=100) value2=build_register_value((digit%1000)/100,16);
    if(digit>=1000) value1=build_register_value(digit/1000,24);
    valuer2=value1|value2|value3|value4;
    return valuer2;
}
// 构造万-千万位数据
uint32_t r2_value(int digit) {
    uint32_t valuer1 =0, value1=0xFF<<24,value2=0xFF<<16,value3=0xFF<<8,value4=0xFF<<0;
    if(digit>=10000000) value1=build_register_value(digit/10000000,24);
    if(digit>=1000000) value2=build_register_value((digit/1000000)%10,16);
    if(digit>=100000) value3=build_register_value((digit%1000000)/100000,8);
    if(digit>=10000) value4=build_register_value((digit%100000)/10000,0);
    valuer1=value1|value2|value3|value4;
    return valuer1;
}

// 全局变量
int counting=0;
int mode=0;
int time_value=0;
// 按钮轮询检测
int check_button() {
    int btn_value = READ_GPIO(GPIO2_BTNs);
    int btc = btn_value & 0x1;
    int btu = btn_value & 0x2;
    int btl = btn_value & 0x4;
    int btr = btn_value & 0x8;
    int btd = btn_value & 0x10;
    if (btu==0x2) mode=1;//表白模式
    if(btl==0x4) mode=2;//暂停
    if(btr==0x8) mode=3;//倒计时
    if(btd==0x10) mode=4;//计数时间
    if(btc==0x1) mode=0;//显示形式，中心键
    return mode;
}

int main(void) {
    // 初始化 UART
    uartInit();
    // 设置 GPIO 方向：低16位输出（LED），高16位输入（开关）
    WRITE_GPIO(GPIO_INOUT, 0xFFFF);
    int En_Value=0xFFFF,display_value=0x00000000;
    WRITE_GPIO(GPIO_INOUT, En_Value);

    WRITE_GPIO(GPIO2_INOUT, 0x0);
    while (1) {
        check_button();
        
        counting++;
        display_value = READ_GPIO(GPIO_SWs) >> 16;
        // 更新 LED
        WRITE_GPIO(GPIO_LEDs, display_value);
        switch (mode)
        {
        case 1:
            *REG1 = 0xC481C1FE;
            *REG2 =0xF181E3B0;
            break;//表白模式
        case 2:
            *REG1 = r1_value(time_value);
            *REG2 =r2_value(time_value);
            break;//暂停滞留
        case 3:
            if(counting%DELAY==0){
                time_value--;
            }
            *REG1 = r1_value(time_value);
            *REG2 =r2_value(time_value);
            break;//倒计时
        case 4:
            if(counting%DELAY==0){
                time_value++;
            }
            *REG1 = r1_value(time_value);
            *REG2 =r2_value(time_value);
            break;//递增模式
        default:
            *REG1 = reg1_value(display_value);
            *REG2 =reg2_value(display_value);
            time_value=display_value;
            break;
        }
        
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
