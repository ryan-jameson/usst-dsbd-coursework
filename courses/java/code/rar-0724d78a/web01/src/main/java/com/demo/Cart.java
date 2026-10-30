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

    public void removeProduct(String productId) {
    	int index=-1;
   	 	for (Product p : products) {
   	 		index+=1;
            if (p.getId().equals(productId)) {
                break; // 找到后退出循环
            }
        }//查找商品方法,获得相应索引
    	products.remove(index);
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
