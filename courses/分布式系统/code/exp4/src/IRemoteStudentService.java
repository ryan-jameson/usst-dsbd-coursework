import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

/**
 * 学生信息远程服务接口，定义了增删改查等操作。
 */
public interface IRemoteStudentService extends Remote {

    /** 添加学生 */
    void addStudent(Student student) throws RemoteException;

    /** 按学号删除学生 */
    void deleteStudent(String studentId) throws RemoteException;

    /** 更新学生信息 */
    void updateStudent(Student student) throws RemoteException;

    /** 查询单个学生 */
    Student queryStudent(String studentId) throws RemoteException;

    /** 获取所有学生列表（便于测试） */
    List<Student> getAllStudents() throws RemoteException;
}
