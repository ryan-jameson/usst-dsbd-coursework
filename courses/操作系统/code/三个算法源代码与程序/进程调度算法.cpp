#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdbool.h>
#include <windows.h>

typedef struct node{
  char name[10];//进程名字 
  int prio;//优先级数 
  int round;//时间片长度 
  int cputime;//服务时间 
  int needtime;//剩余时间 
  int count;//运行次数 
  char state;//状态R运行，W就绪，F结束 
  struct node *next;
}PCB;

PCB *finish,*ready,*run,*r,*f;//完结队列、就绪队列、运行队列、就绪队尾、完结队尾 
int N;

void firstin()//进程块开始运行 
{
  run = ready;
  run->state = 'R';
  ready = ready->next;
}
   
void prt1(char a)//输出头 
{
  if(a=='P'||a == 'p') 
    printf("Name  elapsed time   remaining time   count   priority  state\n");
  else if(a =='r'||a =='R')
    printf("Name  elapsed time   remaining time   count   round   state\n");
}

void prt2(char a ,PCB *q)//输出行 
{
     if(a=='P'||a == 'p')
     printf("%-10s%-15d%-15d%-12d%-10d%c\n",q->name,q->cputime,q->needtime,q->count,q->prio,q->state);
     else if(a == 'r'|| a == 'R')
     printf("%-10s%-15d%-15d%-12d%-10d%c\n",q->name,q->cputime,q->needtime,q->count,q->round,q->state);
}

void prt(char algo)
{
     PCB *p;
     prt1(algo);
     if(run != NULL)prt2(algo,run);//输出Run 
     p = ready;
     while(p != NULL)
     {
         prt2(algo,p);
         p = p->next;
     }//就绪队列 
     p = finish;
     while(p != NULL)
     {
         prt2(algo,p);
         p = p->next;
     }//完成队列 
     p = ready;
     printf("Ready query:");
     while(p != NULL)
     {
         printf("%s",p->name);
         p = p->next;
         if(p!=NULL) printf("、"); 
     }//就绪队列 进程名输出 
     p = finish;
     printf("\nFinished query:");
     while(p != NULL)
     {
         printf("%s",p->name);
         p = p->next;
         if(p!=NULL) printf("、"); 
     }//完成队列 进程名输出 
     printf("\n");
}

void insert1(PCB *q)//按照优先级插入进程控制块 
{
   PCB *p1,*s,*r;
   s = q;
   p1 = ready;
   r = p1;
   while(p1 != NULL){
		if(p1->prio >= s->prio){
         	r = p1;
         	p1 = p1->next;
    	}//r为插入位置的前驱，p1用来跟插入进程控制块比较 
    	else break;//找到位置退出循环 
   }
   if(r!= p1){ 
		r->next = s;
		s->next = p1;
   }else{//如果是队首 
		s->next = p1;
		ready = s;//插入进程在队首 
   }
}

void creat1(char alg)
{
     PCB *p;
     int i,time;
     char na[10];
     ready = NULL;
     finish = NULL;
     run = NULL;
     for(i = 1; i <= N; i++)
     {
       p = (PCB *)malloc(sizeof(PCB));
       printf("输入第%d个进程号:",i);
       scanf("%s",na);
       printf("输入运行时间:");
       scanf("%d",&time);
       strcpy(p->name,na);
       p->cputime = 0;
       p->needtime = time;
       p->count=0;
       p->state = 'W';
       p->prio = 50-time;
       if(ready != NULL) insert1(p);//按优先级降序排列进入就绪队列 
       else{
         p->next = ready;
         ready = p;
        }//就绪队列为空的时候将进程控制块排列进入就绪队列 
     }
     //clrscr();
     printf("   抢占优先级算法输出信息:\n");
     printf("*****************************************\n");
     prt(alg);
}

void creat2(char alg)
{
     PCB *p;
     int i,time,round;
     char na[10];
     ready = NULL;
     finish = NULL;
     run = NULL;
     printf("请输入时间片：");
     scanf("%d",&round);
     
     for(i = 1; i <= N; i++)
     {
       p = (PCB *)malloc(sizeof(PCB));
       printf("输入第%d个进程号:",i);
       scanf("%s",na);
       printf("输入运行时间:");
       scanf("%d",&time);
       strcpy(p->name,na);
       p->cputime = 0;
       p->needtime = time;
       p->state = 'W';
       p->count  = 0;
       p->round  = round;
       p->next = NULL;
       if(i == 1){
       		r = ready = p;
	   }else{
       		r->next = p;
       		r = p;  
	   }/*按顺序插入到ready链表中*/
     }
     //clrscr();
     printf("     时间片轮转算法输出信息:\n");
     printf("*****************************************\n");
}
int flag=-1;//初次完成标记，用于初始化finish队列 
void dynamite(){
	PCB *p;
	p=ready;
	while(p != NULL)
     {
         p->prio++;
         p = p->next;
     }//就绪队列 
} 
void priority(char alg)  //优先数调度算法
{
	 firstin(); 
	 prt(alg);//第一次输出 
     while(run != NULL){
       run->cputime += 1;
       run->needtime -= 1;
       //run->prio -= 3;
       run->count++;
       dynamite();//动态自增优先级 
       if(run->needtime == 0){
       	  flag++;
       	  if(!flag){
       	  	run->next = finish;
			f=finish=run;//第一次完成，初始化finish队列 
		  }else{
			f->next=run;
			f=run;
			f->next=NULL;
		  }//后续完成，连接到队尾 
          run->state = 'F';
          run = NULL;//完成后进入完结队列 
          if(ready != NULL) firstin();
       }else{//还有余量 
       		if((ready != NULL) && (run->prio < ready->prio)){//查看现在运行的进程是否优先级低于就绪队列的进程 
            run->state = 'W';
            insert1(run);//重新插入到继续队列正在运行的进程控制块 
            firstin();}
	   } 
	  Sleep(2000);
      prt(alg);
	}
}

void roundrun(char alg)  //时间片轮转调度算法
{
  
  while(N){
  	Sleep(2000);//延迟输出 
	firstin(); //run每次运行ready的队头 
	prt(alg);//在开始运行前输出 
    run->count++;//每运行一次计数器加1  
    if(run->needtime < run->round)//当剩余时间小于时间片轮转时间时的情况 
    {
        run->cputime += run->needtime;
        run->needtime = 0;
    }else{
        run->cputime += run->round;
        run->needtime -= run->round;  
    }
    run->state = 'W';//变为等待 
    if(run->needtime == 0){//当run结束时放入finish队列里
    	flag++;//计数完成队列数量
		if(flag==0){
			run->next = finish;
			f=finish=run;//第一次完成，初始化finish队列 
		}else{
			f->next=run;
			f=run;
			f->next=NULL;
		}
        run->state = 'F';
        N--;//进程数少1 
    }else{
		r->next=run;//create2产生的队尾 
        r = run;//如果run还有余量，将其赋值到队尾 
        r->next = NULL; //下一个为空 
    }
  }
  run=NULL;
  prt(alg);//最后输出所有结束队列 
}


main()
{
      char algo;
      //clrscr();
      printf("选择算法:P/R(抢占优先级算法/时间片轮转算法)\n");
      scanf("%c",&algo);
      printf("输入进程数:\n");
      scanf("%d",&N);
      if(algo == 'P'||algo == 'p')
      {
        creat1(algo);
        priority(algo);
      }
      else if(algo == 'R'||algo == 'r')
      {
        creat2(algo);
        roundrun(algo);
      }
     system("echo 按任意键退出");
     return 0;
} 
