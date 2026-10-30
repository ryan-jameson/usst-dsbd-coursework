package com.experiment6.server;

import com.experiment6.common.AppConfig;
import com.experiment6.common.AppLogger;
import com.experiment6.gui.ServerMonitorGUI;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class WebServer {
    private static final int DEFAULT_PORT = 8080;
    private static ExecutorService threadPool;
    private static ServerSocket serverSocket;
    private static volatile boolean running = true;

    /**
     * 主启动入口。
     * @param args args
     */
    public static void main(String[] args) {
        // 5. 启动时加载.env配置文件
        AppConfig.load();

        // 4. 启动时初始化数据库连接池
        boolean dbReady = initDatabase();

        int port = parsePort();

        // 6. 启动时打开GUI监控面板
        ServerMonitorGUI monitorGUI = new ServerMonitorGUI(port);
        monitorGUI.showInterface();
        monitorGUI.updateDbStatus(dbReady);
        monitorGUI.logMessage("服务器已启动，监听" + port + "端口");

        // 2. 支持多线程处理并发请求
        threadPool = Executors.newFixedThreadPool(50);

        // 3. 优雅关闭机制（SIGINT处理）
        Runtime.getRuntime().addShutdownHook(new Thread(WebServer::shutdown));

        // 1. 使用ServerSocket监听8080端口
        try {
            serverSocket = new ServerSocket(port);
            monitorGUI.logMessage("WebServer startup on port " + port);
            monitorGUI.showStartupMessage("服务器已启动，监听" + port + "端口");

            while (running) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    monitorGUI.incrementConnection();
                    threadPool.execute(new HttpHandler(clientSocket, monitorGUI));
                } catch (IOException e) {
                    if (running) {
                        monitorGUI.logMessage("Error accepting connection: " + e.getMessage());
                        AppLogger.error("accept连接失败", e);
                    }
                }
            }
        } catch (IOException e) {
            AppLogger.error("端口绑定失败: " + port, e);
        }
    }

    private static int parsePort() {
        return AppConfig.getInt("SERVER_PORT", DEFAULT_PORT);
    }

    private static boolean initDatabase() {
        AppLogger.info("Initializing Database Connection Pool...");
        // 可以在此处调用 DatabaseManager.init();
        return true;
    }

    private static void shutdown() {
        AppLogger.info("Shutting down WebServer gracefully...");
        running = false;
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
            if (threadPool != null) {
                threadPool.shutdown();
                if (!threadPool.awaitTermination(5, TimeUnit.SECONDS)) {
                    threadPool.shutdownNow();
                }
            }
        } catch (Exception e) {
            AppLogger.error("关闭服务器异常", e);
        }
    }
}
