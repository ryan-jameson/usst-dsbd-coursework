# 实验四：RMI API - 学生信息管理系统

本实验实现了基于 Java RMI 的学生信息管理系统，提供学生成绩的增删改查操作。

## 目录结构
- `src/Student.java`：学生数据模型，实现 Serializable。
- `src/IRemoteStudentService.java`：RMI 远程接口，定义增删改查和获取全部学生的方法。
- `src/RemoteStudentServiceImpl.java`：远程服务实现，使用 HashMap 作为内存数据库并记录操作日志。
- `src/RMIServer.java`：服务器端主程序，创建注册表并绑定远程对象。
- `src/RMIClient.java`：客户端主程序，演示添加、查询、修改、删除等操作。
- `out/`：编译后的 .class 输出目录。

## 编译
在 PowerShell 中执行（确保当前目录为 `exp4`）：
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp4"
javac -d out src\Student.java src\IRemoteStudentService.java src\RemoteStudentServiceImpl.java src\RMIServer.java src\RMIClient.java
```

## 运行
1) 启动 RMI 服务器（会在进程内创建 1099 端口的 registry）
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp4"
java -cp out RMIServer
```
看到输出 `RMI Server is ready... (bind name: StudentService)` 表示成功。

2) 另开终端启动客户端测试
```powershell
Set-Location -Path "e:\平时作业\分布式系统\exp4"
java -cp out RMIClient
```
客户端将依次执行：添加两个学生 -> 查询 -> 修改 -> 删除 -> 再次查询删除的记录，并在控制台打印结果。

## 代码要点
- 远程接口方法均抛出 `RemoteException`。
- 远程实现继承 `UnicastRemoteObject`，HashMap 模拟内存数据库，操作带日志。
- 学生模型包含学号、姓名、语文/数学/英语成绩，提供构造器、Getter/Setter、toString。

## 注意
- 确保 1099 端口未被占用。
- 运行时需保持 server 进程运行，再启动 client。
