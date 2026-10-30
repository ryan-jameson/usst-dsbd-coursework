import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

/**
 * 基于 Socket 的简易 HTTP/1.0 客户端，支持 GET 与 POST。
 * 明确拆分 sendMessage 和 receiveMessage 方法以满足实验核心要求。
 */
public class HttpClient {
    private final String host;
    private final int port;

    public HttpClient(String host, int port) {
        this.host = host;
        this.port = port;
    }

    private String normalizePath(String path) {
        if (path == null || path.isEmpty()) return "/";
        if (!path.startsWith("/")) return "/" + path;
        return path;
    }

    /**
     * 构建并发送 GET 请求。
     */
    public HttpResponse doGET(String path) throws IOException {
        String normalizedPath = normalizePath(path);
        // 构建符合 HTTP/1.0 规范的请求头部报文
        String requestHeader = "GET " + normalizedPath + " HTTP/1.0\r\n" +
                "Host: " + host + "\r\n" +
                "Connection: close\r\n" +
                "User-Agent: SimpleBrowser/1.0\r\n" +
                "\r\n";
        
        return executeRequest(requestHeader, null);
    }

    /**
     * 构建并发送 POST 请求，附带表单数据。
     */
    public HttpResponse doPOST(String path, String formData) throws IOException {
        String normalizedPath = normalizePath(path);
        if (formData == null) formData = "";
        
        byte[] bodyBytes = formData.getBytes(StandardCharsets.UTF_8);

        // 构建符合 HTTP/1.0 规范的请求报文
        String requestHeader = "POST " + normalizedPath + " HTTP/1.0\r\n" +
                "Host: " + host + "\r\n" +
                "Connection: close\r\n" +
                "User-Agent: SimpleBrowser/1.0\r\n" +
                "Content-Type: application/x-www-form-urlencoded\r\n" +
                "Content-Length: " + bodyBytes.length + "\r\n" +
                "\r\n";
                
        return executeRequest(requestHeader, bodyBytes);
    }

    /**
     * 执行完整请求流程：建立 Socket -> sendMessage -> receiveMessage。
     */
    private HttpResponse executeRequest(String requestHeader, byte[] requestBody) throws IOException {
        try (Socket socket = new Socket(host, port);
             OutputStream out = socket.getOutputStream();
             InputStream in = socket.getInputStream()) {

            // (1) 使用 sendMessage 方法发送符合 http 协议定义的消息
            sendMessage(out, requestHeader, requestBody);

            // (2) 使用 receiveMessage 方法接收返回的页面源文件并解析
            return receiveMessage(in);
        }
    }

    /**
     * ★核心要求 (1)：使用 sendMessage 发送消息给 Web 服务器
     */
    private void sendMessage(OutputStream out, String header, byte[] body) throws IOException {
        System.out.println(">>> [sendMessage] 开始发送请求此报文给服务器...");
        out.write(header.getBytes(StandardCharsets.UTF_8));
        if (body != null && body.length > 0) {
            out.write(body);
        }
        out.flush();
        System.out.println(">>> [sendMessage] 消息发送完毕。");
    }

    private String readHeaderLine(InputStream in) throws IOException {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        int b;
        while ((b = in.read()) != -1) {
            if (b == '\n') break;
            if (b != '\r') bos.write(b);
        }
        if (bos.size() == 0 && b == -1) return null;
        return bos.toString(StandardCharsets.UTF_8.name());
    }

    /**
     * ★核心要求 (2)：使用 receiveMessage 接收返回的页面源文件
     */
    private HttpResponse receiveMessage(InputStream in) throws IOException {
        System.out.println("<<< [receiveMessage] 开始接收服务器响应...");
        HttpResponse response = new HttpResponse();

        // 1. 解析状态行
        String statusLine = readHeaderLine(in);
        response.setStatusLine(statusLine);
        if (statusLine != null && statusLine.split(" ").length >= 2) {
            try {
                response.setStatusCode(Integer.parseInt(statusLine.split(" ")[1]));
            } catch (NumberFormatException ignored) {}
        }

        // 2. 解析响应头
        String line;
        int contentLength = -1;
        boolean isChunked = false;
        while ((line = readHeaderLine(in)) != null && !line.isEmpty()) {
            int colon = line.indexOf(":");
            if (colon > 0) {
                String key = line.substring(0, colon).trim();
                String value = line.substring(colon + 1).trim();
                response.addHeader(key, value);
                if ("Content-Length".equalsIgnoreCase(key)) {
                    try { contentLength = Integer.parseInt(value); } 
                    catch (NumberFormatException ignored) {}
                }
                if ("Transfer-Encoding".equalsIgnoreCase(key) && value.toLowerCase().contains("chunked")) {
                    isChunked = true;
                }
            }
        }

        // 3. 读取响应体 (页面源文件)
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        if (isChunked) {
             while ((line = readHeaderLine(in)) != null && !line.isEmpty()) {
                 int chunkSize = Integer.parseInt(line.trim(), 16);
                 if (chunkSize == 0) break;
                 for (int i = 0; i < chunkSize; i++) {
                     int b = in.read();
                     if (b == -1) break;
                     baos.write(b);
                 }
                 readHeaderLine(in); // 跳过 chunk 后的 \r\n
             }
        } else if (contentLength >= 0) {
            for (int i = 0; i < contentLength; i++) {
                int b = in.read();
                if (b == -1) break;
                baos.write(b);
            }
        } else {
            byte[] buffer = new byte[4096];
            int len;
            while ((len = in.read(buffer)) != -1) {
                baos.write(buffer, 0, len);
            }
        }
        
        response.setBody(baos.toString(StandardCharsets.UTF_8));
        System.out.println("<<< [receiveMessage] 页面源文件接收解析完毕，状态码: " + response.getStatusCode());
        return response;
    }
}
