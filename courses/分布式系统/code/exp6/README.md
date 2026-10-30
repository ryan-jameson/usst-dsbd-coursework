# 实验六：实现一个基本的 Web 服务器程序

本实验实现了一个基于 Java Socket 的简易 Web 服务器，支持静态文件与 CGI 调用，监听 8080 端口。

## 目录结构
- `src/WebServer.java`：服务器主类，创建 `ServerSocket(8080)`，循环接受连接并启动线程处理。
- `src/ClientHandler.java`：每个连接的处理器，解析请求行，路由静态文件或 `/cgi-bin/` CGI，返回 HTTP 响应。
- `webroot/index.html`：默认首页。
- `webroot/test.html`：表单测试页面，POST 提交到 `/cgi-bin/test.bat`。
- `cgi-bin/test.bat`：示例 CGI 脚本（Windows 批处理），输出 HTML 与当前时间。
- `out/`：编译输出目录。

## 编译
在 PowerShell 中（当前目录为 `exp6`）：
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp6"
javac -d out src\WebServer.java src\ClientHandler.java
```

## 运行
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp6"
java -cp out WebServer
```
- 服务器监听 8080，控制台会输出收到的请求行。
- 访问 http://localhost:8080/ 加载首页；http://localhost:8080/test.html 加载表单页面。
- 访问 http://localhost:8080/cgi-bin/test.bat 执行 CGI 脚本，返回时间信息。

## 功能要点
- **请求解析**：读取请求第一行（如 `GET /index.html HTTP/1.0`），校验仅允许 GET/POST；读取请求头并消费 Content-Length。
- **静态文件**：根目录 `./webroot`，`/` 映射 `index.html`；按扩展名映射 MIME；不存在返回 404；路径包含 `..` 则 403，防目录穿越。
- **CGI 执行**：检测 `/cgi-bin/` 前缀，映射到 `./cgi-bin`，用 `cmd /c script` 执行 `.bat`，捕获输出作为响应体，失败返回 500。
- **HTTP 响应头**：`Content-Type`、`Content-Length`、`Connection: close`，行结束符严格 `\r\n`，空行分隔头体。

## 注意
- 确保 8080 端口空闲。
- CGI 示例需在 Windows 环境运行（使用批处理）。
- 仅演示 HTTP/1.0 关闭式连接，未实现持久连接与完整 CGI 头处理。
