#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#define MAX_PROCESS 10
#define MAX_RESOURCE 10

// 全局数据结构
int m, n; // 资源类型数、进程数
int total[MAX_RESOURCE]; // 系统资源总量
int available[MAX_RESOURCE]; // 可用资源
int max[MAX_PROCESS][MAX_RESOURCE]; // 最大需求矩阵
int allocation[MAX_PROCESS][MAX_RESOURCE]; // 已分配矩阵
int need[MAX_PROCESS][MAX_RESOURCE]; // 需求矩阵
char process_names[MAX_PROCESS][3]; // 进程名称数组，前面为进程的数量，后面为进程名称字符的最大值 

// 安全序列检查函数，检查完再输出状态 
bool security_check(int work[]) {
    bool finish[MAX_PROCESS] = {false};//进程检查状态 
    int work_copy[MAX_RESOURCE];
    memcpy(work_copy, work, m * sizeof(int));//将work矩阵映射到work_copy ，work_copy的作用是不打乱work数组初始化状态 ，m*sizeof(int)为需要复制的字节数，m个资源 

    for(int count = 0; count < n; ++count) {
        bool found = false;
        for(int i = 0; i < n; ++i) {
            if(finish[i]) continue;//如果该进程已经被检查过则进入下一个循环 

            // 检查需求是否小于等于当前可用资源
            bool can_allocate = true;
            for(int j = 0; j < m; ++j) {
                if(need[i][j] > work_copy[j]) {
                    can_allocate = false;
                    break;
                }//如果进程需求数组对应位置不能被满足，则进入下一个大循环 
            }

            if(can_allocate) {
                // 分配资源给进程
                for(int j = 0; j < m; ++j){
                	work_copy[j] += allocation[i][j];
				}
                finish[i] = true;//该进程已经被检查过 
                found = true;//第count轮已经找到适合的进程 
                break;
            }
        }
        if(!found) return false;//第count轮没有找到合适进程，检查不通过！！！修改 
    }
    return true;
}

//打印安全检查状况函数，只有在安全检查通过的时候才调用 
void prints(int work[]){
	bool finish[MAX_PROCESS] = {false};//进程检查状态 
	printf("%5s Work\tNeed\tAllocation  Work+Allocation Finish\n"," ");
	int work_copy[MAX_RESOURCE];
    memcpy(work_copy, work, m * sizeof(int));
    for(int count = 0; count < n; ++count) {
        for(int i = 0; i < n; ++i) {
            if(finish[i]) continue;//如果该进程已经被检查过则进入下一个循环 

            // 检查需求是否小于等于当前可用资源
            bool can_allocate = true;
            for(int j = 0; j < m; ++j) {
                if(need[i][j] > work_copy[j]) {
                    can_allocate = false;
                    break;
                }//如果进程需求数组对应位置不能被满足，则进入下一个大循环 
            }

            if(can_allocate) {
                // 打印分配过程
                printf("%s ", process_names[i]);
                printf("%2d %2d %2d  ", work_copy[0], work_copy[1], work_copy[2]);
                printf("%2d %2d %2d  ", need[i][0], need[i][1], need[i][2]);
                printf("%2d %2d %2d  ", allocation[i][0], allocation[i][1], allocation[i][2]);

                // 分配资源给进程
                for(int j = 0; j < m; ++j){
                	work_copy[j] += allocation[i][j];
				}

                printf("   %2d %2d %2d\t      T\n", work_copy[0], work_copy[1], work_copy[2]);//work+allocation, 状态 
                finish[i] = true;//该进程已经被检查过 
                break;
            }
        }
    }
} 

// 处理资源请求函数
void handle_request() {
    char name[3];
    int request[MAX_RESOURCE];
    printf("Please input the customer's name and request:\n");
    scanf("%s", name);
    for(int i = 0; i < m; ++i) scanf("%d", &request[i]);//输入请求数组 

    // 查找进程索引
    int pid = -1;
    for(int i = 0; i < n; ++i){
    	if(strcmp(process_names[i], name) == 0){ 
			pid = i; 
			break; 
		}
	}//逐个查询进程名是否有效 
    if(pid == -1) {
        printf("Invalid process name!\n");
        return;
    }//最后标记检查，没找到则输出无效 

    // 检查请求合法性
    for(int j = 0; j < m; ++j) {
        if(request[j] > need[pid][j]) {
            printf("Request exceeds declared maximum!\n");
            return;
        }
        if(request[j] > available[j]) {
            printf("RESOURCE INSUFFICIENT!!!\n");
            printf("CUSTOMER %s CAN NOT OBTAIN RESOURCES IMMEDIATELY.\n", name);
            return;
        }
    }

    // 尝试分配资源
    int old_available[MAX_RESOURCE], old_allocation[MAX_RESOURCE], old_need[MAX_RESOURCE];
    memcpy(old_available, available, sizeof(available));
    memcpy(old_allocation, allocation[pid], sizeof(allocation[pid]));
    memcpy(old_need, need[pid], sizeof(need[pid]));//将以上资源复制到旧资源数组，准备更新资源 

    for(int j = 0; j < m; ++j) {
        available[j] -= request[j];
        allocation[pid][j] += request[j];
        need[pid][j] -= request[j];
    }

    // 执行安全性检查
    if(security_check(available)) {
    	prints(available);//打印安全检查状况，没通过就不打印 
        printf("\nSYSTEM SECURITY!!!\n");
        printf("CUSTOMER %s CAN GET RESOURCES IMMEDIATELY.\n", name);
    } else {
        // 回滚分配
        memcpy(available, old_available, sizeof(available));
        memcpy(allocation[pid], old_allocation, sizeof(allocation[pid]));
        memcpy(need[pid], old_need, sizeof(need[pid]));//不安全，则不能分配，原来的不生效，让资源回滚 
        printf("\nSYSTEM INSECURITY!!!\n");
        printf("CUSTOMER %s CAN NOT OBTAIN RESOURCES IMMEDIATELY.\n", name);
    }
}

int main() {
    // 输入系统基本信息
    printf("Input the type of resource and number of customer:\n");
    scanf("%d%d", &m, &n);
    
    printf("Input the total amount of each resource:\n");
    for(int i = 0; i < m; ++i) 
        scanf("%d", &total[i]);

    // 输入进程信息
    printf("Input the amount of resource (maximum, allocated) of each customer:\n");
    for(int i = 0; i < n; ++i) {
        scanf("%s", process_names[i]);
        for(int j = 0; j < m; ++j)
            scanf("%d%*c", &max[i][j]); // 跳过逗号
        for(int j = 0; j < m; ++j)
            scanf("%d%*c", &allocation[i][j]);
    }

    // 计算需求矩阵和可用资源
    for(int i = 0; i < n; ++i)
        for(int j = 0; j < m; ++j)
            need[i][j] = max[i][j] - allocation[i][j];

    // 初始化可用资源
    for(int j = 0; j < m; ++j) {
        int sum = 0;
        for(int i = 0; i < n; ++i)
            sum += allocation[i][j];
        available[j] = total[j] - sum;
    }

    // 主菜单
    while(true) {
        printf("\n1、judge the system security\n");
        printf("2、judge the request security\n");
        printf("3、quit\n");
        
        int choice;
        scanf("%d", &choice);
        
        if(choice == 1) {
            if(security_check(available)){
            	prints(available); 
                printf("\nSYSTEM SECURITY!!!\n");
			}
            else printf("\nSYSTEM INSECURITY!!!\n");
        } 
        else if(choice == 2) {
            handle_request();
        }
        else if(choice == 3) {
            break;
        }
    }

    return 0;
}
