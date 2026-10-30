# 实验6-m：智能内容分发与动态网页生成系统

本项目是实验6的增强版，包含 Web 服务器、数据库、AI 生成与可视化监控面板。

## 目录结构
- `src/main/java/com/experiment6/server`：Web服务器与HTTP处理
- `src/main/java/com/experiment6/ai`：AI内容生成器
- `src/main/java/com/experiment6/database`：数据库访问层
- `src/main/java/com/experiment6/gui`：监控面板
- `src/main/java/com/experiment6/client`：客户端（数据库查询 + AI生成页面）
- `src/main/resources`：`.env`、静态资源与CGI脚本
- `scripts`：初始化/启动脚本

## 启动步骤
1. 运行 `scripts/init_all.cmd` 完成初始化
2. 启动服务器：`scripts/start_server.bat`
3. 启动客户端：`scripts/start_client.bat`

## 功能概览
- 监听8080端口并处理HTTP请求
- 静态资源服务与CGI脚本执行
- AI生成个性化HTML页面
- MySQL用户画像与访问日志
- GUI监控面板（请求日志/统计/导出）
