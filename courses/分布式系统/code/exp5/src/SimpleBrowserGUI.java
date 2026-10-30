import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

public class SimpleBrowserGUI extends JFrame {

    private final JPanel cardPanel;
    private final RoundedTextField topUrlField;
    private final RoundedTextField homeUrlField;
    
    private final JEditorPane browserView;
    private final JTextArea sourceView;

    public SimpleBrowserGUI() {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        setTitle("简约浏览器 - Internet应用");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1000, 700);
        setLocationRelativeTo(null);
        getContentPane().setBackground(Color.WHITE);

        // 1. 恒定的顶部栏
        JPanel topPanel = new JPanel(new BorderLayout());
        topPanel.setBackground(Color.WHITE);
        topPanel.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));

        topUrlField = new RoundedTextField(50);
        topUrlField.setFont(new Font("Microsoft YaHei", Font.PLAIN, 15));
        topUrlField.addActionListener(e -> navigate(topUrlField.getText()));

        JPanel centerTop = new JPanel(new FlowLayout(FlowLayout.CENTER, 0, 0));
        centerTop.setBackground(Color.WHITE);
        centerTop.add(topUrlField);

        JButton homeBtn = new JButton(new HouseIcon());
        homeBtn.setContentAreaFilled(false);
        homeBtn.setBorderPainted(false);
        homeBtn.setFocusPainted(false);
        homeBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        homeBtn.setToolTipText("回到首页");
        homeBtn.addActionListener(e -> switchToHome());

        topPanel.add(centerTop, BorderLayout.CENTER);
        topPanel.add(homeBtn, BorderLayout.EAST);

        // 2. 卡片主内容区
        cardPanel = new JPanel(new CardLayout());
        cardPanel.setBackground(Color.WHITE);

        // --- 首页 View ---
        JPanel homeView = new JPanel(new GridBagLayout());
        homeView.setBackground(Color.WHITE);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0; gbc.gridy = 0;
        gbc.insets = new Insets(0, 0, 40, 0);

        JLabel titleLabel = new JLabel("<html><div style='text-align:center;'><h1 style='font-size:3.5em; color:#333333; margin:0; font-family:\"Microsoft YaHei\", sans-serif;'>Internet 应用</h1></div></html>");
        homeView.add(titleLabel, gbc);

        gbc.gridy = 1;
        homeUrlField = new RoundedTextField(40);
        homeUrlField.setFont(new Font("Microsoft YaHei", Font.PLAIN, 18));
        homeUrlField.addActionListener(e -> navigate(homeUrlField.getText()));
        homeView.add(homeUrlField, gbc);

        // --- 浏览器 View ---
        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
        tabbedPane.setBackground(Color.WHITE);

        browserView = new JEditorPane();
        browserView.setEditable(false);
        browserView.setContentType("text/html");

        sourceView = new JTextArea();
        sourceView.setEditable(false);
        sourceView.setFont(new Font("Consolas", Font.PLAIN, 14));
        sourceView.setLineWrap(true);

        tabbedPane.addTab("网页页面", new JScrollPane(browserView));
        tabbedPane.addTab("源代码", new JScrollPane(sourceView));

        // 添加卡片
        cardPanel.add(homeView, "HOME");
        cardPanel.add(tabbedPane, "BROWSER");

        // 组装框架
        setLayout(new BorderLayout());
        add(topPanel, BorderLayout.NORTH);
        add(cardPanel, BorderLayout.CENTER);

        switchToHome();
    }

    private void switchToHome() {
        topUrlField.setVisible(false);
        homeUrlField.setText("");
        CardLayout cl = (CardLayout) cardPanel.getLayout();
        cl.show(cardPanel, "HOME");
    }

    private void switchToBrowser() {
        topUrlField.setVisible(true);
        CardLayout cl = (CardLayout) cardPanel.getLayout();
        cl.show(cardPanel, "BROWSER");
    }

    private void navigate(String urlString) {
        urlString = urlString.trim();
        if (urlString.isEmpty()) return;

        if (!urlString.startsWith("http://") && !urlString.startsWith("https://")) {
            urlString = "http://" + urlString;
        }

        topUrlField.setText(urlString);

        try {
            URI uri = new URI(urlString);
            String host = uri.getHost();
            int port = uri.getPort();
            if (port == -1) {
                port = "https".equalsIgnoreCase(uri.getScheme()) ? 443 : 80;
            }
            if ("https".equalsIgnoreCase(uri.getScheme())) {
                JOptionPane.showMessageDialog(this, "当前实现为简易的Socket HTTP/1.0，不支持 HTTPS 请求，请尝试 http:// 网站（如 http://httpbin.org ）", "协议不支持", JOptionPane.WARNING_MESSAGE);
                return;
            }
            if (host == null) {
                JOptionPane.showMessageDialog(this, "解析主机名失败，请检查网址格式。", "错误", JOptionPane.ERROR_MESSAGE);
                return;
            }

            String tempPath = uri.getPath();
            if (tempPath == null || tempPath.isEmpty()) {
                tempPath = "/";
            }
            if (uri.getQuery() != null) {
                tempPath += "?" + uri.getQuery();
            }
            
            final String finalPath = tempPath;
            final int finalPort = port;
            final String finalHost = host;

            // 开启新线程请求网络，防止阻塞 UI
            new Thread(() -> {
                try {
                    HttpClient client = new HttpClient(finalHost, finalPort);
                    HttpResponse resp = client.doGET(finalPath);

                    String html = resp.getBody();
                    if (html == null) html = "";

                    // JEditorPane (HTML 3.2) 解析现代网页很容易抛出异常或假死
                    // 我们尽量提取 body 内容，并移除所有 <script>、<style>、<link> 等无关标签
                    String safeHtml = html;
                    if (safeHtml.toLowerCase().contains("<body") && safeHtml.toLowerCase().contains("</body>")) {
                        int start = safeHtml.toLowerCase().indexOf("<body");
                        int end = safeHtml.toLowerCase().lastIndexOf("</body>") + 7;
                        if (start < end) {
                            safeHtml = safeHtml.substring(start, end);
                        }
                    }
                    safeHtml = safeHtml.replaceAll("(?is)<script.*?>.*?</script>", "")
                                       .replaceAll("(?is)<style.*?>.*?</style>", "")
                                       .replaceAll("(?is)<link.*?>", "");

                    // 切回主线程更新 UI
                    String finalHtml = html;
                    String finalSafeHtml = safeHtml;
                    SwingUtilities.invokeLater(() -> {
                        sourceView.setText(finalHtml);
                        sourceView.setCaretPosition(0);
                        try {
                            browserView.setText("<html><body>" + finalSafeHtml + "</body></html>");
                        } catch (Exception ex) {
                            browserView.setText("<h2>页面渲染器不支持该格式，详见源代码标签页</h2>");
                        }
                        // 更新并切到浏览视图
                        switchToBrowser();
                    });

                } catch (IOException e) {
                    SwingUtilities.invokeLater(() -> {
                        browserView.setText("<h2>连接失败或请求异常</h2><p>" + e.getMessage() + "</p>");
                        sourceView.setText(e.getMessage());
                        switchToBrowser();
                    });
                }
            }).start();

        } catch (URISyntaxException e) {
            JOptionPane.showMessageDialog(this, "无效的URL格式", "错误", JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SimpleBrowserGUI().setVisible(true));
    }

    // 内部类：绘制圆角的文字输入框，极简风格
    class RoundedTextField extends JTextField {
        public RoundedTextField(int columns) {
            super(columns);
            setOpaque(false);
            setBorder(BorderFactory.createEmptyBorder(8, 15, 8, 15));
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(Color.WHITE);
            g2.fillRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 30, 30);
            super.paintComponent(g);
            g2.dispose();
        }

        @Override
        protected void paintBorder(Graphics g) {
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(new Color(180, 180, 180));
            g2.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 30, 30);
            g2.dispose();
        }
    }

    // 内部类：手绘小房子图标
    class HouseIcon implements Icon {
        @Override
        public void paintIcon(Component c, Graphics g, int x, int y) {
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(new Color(100, 100, 100));
            g2.setStroke(new BasicStroke(2f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
            
            // Roof
            int[] xPoints = {x + 2, x + 12, x + 22};
            int[] yPoints = {y + 12, y + 2, y + 12};
            g2.drawPolyline(xPoints, yPoints, 3);
            
            // House body
            g2.drawRect(x + 4, y + 12, 16, 10);
            
            // Door
            g2.drawRect(x + 10, y + 16, 4, 6);
            
            g2.dispose();
        }

        @Override
        public int getIconWidth() { return 24; }
        @Override
        public int getIconHeight() { return 24; }
    }
}

