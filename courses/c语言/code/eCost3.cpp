#include <stdio.h>
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
