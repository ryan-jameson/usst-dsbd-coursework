import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.rmi.Naming;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.List;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

/**
 * RMI 客户端图形界面程序，支持交互式增删改查。
 */
public class RMIClient extends JFrame {

    private IRemoteStudentService service;

    private JTextField idField, nameField, chineseField, mathField, englishField;
    private JTextArea logArea;

    public RMIClient() {
        setTitle("RMI 分布式学生管理系统 - 客户端");
        setSize(700, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // --- 顶部输入区 ---
        JPanel inputPanel = new JPanel(new GridLayout(2, 6, 5, 5));
        inputPanel.add(new JLabel("学号:"));
        idField = new JTextField();
        inputPanel.add(idField);

        inputPanel.add(new JLabel("姓名:"));
        nameField = new JTextField();
        inputPanel.add(nameField);

        inputPanel.add(new JLabel("语文:"));
        chineseField = new JTextField();
        inputPanel.add(chineseField);

        inputPanel.add(new JLabel("数学:"));
        mathField = new JTextField();
        inputPanel.add(mathField);

        inputPanel.add(new JLabel("英语:"));
        englishField = new JTextField();
        inputPanel.add(englishField);

        // 占位
        inputPanel.add(new JLabel(""));
        inputPanel.add(new JLabel(""));

        // --- 中间按钮区 ---
        JPanel btnPanel = new JPanel();
        JButton btnConnect = new JButton("连接服务器");
        JButton btnAdd = new JButton("添加学生");
        JButton btnUpdate = new JButton("修改成绩");
        JButton btnDelete = new JButton("删除学生(按学号)");
        JButton btnQuery = new JButton("查询单个(按学号)");
        JButton btnQueryAll = new JButton("查询全部");

        btnPanel.add(btnConnect);
        btnPanel.add(btnAdd);
        btnPanel.add(btnUpdate);
        btnPanel.add(btnDelete);
        btnPanel.add(btnQuery);
        btnPanel.add(btnQueryAll);

        // --- 底部日志区 ---
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setRows(12);
        JScrollPane scrollPane = new JScrollPane(logArea);

        add(inputPanel, BorderLayout.NORTH);
        add(scrollPane, BorderLayout.CENTER);
        add(btnPanel, BorderLayout.SOUTH);

        // 绑定事件
        btnConnect.addActionListener(e -> connectServer());
        btnAdd.addActionListener(e -> addStudent());
        btnUpdate.addActionListener(e -> updateStudent());
        btnDelete.addActionListener(e -> deleteStudent());
        btnQuery.addActionListener(e -> queryStudent());
        btnQueryAll.addActionListener(e -> queryAllStudents());
    }

    private void log(String msg) {
        logArea.append(msg + "\n");
        logArea.setCaretPosition(logArea.getDocument().getLength());
    }

    private void connectServer() {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            service = (IRemoteStudentService) registry.lookup("StudentService");
            log(">>> 成功连接到 RMI 服务端！");
        } catch (Exception ex) {
            log("!!! 连接失败: " + ex.getMessage());
            ex.printStackTrace();
        }
    }

    private Student buildStudentFromInput() {
        try {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();
            double c = Double.parseDouble(chineseField.getText().trim());
            double m = Double.parseDouble(mathField.getText().trim());
            double e = Double.parseDouble(englishField.getText().trim());
            if (id.isEmpty() || name.isEmpty()) {
                throw new IllegalArgumentException("学号和姓名不能为空");
            }
            return new Student(id, name, c, m, e);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "输入数据无效: " + e.getMessage());
            return null;
        }
    }

    private void addStudent() {
        if (service == null) { log("请先连接服务器!"); return; }
        Student s = buildStudentFromInput();
        if (s == null) return;
        try {
            service.addStudent(s);
            log("[添加成功] " + s.toString());
        } catch (Exception ex) {
            log("添加失败: " + ex.getMessage());
        }
    }

    private void updateStudent() {
        if (service == null) { log("请先连接服务器!"); return; }
        Student s = buildStudentFromInput();
        if (s == null) return;
        try {
            service.updateStudent(s);
            log("[修改成功] " + s.toString());
        } catch (Exception ex) {
            log("修改失败: " + ex.getMessage());
        }
    }

    private void deleteStudent() {
        if (service == null) { log("请先连接服务器!"); return; }
        String id = idField.getText().trim();
        if (id.isEmpty()) { log("请输入要删除的学号!"); return; }
        try {
            service.deleteStudent(id);
            log("[删除成功] 学号: " + id);
        } catch (Exception ex) {
            log("删除失败: " + ex.getMessage());
        }
    }

    private void queryStudent() {
        if (service == null) { log("请先连接服务器!"); return; }
        String id = idField.getText().trim();
        if (id.isEmpty()) { log("请输入查询的学号!"); return; }
        try {
            Student s = service.queryStudent(id);
            if (s != null) {
                log("[查询结果] " + s.toString());
                nameField.setText(s.getName());
                chineseField.setText(String.valueOf(s.getChineseScore()));
                mathField.setText(String.valueOf(s.getMathScore()));
                englishField.setText(String.valueOf(s.getEnglishScore()));
            } else {
                log("[查询结果] 未找到学号为 " + id + " 的学生");
            }
        } catch (Exception ex) {
            log("查询失败: " + ex.getMessage());
        }
    }

    private void queryAllStudents() {
        if (service == null) { log("请先连接服务器!"); return; }
        try {
            List<Student> list = service.getAllStudents();
            log("=========== 最新所有学生数据 ===========");
            if (list.isEmpty()) {
                log("（暂无数据）");
            } else {
                for (Student s : list) {
                    log(s.toString());
                }
            }
            log("=========================================");
        } catch (Exception ex) {
            log("查询全部失败: " + ex.getMessage());
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new RMIClient().setVisible(true);
        });
    }
}
