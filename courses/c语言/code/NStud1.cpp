#include<stdio.h> 
void exit(){
	printf("欢迎下次再次使用，Byebye!\n");
}
main(){ 
	int t,x;
	printf("____________________________________\n");
	printf("1:输入学生信息\n");
	printf("2:列出学生信息\n");
	printf("3:按学号查找学生信息\n");
	printf("0:退出\n");
	printf("____________________________________\n");
	while(1){
		printf("input选项（0-3）："); 
		scanf("%d",&t);
		if((t<=4)&&(t>0)){
			switch(t){
				case 1:printf("调用自定义函数add");continue;
				case 2:printf("调用自定义函数list");continue;
				case 3:printf("调用自定义函数find");continue;
			}	
		}else {
			exit();
			break;
		}
	} 
	return 0;
}
