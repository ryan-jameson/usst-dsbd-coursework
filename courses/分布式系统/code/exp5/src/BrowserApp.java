/**
 * 控制台测试主程序：演示 GET 与 POST 请求。
 */
public class BrowserApp {
    public static void main(String[] args) {
        String host = "localhost";
        int port = 8080;

        try {
            HttpClient client = new HttpClient(host, port);

            System.out.println("=== 测试案例 1：GET /index.html ===");
            client.doGET("/index.html");

            System.out.println("=== 测试案例 2：POST /cgi-bin/test.bat ===");
            String formData = "name=Alice&score=90";
            client.doPOST("/cgi-bin/test.bat", formData);

        } catch (Exception e) {
            System.err.println("请求失败，请确保 Web 服务器已启动。错误: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
