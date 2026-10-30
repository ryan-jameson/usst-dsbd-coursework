package com.experiment6.server;

import com.experiment6.common.AppConfig;
import com.experiment6.common.AppLogger;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

/**
 * 静态资源引擎。
 */
public class StaticResourceEngine {
    /**
     * 读取静态文件内容。
     * @param path 请求路径
     * @return StaticResource
     */
    public StaticResource load(String path) {
        String root = AppConfig.get("WEBROOT_PATH", "src/main/resources/webroot");
        String cleanPath = path.equals("/") ? "/index.html" : path;
        if (cleanPath.contains("..")) {
            return new StaticResource(403, "text/html; charset=UTF-8", "<h2>Forbidden</h2>");
        }
        File file = new File(root, cleanPath.substring(1));
        if (!file.exists() || file.isDirectory()) {
            return new StaticResource(404, "text/html; charset=UTF-8", "<h2>Not Found</h2>");
        }
        try {
            byte[] bytes = Files.readAllBytes(file.toPath());
            return new StaticResource(200, guessContentType(file.getName()), bytes);
        } catch (IOException e) {
            AppLogger.error("读取静态文件失败", e);
            return new StaticResource(500, "text/html; charset=UTF-8", "<h2>Server Error</h2>");
        }
    }

    private String guessContentType(String name) {
        String lower = name.toLowerCase();
        if (lower.endsWith(".html") || lower.endsWith(".htm")) return "text/html; charset=UTF-8";
        if (lower.endsWith(".css")) return "text/css; charset=UTF-8";
        if (lower.endsWith(".js")) return "application/javascript; charset=UTF-8";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        if (lower.endsWith(".gif")) return "image/gif";
        return "application/octet-stream";
    }

    /**
     * 静态资源返回对象。
     */
    public static class StaticResource {
        public final int status;
        public final String contentType;
        public final byte[] body;

        /**
         * 构造静态资源（字符串）。
         */
        public StaticResource(int status, String contentType, String body) {
            this(status, contentType, body.getBytes());
        }

        /**
         * 构造静态资源（二进制）。
         */
        public StaticResource(int status, String contentType, byte[] body) {
            this.status = status;
            this.contentType = contentType;
            this.body = body;
        }
    }
}
