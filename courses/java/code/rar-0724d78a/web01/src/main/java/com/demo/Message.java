package com.demo;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;


public class Message {
    private String username;
    private String message;
    private long timestamp;

    // 无参构造函数
    public Message() {
    }

    // 带参数的构造函数
    public Message( String username, String message,long timestamp) {
        this.username = username;
        this.message = message;
        this.timestamp=timestamp;
       }


    // username 的 getter 和 setter 方法
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    // message 的 getter 和 setter 方法
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getTimestamp() {
    	 // 将时间戳转换为LocalDateTime对象
        LocalDateTime dateTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(timestamp), ZoneId.systemDefault());

        // 创建一个DateTimeFormatter对象，并指定日期时间格式
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        // 使用DateTimeFormatter对象格式化LocalDateTime对象
        String formattedDate = dateTime.format(formatter);
        return formattedDate;
    }
}
