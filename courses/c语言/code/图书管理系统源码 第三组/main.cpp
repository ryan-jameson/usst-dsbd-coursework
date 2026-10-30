#include <windows.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
using namespace std;

void printred(){
	HANDLE hout;
	hout=GetStdHandle(STD_OUTPUT_HANDLE);
    SetConsoleTextAttribute(hout,4);
}//红色 

void printgreen(){
	HANDLE hout;
	hout=GetStdHandle(STD_OUTPUT_HANDLE);
    SetConsoleTextAttribute(hout,2);
}//绿色 

void printpurple(){
	HANDLE hout;
	hout=GetStdHandle(STD_OUTPUT_HANDLE);
    SetConsoleTextAttribute(hout,5);
}//紫色

void printn(){
	HANDLE hout;
	hout=GetStdHandle(STD_OUTPUT_HANDLE);
    SetConsoleTextAttribute(hout,15);
}//正常颜色

void printRed(const char* s){
	printred();
	printf("%s",s);
	printn();
} //红色导入 

void printGreen(const char* s){
	printgreen();
	printf("%s",s);
	printn();
} //绿色导入 

void printPurple(const char* s){
	printpurple();
	printf("%s",s);
	printn();
} //紫色导入 

struct book{
	char u[20];
	char bookname[100];
	char print[100];
	float price;
}b;//图书结构体 

struct user{
	int level;
	char username[20];
	char password[20];
}ui;//用户结构体 

typedef struct node{
	book data;
	struct node*next;
}node,*blist; //图书链表

typedef struct unode{
	user data;
	struct unode*next;
}unode,*ulist;//用户链表 

//商品函数 
void addbook(blist &L){
	printf("请输入要放入的书籍\n书名：");
	scanf("%s",&b.bookname);
	printf("出版社：");
	scanf("%s",&b.print);
	printf("价格：");
	scanf("%f",&b.price);//注入图书信息 
		
	blist q=new node;
	strcpy(q->data.bookname,b.bookname);
	strcpy(q->data.print,b.print);
	q->data.price=b.price;
	q->next=L->next;
	L->next=q;//头插法 
}//添加图书 
		
void createbooklist(blist &D){
	D=new node;
	D->next=NULL; 
	FILE* pf=fopen("adminbooks.txt","r");
	while(!feof(pf)){
    	blist p=new node;
        fscanf(pf,"%s\t%s\t%f\n",p->data.bookname,p->data.print,&p->data.price);
        p->next=D->next;
        D->next=p;
	}
	fclose(pf);
} //创建库存链表
		 
void createshoplist(blist &E){
	E=new node;
	E->next=NULL; 
	FILE* ef=fopen("userbooks.txt","r");
	while(!feof(ef)){
    	blist p=new node;
        fscanf(ef,"%s\t%s\t%s\t%f\n",p->data.u,p->data.bookname,p->data.print,&p->data.price);
		p->next=E->next;
        E->next=p;
	}
	fclose(ef);
} //创建购物车链表,全体购物车链表，而后再通过删除分出单独的链表，单独链表操作完成以后接入总链表并保存
		
void singleshoplist(blist &S,char u[]){
	S=new node;
	S->next=NULL;
	blist E;
	createshoplist(E);
	blist p=E->next;
	blist p1=E;
	
	while(p!=NULL){
		if(strcmp(p->data.u,u)==0){
			blist q=new node;
			strcpy(q->data.u,p->data.u);
			strcpy(q->data.bookname,p->data.bookname);
			strcpy(q->data.print,p->data.print);
			q->data.price=p->data.price; 
			q->next=S->next;
			S->next=q; //注入新的链表 
			
			p1->next=p->next ; 
			delete p;
			blist p=p1->next; //删除结点以便操作保存 
		}else{
			p1=p1->next;
			p=p->next;
		}
	}
} //单人的购物车链表 
		
blist find(char name[],blist &L){
	blist q=L->next;
	blist p=L; 
	do{
		if(strcmp(q->data.bookname,name)==0){
			return p; 
			break;
		}	
		p=q; 
		q=q->next;
	}while(q!=NULL);
	return NULL;
}//查找函数，用于删除、查找,输出链表对应的前一个节点 
		
void findbook(blist &L){
	printPurple("请输入要查找的书籍！\n");
	char findname[100]; 
	scanf("%s",&findname);
	if(find(findname,L)!=NULL){
		blist p=find(findname,L)->next;
		printGreen("查找成功!\n");
		printf("图书名称：%s\t出版社：%s\t价格：%.2f\n",p->data.bookname,p->data.print,p->data.price); 
	}else printRed("查找失败，不存在这本书！\n");
} //查找函数，可通用 
		 
