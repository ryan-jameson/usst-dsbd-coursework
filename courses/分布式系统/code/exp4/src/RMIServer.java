import java.awt.BorderLayout;
import java.io.OutputStream;
import java.io.PrintStream;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.SwingUtilities;

/**
 * RMI 服务器端主程序 - 图形化监控界面。
 */
public class RMIServer extends JFrame {
    private JTextArea logArea;
    private JButton btnStart;
    private boolean isRunning = false;

    public RMIServer() {
        setTitle("RMI 分布式学生管理系统 - 服务端控制台");
        setSize(700, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // --- 顶部控制区 ---
        JPanel topPanel = new JPanel();
        btnStart = new JButton("启动 RMI 服务端");
        topPanel.add(btnStart);

        // --- 中央日志区 ---
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setRows(15);
        JScrollPane scrollPane = new JScrollPane(logArea);

        add(topPanel, BorderLayout.NORTH);
        add(scrollPane, BorderLayout.CENTER);

        // 重定向日志输出 (将 System.out 和 System.err 输出到界面)
        redirectSystemStreams();

        // 按钮事件
        btnStart.addActionListener(e -> startServer());
    }

    private void redirectSystemStreams() {
        OutputStream out = new OutputStream() {
            @Override
            public void write(int b) {
                updateTextArea(String.valueOf((char) b));
            }
            @Override
            public void write(byte[] b, int off, int len) {
                updateTextArea(new String(b, off, len));
            }
        };
        System.setOut(new PrintStream(out, true));
        System.setErr(new PrintStream(out, true));
    }

    private void updateTextArea(final String text) {
        SwingUtilities.invokeLater(() -> {
            logArea.append(text);
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }

    private void startServer() {
        if (isRunning) {
            System.out.println("服务端已经在运行中...");
            return;
        }
        
        // 我们用新线程开启，避免阻塞UI刷新
        new Thread(() -> {
            try {
                System.out.println("正在启动 RMI registry (1099端口)...");
                // 启动 rmiregistry（端口 1099）
                Registry registry = LocateRegistry.createRegistry(1099);

                System.out.println("正在连接数据库并初始化服务...");
                // 实例化服务实现 (此时会读 .env 并连数据库)
                IRemoteStudentService service = new RemoteStudentServiceImpl();

                // 绑定远程对象
                registry.bind("StudentService", service);

                System.out.println(">>> 启动成功！RMI Server is ready... (name: StudentService) <<<");
                SwingUtilities.invokeLater(() -> btnStart.setEnabled(false));
                isRunning = true;
            } catch (RemoteException e) {
                System.err.println("RMI 服务器启动失败 (可能是端口被占用): " + e.getMessage());
            } catch (Exception e) {
                System.err.println("服务端异常: " + e.getMessage());
            }
        }).start();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new RMIServer().setVisible(true);
        });
    }
}
