# ExStages

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 原幻灯片 1

周期i
xor t6,t6,t1
周期i+1
周期i-1
bne a0,a1,208

EX1

sub t4,t4,t1
or t5,t5,t1


addi a0,a0,1
add t3,t3,t1


EX2
EX3
sub t4,t4,t1
or t5,t5,t1


addi a0,a0,1
add t3,t3,t1


xor t6,t6,t1
bne a0,a1,208


xor t6,t6,t1
bne a0,a1,208


sub t4,t4,t1
or t5,t5,t1


addi a0,a0,1
add t3,t3,t1


I0流水线
I1流水线
I0流水线
I1流水线
I0流水线
I1流水线