void deletebook(blist &L){
	char deletebookname[100];
	printPurple("请输入您想删除的书籍：");
	scanf("%s",&deletebookname);
	blist p=find(deletebookname,L);
	if(p!=NULL){
		blist q=p->next;
		p->next=q->next;
		delete q;
		return printGreen("删除成功！\n");
	}else return printRed("未找到该书本，删除失败！\n") ;
}//删除书籍，可通用 
		
void showadmin(blist &D){
	blist p=D->next;
	while(p!=NULL){
		printf("%s\t%s\t%.2f\n",p->data.bookname,p->data.print,p->data.price);
		p=p->next;
	}
} //显示所有库存书籍，可通用 

void showall(blist &L){
	blist p=L->next;
	while(p!=NULL){
		printf("%s\t%s\t%s\t%.2f\n",p->data.u,p->data.bookname,p->data.print,p->data.price);
		p=p->next;
	}
} //显示所有购物车数据 
		
void saveadmin(blist &L){
	blist p=L->next;
	FILE* pf=fopen("adminbooks.txt","w");
	while(p!=NULL){
		fprintf(pf,"%s\t%s\t%.2f\n",p->data.bookname,p->data.print,p->data.price);
        p=p->next;
	} 
	return printGreen("保存成功"); 
	fclose(pf);
}//保存管理员书籍 ,不通用 
		
void saveclient(char u[],blist &S){
	blist E;
	createshoplist(E);
	singleshoplist(S,u);
	blist q=S->next;//导出个人购物车数据 
			
	while(q!=NULL){
		blist qq=new node;
		strcpy(qq->data.u,q->data.u);
		strcpy(qq->data.bookname,q->data.bookname);
		strcpy(qq->data.print,q->data.print);
		qq->data.price=q->data.price; 
		qq->next=E->next;
		E->next=qq;
		q=q->next;
	}//注入新节点 
			
	blist p=E->next; 
	FILE* ef=fopen("userbooks.txt","w");
	while(p!=NULL){
		fprintf(ef,"%s\t%s\t%s\t%.2f\n",p->data.u,p->data.bookname,p->data.print,p->data.price);
        p=p->next;
	} 
	return printGreen("保存成功"); 
	fclose(ef);
}//保存用户购物车书籍 ,不通用 
		
void pay(blist &L){
	blist D;
	createbooklist(D);
	blist d=D->next;//导入库存链表，查看库存 
	
	blist p=L->next;
	float ap;
	while(p!=NULL){
		if(find(p->data.bookname,D)==NULL){
			blist  pdel=p;
			blist ptem=find(p->data.bookname,L);
			ptem->next=pdel->next;
			delete pdel;
			printRed("库存不足，请重新查看购物车！\n");
			p=p->next;
			continue; //根据库存删除购物车链表 
		}
		ap+=p->data.price;
		p=p->next;
	}
	printf("总价是%.2f元，是否购买？1:购买 2:我再想想\n",ap);//计价
			 
	int option;
	scanf("%d",&option);
	while(1){
		switch(option){
			case 1:{
				while(L->next!=NULL){
					blist qdel=L->next;
					L->next=qdel->next;
					blist dtemp=find(qdel->data.bookname,D);
					blist ddel=dtemp->next;//找到库存链表中删除的结点 
					
					dtemp->next=ddel->next;
					delete ddel;//删除库存结点 
							
					delete qdel;
				}//释放购物车链表 
				return printGreen("购买成功！欢迎下次惠顾！\n");
			}//清空链表操作
			case 2:return;
			default: printRed("Error!Please enter right idx");return;
		}
		Sleep(10);
	}
}//支付函数

void addnewbook(char u[]){
	char bookname[100];
	printPurple("请输入你想添加的书籍书名：");
	scanf("%s",&bookname);
	blist D;
	createbooklist(D);
	if(find(bookname,D)!=NULL){
		blist q=find(bookname,D)->next;
		FILE* ef=fopen("userbooks.txt","a");
		fprintf(ef,"%s\t%s\t%s\t%.2f\n",u,q->data.bookname,q->data.print,q->data.price);
		fclose(ef);
		return printGreen("成功添加\n");
	}else return printRed("添加失败！请重试\n"); 
}//添加新书进入总购物车链表 

//用户函数 
void clientlog(ulist &C){
    C=new unode;
    C->next=NULL;
    FILE* file=fopen("clients.txt","r");
    while(!feof(file)){
    	ulist p=new unode;
        fscanf(file,"%s\t%s\n",p->data.username,p->data.password);
        p->next=C->next;
        C->next=p;
	}
    fclose(file);
}//载入用户链表
		
