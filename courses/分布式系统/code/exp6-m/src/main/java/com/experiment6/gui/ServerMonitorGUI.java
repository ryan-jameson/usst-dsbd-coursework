package com.experiment6.gui;

import com.experiment6.common.AppLogger;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.TitledBorder;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ServerMonitorGUI {
    private JFrame frame;
    private JLabel lblStatus;
    private JLabel lblPort;
    private JLabel lblStartTime;
    private JLabel lblConnections;
    private JLabel lblTotalRequests;
    private JLabel lblAiRequests;
    private JLabel lblDbStatus;
    private JTable logTable;
    private DefaultTableModel tableModel;
    private JLabel trendPlaceholder;
    private JLabel responsePlaceholder;
    private JLabel piePlaceholder;
    
    private int currentConnections = 0;
    private long totalRequests = 0;
    private long aiRequests = 0;
    private long startTime;
    private final int port;
    private String lastHttpTrace = "";
    private String lastCgiLog = "";

    public ServerMonitorGUI() {
        this(8080);
    }

    public ServerMonitorGUI(int port) {
        this.port = port;
        startTime = System.currentTimeMillis();

        frame = new JFrame("🚀 智能Web服务器监控中心 - 实验6");
        frame.setSize(1200, 800);
        frame.setLayout(new BorderLayout());
        frame.getContentPane().setBackground(ThemeManager.BACKGROUND_DARK);
        frame.setResizable(true);

        frame.add(buildStatusBar(), BorderLayout.NORTH);
        frame.add(buildCenterPanel(), BorderLayout.CENTER);
        frame.add(buildBottomActions(), BorderLayout.SOUTH);

        startUptimeThread();
    }
    
    private void startUptimeThread() {
        new Thread(() -> {
            while(true) {
                try {
                    Thread.sleep(1000);
                    long seconds = (System.currentTimeMillis() - startTime) / 1000;
                    SwingUtilities.invokeLater(() -> lblStatus.setText("● 运行中  |  运行时间: " + seconds + "s"));
                } catch (InterruptedException ignored) {}
            }
        }).start();
    }

    /**
     * 显示监控界面。
     */
    public void showInterface() {
        SwingUtilities.invokeLater(() -> {
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }

    /**
     * 增加连接计数。
     */
    public synchronized void incrementConnection() {
        currentConnections++;
        updateConnectionLabel();
    }

    /**
     * 减少连接计数。
     */
    public synchronized void decrementConnection() {
        currentConnections--;
        if (currentConnections < 0) currentConnections = 0;
        updateConnectionLabel();
    }
    
    private void updateConnectionLabel() {
        SwingUtilities.invokeLater(() -> lblConnections.setText("连接数: " + currentConnections));
    }

    /**
     * 记录系统日志。
     * @param msg 日志内容
     */
    public void logMessage(String msg) {
        System.out.println("[ServerMonitor] " + msg);
    }

    /**
     * 添加请求日志。
     */
    public void addLogEntry(String ip, String method, String path, int status, long duration, boolean isAi) {
        SwingUtilities.invokeLater(() -> {
            String time = new SimpleDateFormat("HH:mm:ss").format(new Date());
            totalRequests++;
            if (isAi) aiRequests++;
            tableModel.insertRow(0, new Object[]{time, ip, method, path, status, isAi ? "✅" : "❌"});
            updateStatsLabel();
            // 保持日志最多1000行
            if (tableModel.getRowCount() > 1000) {
                tableModel.removeRow(1000);
            }
        });
    }

    private JPanel buildStatusBar() {
        JPanel statusBar = new JPanel(new GridLayout(2, 1));
        statusBar.setBackground(ThemeManager.PANEL_DARK);
        statusBar.setBorder(new EmptyBorder(10, 16, 10, 16));

        JPanel row1 = new JPanel(new FlowLayout(FlowLayout.LEFT, 18, 2));
        row1.setBackground(ThemeManager.PANEL_DARK);
        lblStatus = new JLabel("● 运行中");
        lblStatus.setForeground(ThemeManager.ACCENT_GREEN);
        lblStatus.setFont(new Font("微软雅黑", Font.BOLD, 14));

        lblPort = new JLabel("端口: " + port);
        lblPort.setForeground(ThemeManager.TEXT_PRIMARY);
        lblStartTime = new JLabel("启动时间: " + new SimpleDateFormat("HH:mm:ss").format(new Date()));
        lblStartTime.setForeground(ThemeManager.TEXT_PRIMARY);

        row1.add(lblStatus);
        row1.add(lblPort);
        row1.add(lblStartTime);

        JPanel row2 = new JPanel(new FlowLayout(FlowLayout.LEFT, 18, 2));
        row2.setBackground(ThemeManager.PANEL_DARK);
        lblConnections = new JLabel("连接数: 0");
        lblConnections.setForeground(ThemeManager.TEXT_SECONDARY);
        lblTotalRequests = new JLabel("总请求: 0");
        lblTotalRequests.setForeground(ThemeManager.TEXT_SECONDARY);
        lblAiRequests = new JLabel("AI生成: 0 (0%)");
        lblAiRequests.setForeground(ThemeManager.TEXT_SECONDARY);
    lblDbStatus = new JLabel("数据库状态: 未连接");
        lblDbStatus.setForeground(ThemeManager.ACCENT_BLUE);

        row2.add(lblConnections);
        row2.add(lblTotalRequests);
        row2.add(lblAiRequests);
        row2.add(lblDbStatus);

        statusBar.add(row1);
        statusBar.add(row2);
        return statusBar;
    }

    private JPanel buildCenterPanel() {
        JPanel center = new JPanel();
        center.setBackground(ThemeManager.BACKGROUND_DARK);
        center.setLayout(new BorderLayout(12, 12));
        center.setBorder(new EmptyBorder(12, 16, 12, 16));

        JPanel chartsPanel = new JPanel(new GridLayout(1, 2, 12, 12));
        chartsPanel.setBackground(ThemeManager.BACKGROUND_DARK);

    JPanel trendPanel = new JPanel(new GridLayout(2, 1));
        trendPanel.setBackground(ThemeManager.PANEL_DARK);
        trendPanel.setBorder(new TitledBorder(null, "请求量趋势图", TitledBorder.LEFT, TitledBorder.TOP, new Font("微软雅黑", Font.BOLD, 12), ThemeManager.TEXT_PRIMARY));
    trendPlaceholder = new JLabel("[折线图组件]", SwingConstants.CENTER);
        trendPlaceholder.setForeground(ThemeManager.TEXT_SECONDARY);
    responsePlaceholder = new JLabel("[响应时间分布]", SwingConstants.CENTER);
    responsePlaceholder.setForeground(ThemeManager.TEXT_SECONDARY);
    trendPanel.add(trendPlaceholder);
    trendPanel.add(responsePlaceholder);

        JPanel piePanel = new JPanel(new BorderLayout());
        piePanel.setBackground(ThemeManager.PANEL_DARK);
        piePanel.setBorder(new TitledBorder(null, "AI生成占比饼图", TitledBorder.LEFT, TitledBorder.TOP, new Font("微软雅黑", Font.BOLD, 12), ThemeManager.TEXT_PRIMARY));
        piePlaceholder = new JLabel("[饼图组件]", SwingConstants.CENTER);
        piePlaceholder.setForeground(ThemeManager.TEXT_SECONDARY);
        piePanel.add(piePlaceholder, BorderLayout.CENTER);

        chartsPanel.add(trendPanel);
        chartsPanel.add(piePanel);

        JPanel tablePanel = new JPanel(new BorderLayout());
        tablePanel.setBackground(ThemeManager.PANEL_DARK);
        JLabel logTitle = new JLabel("📋 实时请求日志");
        logTitle.setForeground(ThemeManager.TEXT_PRIMARY);
        logTitle.setBorder(new EmptyBorder(8, 8, 6, 8));
        tablePanel.add(logTitle, BorderLayout.NORTH);

        String[] columnNames = {"时间", "IP", "方法", "路径", "状态", "AI"};
        tableModel = new DefaultTableModel(columnNames, 0);
        logTable = new JTable(tableModel);
        logTable.setBackground(new Color(55, 55, 55));
        logTable.setForeground(ThemeManager.TEXT_PRIMARY);
        logTable.setFont(new Font("Consolas", Font.PLAIN, 13));
        logTable.getTableHeader().setBackground(new Color(70, 70, 70));
        logTable.getTableHeader().setForeground(ThemeManager.TEXT_PRIMARY);
        logTable.setRowHeight(24);

        JScrollPane scrollPane = new JScrollPane(logTable);
        scrollPane.getViewport().setBackground(ThemeManager.PANEL_DARK);
        tablePanel.add(scrollPane, BorderLayout.CENTER);

        center.add(chartsPanel, BorderLayout.NORTH);
        center.add(tablePanel, BorderLayout.CENTER);
        return center;
    }

    private JPanel buildBottomActions() {
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 8));
        bottom.setBackground(ThemeManager.PANEL_DARK);

        JButton btnRefresh = createActionButton("刷新日志", ThemeManager.ACCENT_BLUE);
        btnRefresh.addActionListener(e -> refreshLogs());

        JButton btnExport = createActionButton("导出CSV", ThemeManager.ACCENT_BLUE);
        btnExport.addActionListener(e -> exportLogs());

        JButton btnClear = createActionButton("清空日志", ThemeManager.ACCENT_BLUE);
        btnClear.addActionListener(e -> clearLogs());

        JButton btnDb = createActionButton("数据库状态", ThemeManager.ACCENT_GREEN);
        btnDb.addActionListener(e -> JOptionPane.showMessageDialog(frame, "数据库连接状态: " + lblDbStatus.getText()));

        JButton btnAi = createActionButton("AI配置", ThemeManager.ACCENT_GREEN);
        btnAi.addActionListener(e -> JOptionPane.showMessageDialog(frame, "AI配置已从 .env 加载"));

    JButton btnHelp = createActionButton("帮助", ThemeManager.ACCENT_GREEN);
    btnHelp.addActionListener(e -> showHelpDialog());

        bottom.add(btnRefresh);
        bottom.add(btnExport);
        bottom.add(btnClear);
        bottom.add(btnDb);
        bottom.add(btnAi);
        bottom.add(btnHelp);
        return bottom;
    }

    private JButton createActionButton(String text, Color color) {
        JButton button = new JButton(text);
        button.setBackground(color);
        button.setForeground(ThemeManager.TEXT_PRIMARY);
        button.setFocusPainted(false);
        return button;
    }

    private void refreshLogs() {
        logMessage("刷新日志按钮已触发");
    }

    private void exportLogs() {
        JFileChooser chooser = new JFileChooser();
        chooser.setSelectedFile(new File("request_logs.csv"));
        int result = chooser.showSaveDialog(frame);
        if (result != JFileChooser.APPROVE_OPTION) return;

        File file = chooser.getSelectedFile();
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
            for (int col = 0; col < tableModel.getColumnCount(); col++) {
                writer.write(tableModel.getColumnName(col));
                writer.write(col == tableModel.getColumnCount() - 1 ? "\n" : ",");
            }
            for (int row = 0; row < tableModel.getRowCount(); row++) {
                for (int col = 0; col < tableModel.getColumnCount(); col++) {
                    writer.write(String.valueOf(tableModel.getValueAt(row, col)));
                    writer.write(col == tableModel.getColumnCount() - 1 ? "\n" : ",");
                }
            }
            JOptionPane.showMessageDialog(frame, "日志导出成功: " + file.getAbsolutePath());
        } catch (Exception ex) {
            AppLogger.error("导出日志失败", ex);
            JOptionPane.showMessageDialog(frame, "导出失败: " + ex.getMessage());
        }
    }

    private void clearLogs() {
        tableModel.setRowCount(0);
        totalRequests = 0;
        aiRequests = 0;
        updateStatsLabel();
    }

    private void updateStatsLabel() {
        double ratio = totalRequests == 0 ? 0 : (aiRequests * 100.0 / totalRequests);
        lblTotalRequests.setText("总请求: " + totalRequests);
        lblAiRequests.setText(String.format("AI生成: %d (%.0f%%)", aiRequests, ratio));
    }

    /**
     * 更新数据库状态显示。
     * @param connected 是否已连接
     */
    public void updateDbStatus(boolean connected) {
        lblDbStatus.setText("数据库状态: " + (connected ? "已连接" : "未连接"));
        lblDbStatus.setForeground(connected ? ThemeManager.ACCENT_GREEN : ThemeManager.ACCENT_BLUE);
    }

    /**
     * 更新HTTP请求响应追踪信息。
     * @param trace 完整HTTP交互内容
     */
    public void updateHttpTrace(String trace) {
        lastHttpTrace = trace;
    }

    /**
     * 更新CGI执行日志。
     * @param log CGI日志
     */
    public void updateCgiLog(String log) {
        lastCgiLog = log;
    }

    /**
     * 显示服务器启动提示。
     * @param message 提示信息
     */
    public void showStartupMessage(String message) {
        SwingUtilities.invokeLater(() -> JOptionPane.showMessageDialog(frame, message));
    }

    private void showHelpDialog() {
        StringBuilder sb = new StringBuilder();
        sb.append("实验6监控面板：支持日志查看、导出与AI统计\n\n");
        sb.append("最近一次HTTP请求/响应：\n");
        sb.append(lastHttpTrace.isEmpty() ? "(暂无)" : lastHttpTrace);
        sb.append("\n\n最近一次CGI执行日志：\n");
        sb.append(lastCgiLog.isEmpty() ? "(暂无)" : lastCgiLog);
        JOptionPane.showMessageDialog(frame, sb.toString());
    }
}
