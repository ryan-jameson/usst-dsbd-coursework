#include <stdio.h>
using namespace std;

int main(){
	FILE *file=fopen("test.txt","r+");
	char s[100] ;
	if(file!=NULL){
		fputs("我会变得更加优秀\n",file); 
		fclose(file);
		FILE *file=fopen("test.txt","r+");
		fgets(s,100,file);
		fclose(file);
	}else printf("打开文件失败：test.txt\n");
	
	printf("%s",s);
	return 0;
} 
