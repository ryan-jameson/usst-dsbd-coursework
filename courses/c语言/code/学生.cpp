#include<stdio.h>
#include<string.h>
#include<iostream>

struct student{// 定义学生信息类型
	int  number;  // 学号
	char name[7];// 姓名
	float score[3];// 数学、物理、C语言成绩
}stu[100];

int n;//记录学生人数

void exit(){
	printf("欢迎下次再次使用，Byebye!\n");
}//退出语句 

void menu(){
	printf("____________________________________\n");
	printf("1:输入学生信息\n");
	printf("2:列出学生信息\n");
	printf("3:按学号查找学生信息\n");
	printf("0:退出\n");
	printf("____________________________________\n");
} //主菜单函数

int add(student stu[],int n){
	
	printf("学号：");
	scanf("%d",&stu[n].number);
	printf("姓名：");
	scanf("%s",&stu[n].name);
	printf("数学 物理 c语言：");
	scanf("%f %f %f",&stu[n].score[0],&stu[n].score[1],&stu[n].score[2]);//输入信息 
	
	for(int i=1;i<n;i++){
		if(stu[i].number==stu[n].number){
			stu[n]=stu[0];
			return 0;
			break;
		}
	}//查看是否重复输入 
	
	return 1;
}//添加学生信息 

int find(int number){
	int i;
	for(i=1;i<=n;i++){
		if(stu[i].number==number){
			printf("____________________________________\n");
			printf("学号\t姓名\t数学\t物理\tC语言\n");
			printf("%4d\t%4s\t%4.1f\t%4.1f\t%5.1f\n",stu[i].number,stu[i].name,stu[i].score[0],stu[i].score[1],stu[i].score[2]);
			printf("____________________________________\n");
			return 1;
			break;
		}
	}
	return 0;
}//查找功能 

void list(student stu[],int n){
	printf("____________________________________\n");
	printf("学号\t姓名\t数学\t物理\tC语言\n");
	for(int i=1;i<=n;i++){
		printf("%d\t%s\t%.1f\t%.1f\t%.1f\n",stu[i].number,stu[i].name,stu[i].score[0],stu[i].score[1],stu[i].score[2]);
	}
	printf("____________________________________\n");
}//输出列表 

main(){ 
	menu();//先输出主菜单 
	int t,i,number; 
	while(1){
		printf("input选项（0-3）："); 
		scanf("%d",&t);
		if((t<=4)&&(t>0)){
			switch(t){
				case 1:{
					n++;
					if(!add(stu,n)){
						printf("重复输入，请重试！\n");
						n--;
					}
					continue;
				}//add函数调用，增加n，重复输入就减少n 
				
				case 2:list(stu,n);continue;
				
				case 3:{
					printf("请输入要查找的学号：");
					scanf("%d",&number);
					if(!find(number)) printf("未找到，请重试！\n");
					continue;
				}
			}	
		}else {
			exit();
			break;
		}
	} 
}
