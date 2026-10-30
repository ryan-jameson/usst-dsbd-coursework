// User.java
package com.demo;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class User implements Serializable {
	private static final long serialVersionUID = 1L;
    private String username;
    private String password;
    private List<BrowsingHistory> browsingHistories; // 存储多个商品的浏览历史
    private Cart shoppingCart;
    public User() {
    }
    public User(String username, String password) {
        this.username = username;
        this.password = password;
        this.browsingHistories = new ArrayList<>();
        this.shoppingCart = new Cart();
    }

    // Getter和Setter方法
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void addBrowsingHistory(BrowsingHistory history) {
        browsingHistories.add(history);
    }

    public List<BrowsingHistory> getBrowsingHistories() {
        return browsingHistories;
    }

    public Cart getShoppingCart() {
        return shoppingCart;
    }
    public void setShoppingCart(Cart shoppingCart) {
    	this.shoppingCart = shoppingCart;
    }
}