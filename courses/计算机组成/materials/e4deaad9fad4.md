# RVfpgaModifications

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

RVfpga系统修改

在本文档中，我们总结了为完成RVfpga实验6-10中的练习而必须对RVfpga系统进行的更改。此RVfpga系统扩展版本（位于[RVfpgaPath]/RVfpga/Labs/RVfpgaLabsSolutions/RVfpga_Solutions/src）包括所有更改。我们在此处描述了完成每项实验练习所需的特定更改。

以下练习需要对RVfpga系统进行更改：
实验6 – 练习3
实验6 – 练习4
实验7 – 练习3
实验8 – 练习2
实验9 – 练习2




实验6 – 练习3. 扩展RVfpgaNexys以访问五个板上按钮。

rvpfganexys.xdc



rvpfganexys.sv





swervolf_core.v





wb_intercon.vh





wb_intercon.v






实验6 – 练习4. 为五个板上按钮设计另一个控制器。与之前的练习不同的是，在本练习中，您必须在Verilog/SystemVerilog中实现自己的GPIO控制器。

rvpfganexys.xdc



rvpfganexys.sv





swervolf_core.v





swervolf_syscon.v








实验7 – 练习3. 修改本实验中所述的控制器，以便8位7段显示屏可以显示ON/OFF LED的任意组合。

swervolf_syscon.v







实验8 – 练习2. 修改RVfpgaNexys以将定时器的PWM输出信号连接到Nexys A7电路板上的两个三色LED之一。

rvpfganexys.xdc



rvpfganexys.sv

 





swervolf_core.v





wb_intercon.vh





wb_intercon.v






实验9 – 练习2. 扩展RVfpgaNexys以包含第二个中断源（与IRQ4连接），该中断源来自实验6中用于控制板上按钮的第二个GPIO。

swervolf_core.v



swervolf_syscon.v
