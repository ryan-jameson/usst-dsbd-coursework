# RVfpga_Lab00_LabsOverview

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

Imagination大学计划




RVfpga实验0
RVfpga实验概述








致谢


作者
Sarah Harris教授（ HYPERLINK "https://www.linkedin.com/in/sarah-harris-12720697/" https://www.linkedin.com/in/sarah-harris-12720697/）
Daniel Chaver教授（ HYPERLINK "https://www.linkedin.com/in/daniel-chaver-a5056a156/" https://www.linkedin.com/in/daniel-chaver-a5056a156/）
Zubair Kakakhel（https://www.linkedin.com/in/zubairlk/）
M. Hamza Liaqat（https://www.linkedin.com/in/muhammad-hamza-liaqat-ab73a0195/）
顾问
David Patterson教授（https://www.linkedin.com/in/dave-patterson-408225/）
贡献者
Robert Owen（https://www.linkedin.com/in/robert-owen-4335931/）
Olof Kindgren（https://www.linkedin.com/in/olofkindgren/）
Luis Piñuel教授（https://www.linkedin.com/in/lpinuel/）
Ivan Kravets（https://www.linkedin.com/in/ivankravets/）
Valerii Koval（https://www.linkedin.com/in/valeros/）
Ted Marena（https://www.linkedin.com/in/tedmarena/）
Roy Kravitz教授（https://www.linkedin.com/in/roy-kravitz-4725963/）
联合作者
José Ignacio Gómez教授（https://www.linkedin.com/in/jos%C3%A9-ignacio-gomez-182b981/）
Christian Tenllado教授（ HYPERLINK "https://www.linkedin.com/in/christian-tenllado-31578659/" https://www.linkedin.com/in/christian-tenllado-31578659/）
Daniel León教授（ HYPERLINK "http://www.linkedin.com/in/danileon-ufv" www.linkedin.com/in/danileon-ufv）
Katzalin Olcoz教授（ HYPERLINK "https://www.linkedin.com/in/katzalin-olcoz-herrero-5724b0200/" https://www.linkedin.com/in/katzalin-olcoz-herrero-5724b0200/）
Alberto del Barrio教授（ HYPERLINK "https://www.linkedin.com/in/alberto-antonio-del-barrio-garc%C3%ADa-1a85586a/" https://www.linkedin.com/in/alberto-antonio-del-barrio-garc%C3%ADa-1a85586a/）
Fernando Castro教授（ HYPERLINK "https://www.linkedin.com/in/fernando-castro-5993103a/" https://www.linkedin.com/in/fernando-castro-5993103a/）
Manuel Prieto教授（https://www.linkedin.com/in/manuel-prieto-matias-02470b8b/）
Francisco Tirado教授（ HYPERLINK "https://www.linkedin.com/in/francisco-tirado-fern%C3%A1ndez-40a45570/" https://www.linkedin.com/in/francisco-tirado-fern%C3%A1ndez-40a45570/）
Román Hermida教授（https://www.linkedin.com/in/roman-hermida-correa-a4175645/）
Cathal McCabe（https://www.linkedin.com/in/cathalmccabe/）
Dan Hugo（ HYPERLINK "https://www.linkedin.com/in/danhugo/" https://www.linkedin.com/in/danhugo/）
Braden Harwood（ HYPERLINK "https://www.linkedin.com/in/braden-harwood/" https://www.linkedin.com/in/braden-harwood/）
David Burnett（https://www.linkedin.com/in/david-burnett-3b03778/）
Gage Elerding（https://www.linkedin.com/in/gage-elerding-052b16106/）
Brian Cruickshank（https://www.linkedin.com/in/bcruiksh/）
Deepen Parmar（https://www.linkedin.com/in/deepen-parmar/）
Thong Doan（https://www.linkedin.com/in/thong-doan/）
Oliver Rew（https://www.linkedin.com/in/oliver-rew/）
Niko Nikolay（ HYPERLINK "https://www.linkedin.com/in/roy-kravitz-4725963/" https://www.linkedin.com/in/roy-kravitz-4725963/）
Guanyang He（https://www.linkedin.com/in/guanyang-he-5775ba109/）
Ataur Patwary教授（https://www.linkedin.com/in/ataurpatwary/）
前言

RVfpga计算机体系结构课程通过具体实验帮助用户了解商用RISC-V处理器、RISC-V SoC和RISC-V生态系统。本课程按照以下顺序介绍系统：从基础数字设计和信号到指令集架构和处理器，再到编程环境、引导代码和编译器。用户可以通过RVfpga课程全面的了解RISC-V系统。用户不仅可以了解RISC-V SoC和RISC-V生态系统的工作状态，还能够掌握如何使用并扩展RISC-V处理器和系统来支持未来的项目和研究。

David Patterson教授（因对RISC的贡献而与John Hennessy共获ACM A.M.图灵奖）表示：“RISC-V正在推动处理器设计以及软件/硬件协同设计发生巨大变革。RISC-V是一种支持开源硬件实现的开放式架构。这种全新设计意味着软件开发可与硬件开发同步进行，从而加快设计速度。RVfpga课程可加强对RISC-V处理器、RISC-V生态系统和RISC-V SoC的了解。本课程可帮助用户深入了解日益普及的工业级处理器架构和系统，这将在他们的整个学术生涯和职业生涯中发挥巨大作用。


RVfpga实验概述

