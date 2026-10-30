#include <bits/stdc++.h>
#include <stdlib.h>
typedef int BTDataType;
typedef struct BinaryTreeNode{
	BTDataType data;
	struct BinaryTreeNode* left;
	struct BinaryTreeNode* right;
}BTNode;

BTNode* BuyBTNode(BTDataType x){
	//单个结点创建
	BTNode* tmp=(BTNode*)malloc(sizeof(BTNode));
	//判断是否申请成功
	if(tmp==NULL){
		printf("创建失败 请重试\n"); 
	} 
	tmp->data=x;
	tmp->left=tmp->right=NULL;
	return tmp;
} 
// 二叉树前序遍历  根左右 
void BinaryTreePrevOrder(BTNode* root){
	//递归返回条件
    if (root == NULL)
		return;
    //打印根节点
	printf("%d\t", root->data);
    //递归访问左子树
	BinaryTreePrevOrder(root->left);
    //递归访问右子树
	BinaryTreePrevOrder(root->right);
}
// 二叉树中序遍历 左根右 
void BinaryTreeInOrder(BTNode* root){
	//递归返回条件
    if (root == NULL)
		return;
    //中序遍历左子树
	BinaryTreeInOrder(root->left);
    //访问根结点
	printf("%d\t", root->data);
    //中序遍历右子树
	BinaryTreeInOrder(root->right);
}
// 二叉树后序遍历 左右根 
void BinaryTreePostOrder(BTNode* root){
	//递归返回条件
    if (root == NULL)
		return;
    //中序遍历左子树
	BinaryTreeInOrder(root->left);
    //中序遍历右子树
	BinaryTreeInOrder(root->right);
	 //访问根结点
	printf("%d\t", root->data);
}

int leftnum=0,rightnum=0;
int GetDeep(BTNode* root){
	//递归返回条件
	int deep;
	 if(root==NULL) return 0;
	 else{
	 	leftnum=GetDeep(root->left);
	 	rightnum=GetDeep(root->right);
	 	deep=std::max(rightnum,leftnum);
	 	deep++;
	 	return deep;
	 } 
}
int main(){
	BTNode* n1=BuyBTNode(1);
	BTNode* n2=BuyBTNode(2);
	BTNode* n3=BuyBTNode(3);
	BTNode* n4=BuyBTNode(4);
	BTNode* n5=BuyBTNode(5);
	BTNode* n6=BuyBTNode(6);
	
	n1->left=n2;
	n1->right=n3;
	n2->left=n4;
	n2->right=n5;
	n3->right=n6;
	
	printf("前序遍历："); 
	BinaryTreePrevOrder(n1);//先序 
	printf("\n"); 
	printf("中序遍历："); 
	BinaryTreeInOrder(n1);//中序 
	printf("\n"); 
	printf("后序遍历："); 
	BinaryTreePostOrder(n1);//后序 
	printf("\n"); 
	printf("二叉树高：");
	printf("%d", GetDeep(n1));
} 

