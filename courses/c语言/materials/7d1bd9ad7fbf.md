# 作业1

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

一、1.① (choice<0)||(choice>4)
②(choice<=4)&&(choice>0)
③choice
④break
①i+1
②b[i]<=x
③b[j+1]=b[j]
④sort(a[],10)
⑤insert(a[],11,y)
①float
②rubbish a[]
③a[i].kind[]
④a[j].quantity
二、1.#include <stdio.h>
using namespace std;
float ecost(float e){
if(e<0) return 0.0;
else{
if(e<=3000) return e*0.6;
else{
if(e<=5000) return e*0.6+(e-3000)*0.1;
else return e*0.6+(e-3000)*0.1+(e-5000)*0.2;
}
}
}

int main(){
float e,c,c3;
FILE* file=fopen("eCostdata.txt","w+");
fprintf(file,"(1)");
scanf("%f",&e);
c=ecost(e);
if(e>5000){
c3=(e-5000)*0.9;
}else c3=0;
fprintf(file,"%.0f度时年电费：%.0f元\n",e,c);
fprintf(file,"(2) 第三档电价：%.3f元\n",c3);
fclose(file);
return 0;

} 
2.#include <stdio.h>
using namespace std;

float ecost(float e,float estd[]){
float c;
int stage,price;
for(int i=0;i<estd[0];i+=1){
stage=2*i+1;
price=2*i+2;
if(e<estd[stage]) break;
else c+=(e-estd[stage])*estd[price];
}
return c;
}

int main(){
float e,c;
float estd[]={3,0,0.6,3000,0.1,5000,0.2};
scanf("%f",&e);
c=ecost(e,estd);
printf("%.2f度时年电费：%.2f元\n",e,c);
return 0;

} 
3.#include <stdio.h>
using namespace std;

float ecost(float e,float estd[]){
float c;
int stage,price;
for(int i=0;i<estd[0];i+=1){
stage=2*i+1;
price=2*i+2;
if(e<estd[stage]) break;
else c+=(e-estd[stage])*estd[price];
}
return c;
}

int main(){
float e,c,estd[100];
printf("请输入电费档位：");
scanf("%f",&estd[0]);
for(int i=0;i<estd[0];i++){
printf("请输入第%d档电量:",i+1);
scanf("%f",&estd[2*i+1]);
printf("请输入第%d档电费：",i+1);
scanf("%f",&estd[2*i+2]);
}
printf("请输入用电量：");
scanf("%f",&e);
c=ecost(e,estd);
printf("%.2f度时年电费：%.2f元\n",e,c);
return 0;

} 
4.#include<stdio.h>
using namespace std;

float ecost(float e,float estd[]){
float c;
int stage,price;
for(int i=0;i<estd[0];i+=1){
stage=2*i+1;
price=2*i+2;
if(e<estd[stage]) break;
else c+=(e-estd[stage])*estd[price];
}
return c;
}//电价收费函数，输入电费标准及电量 

int readstd(float estd[]){
FILE *file = fopen("eCost4Std.txt", "r");
    if (file != NULL) {
    fscanf(file,"%f\t",&estd[0]);
    for(int i=0;i<estd[0];i++){
    fscanf(file,"%f\t%f\t",&estd[2*i+1],&estd[2*i+2]);
}//根据档位数量逐个输入到数组中 
        return 1;
    } else {
        printf("电费标准文件打开失败：eCost4Std.txt\n");
        return -1;
    }
    fclose(file);
}//电费标准输入函数 

int readind(float indm[]){
FILE *file = fopen("eCost4Ind.txt", "r");
    if (file != NULL) {
    int i=0;
    while(1){
    fscanf(file,"%f\t",&indm[i]);
    if(indm[i]==-1) break;
    i++;
}
return 1;//逐个输入indm 
    } else {
        printf("电表读数文件打开失败：eCost4Ind.txt\n");
        return -1;
    }
    fclose(file);
}//电表数值输入函数 

void prtcostm(float indm[], float estd[]){
float c[60];
if(readstd(estd)&&readind(indm)){
printf("期,电表读数,年用电量,当年费用,当期费用\n");
printf("%2d,%8.1f,%8.1f\n",0,indm[0],0.0);
for(int i=1;indm[i]!=-1;i++){
float e=indm[i]-indm[0];
c[i]=ecost(e,estd);
printf("%2d,%8.1f,%8.1f,%8.2f,%8.2f\n",i,indm[i],e,c[i],c[i]-c[i-1]);
} 
}
}//输出电表总读数 
int main(void){
float estd[23];
float indm[60];
if(readstd(estd)&&readind(indm)) prtcostm(indm, estd);
return 0;
}
二、1.#include<stdio.h>
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
2.#include<stdio.h>
#include<string.h>

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

printf("学号：[已匿名];
scanf("%d",&stu[n].number);
printf("姓名：[已匿名];
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
printf("请输入要查找的学号：[已匿名];
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
