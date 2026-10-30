#include <bits/stdc++.h>
#define MAXSIZE 100
int r[MAXSIZE]={0};//创建有序表 

typedef struct BSTNode{
	int key;//关键词 
	struct BSTNode *lchild,*rchild;
}BSTNode; 

BSTNode* InsertBSTNode(BSTNode* bt,int k){
	if(bt==NULL){
		bt=(BSTNode*)malloc(sizeof(BSTNode));
		bt->key=k;
		bt->lchild=bt->rchild=NULL;
	}//如果结点是空的，直接创建一个新节点 
	else if(k<bt->key) bt->lchild=InsertBSTNode(bt->lchild,k); //小于键值，往左构建 
	else bt->rchild=InsertBSTNode(bt->rchild,k); //大于键值，往右构建 
	return bt; //返回结点 
}//创建结点函数 

BSTNode* CreateBSTtree(int n){
	BSTNode* bt=NULL;//起始空节点 
	int key;//关键词 
	
	for(int i=0;i<n;i++){
		printf("输入键值\n");
		scanf("%d",&key);//输入关键词 
		bt=InsertBSTNode(bt,key);//插入并创建结点 
	}
	return bt;//返回根结点 
}//创建排序树

int SearchBSTtree(BSTNode* bt,int k){
	while(bt!=NULL){
		if(k==bt->key) return 1;
		else if(k<bt->key) bt=bt->lchild;
		else bt=bt->rchild;
	}
	return 0;
}//在二叉排序树中查找相关键值 
 
int j=0;//有序表的存储位置 
void PrintBSTtree(BSTNode* bt){
	if (bt == NULL)
		return;
    //中序遍历左子树
	PrintBSTtree(bt->lchild);
    //访问根结点
	printf("%d\t", bt->key);
	r[j]=bt->key;
	j++;//将树节点关键词输入到有序表当中，每输入一个就将存储位置往后移 
    //中序遍历右子树
	PrintBSTtree(bt->rchild);
} //中序遍历输出排序树，如果是递增序列代表构建成功

int FIND(int n,int k){
	int i,low=0,high=n-1,mid,find=0;
	while(low<=high && find==0){
		mid=(low+high)/2;
		if(k==r[mid]){
			find=1;
			i=mid;
		}else if(k<r[mid]) high=mid-1;
		else low=mid+1;
	}
	if(find) return i+1;
	else return -1;
} //有序表的二分查找 

main(){
	int n,k;//键值数量 查找的键值 
	printf("输入键值数量\n");
	scanf("%d",&n);
	BSTNode* bt;
	bt=CreateBSTtree(n);
	PrintBSTtree(bt); 
	printf("\n输入键值\n");
	scanf("%d",&k);
	if(SearchBSTtree(bt,k)) printf("查找成功！\n");
	else printf("查找失败\n");
	if(FIND(n,k)!=-1) printf("查找成功！位于第%d位\n",FIND(n,k));
	else printf("查找失败\n");
} 
