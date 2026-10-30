package com.experiment6.server;

import com.experiment6.common.AppConfig;
import com.experiment6.common.AppLogger;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * CGI路由网关。
 */
public class CgiGateway {

    /**
     * 处理CGI请求。
     * @param path 路径
     * @param method 方法
     * @param body 请求体
     * @return CGI输出结果
     */
    public String handleCgiRequest(String path, String method, String body) {
        String scriptName = path.substring(path.lastIndexOf("/") + 1);
        String cgiRoot = AppConfig.get("CGI_PATH", "src/main/resources/cgi-bin");
        File scriptFile = new File(cgiRoot, scriptName);

        if (!scriptFile.exists() || scriptName.contains("..")) {
            AppLogger.info("CGI禁止访问: " + scriptName);
            return "<html><body><h2>404 CGI Script Not Found or Forbidden</h2></body></html>";
        }

        try {
            String[] cmd;
            if (scriptName.endsWith(".bat")) {
                cmd = new String[]{"cmd.exe", "/c", scriptFile.getAbsolutePath()};
            } else if (scriptName.endsWith(".sh")) {
                cmd = new String[]{"sh", scriptFile.getAbsolutePath()};
            } else {
                return "<html><body><h2>500 Unsupported CGI extension</h2></body></html>";
            }

            Map<String, String> envMap = new HashMap<>(System.getenv());
            envMap.put("REQUEST_METHOD", method);
            envMap.put("QUERY_STRING", extractQuery(path));
            if ("POST".equalsIgnoreCase(method) && body != null) {
                envMap.put("CONTENT_LENGTH", String.valueOf(body.getBytes(StandardCharsets.UTF_8).length));
            }
            String[] envp = envMap.entrySet().stream()
                    .map(e -> e.getKey() + "=" + e.getValue())
                    .toArray(String[]::new);

            AppLogger.info("CGI调用: " + scriptFile.getAbsolutePath());
            Process process = Runtime.getRuntime().exec(cmd, envp, scriptFile.getParentFile());

            if ("POST".equalsIgnoreCase(method) && body != null && !body.isEmpty()) {
                try (OutputStream os = process.getOutputStream()) {
                    os.write(body.getBytes(StandardCharsets.UTF_8));
                    os.flush();
                }
            }

            boolean finished = process.waitFor(10, TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                AppLogger.error("CGI执行超时", null);
                return "<html><body><h2>504 CGI Execution Timeout</h2></body></html>";
            }

            try (BufferedReader br = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append("\n");
                }
                return sb.toString();
            }
        } catch (Exception e) {
            AppLogger.error("CGI执行异常", e);
            return "<html><body><h2>500 Internal Server Error</h2><p>" + e.getMessage() + "</p></body></html>";
        }
    }

    private String extractQuery(String path) {
        int idx = path.indexOf('?');
        return idx == -1 ? "" : path.substring(idx + 1);
    }
}
