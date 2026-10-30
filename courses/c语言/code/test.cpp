#include <string.h>
#include <stdlib.h>
#include <stdio.h>
using namespace std;
main(){
	char str1[]="pple";
	char str2[]="apple";
	strcpy(str2,str1);
	if(strcmp(str1,str2)==0) printf("good");
	else{
		printf("%s",str1);
		printf("bad");
	}
}

