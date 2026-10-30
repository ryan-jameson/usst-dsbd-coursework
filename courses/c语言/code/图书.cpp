#include <stdio.h>
#include <stdlib.h>

int n,ln;//记录图书数量
struct book{
    long num;
    char name[100];
    char print[100];
    float p;
}b[1000],lb[1000];//图书信息数组，输入到data中

typedef struct node{
    book data;
    struct node*next;
}node,*linklist;//定义单链表

int chushi(linklist &L){
    L=(linklist)malloc(sizeof(node));
    L->next=NULL;
    return 1;//检查是否可创建链表
}

int check(long num){
    for(int j=0;j<n;j++){
            if(b[j].num==num){
                printf("以重复输入，请重试");
                return 0;
                break;
            }
        }
    return 1;
}//检查是否重复输入

void type(){
    printf("请键入图书信息，按0表示结束\n");
    while(1){
        printf("图书号：");
        scanf("%ld",&b[n].num);
        if(b[n].num==0) break;

        if(check(b[n].num)){
            printf("图书名称：");
            scanf("%s",&b[n].name);
            printf("出版社：");
            scanf("%s",&b[n].print);
            printf("价格：");
            scanf("%f",&b[n].p);

            if(b[n].p<10){
                lb[ln]=b[n];
                ln++;
            }//键入低价图书数组

            n++;
        }else{
            b[n].num=0;
            continue;
        }//键入进入结构体数组
    }
    FILE* file=fopen("books.txt","w+");
    FILE* pf=fopen("offbooks.txt","w+");
    for(int i=0;i<n;i++){
        fprintf(file,"%ld\t%s\t%s\t%.2f\n",b[i].num,b[i].name,b[i].print,b[i].p);
    }
    for(int i=0;i<ln;i++){
        fprintf(pf,"%ld\t%s\t%s\t%.2f\n",b[i].num,b[i].name,b[i].print,b[i].p);
    }
    fclose(file);
    fclose(pf);
}//写入文件操作

void create(linklist &L,int n){
    L=new node;
    L->next=NULL;
    FILE* file=fopen("books.txt","r");
    for(int i=0;i<n;i++){
    	linklist p=new node;
        fscanf(file,"%ld\t%s\t%s\t%f\n",&p->data.num,&p->data.name,&p->data.print,&p->data.p);
        p->next=L->next;
        L->next=p;
    }
    fclose(file);
}//文件读取链表操作

void insert(linklist &L,book b){
    if(check(b.num)){
        FILE* file=fopen("books.txt","a");
        fprintf(file,"%ld\t%s\t%s\t%.2f\n",b.num,b.name,b.print,b.p);
        fclose(file);
        
		linklist p=new node;
        p->data=b;
        p->next=L->next;
        L->next=p;
        n++;
        if(b.p<10){
            lb[ln]=b;
            ln++;
         }//键入低价图书数组
         
    }
}//插入操作，写入文件同时写入链表

int select(linklist &L,char s[]){
    linklist p=L->next;
    for(int j=0;j<n;j++){
        if(p->data.name==s || p->data.print==s){
            return 1;
            break;
        }
        p=p->next;
    }
    return 0;
}//查找操作

main(){
    linklist L;
    book b;
    char s[100];
    type();
    if(chushi(L)){
    	create(L,n);
    	printf("请输入要插入的图书信息\n图书号：");
    	scanf("%ld",&b.num);
    	printf("图书名称：");
    	scanf("%s",&b.name);
    	printf("出版社：");
    	scanf("%s",&b.print);
    	printf("价格：");
    	scanf("%f",&b.p);
    	insert(L,b);
	
    	printf("请输入要查找的书面或出版社:");
    	scanf("%s",&s);
    	if(select(L,s)) printf("查找成功！\n");
        else printf("查找失败");
	}

}