这些RVfpga实验通过动手练习帮助用户增进对RISC-V硬件和软件的了解。在开始RVfpga实验之前，必须完成Imagination大学计划（ HYPERLINK "https://university.imgtec.com/" https://university.imgtec.com/）提供的“RVfpga入门指南”中所述的准备工作。例如，必须依据该指南中的说明安装Xilinx的Vivado、PlatformIO和Verilator（如果尚未安装）。此外，请确保已将从Imagination大学计划下载的RVfpga文件夹复制到您的计算机上。我们将RVfpga文件夹所在目录的绝对路径称为[RVfpgaPath]。RVfpga/src文件夹包含RVfpga系统（即，我们将在所有实验中使用和修改的RISC-V SoC）的Verilog和SystemVerilog源文件。RVfpga/Labs文件夹包含 REF _Ref87939179 \h 表1中列出的各个实验的资源。

表 SEQ Table \* ARABIC 1. RVfpga Labs

编号
标题
第1部分
0
RVfpga实验概述

1
创建Vivado项目

2
C语言编程

3
RISC-V汇编语言

4
函数调用

5
图像处理：采用C语言和汇编语言的项目

6
I/O简介

7
7段显示屏

8
定时器

9
中断驱动I/O

10
串行总线
第2部分
11
SweRV EH1配置和结构。性能监视

12
算术/逻辑指令：add

13
访存指令：lw和sw指令

14
结构冒险

15
数据冒险

16
控制冒险。分支指令：beq和分支预测器

17
超标量执行

18
向内核添加新功能（指令和硬件计数器）

19
存储器层级：指令高速缓存（I$）

20
I$、ICCM、DCCM和基准测试


SweRV EH1参考

实验1-10（第1部分）说明如何使用RISC-V SoC和工具链（编译器和仿真器）以及如何向SoC添加外设。具体来说：这些实验展示了如何查看SweRVolfX SoC源代码并确定其目标FPGA（实验1）、如何在RVfpgaNexys、RVfpgaSim和Whisper上运行程序（实验2-5）以及如何修改RVfpga系统以添加外设（实验6-10）。

实验11-20（第2部分）重点关注微架构和存储器层级；这些实验展示了如何理解RISC-V流水线以及如何为RISC-V内核使用或添加功能，包括附加指令、其他分支预测器和存储器功能。


这些实验非常适合作为本科两个学期的课程。实验11-20也可作为硕士课程。在学习本RVfpga课程之前，学生应了解逻辑设计、计算机架构、处理器设计、输入/输出系统和C语言/汇编语言编程方面的基础知识。相关材料已包含在以下教科书中：《数字设计和计算机体系结构》RISC-V版本（作者：Harris & Harris）© Elsevier，2021年10月。

 REF _Ref87940429 \h  \* MERGEFORMAT 表2列出了进行这些实验所需的软件和可选的硬件。所有软件均免费提供。无需Nexys A7 FPGA板（或等效的Nexys DDR FPGA板）即可完成这些实验。可以使用Whisper（Western Digital的指令集仿真器）和Verilator（一种开源HDL仿真器）完成这些实验。

表 SEQ Table \* ARABIC 2. 所需的软件和可选的硬件
软件
Vivado 2019.2 WebPACK*
https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/2019-2.html
VS Code
https://code.visualstudio.com/Download
PlatformIO
https://platformio.org/（安装在VSCode内部）
Verilator和GTKWave
https://github.com/verilator/verilator
http://gtkwave.sourceforge.net/ 
Whisper（Western Digital的RISC-V指令集仿真器）
 HYPERLINK "https://github.com/chipsalliance/SweRV-ISS" https://github.com/chipsalliance/SweRV-ISS（安装在PlatformIO内部）

RISC-V工具链和OpenOCD
https://github.com/riscv/riscv-gnu-toolchain、 HYPERLINK "https://github.com/riscv/riscv-openocd" https://github.com/riscv/riscv-openocd（安装在PlatformIO内部）
硬件
Nexys A7 FPGA开发板*
https://store.digilentinc.com/nexys-a7-fpga-trainer-board-recommended-for-ece-curriculum/
RISC-V内核和片上系统（SoC）
Western Digital的SweRV EH1
 HYPERLINK "https://github.com/chipsalliance/Cores-SweRV" https://github.com/chipsalliance/Cores-SweRV（包含在RVfpga软件包内）
SweRVolf
https://github.com/chipsalliance/Cores-SweRVolf（包含在RVfpga软件包内）
* 可选

RVfpga/src文件夹的结构在GSG和实验1-20中说明。

RVfpga/Labs文件夹的结构如下：

文件夹LabInstructions：
各实验的说明，包括相关任务和练习。
文件夹Figures：各实验的说明中使用的图。

文件夹Lab1、Lab2...Lab19和Lab20：执行实验时使用的资源。

文件夹RVfpgaLabsSolutions：各实验的练习解答：在将RVfpga分发给学生之前，讲师应先将此文件夹删除。
文件夹Programs_Solutions：包含所提供任务和练习的解决方案的文档和软件。
文件夹RVfpga_Solutions：根据实验6-10中的练习的指示进行扩展修改后的RVfpga系统源代码（Verilog和SystemVerilog）。源代码位于文件夹[RVfpgaPath]/RVfpga/Labs/RVfpgaLabsSolutions/RVfpga_Solutions/src中，该文件夹还提供比特流（rvfpganexys.bit）。文档[RVfpgaPath]/RVfpga/Labs/RVfpgaLabsSolutions/RVfpga_Solutions/RVfpgaModifications.docx说明了在实验6-10的练习中对RVfpga系统进行的修改。请注意，并非所有练习均提供解决方案。
