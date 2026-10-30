public class FindMinMax{
    public static void main(String[] args) {
        int[] arr = {3, 5, 1, 8, -2, 7};
        
        if(arr==null || arr.length==0){
            System.out.println("数组为空。 - FindMinMax.java:6");
            return;
        }

        int min = arr[0];
        int max = arr[0];

        for(int i=1; i<arr.length; i++){
            if(arr[i] < min){
                min = arr[i];
            }
            else if(arr[i] > max){
                max = arr[i];
            }
        }

        System.out.println("最小值: - FindMinMax.java:22" + min);    
        System.out.println("最大值: - FindMinMax.java:23" + max);
    }

}