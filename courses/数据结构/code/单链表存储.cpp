#include <bits/stdc++.h>
#define MAXSIZE 100


typedef struct RecNode{
	int data;
	struct RecNode* next;
}RecNode; 

RecNode* InitLink(){
	RecNode* L;
	L=(RecNode*)malloc(sizeof(RecNode));
	L->next=NULL;//头结点 
	return L;
}//链表初始化 

void CreateRec(RecNode* L,int n){
	RecNode* r=L;
	for(int i=0;i<n;i++){
		RecNode* p;
		p=(RecNode*)malloc(sizeof(RecNode));
		printf("输入表键值\n");
		scanf("%d",&p->data);//输入表键值 
		r->next=p;
		r=p;
		r->next=NULL;//尾插法 
	} 
	RecNode* s=L->next;
	for(int i=0;i<n;i++){
		printf("%d\t",s->data);
		s=s->next;
	} //输出整个原始表查看是否输入完成 
	printf("\n");
}
void InsertSort(RecNode *L,int n){
	RecNode* p = L->next; // 第一个结点 
    RecNode* tmp;
    
	for(int i=0;i<n-1;i++) {
		RecNode* pre = L; // 头结点
        tmp = p->next; // 被排序结点 
        
        if (p->data >tmp->data) { // p的数据大于前一个节点的数据
            // 从头结点开始移动pre
             RecNode* s;
			 s=(RecNode*)malloc(sizeof(RecNode));
			 s->data=tmp->data;//结点键值导出 
			 p->next=tmp->next;
			 free(tmp);//删除结点
			  
            while (pre->next->data< s->data) {
                pre = pre->next;
            }
            // 将tmp插入到pre之后
            s->next = pre->next;
            pre->next = s;
        }
    }
    
}//直接插入排序 

void PrintList(RecNode* L,int n) {
    RecNode* p = L->next; // 跳过头结点
    for(int i=0;i<n;i++){
		printf("%d\t",p->data);
		p=p->next;
	} //输出整个原始表查看是否输入完成 
    printf("\n");
}//打印链表 

void SelectSort(RecNode* L,int n) {
	RecNode* p = L->next; // 第一个数据节点
    int min;
	
    for (int i = 0; i < n - 1; i++) {
        min = p->data; // 假设当前节点是最小值
        RecNode* pre = p->next; // 移动到下一个节点
		
        while (pre != NULL) {
            if (pre->data < min) {
                min = pre->data; // 更新最小值节点
            }
            pre = pre->next;
        }

        if (min= p->data) {
            // 交换L->next和minNode的值
            int temp = min;
            min = p->data;
            p->data = temp;
        }
        p=p->next;
    }
}//简单选择排序 

main(){
	int n;//表长
	printf("输入表长\n");
	scanf("%d",&n);//输入表长
	RecNode* L=InitLink(); 
	CreateRec(L,n);
	printf("直接插入排序\n");
	InsertSort(L,n); 
	PrintList(L,n); 
	printf("简单选择排序\n");
	SelectSort(L,n);
	PrintList(L,n); 
}
