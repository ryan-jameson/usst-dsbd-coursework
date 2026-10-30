#include <bits/stdc++.h>

#define MAXSIZE 100
typedef struct{
	char data[MAXSIZE];
	int length;
}SqString;

void InitSqString(SqString *s){
	char x;
	while(s->length<=MAXSIZE){
		scanf("%c",&x);
		if(x!='\n'){
			s->data[s->length]=x;
			s->length++;
			continue;
		}
		else break;//输入直到换行符，否则一直循环 
	}
}

int BF(SqString s,SqString t){
	int lens=s.length;
	int lent=t.length;
	int i=0;
	int j=0;
	for (; i < lens; i++) {
    	for (j=0; j < lent; j++) {
            if (s.data[i + j] != t.data[j]) break;//如果有一位不符合，跳出循环 
        }
        if(j==lent) return 1;//完全符合，则j会多进一位，与lent相等 
	}
	return -1;
}//BF算法

int* Getnext(SqString t) {
	static int next[MAXSIZE]={0};//初始化 
	int lent=t.length;
	int k=0;
	for(int i=0;i<=lent;i++){
		if(i==0) next[i]=-1;
		else{
			if(i==1) next[i]=0;
			else{
				k=next[i-1];
				while(k>=0){
					if(t.data[k]==t.data[i-1]) {next[i]=k+1;break;}
					else k--;
				}
			}
		}
		k=0;//清空k的值 
	}
	return next; //输出next整个数组 
}

int KMP(SqString s,SqString t){
	int *next;
	next=Getnext(t);
	int lens=s.length;
	int lent=t.length;
	int i=0;
	int j=0;

	while(i<lens){
		if(s.data[i]==t.data[j]){
			i++;
			j++;
			if(j==lent) return 1;
		}else{
			if(next[j]==-1) i++;
			else j=next[j];
		}
	}
	return -1;
} 

main(){
	SqString s,t;
	printf("输入模板串\n");
	InitSqString(&t);
	printf("输入主串\n");
	InitSqString(&s);

	if(BF(s,t)!=-1) printf("匹配成功！\n");
	else printf("匹配失败！\n");
	
	if(KMP(s,t)!=-1)  printf("匹配成功！\n");
	else printf("匹配失败！\n");
}
