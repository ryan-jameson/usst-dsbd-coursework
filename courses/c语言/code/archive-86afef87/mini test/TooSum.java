import java.util.HashMap;
import java.util.Map;

public class TooSum {
    public static void main(String[] args) {
        Map<Integer, Integer> map = new HashMap<>();
        int[] nums = {2, 7, 6, 11, 15, 3};
        int target = 9;
        boolean found = false; 

        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                System.out.println("索引对为： - TooSum.java:14" + map.get(complement) + "," + i); 
                found = true;
            }
            map.put(nums[i], i);
        }

        if (!found) {
            System.out.println("没有找到和为 - TooSum.java:21" + target + " 的两个数。");
        }
    }
}