#include <bits/stdc++.h>
void exit(){
	printf("程序结束\n");
}
#define  MAXSIZE 100     
typedef  struct {
    int *elem;
    int length;
} SqList;  // 顺序表

SqList InitList(){
	SqList L; 
	L.elem=new int[MAXSIZE];
	if (!L.elem) exit();//未分配成功 
	L.length=0;
	return L;
} 

void Createlist(SqList &L){
	int n;//输入元素数量
	printf("请输入元素数量：");
	scanf("%d",&n); 
	 
	if(n>MAXSIZE) exit();
	else{
		for(int i=0;i<n;i++){
			printf("请输入第%d位元素:",i+1);
			scanf("%d",&L.elem[i]); 
			L.length++;
		}
		printf("创建成功\n"); 
	}
}//创建顺序表 

void ListInsert(SqList &L){
	int n;//插入位数
	int e;//插入元素
	printf("请输入插入位数：");
	scanf("%d",&n);
	
	printf("请输入插入元素：");
	scanf("%d",&e) ;
	
	if(n>L.length) exit();
	else{
		for(int i=L.length-1;i>=n-1;i--){
			L.elem[i+1]=L.elem[i];
		} 
		L.elem[n-1]=e;
		L.length++;
		printf("插入成功\n");
	}
}

int FindElem(SqList &L,int e){
	for(int i=0;i<L.length;i++){
		if(L.elem[i]==e) return i;
	}
	return -1;
}//查找函数，用于删除或者查找,输出元素所在位数，如果找不到输出-1 
 
void ListDelete(SqList &L){
	int e;//删除元素 
	printf("请输入删除元素：");
	scanf("%d",&e) ;
	
	int i;
	i=FindElem(L,e);//输出元素所在位数
	 
	if(i!=-1){
		for(int j=i;j<L.length;j++){
			L.elem[j]=L.elem[j+1];
		}
		L.length--;
	}else exit();
}//删除顺序表程序 

void Search(SqList &L){
	int e;//查找元素 
	printf("请输入查找元素：");
	scanf("%d",&e) ;
	
	int i;
	i=FindElem(L,e);//输出元素所在位数
	 
	if(i!=-1) printf("查找成功！位于第%d位\n",i+1); 
	else printf("查找失败，元素不存在！\n");
}//查找函数，输出元素是否存在
 
void printList(SqList &L){
	for(int i=0;i<L.length;i++){
		printf("%d\n",L.elem[i]);
	}
}//顺序表输出

 
typedef struct LNode{
	int data;
	struct LNode* next;
}LNode;//单链表

LNode* InitLink(){
	LNode* L;
	L=(LNode*)malloc(sizeof(LNode));
	L->next=NULL;//头结点 
	return L;
}//链表初始化 

void CreateLinkList(LNode* L){
	int n;//输入元素数量
	printf("请输入元素数量：");
	scanf("%d",&n); 
	
	for(int i=n;i>0;i--){
		LNode* p;
		p=(LNode*)malloc(sizeof(LNode));
		printf("请输入第%d位元素:",i);
		scanf("%d",&p->data); 
		p->next=L->next;
		L->next=p;//插入表头 
	}
}//单链表创建

void LinkListInsert(LNode* L){
	LNode* p;
	p=(LNode*)malloc(sizeof(LNode));
	
	int e;//插入元素	
	printf("请输入插入元素：");
	scanf("%d",&e) ;
	
	p->data=e;
	p->next=L->next;
	L->next=p;//头插法
}//单链表插入

LNode* Find(LNode* L,int e){
	LNode* p=L;
	LNode* f=p->next;
	while(f!=NULL){
		if(f->data==e) return p;
		p=p->next;
		f=p->next;
	}
	return NULL;
}//查找函数，用于删除或者查找,输出元素所在前一位单元，如果找不到输出NULL

void LinkDelete(LNode* L){
	int e;//删除元素 
	printf("请输入删除元素：");
	scanf("%d",&e) ;
	
	LNode* p=Find(L,e);
	LNode* d;
	if(p!=NULL){
		d=p->next;
		p->next=d->next;
		free(d);
		printf("删除成功！\n");
	}else printf("元素未找到！删除失败\n");
} 

void SearchLink(LNode* L){
	int e;//查找元素 
	printf("请输入查找元素：");
	scanf("%d",&e) ;
	
	LNode* p=Find(L,e);//输出元素所在前一个单元 
	 
	if(p!=NULL){
		printf("查找成功！\n");
	}else printf("元素未找到！\n");
}//查找函数，输出元素是否存在
 
void printLink(LNode* L){
	LNode* p;
	p=L->next;
	while(p!=NULL){
		printf("%d\t",p->data);
		p=p->next; 
	}
}//顺序表输出

main(){
	SqList L1=InitList();
	printf("初始化顺序表成功！\n");
	Createlist(L1);
	ListInsert(L1);
	ListDelete(L1);
	Search(L1);
	printList(L1);
	
	LNode* L2=InitLink();
	printf("初始化单链表成功！\n");
	CreateLinkList(L2);
	LinkListInsert(L2);
	LinkDelete(L2);
	SearchLink(L2);
	printLink(L2);
} 
