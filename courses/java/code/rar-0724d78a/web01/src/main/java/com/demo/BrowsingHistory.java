package com.demo;
import java.io.Serializable;
import java.util.Date;

public class BrowsingHistory implements Serializable {
	private static final long serialVersionUID = 1L;
    private Product product;
    private int viewCount;
    private Date lastViewed;

    public BrowsingHistory(Product product) {
        this.product = product;
        this.viewCount = 1; // 初始化浏览次数为1
        this.lastViewed = new Date(); // 最后浏览时间设置为当前时间
    }

    public void incrementViewCount() {
        this.viewCount++;
    }

    public Product getProduct() {
        return product;
    }

    public int getViewCount() {
        return viewCount;
    }

    public Date getLastViewed() {
        return lastViewed;
    }
}
