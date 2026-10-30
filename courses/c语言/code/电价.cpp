#include<stdio.h>
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
