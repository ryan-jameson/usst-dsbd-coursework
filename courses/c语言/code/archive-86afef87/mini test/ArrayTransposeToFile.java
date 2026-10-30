import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;

public class ArrayTransposeToFile {

    public static void main(String[] args) {
        int[][] originalArrays = {
                {1, 2, 3, 4},
                {5, 6, 7, 8},
                {9, 10, 11, 12}
        };

        int rows = originalArrays.length;
        int cols = originalArrays[0].length;
        int[][] transposedArrays = new int[cols][rows]; 
        
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                transposedArrays[j][i] = originalArrays[i][j]; 
            }
        }

        String filename = "arrays_output.txt";
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            
            writer.write("原二维数组:");
            writer.newLine();
            writeToFile(writer, originalArrays);
            
            writer.newLine(); 
   =
            writer.write("转置后的二维数组:");
            writer.newLine();
            writeToFile(writer, transposedArrays);
            
        } catch (IOException e) {
            System.err.println("写入文件时发生了以下错误： - ArrayTransposeToFile.java:39" + e.getMessage());
        }
    }
  
    private static void writeToFile(BufferedWriter writer, int[][] Arrays) throws IOException {
        for (int[] row : Arrays) {
            String rowStr = Arrays.toString(row);
            writer.write(rowStr);
            writer.newLine();
        }
    }
}