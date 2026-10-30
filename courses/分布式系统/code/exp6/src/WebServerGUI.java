import javax.swing.*;
import java.awt.*;
import java.io.OutputStream;
import java.io.PrintStream;

public class WebServerGUI {
    private JFrame frame;
    private JTextArea logArea;
    private JButton btnStart;
    private Thread serverThread;

    public WebServerGUI() {
        frame = new JFrame("Web 服务器控制台 - AI版");
        frame.setSize(600, 400);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 14));
        logArea.setBackground(new Color(30, 30, 30));
        logArea.setForeground(new Color(200, 200, 200));
        JScrollPane scrollPane = new JScrollPane(logArea);
        frame.add(scrollPane, BorderLayout.CENTER);

        JPanel panel = new JPanel();
        btnStart = new JButton("启动服务器 (端口 8080)");
        btnStart.setFont(new Font("微软雅黑", Font.BOLD, 14));
        btnStart.addActionListener(e -> startServer());
        panel.add(btnStart);
        frame.add(panel, BorderLayout.NORTH);

        redirectSystemOut();
    }

    private void startServer() {
        if (serverThread == null || !serverThread.isAlive()) {
            btnStart.setEnabled(false);
            btnStart.setText("服务器运行中...");
            serverThread = new Thread(() -> {
                WebServer.main(new String[]{});
            });
            serverThread.start();
        }
    }

    private void redirectSystemOut() {
        OutputStream out = new OutputStream() {
            @Override
            public void write(int b) {
                SwingUtilities.invokeLater(() -> {
                    logArea.append(String.valueOf((char) b));
                    logArea.setCaretPosition(logArea.getDocument().getLength());
                });
            }
        };
        System.setOut(new PrintStream(out, true));
        System.setErr(new PrintStream(out, true));
    }

    public void show() {
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new WebServerGUI().show());
    }
}
