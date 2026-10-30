# 实验五：Internet 应用 - 简易 HTTP 客户端浏览器

本实验使用 Java Socket 手动构造 HTTP/1.0 报文，支持 GET 与 POST，解析响应头与响应体，并提供控制台与可选 Swing GUI 演示。

## 目录结构
- `src/HttpResponse.java`：HTTP 响应模型，包含状态行/状态码、头部 Map、正文。
- `src/HttpClient.java`：核心 Socket 客户端，支持 `sendGetRequest` 与 `sendPostRequest`，解析响应。
- `src/BrowserApp.java`：控制台演示主程序，包含 GET 与 POST 两个测试用例。
- `src/SimpleBrowserGUI.java`：可选 Swing 简易浏览器界面（URL、GET/POST、表单输入、结果展示）。
- `out/`：编译输出目录。

## 编译
在 PowerShell 执行（当前目录需为 `exp5`）：
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp5"
javac -d out src\HttpResponse.java src\HttpClient.java src\BrowserApp.java src\SimpleBrowserGUI.java
```

## 运行
### 控制台测试
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp5"
java -cp out BrowserApp
```
- 测试 1：GET http://localhost:8080/index.html （假设实验六 Web 服务器已启动）
- 测试 2：POST http://localhost:8080/cgi-bin/test.bat，表单数据 `name=Alice&score=90`
- 若连接失败，会提示“请确保 Web 服务器已启动”。

推荐在线测试（适合展示 GET/POST）：
- GET：`http://httpbin.org/get`
- POST：`http://httpbin.org/post`

提示：很多网站不接受 POST，因此会返回 405（Method Not Allowed）。httpbin 会把你发过去的参数原样回显，最适合实验演示。

### Swing GUI（可选）
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp5"
java -cp out SimpleBrowserGUI
```
- 顶部输入完整 URL，选择 GET 或 POST；POST 时在表单区填入 `key=value&key2=value2`。
- 点击“发送”查看响应头与正文。

## 设计要点
- 严格使用 `\r\n` 构建 HTTP/1.0 请求行与头部。
- `Content-Type: application/x-www-form-urlencoded`、`Content-Length` 按 UTF-8 字节长度计算。
- 解析响应时先读状态行与头，若有 `Content-Length` 则按长度读取，否则读到连接关闭。
- 每次请求使用 try-with-resources 确保 Socket/流正确关闭。

## 依赖
- 仅使用 JDK 标准库，无额外依赖。