void adminlog(ulist &A){
	A=new unode;
	A->next=NULL;
    FILE* fi=fopen("admin.txt","r");
    while(!feof(fi)){
    	ulist p=new unode;
        fscanf(fi,"%s\t%s\n",p->data.username,p->data.password);
        p->next=A->next;
        A->next=p;
	}
    fclose(fi);
} //载入管理员链表 
		
void add(char username[],char password[]){
	FILE* file=fopen("clients.txt","a");
	fprintf(file,"\n%s\t%s",username,password);
	fclose(file);
	return printGreen("成功添加\n");
}//注册添加 
		
void show(ulist &L){
	ulist p=L->next;
	while(p!=NULL){
		printf("%s\t%s\n",p->data.username,p->data.password);
		p=p->next;
	} 
}//展示客户列表和管理员列表 ,通用
		
void save(ulist &L){
	ulist p=L->next;
	FILE* fi=fopen("admin.txt","w");
	while(p!=NULL){
		fprintf(fi,"%s\t%s\n",p->data.username,p->data.password);
        p=p->next;
	} 
	fclose(fi);
	return printGreen("保存成功\n"); 
}//保存管理员链表 
		
ulist finduser(char name[],ulist &L){
	ulist q=L->next;
	ulist p=L;
	do{
		if(strcmp(q->data.username,name)==0){
			return p; 
			break;
		}	
		p=q; 
		q=q->next;
	}while(q!=NULL);
	return NULL;
}//查找管理员函数，用于删除、添加防止重复，输出链表对应的前一个节点 
		
void deleteuser(ulist &L){
	char deletename[20]; 
	printf("请输入你要删除的用户账号：");
	scanf("%s",&deletename); 
	ulist q=finduser(deletename,L);
	if(q!=NULL){
		ulist p=q->next;
		q->next=p->next;
		delete p;
		return printGreen("成功删除！\n");
	}else return printRed("未找到该用户，删除失败！\n") ;
}//删除用户，可通用，注销或删除管理员 
		
void addadmin(ulist &L){
	char addname[20];
	printf("请输入你要添加的管理员账号：");
	scanf("%s",&addname);
	ulist C;
	clientlog(C);
	ulist q=finduser(addname,C);
	if(q!=NULL){
		ulist p=q->next;
		ulist pp=new unode;
		strcpy(pp->data.username,p->data.username);
		strcpy(pp->data.password,p->data.password);
		pp->next=L->next;
		L->next=pp;
		return printGreen("成功添加！\n");
	}else return printRed("未找到该用户，添加失败！\n") ;
}//添加管理员，从client列表中的结点匹配后用头插法接入admin列表 

//UI函数 
void _register();
void login();
bool _islogin=false;//已读及登录状态

void UIloginn(){
    Sleep(1); 
    while(!_islogin){
        system("cls");
        printf("------------------Login Menu------------------\n");
        printf("                   1 注册                     \n");
        printf("                   2 登录                     \n");
        printf("                   0 退出                     \n");//第一菜单样式 
        printf("\n输入序号:");
        
        int opt;
        scanf("%d",&opt);
        switch(opt){
            case 0:return;
            case 1:_register();break;
            case 2:login();break;
            default: printRed("请选择正确选项！\n");continue;
        }
        Sleep(1000);
    }
}//第一菜单选择 
        
int checklog(char name[],char password[],ulist &L){
    ulist p=L;
    while(p->next!=NULL){
        p=p->next;
        if(strcmp(p->data.username,name)==0 && strcmp(p->data.password,password)==0){
        	return 1;
        	break;
		}
	} 
	return 0;
} //链表操作 ,查询登录是否正确 

int checkre(char name[],ulist &L){
    ulist p=L;
    while(p->next!=NULL){
        p=p->next;
        if(strcmp(p->data.username,name)==0){
        	return 1;
        	break;
		}
	} 
	return 0;
} //链表操作 ,查询注册用户名是否重复 

void login(){
    int i;//登录次数
	 
    while(i<=2){
        system("cls");
        printf("--------------------Login---------------------\n");
        printf("   UserName:");
        char name[20],password[20];
        scanf("%s",&name);
        printf("   Password:");
        scanf("%s",&password);//输入账号密码 
		
        ulist C;
        ulist A;
        clientlog(C);
        adminlog(A);
        if(checklog(name,password,A)){
            _islogin=true;
            ui.level=1;
            strcpy(ui.username,name);
            Sleep(1000);
    		return printGreen("   Successfully login\n");
        }else{
        	if(checklog(name,password,C)){
            	_islogin=true;
            	strcpy(ui.username,name);
            	ui.level=-1;
            	Sleep(1000);
            	return printGreen("   Successfully login\n");
			}else return printRed("   Incorrect username or password\n");
		}
		i++;//设置三次输入密码限制  
	}
        	
	if(!_islogin){
		Sleep(1000);
        printRed("已超过登录次数限制\n"); 
		return;//登录失败 
	}
}//登录函数，校验密码 
        
