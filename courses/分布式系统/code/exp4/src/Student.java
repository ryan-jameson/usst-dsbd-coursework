import java.io.Serializable;

/**
 * 学生实体模型，实现 Serializable 以便通过 RMI 进行远程传输。
 */
public class Student implements Serializable {
    private static final long serialVersionUID = 1L;

    // 学号
    private String studentId;
    // 姓名
    private String name;
    // 语文成绩
    private double chineseScore;
    // 数学成绩
    private double mathScore;
    // 英语成绩
    private double englishScore;

    public Student() {
    }

    public Student(String studentId, String name, double chineseScore, double mathScore, double englishScore) {
        this.studentId = studentId;
        this.name = name;
        this.chineseScore = chineseScore;
        this.mathScore = mathScore;
        this.englishScore = englishScore;
    }

    public String getStudentId() {
        return studentId;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getChineseScore() {
        return chineseScore;
    }

    public void setChineseScore(double chineseScore) {
        this.chineseScore = chineseScore;
    }

    public double getMathScore() {
        return mathScore;
    }

    public void setMathScore(double mathScore) {
        this.mathScore = mathScore;
    }

    public double getEnglishScore() {
        return englishScore;
    }

    public void setEnglishScore(double englishScore) {
        this.englishScore = englishScore;
    }

    @Override
    public String toString() {
        return "Student{" +
                "studentId='" + studentId + '\'' +
                ", name='" + name + '\'' +
                ", chineseScore=" + chineseScore +
                ", mathScore=" + mathScore +
                ", englishScore=" + englishScore +
                '}';
    }
}
