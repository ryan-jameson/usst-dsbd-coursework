import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

/**
 * 处理单个客户端连接的任务，实现静态文件与 CGI 路由。
 */
public class ClientHandler implements Runnable {
    private static final String WEB_ROOT = "webroot"; // 静态资源根目录
    private static final String CGI_ROOT = "cgi-bin"; // CGI 根目录

    private final Socket socket;

    public ClientHandler(Socket socket) {
        this.socket = socket;
    }

    @Override
    public void run() {
        try (InputStream in = socket.getInputStream();
             OutputStream out = new BufferedOutputStream(socket.getOutputStream());
             BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {

            // 解析请求行
            String requestLine = reader.readLine();
            if (requestLine == null || requestLine.isEmpty()) {
                return;
            }
            System.out.println("[REQUEST] " + requestLine);

            String[] parts = requestLine.split(" ");
            if (parts.length < 3) {
                writeError(out, 400, "Bad Request", "非法请求行");
                return;
            }
            String method = parts[0]; // 当前实验主要处理 GET/POST
            String path = parts[1];

            // 简单校验仅允许 GET/POST，其它返回 405
            if (!"GET".equalsIgnoreCase(method) && !"POST".equalsIgnoreCase(method)) {
                writeError(out, 405, "Method Not Allowed", "仅支持 GET/POST");
                return;
            }

            // 读取请求头，简单解析 Content-Length 以便消费请求体
            Map<String, String> headers = new HashMap<>();
            String line;
            int contentLength = 0;
            while ((line = reader.readLine()) != null) {
                if (line.isEmpty()) break;
                int idx = line.indexOf(":");
                if (idx > 0) {
                    String key = line.substring(0, idx).trim();
                    String value = line.substring(idx + 1).trim();
                    headers.put(key, value);
                    if ("Content-Length".equalsIgnoreCase(key)) {
                        try {
                            contentLength = Integer.parseInt(value);
                        } catch (NumberFormatException ignored) {}
                    }
                }
            }
            // 消费请求体（如果有），本实验 CGI 不必使用，但需读掉防止影响后续连接（HTTP/1.0 关闭连接，这里读完即可）
            if (contentLength > 0) {
                char[] buf = new char[contentLength];
                int read = 0;
                while (read < contentLength) {
                    int r = reader.read(buf, read, contentLength - read);
                    if (r == -1) break;
                    read += r;
                }
            }

            // 路由：CGI 或静态
            if (path.startsWith("/cgi-bin/")) {
                handleCgi(path, out);
            } else {
                handleStatic(path, out);
            }

        } catch (Exception e) {
            try {
                writeError(socket.getOutputStream(), 500, "Internal Server Error", "服务器异常: " + e.getMessage());
            } catch (IOException ignored) {}
        } finally {
            try { socket.close(); } catch (IOException ignored) {}
        }
    }

    private void handleStatic(String path, OutputStream out) throws IOException {
        // 目录穿越防护
        if (path.contains("..")) {
            writeError(out, 403, "Forbidden", "非法路径");
            return;
        }
        if ("/".equals(path)) {
            path = "/index.html";
        }
        Path filePath = Paths.get(WEB_ROOT, path.substring(1)).normalize();
        File file = filePath.toFile();
        if (!file.exists() || file.isDirectory()) {
            writeError(out, 404, "Not Found", "文件不存在");
            return;
        }
        byte[] data = Files.readAllBytes(filePath);
        String contentType = guessContentType(filePath.toString());
        writeResponse(out, 200, "OK", contentType, data);
    }

    private void handleCgi(String path, OutputStream out) throws IOException {
        String cgiRelative = path.substring("/cgi-bin/".length());
        if (cgiRelative.contains("..")) {
            writeError(out, 403, "Forbidden", "非法路径");
            return;
        }
        Path scriptPath = Paths.get(CGI_ROOT, cgiRelative).normalize();
        File script = scriptPath.toFile();
        if (!script.exists() || script.isDirectory()) {
            writeError(out, 404, "Not Found", "CGI 脚本不存在");
            return;
        }

        Process process = null;
        try {
            // Windows 下执行 .bat 通过 cmd /c
            process = Runtime.getRuntime().exec(new String[]{"cmd.exe", "/c", script.getAbsolutePath()});
            byte[] output = process.getInputStream().readAllBytes();
            int exit = process.waitFor();
            if (exit != 0) {
                writeError(out, 500, "Internal Server Error", "CGI 执行失败，退出码=" + exit);
                return;
            }
            // 简化：不解析 CGI 头，统一作为 text/html 返回
            writeResponse(out, 200, "OK", "text/html; charset=UTF-8", output);
        } catch (Exception e) {
            writeError(out, 500, "Internal Server Error", "CGI 异常: " + e.getMessage());
        } finally {
            if (process != null) {
                process.destroy();
            }
        }
    }

    private void writeResponse(OutputStream out, int statusCode, String statusText, String contentType, byte[] body) throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append("HTTP/1.0 ").append(statusCode).append(' ').append(statusText).append("\r\n");
        sb.append("WEBServer: 1.0\r\n");
        sb.append("content_type: ").append(contentType).append("\r\n");
        sb.append("content_length: ").append(body.length).append("\r\n");
        sb.append("\r\n");
        out.write(sb.toString().getBytes(StandardCharsets.UTF_8));
        out.write(body);
        out.flush();
    }

    private void writeError(OutputStream out, int statusCode, String statusText, String message) throws IOException {
        String html = "<html><body><h1>" + statusCode + " " + statusText + "</h1><p>" + message + "</p></body></html>";
        writeResponse(out, statusCode, statusText, "text/html; charset=UTF-8", html.getBytes(StandardCharsets.UTF_8));
    }

    private String guessContentType(String path) {
        String lower = path.toLowerCase();
        if (lower.endsWith(".html") || lower.endsWith(".htm")) return "text/html; charset=UTF-8";
        if (lower.endsWith(".css")) return "text/css; charset=UTF-8";
        if (lower.endsWith(".js")) return "application/javascript; charset=UTF-8";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        if (lower.endsWith(".gif")) return "image/gif";
        if (lower.endsWith(".txt")) return "text/plain; charset=UTF-8";
        return "application/octet-stream";
    }
}
