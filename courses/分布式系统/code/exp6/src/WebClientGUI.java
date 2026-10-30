import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class WebClientGUI {
    private JFrame frame;
    private JTextArea chatArea;
    private JTextField inputField;
    private JButton btnSend;
    private JButton btnSendWithDB;

    // 配置参数区
    private String AI_API_URL;
    private String AI_API_KEY;
    private String AI_MODEL_NAME;
    private String DB_URL;
    private String DB_USER;
    private String DB_PASS;

    public WebClientGUI() {
        loadEnvironmentConfig();

        frame = new JFrame("AI 智能双向客户端 (连通大模型与 MySQL)");
        frame.setSize(750, 550);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout(10, 10));

        // 聊天显示区
        chatArea = new JTextArea();
        chatArea.setEditable(false);
        chatArea.setLineWrap(true);
        chatArea.setWrapStyleWord(true);
        chatArea.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        chatArea.setBackground(new Color(245, 245, 245));
        
        JScrollPane scrollPane = new JScrollPane(chatArea);
        scrollPane.setBorder(BorderFactory.createTitledBorder("交互与数据记录"));
        frame.add(scrollPane, BorderLayout.CENTER);

        // 底部输入区
        JPanel bottomPanel = new JPanel(new BorderLayout(5, 5));
        bottomPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        inputField = new JTextField();
        inputField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        inputField.addActionListener(e -> sendMessage(false));
        bottomPanel.add(inputField, BorderLayout.CENTER);

        JPanel btnPanel = new JPanel(new GridLayout(1, 2, 5, 0));
        btnSend = new JButton("直接对话(无DB)");
        btnSend.setFont(new Font("微软雅黑", Font.BOLD, 13));
        btnSend.addActionListener(e -> sendMessage(false));
        btnPanel.add(btnSend);

        btnSendWithDB = new JButton("结合数据库流数据询问AI");
        btnSendWithDB.setFont(new Font("微软雅黑", Font.BOLD, 13));
        btnSendWithDB.setForeground(new Color(0, 102, 204));
        btnSendWithDB.addActionListener(e -> sendMessage(true));
        btnPanel.add(btnSendWithDB);

        bottomPanel.add(btnPanel, BorderLayout.EAST);
        frame.add(bottomPanel, BorderLayout.SOUTH);
    }

    private void loadEnvironmentConfig() {
        Properties props = new Properties();
        try (FileInputStream fis = new FileInputStream("../.env")) {
            props.load(fis);
            
            DB_URL = cleanProp(props.getProperty("DB_URL"));
            DB_USER = cleanProp(props.getProperty("DB_USER"));
            DB_PASS = cleanProp(props.getProperty("DB_PASS"));
            
            String rawBaseUrl = cleanProp(props.getProperty("BASE_URL"));
            if (!rawBaseUrl.endsWith("/chat/completions")) {
                rawBaseUrl = rawBaseUrl.endsWith("/") ? rawBaseUrl + "chat/completions" : rawBaseUrl + "/chat/completions";
            }
            AI_API_URL = rawBaseUrl;
            AI_API_KEY = cleanProp(props.getProperty("API_KEY"));
            AI_MODEL_NAME = cleanProp(props.getProperty("MODEL_NAME", "gpt-3.5-turbo"));
            
        } catch (Exception e) {
            System.err.println("读取 ../.env 失败: " + e.getMessage());
        }
    }

    private String cleanProp(String val) {
        if (val == null) return null;
        val = val.trim();
        if (val.startsWith("\"") && val.endsWith("\"")) {
            val = val.substring(1, val.length() - 1);
        }
        return val;
    }

    private void sendMessage(boolean useDB) {
        String text = inputField.getText().trim();
        if (text.isEmpty()) return;

        appendLog("【你" + (useDB ? " (附带数据库流)" : "") + " 】: " + text);
        inputField.setText("");
        btnSend.setEnabled(false);
        btnSendWithDB.setEnabled(false);

        new Thread(() -> {
            try {
                String promptContext = text;
                if (useDB) {
                    appendLog("【系统】正在获取 MySQL 数据库内容...");
                    String dbData = fetchDatabaseContext();
                    promptContext = "请根据以下的数据库内容，回答我的问题：\n【数据库内容：】" + dbData + "\n\n【我的问题：】" + text;
                }
                
                String response = callAIServer(promptContext);
                appendLog("【AI (" + AI_MODEL_NAME + ")】: " + parseJsonSimpleResponse(response));
            } catch (Exception ex) {
                appendLog("【错误】: 无法处理请求 (" + ex.getMessage() + ")");
                ex.printStackTrace();
            } finally {
                SwingUtilities.invokeLater(() -> {
                    btnSend.setEnabled(true);
                    btnSendWithDB.setEnabled(true);
                });
            }
        }).start();
    }

    private String fetchDatabaseContext() throws Exception {
        if(DB_URL == null) return "【未加载到DB_URL配置】";
        Class.forName("com.mysql.cj.jdbc.Driver");
        StringBuilder sb = new StringBuilder();
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SHOW TABLES")) {
            
            sb.append("存在的表: ");
            while (rs.next()) {
                sb.append(rs.getString(1)).append(" ");
            }
        }
        return sb.toString() + " (此处只简单展示现有表，您可以在此深入定制)";
    }

    private String callAIServer(String message) throws Exception {
        URL url = new java.net.URI(AI_API_URL).toURL();
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        conn.setRequestProperty("Authorization", "Bearer " + AI_API_KEY);
        conn.setDoOutput(true);

        String jsonInputString = "{\"model\": \"" + AI_MODEL_NAME + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + message.replace("\"", "\\\"").replace("\n", "\\n") + "\"}]}";

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInputString.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }

        int code = conn.getResponseCode();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(
                code >= 400 ? conn.getErrorStream() : conn.getInputStream(), StandardCharsets.UTF_8))) {
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
            return response.toString(); 
        }
    }

    private String parseJsonSimpleResponse(String rawJson) {
        // Simple manual JSON extraction avoiding heavy libraries
        String marker = "\"content\":\"";
        int idx = rawJson.indexOf(marker);
        if (idx == -1) return rawJson;
        
        int start = idx + marker.length();
        int end = rawJson.indexOf("\"", start);
        while (end != -1 && rawJson.charAt(end - 1) == '\\') {
            end = rawJson.indexOf("\"", end + 1);
        }
        if (end == -1) return rawJson;
        
        return rawJson.substring(start, end).replace("\\n", "\n").replace("\\\"", "\"");
    }

    private void appendLog(String log) {
        SwingUtilities.invokeLater(() -> {
            chatArea.append(log + "\n\n");
            chatArea.setCaretPosition(chatArea.getDocument().getLength());
        });
    }

    public void show() {
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    public static void main(String[] args) {
        try { UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName()); } catch (Exception ignored) {}
        SwingUtilities.invokeLater(() -> new WebClientGUI().show());
    }
}
