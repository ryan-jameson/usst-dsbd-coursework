# 第三章

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 2

3.2 Chukwa 数据采集
• Adaptors 和 Agents
✓ 在每个数据的产生端，使用一个 Agent 来采集感兴趣的数据
✓ 每一类数据通过一个 Adaptor 来实现（命令行输出、Log 文件等）
✓ Adaptor 会定期运行或事件驱动地执行
✓ Agent 采用“watchdog”机制，自动重启终止的数据采集进程
✓ 对关键的数据在多台机器上部署相同的 Agent，从而实现容错

• Collectors
✓ 先部分合并数据，再写入集群，避免大量小文件的写入
✓ 允许和鼓励设置多个 Collector
✓ Agents 随机地从 Collectors 列表中选择一个传输数据，实现负载均衡

• Map/Reduce
✓ Demux 作业负责对数据的分类，排序和去重
✓ Archive 作业负责把同类型的数据文件合并

设计亮点：
• 避免小文件：通过 Collector 先合并再写入 HDFS，提升存储效率。
• 负载均衡：Agent 随机选择 Collector 发送数据，避免单个
Collector 过载。
• 容错机制：关键数据可以部署多个相同的 Agent，实现冗余采集。
• 数据后处理：通过 MapReduce 做 Demux（分类、去重）和 Archive
（合并），最终数据可存入 MySQL 或 HBase 供展示。
局限：
• 依赖 MapReduce，延迟较高，不适合实时性要求强的场景。
• 生态发展停滞，逐渐被 Flume、Kafka 等替代。

## 分节 3

3.5 Kafka 数据采集
• Apache Kafka 是一种分布式发布-订阅消息系统
• Kafka 能高效地处理大量实时数据，具有快速、可扩展、分布式、
分区和多副本等特点
• Kafka 架构具有高可扩展性、容错性和高并发性、高吞吐量

• Consumers：消息接收者，可订阅一个或多个话题，接收 Broker 发送的数据；
• Broker：服务代理，组成 Kafka 集群，并保存已发布的消息；
• Producers：消息发布者，能够发布消息到 topics（消息的分类名）进程；
1、Topics
• Topics 是消息的分类名
• 一个 Topic 分成多个 Partition，可并行处理
• Partition 内部消息是有序的
• 一个 Partition 对应一个 Broker，一个 Broker 管理多个 Partition

2、Producers
• 向主题发布数据
• 直接发送消息到 Broker 上的 leader 分区
• 自己控制消息被推送到哪些分区
• 以 Batch 的方式推送数据
• 异步、并行地发送消息
3、Consumers
• 特征消费组：Queuing（队列）和 Publish-SubScribe（发布-订阅）
• 以 Group 的形式消费 Topics
• Group 内：队列消费模式（Queuing）
• Group 间：发布-订阅消费模式（Publish-SubScribe）

## 分节 4

6、Kafka 架构核心特性
• 压缩功能
• 消息可靠性
• 备份机制

实现语言

框架

负载均衡

容错性

Agent

Collector

Store

Scriba

C/C++

Collector 和 Store 间 Thrift
Thrift
Push/Push 有，Agent 和 Collector Client,需要
Server
间的需要自己实现
自己实现

Chukwa

Java

Push/Push 自定义 Agent 之间有

ZK

需要自己实
现

支持 HDFS

Scala

Agent 可通过 Collector
自动识别并从
Push/Pull
ZK
Collector、Store 中获
取数据

需要自己实
现

支持 HDFS

Java

Agent, Collector 及
Store 之间均有容错机
Push/Push
ZK
制，三种级别的可用性保
证

提供了丰富
的 Agent

支持 HDFS

Kafka

Flume

支持 HDFS
