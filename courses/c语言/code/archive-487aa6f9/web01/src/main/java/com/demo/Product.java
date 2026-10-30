package com.demo;
import java.io.Serializable;

public  class Product implements Serializable{
	private static final long serialVersionUID = 1L;
    private String id;
    private String imageUrl;
    private String name;
    private double price;
    private String description;
    private int clickCount; // 点击次数

    public Product() {
    }
    public Product(String id,String imageUrl,String name,double price,String description) {
    	this.id = id;
    	this.imageUrl = imageUrl;
    	this.name = name;
    	this.price = price;
    	this.description = description;
    	this.clickCount = 0; // 初始化点击次数为0
    }

    // Getter和Setter方法
    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getImageUrl() {
        return this.imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getPrice() {
        return this.price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
    public int getClickCount() {
        return clickCount;
    }

    public void setClickCount(int clickCount) {
        this.clickCount = clickCount;
    }
}