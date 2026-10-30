package com.demo;

public class Message {
    private String username;
    private String message;


    // 无参构造函数
    public Message() {
    }

    // 带参数的构造函数
    public Message( String username, String message) {
        this.username = username;
        this.message = message;
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



    // 可以重写 toString 方法来提供 Message 对象的字符串表示
    @Override
    public String toString() {
        return "Message{" +
                ", username='" + username + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}
