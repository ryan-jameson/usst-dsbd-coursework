package com.experiment6.ai;

import com.experiment6.common.AppConfig;
import com.experiment6.common.AppLogger;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

/**
 * AI内容生成器。
 */
public class AiContentGenerator {

    private static final ConcurrentHashMap<String, String> cache = new ConcurrentHashMap<>();

    /**
     * 生成个性化HTML内容。
     * @param userIp 用户IP
     * @param path 请求路径
     * @return HTML内容
     */
    public String generateProfileContent(String userIp, String path) {
        String cacheKey = userIp + ":" + path;
        if (cache.containsKey(cacheKey)) {
            return cache.get(cacheKey);
        }

        int timeoutMs = AppConfig.getInt("AI_TIMEOUT_MS", 5000);
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<String> future = executor.submit(() -> callOpenAiApi(userIp, path));

        try {
            String aiResult = future.get(timeoutMs, TimeUnit.MILLISECONDS);
            cache.put(cacheKey, aiResult);
            return aiResult;
        } catch (TimeoutException e) {
            future.cancel(true);
            AppLogger.error("AI调用超时", e);
            return "<html><body><h2>Server is busy, AI timeout. Default content.</h2></body></html>";
        } catch (Exception e) {
            AppLogger.error("AI生成异常", e);
            return "<html><body><h2>AI Generator Exception: " + e.getMessage() + "</h2></body></html>";
        } finally {
            executor.shutdown();
        }
    }

    private String callOpenAiApi(String userIp, String path) throws Exception {
        String prompt = "用户IP{" + userIp + "}访问了{" + path + "}，请生成一个个性化HTML页面，包含欢迎信息和推荐内容。";

        String apiBase = AppConfig.get("AI_API_URL", "https://api.chatanywhere.org/v1");
        String apiUrl = apiBase.endsWith("/chat/completions") ? apiBase : apiBase + "/chat/completions";
        String apiKey = AppConfig.get("AI_API_KEY", "");
        String model = AppConfig.get("AI_MODEL", "gpt-3.5-turbo");

        URL url = new java.net.URI(apiUrl).toURL();
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        if (!apiKey.isEmpty()) {
            conn.setRequestProperty("Authorization", "Bearer " + apiKey);
        }
        conn.setDoOutput(true);

        String jsonPayload = "{\"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + prompt.replace("\"", "\\\"").replace("\n", "\\n") + "\"}], \"max_tokens\": " + AppConfig.getInt("AI_MAX_TOKENS", 1000) + "}";

        try (OutputStream os = conn.getOutputStream()) {
            os.write(jsonPayload.getBytes(StandardCharsets.UTF_8));
            os.flush();
        }

        int code = conn.getResponseCode();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(
                code >= 400 ? conn.getErrorStream() : conn.getInputStream(), StandardCharsets.UTF_8))) {
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
            return extractContent(response.toString());
        }
    }

    private String extractContent(String rawJson) {
        String marker = "\"content\":\"";
        int idx = rawJson.indexOf(marker);
        if (idx == -1) return rawJson;

        int start = idx + marker.length();
        int end = rawJson.indexOf("\"", start);
        while (end != -1 && rawJson.charAt(end - 1) == '\\') {
            end = rawJson.indexOf("\"", end + 1);
        }
        if (end == -1) return rawJson;

        return rawJson.substring(start, end).replace("\\n", "\n").replace("\\\"", "\"");
    }
}
