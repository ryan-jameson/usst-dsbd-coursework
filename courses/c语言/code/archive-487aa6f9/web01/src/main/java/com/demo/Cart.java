package com.demo;
import java.util.*;

public class Cart {
	private ArrayList<Product> products;

    public Cart() {
        products = new ArrayList<>();
    }

    public void addProduct(Product product) {
        products.add(product);
    }

    public void removeProduct(Product product) {
    	int index=products.indexOf(product);
    	if(index==-1) {
    		products.remove(0);
    	}else {
    		products.remove(index);
    	}
    }

    public ArrayList<Product> getProducts() {
        return products;
    }

    public double calculateTotalPrice() {
        double total = 0;
        for (Product product : products) {
            total += product.getPrice();
        }
        return total;
    }
 // 清空购物车
    public void clear() {
        products.clear();
    }
}
