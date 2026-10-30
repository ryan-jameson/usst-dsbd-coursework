package com.experiment6.common;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * 简易日志工具：写入日志文件，线程安全。
 */
public class AppLogger {
    private static final Object LOCK = new Object();

    /**
     * 记录INFO日志。
     * @param message 日志内容
     */
    public static void info(String message) {
        write("INFO", message, null);
    }

    /**
     * 记录ERROR日志。
     * @param message 日志内容
     * @param t 异常
     */
    public static void error(String message, Throwable t) {
        write("ERROR", message, t);
    }

    private static void write(String level, String message, Throwable t) {
        String logFile = AppConfig.get("LOG_FILE", "./logs/server.log");
        File file = new File(logFile);
        File dir = file.getParentFile();
        if (dir != null && !dir.exists()) {
            dir.mkdirs();
        }
        String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        synchronized (LOCK) {
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {
                writer.write("[" + timestamp + "][" + level + "] " + message);
                writer.newLine();
                if (t != null) {
                    writer.write("    " + t.getClass().getName() + ": " + t.getMessage());
                    writer.newLine();
                }
            } catch (IOException ignored) {
                // 避免日志写入导致应用崩溃
            }
        }
    }
}