void _register(){
    system("cls");
    printf("-------------------Register--------------------\n");
    printf("   UserName:");
    char name[20]="",password[20]="";
    scanf("%s",&name);
    printf("   Password:");
    scanf("%s",&password);//输入账号密码 
    
    ulist A;
	ulist C;
	adminlog(A);
	clientlog(C); 
    if(checkre(name,A) || checkre(name,C)){
        printRed("Error!Account already exists");
        Sleep(1000);
        return;
    }
    add(name,password);
    ui.level=-1; 
    strcpy(ui.username,name);
    Sleep(1000);
    _islogin=true;
    return printGreen("   Successfully register\n");
}//注册函数，写入文件

void UIClint();
void UIAdmin();
void UISwitch(){
    if(ui.level==-1) UIClint();
    if(ui.level==1) UIAdmin();
}//Switch代码，选择管理员界面或者客户界面 
        
void UIstart(){
    UIloginn();
    UISwitch();
}//ui操作 

void UIregulate();
void UIAdmin(){
    blist D;
	createbooklist(D); 
	system("cls");
	printf("------------Admin------------\n");
    printf("          1 添加书籍\n");
    printf("          2 删除书籍\n");
    printf("          3 显示所有书籍\n");
    printf("          4 权限管理\n");
    printf("          5 查找书籍\n");
    printf("          6 保存数据\n");
    printf("          7 用户界面\n");
    printf("          0 退出");
    Sleep(1);
        
    while(1){
        int opt;
        printf("\n输入序号:");
        scanf("%d",&opt);
        switch(opt){
            case 0:return;
            case 1: addbook(D);break;
            case 2: deletebook(D);break;
            case 3: showadmin(D);break;
            case 4: UIregulate();break;
            case 5: findbook(D);break;
            case 6: saveadmin(D);break;
            case 7: UIClint();break;
            default:printRed("Error!Please enter right idx");
        }
    	Sleep(1000);
    }
}//管理员界面 
        
void UIregulate(){
    int choice; 
    ulist A;
    ulist C;
    adminlog(A);
    clientlog(C);
	while(1){
		system("cls");
    	printf("------------------Empowerment------------------\n");
        printf("          1 添加管理员\n");
        printf("          2 删除管理员\n"); 
        printf("          3 保存数据\n");
        printf("          4 删除用户账号\n");
        printf("          0 退出\n");
        printf("------------------Admin------------------\n");
        show(A);
        printf("------------------Client------------------\n");
        show(C);
        printf("输入序号:");
        scanf("%d",&choice);
        switch(choice){
            case 0:return;
            case 1: addadmin(A);break; 
            case 2: deleteuser(A);break;
            case 3: save(A);save(C);break;
            case 4: deleteuser(C);break; 
            default:printRed("Error!Please enter right idx");
		}
		Sleep(1000);
	}
}//权限管理界面

void UIshop();
void UIClint(){
    blist E;
	createshoplist(E); 
	blist D;
	createbooklist(D);
	system("cls");
	printf("------------Clint------------\n");
    printf("          1 商城\n");
    printf("          2 搜索书籍\n");
    printf("          3 加入购物车\n");
    printf("          4 查看购物车\n");
    printf("          0 退出\n");
    Sleep(1);
    
    while(1){
        int opt;
        printf("输入序号:");
        scanf("%d",&opt);
        switch(opt){
            case 0: return;
            case 1: showadmin(D);break;
            case 2: findbook(D);break;
            case 3: addnewbook(ui.username);break;
            case 4: UIshop();break;
            default:printRed("Error!Please enter right idx");
    	}
    }
}//用户界面操作 
        
void UIshop(){
    blist S;
    singleshoplist(S,ui.username);
    while(1){
    	system("cls");
    	int opt;
    	printf("------------Shoplist------------\n");
    	printf("          1 结账\n");
    	printf("          2 删除书籍\n");
    	printf("          3 保存数据\n"); 
   		printf("          0 退出\n");//购物车界面 
   		showall(S);
    	printf("输入序号:");
    	scanf("%d",&opt);
    	
    	switch(opt){
        	case 0: return;
        	case 1: pay(S);break;
        	case 2: deletebook(S);break;
        	case 3: saveclient(ui.username,S);break;
        	default:printRed("Error!Please enter right idx");
		}
    	Sleep(1000);
	}
}//购物车界面操作 

int main(){
    UIstart();
    printf("欢迎下次使用，再见！\n"); 
}
