import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.io.FileInputStream;
import java.io.IOException;

/**
 * 学生信息远程服务实现类，使用 MySQL 数据库。
 */
public class RemoteStudentServiceImpl extends UnicastRemoteObject implements IRemoteStudentService {
    private static final long serialVersionUID = 1L;

    private String dbUrl;
    private String dbUser;
    private String dbPass;

    public RemoteStudentServiceImpl() throws RemoteException {
        super();
        loadEnv();
        System.out.println("RemoteStudentServiceImpl 已实例化并读取环境配置");
    }

    private void loadEnv() {
        Properties props = new Properties();
        // 尝试从多个路径加载 .env
        String[] paths = {".env", "../.env", "../../.env"};
        boolean loaded = false;
        for (String path : paths) {
            try (FileInputStream fis = new FileInputStream(path)) {
                props.load(fis);
                dbUrl = props.getProperty("DB_URL");
                dbUser = props.getProperty("DB_USER");
                dbPass = props.getProperty("DB_PASS");
                System.out.println("成功加载配置: " + path);
                loaded = true;
                break;
            } catch (IOException e) {
                // Ignore and try next path
            }
        }
        if (!loaded) {
            System.err.println("无法加载.env文件，请确保文件存在！");
        }
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(dbUrl, dbUser, dbPass);
    }

    @Override
    public synchronized void addStudent(Student student) throws RemoteException {
        if (student == null || student.getStudentId() == null) {
            throw new RemoteException("学生或学号不能为空");
        }
        String sql = "INSERT INTO student (student_id, name, chinese_score, math_score, english_score) VALUES (?, ?, ?, ?, ?)";
        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, student.getStudentId());
            pstmt.setString(2, student.getName());
            pstmt.setDouble(3, student.getChineseScore());
            pstmt.setDouble(4, student.getMathScore());
            pstmt.setDouble(5, student.getEnglishScore());
            pstmt.executeUpdate();
            System.out.println("[ADD] Added student: " + student.getStudentId());
        } catch (SQLException e) {
            e.printStackTrace();
            throw new RemoteException("数据库操作失败: " + e.getMessage());
        }
    }

    @Override
    public synchronized void deleteStudent(String studentId) throws RemoteException {
        String sql = "DELETE FROM student WHERE student_id = ?";
        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, studentId);
            pstmt.executeUpdate();
            System.out.println("[DELETE] Deleted studentId: " + studentId);
        } catch (SQLException e) {
            e.printStackTrace();
            throw new RemoteException("数据库操作失败: " + e.getMessage());
        }
    }

    @Override
    public synchronized void updateStudent(Student student) throws RemoteException {
        if (student == null || student.getStudentId() == null) {
            throw new RemoteException("学生或学号不能为空");
        }
        String sql = "UPDATE student SET name = ?, chinese_score = ?, math_score = ?, english_score = ? WHERE student_id = ?";
        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, student.getName());
            pstmt.setDouble(2, student.getChineseScore());
            pstmt.setDouble(3, student.getMathScore());
            pstmt.setDouble(4, student.getEnglishScore());
            pstmt.setString(5, student.getStudentId());
            pstmt.executeUpdate();
            System.out.println("[UPDATE] Updated student: " + student.getStudentId());
        } catch (SQLException e) {
            e.printStackTrace();
            throw new RemoteException("数据库操作失败: " + e.getMessage());
        }
    }

    @Override
    public synchronized Student queryStudent(String studentId) throws RemoteException {
        String sql = "SELECT * FROM student WHERE student_id = ?";
        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, studentId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Student s = new Student(
                        rs.getString("student_id"),
                        rs.getString("name"),
                        rs.getDouble("chinese_score"),
                        rs.getDouble("math_score"),
                        rs.getDouble("english_score")
                    );
                    System.out.println("[QUERY] Query studentId: " + studentId);
                    return s;
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            throw new RemoteException("数据库操作失败: " + e.getMessage());
        }
        return null;
    }

    @Override
    public synchronized List<Student> getAllStudents() throws RemoteException {
        List<Student> list = new ArrayList<>();
        String sql = "SELECT * FROM student";
        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(new Student(
                    rs.getString("student_id"),
                    rs.getString("name"),
                    rs.getDouble("chinese_score"),
                    rs.getDouble("math_score"),
                    rs.getDouble("english_score")
                ));
            }
        } catch (SQLException e) {
            e.printStackTrace();
            throw new RemoteException("数据库操作失败: " + e.getMessage());
        }
        return list;
    }
}
