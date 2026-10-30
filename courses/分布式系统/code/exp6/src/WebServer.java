import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * 实验六：基本 Web 服务器主类。
 * 监听 8080 端口，接收连接并交给 ClientHandler 多线程处理。
 */
public class WebServer {
    public static final int PORT = 8080;

    public static void main(String[] args) {
        System.out.println("WebServer 启动中，端口: " + PORT);
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket client = serverSocket.accept();
                Thread t = new Thread(new ClientHandler(client));
                t.start();
            }
        } catch (IOException e) {
            System.err.println("服务器异常: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
