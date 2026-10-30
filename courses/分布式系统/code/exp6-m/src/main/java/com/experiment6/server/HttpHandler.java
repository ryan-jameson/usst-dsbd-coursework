package com.experiment6.server;

import com.experiment6.ai.AiContentGenerator;
import com.experiment6.common.AppLogger;
import com.experiment6.database.AccessLogDao;
import com.experiment6.gui.ServerMonitorGUI;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * HTTP请求处理器。
 */
public class HttpHandler implements Runnable {
    private final Socket socket;
    private final ServerMonitorGUI gui;

    /**
     * 构造处理器。
     * @param socket 客户端Socket
     * @param gui 监控面板
     */
    public HttpHandler(Socket socket, ServerMonitorGUI gui) {
        this.socket = socket;
        this.gui = gui;
    }

    @Override
    public void run() {
        long startTime = System.currentTimeMillis();
        String method = "UNKNOWN";
        String path = "/";
        int status = 200;
        boolean aiGenerated = false;
        StringBuilder rawRequest = new StringBuilder();
        StringBuilder rawResponse = new StringBuilder();

        try (InputStream in = socket.getInputStream();
             OutputStream out = socket.getOutputStream();
             BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {

            // 1. 解析HTTP请求行
            String requestLine = reader.readLine();
            if (requestLine == null || requestLine.isEmpty()) return;
            rawRequest.append(requestLine).append("\r\n");
            AppLogger.info("HTTP请求: " + requestLine);
            
            String[] parts = requestLine.split(" ");
            if (parts.length >= 2) {
                method = parts[0];
                path = parts[1];
            }

            // 2. 解析HTTP请求头
            Map<String, String> headers = new HashMap<>();
            String line;
            int contentLength = 0;
            while ((line = reader.readLine()) != null && !line.isEmpty()) {
                rawRequest.append(line).append("\r\n");
                int colonIdx = line.indexOf(":");
                if (colonIdx > 0) {
                    String key = line.substring(0, colonIdx).trim().toLowerCase();
                    String value = line.substring(colonIdx + 1).trim();
                    headers.put(key, value);
                    if ("content-length".equals(key)) {
                        try {
                            contentLength = Integer.parseInt(value);
                        } catch (NumberFormatException e) {
                            contentLength = 0;
                        }
                    }
                }
            }
            rawRequest.append("\r\n");

            // 3. 解析HTTP请求体
            String body = "";
            if (contentLength > 0) {
                char[] bodyChars = new char[contentLength];
                int read = reader.read(bodyChars, 0, contentLength);
                if (read > 0) {
                    body = new String(bodyChars, 0, read);
                }
            }
            
            byte[] responseBytes;
            String contentType = "text/html; charset=UTF-8";
            StaticResourceEngine.StaticResource staticResource;

            // 4, 5, 6 - 路由策略
            if (path.startsWith("/cgi-bin/")) {
                String scriptName = path.substring(path.lastIndexOf("/") + 1);
                String execCmd = scriptName.endsWith(".bat") ? ("cmd.exe /c " + scriptName) : ("sh " + scriptName);
                String cgiResult = new CgiGateway().handleCgiRequest(path, method, body);
                responseBytes = cgiResult.getBytes(StandardCharsets.UTF_8);
                if (gui != null) {
                    gui.updateCgiLog("Runtime.exec: " + execCmd + " | path=" + path);
                }
            } else if (path.startsWith("/profile/")) {
                aiGenerated = true;
                String aiHtml = new AiContentGenerator().generateProfileContent(socket.getInetAddress().getHostAddress(), path);
                responseBytes = aiHtml.getBytes(StandardCharsets.UTF_8);
            } else {
                // 静态资源引擎
                staticResource = new StaticResourceEngine().load(path);
                status = staticResource.status;
                contentType = staticResource.contentType;
                responseBytes = staticResource.body;
            }

            // 构造强HTTP响应
            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(out, StandardCharsets.UTF_8));
            writer.write("HTTP/1.0 " + status + " OK\r\n");
            writer.write("Server: SmartWebServer/1.0\r\n");
            writer.write("Content-Type: " + contentType + "\r\n");
            writer.write("Content-Length: " + responseBytes.length + "\r\n");
            writer.write("Connection: close\r\n\r\n");
            writer.flush();
            out.write(responseBytes);
            out.flush();

            AppLogger.info("HTTP响应: status=" + status + ", path=" + path + ", bytes=" + responseBytes.length);

            rawResponse.append("HTTP/1.0 ").append(status).append(" OK\r\n");
            rawResponse.append("Server: SmartWebServer/1.0\r\n");
            rawResponse.append("Content-Type: ").append(contentType).append("\r\n");
            rawResponse.append("Content-Length: ").append(responseBytes.length).append("\r\n\r\n");

        } catch (Exception e) {
            status = 500;
            AppLogger.error("HTTP处理异常", e);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            // 7. 记录请求日志 (发送给GUI监控并存库)
            if (gui != null) {
                gui.addLogEntry(socket.getInetAddress().getHostAddress(), method, path, status, duration, aiGenerated);
                gui.decrementConnection();
                gui.updateHttpTrace(rawRequest.toString() + rawResponse);
            }
            new AccessLogDao().insert(socket.getInetAddress().getHostAddress(), method, path, rawRequest.toString(), status, (int) duration, aiGenerated);
            try { socket.close(); } catch (IOException ignored) {}
        }
    }
}
