package com.experiment6.client;

import com.experiment6.ai.AiContentGenerator;
import com.experiment6.common.AppLogger;
import com.experiment6.database.UserProfileDao;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

/**
 * 智能Web客户端入口。
 */
public class WebClient {
    private JFrame frame;
    private JTable profileTable;
    private DefaultTableModel tableModel;
    private JEditorPane htmlPane;
    private JTextField pathField;

    /**
     * 启动客户端。
     * @param args args
     */
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new WebClient().show());
    }

    /**
     * 构造客户端界面。
     */
    public WebClient() {
        frame = new JFrame("智能Web客户端 - 实验6");
        frame.setSize(1000, 700);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("用户画像", buildProfilePanel());
        tabs.addTab("AI生成内容", buildAiPanel());
        frame.add(tabs, BorderLayout.CENTER);
    }

    private JPanel buildProfilePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] headers = {"user_id", "ip_address", "visit_count", "preferred_type", "interest_tags"};
        tableModel = new DefaultTableModel(headers, 0);
        profileTable = new JTable(tableModel);
        panel.add(new JScrollPane(profileTable), BorderLayout.CENTER);

        JButton btnRefresh = new JButton("刷新数据库");
        btnRefresh.addActionListener(e -> loadProfiles());
        panel.add(btnRefresh, BorderLayout.SOUTH);
        return panel;
    }

    private JPanel buildAiPanel() {
        JPanel panel = new JPanel(new BorderLayout(8, 8));
        JPanel top = new JPanel(new BorderLayout(8, 8));
        pathField = new JTextField("/profile/demo");
        JButton btnGenerate = new JButton("生成个性化页面");
        btnGenerate.addActionListener(e -> generateHtml());
        top.add(new JLabel("访问路径:"), BorderLayout.WEST);
        top.add(pathField, BorderLayout.CENTER);
        top.add(btnGenerate, BorderLayout.EAST);

        htmlPane = new JEditorPane();
        htmlPane.setContentType("text/html");
        htmlPane.setEditable(false);
        panel.add(top, BorderLayout.NORTH);
        panel.add(new JScrollPane(htmlPane), BorderLayout.CENTER);
        return panel;
    }

    private void loadProfiles() {
        try {
            tableModel.setRowCount(0);
            List<String[]> list = new UserProfileDao().fetchAll();
            for (String[] row : list) {
                tableModel.addRow(row);
            }
        } catch (Exception e) {
            AppLogger.error("加载 user_profile 失败", e);
            JOptionPane.showMessageDialog(frame, "数据库查询失败: " + e.getMessage());
        }
    }

    private void generateHtml() {
        String path = pathField.getText().trim();
        if (path.isEmpty()) return;
        try {
            String html = new AiContentGenerator().generateProfileContent("client", path);
            htmlPane.setText(html);
        } catch (Exception e) {
            AppLogger.error("生成HTML失败", e);
            JOptionPane.showMessageDialog(frame, "AI生成失败: " + e.getMessage());
        }
    }

    /**
     * 显示界面。
     */
    public void show() {
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
        loadProfiles();
    }
}
