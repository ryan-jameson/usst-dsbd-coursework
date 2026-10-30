package com.experiment6.common;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

/**
 * 应用配置加载器：从 .env 文件中读取配置。
 */
public class AppConfig {
    private static final Properties CONFIG = new Properties();
    private static boolean loaded = false;

    /**
     * 加载配置文件。
     */
    public static synchronized void load() {
        if (loaded) return;
        String[] candidates = {
                "src/main/resources/.env",
                ".env",
                "../.env"
        };
        for (String path : candidates) {
            try (FileInputStream fis = new FileInputStream(path)) {
                CONFIG.load(fis);
                loaded = true;
                return;
            } catch (IOException ignored) {
                System.err.println("读取配置失败: " + path);
            }
        }
        loaded = true;
    }

    /**
     * 获取字符串配置值。
     * @param key 键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public static String get(String key, String defaultValue) {
        load();
        String value = CONFIG.getProperty(key);
        return value == null ? defaultValue : value.trim();
    }

    /**
     * 获取整数配置值。
     * @param key 键
     * @param defaultValue 默认值
     * @return 整数
     */
    public static int getInt(String key, int defaultValue) {
        load();
        String value = CONFIG.getProperty(key);
        if (value == null || value.trim().isEmpty()) return defaultValue;
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
}
