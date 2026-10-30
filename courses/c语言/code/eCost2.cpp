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
	float e,c;
	float estd[]={3,0,0.6,3000,0.1,5000,0.2};
	scanf("%f",&e);
	c=ecost(e,estd);
	printf("%.2f度时年电费：%.2f元\n",e,c);
	return 0;
	
} 
