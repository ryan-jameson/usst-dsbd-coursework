# Java RMI 学生远程接口与示例

本目录包含一个简单的 RMI 远程接口、实现类，以及服务器/客户端示例。

## 文件说明
- `src/Student.java`：可序列化的学生实体，字段包含学号、姓名、语文成绩、数学成绩、英语成绩。
- `src/IRemoteStudentService.java`：远程接口，继承 `java.rmi.Remote`，声明添加、删除、更新、查询学生的方法（均抛出 `RemoteException`）。
- `src/RemoteStudentServiceImpl.java`：服务实现，继承 `UnicastRemoteObject`，使用 `HashMap` 模拟存储，并在每次操作时输出计数日志。
- `src/RMIServer.java`：服务器端主程序，创建注册表（1099）、实例化并绑定服务。
- `src/RMIClient.java`：客户端主程序，演示添加、查询、删除学生记录。
- `src/HttpRequest.java`：HTTP 请求解析，读取请求行/头/可选正文。
- `src/HttpResponse.java`：HTTP 响应模型（状态码、头、体）。
- `src/HttpClient.java`：基于 Socket 的 HTTP/1.0 客户端，支持 GET/POST、表单编码、响应解析。
- `src/HttpClientGUI.java`：Swing 简易浏览器界面，支持 GET/POST 请求与结果展示。
- `src/WebServer.java`：简易多线程 Web 服务器，监听 8080，支持静态文件和 `/cgi-bin/` CGI 执行。
- `webroot/`：静态资源目录，含 `index.html`、`test.html`。
- `cgi-bin/test.bat`：示例 CGI，输出当前时间。

## 编译
在 PowerShell 中执行（已验证通过）：
```powershell
cd "e:\平时作业\分布式系统"
javac -d out src\Student.java src\IRemoteStudentService.java src\RemoteStudentServiceImpl.java src\RMIServer.java src\RMIClient.java

# HTTP 客户端与 Web 服务器
javac -d out src\HttpRequest.java src\HttpResponse.java src\HttpClient.java src\HttpClientGUI.java src\WebServer.java
```

## 运行
1. 启动服务器（会在进程内创建 1099 端口注册表）
```powershell
cd "e:\平时作业\分布式系统"
java -cp out RMIServer
```
看到输出 `服务器已启动，绑定名称: StudentService` 表示成功。

2. 另开一个终端运行客户端测试
```powershell
cd "e:\平时作业\分布式系统"
java -cp out RMIClient
```

客户端将输出添加/查询/删除的结果，并在服务器端看到操作计数日志。

### 启动简易 WebServer（静态文件 + CGI）
```powershell
cd "e:\平时作业\分布式系统"
java -cp out WebServer
```
- 默认监听 8080，webroot 为 `webroot/`，CGI 路径 `/cgi-bin/`
- 访问 http://localhost:8080/ 查看首页；http://localhost:8080/test.html 查看表单
- 访问 http://localhost:8080/cgi-bin/test.bat 调用示例 CGI（输出当前时间）

### 启动 Swing HTTP 客户端 GUI
```powershell
cd "e:\平时作业\分布式系统"
java -cp out HttpClientGUI
```
- 输入主机、端口、路径，选择 GET 或 POST；POST 时在表单区按行输入 `key=value`
- 结果区域显示状态行、状态码、Content-Type、Content-Length 与响应体

## 注意
- 运行前确保 1099 端口未被占用。
- RMI 示例未做并发持久化，数据保存在内存中，仅供演示。
- WebServer 示例仅作演示，未实现完整 HTTP/1.1 特性。
