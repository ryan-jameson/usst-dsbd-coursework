#include <stdio.h>
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
