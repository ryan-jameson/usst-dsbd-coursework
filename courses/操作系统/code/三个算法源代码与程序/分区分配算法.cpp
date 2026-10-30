#include <stdio.h>
#include<string.h>
#include<stdlib.h>
#include<math.h>
typedef struct MemoryBlock {
    int start;       // 起始地址
    int end;         // 结束地址
    int size;        // 分区大小
    int is_free;     // 是否空闲（1=空闲，0=占用）
    struct MemoryBlock* next;  // 链表指针
} MemoryBlock;

// 全局变量：空闲队列头指针
MemoryBlock* free_list = NULL;

void initialize_memory() {//初始化空闲队列 
    free_list = (MemoryBlock*)malloc(sizeof(MemoryBlock));
    free_list->start = 0;
    free_list->end = 32766;
    free_list->size = 32767;
    free_list->is_free = 1;
    free_list->next = NULL;
}

MemoryBlock* first_fit(int request_size) {//首次适应算法 
    MemoryBlock* current = free_list;
    while (current != NULL) {
        if (current->is_free && current->size >= request_size) {// 找到第一个足够大的空闲块
            return current;  
        }
        current = current->next;
    }
    return NULL;  // 没有足够空间
}

MemoryBlock* best_fit(int request_size) {//最佳适应算法 
    MemoryBlock* current = free_list;
    MemoryBlock* best = NULL;
    int min_diff = INT_MAX;

    while (current != NULL) {
        if (current->is_free && current->size >= request_size) {//找到足够大的空闲块 
            int diff = current->size - request_size;//检查可能产生的碎片大小，尽量碎片最小 
            if (diff < min_diff) {//如果小于最小碎片大小量，那就更新最佳块 
                min_diff = diff;
                best = current; 
            }
        }
        current = current->next;//遍历产生最佳块 
    }
    return best;
}

void allocate_memory(MemoryBlock* block, int request_size) {// 
    int remaining_size = block->size - request_size;
    if (remaining_size > 0) {
        MemoryBlock* busy_block = (MemoryBlock*)malloc(sizeof(MemoryBlock));//创建新的内存块 
        busy_block->end = block->end;//将占用块分割出新的内存块 
        busy_block->start = block->start+remaining_size;//新的块设置在头部
        busy_block->size = request_size;
        busy_block->is_free = 0;
        busy_block->next = block->next;
        // 更新原始块的信息
        block->end=busy_block->start-1; 
        block->size = remaining_size;
        block->is_free=1;//将原始块被占用的信息填补完整 
        block->next=busy_block; 
    }
}

void merge_adjacent_blocks() { //合并空闲块并清除其中为0的块 
    MemoryBlock* h = free_list;
    MemoryBlock* check = h->next;
    while(check!=NULL){
    	if(check->size==0){
    		h->next=check->next;
			free(check); 
		}
		h=h->next;//h为check的前驱结点 
		check=h->next;
	} 
	MemoryBlock* current = free_list;
    while (current != NULL && current->next != NULL) {
    	MemoryBlock* next_block = current->next;//创建新的内存块合并
        if (current->is_free && next_block->is_free) {// 合并 current 和 current->next
            current->end = next_block->end;
            current->size += next_block->size;
            current->next = next_block->next;
            
            free(next_block);//释放原有内存块 
        } else {
            current = current->next;
        }
    }
}

void free_memory(int start_addr, int size) { // 遍历找到需要回收的块（标记为占用）
    MemoryBlock* current = free_list;
    int flag=0;//寻址标记 
    while (current != NULL) {
        if (start_addr >=current->start&& !current->is_free &&start_addr+size-1<=current->end) {//在不空闲队列中找到能容纳的 
        	MemoryBlock* new_block = (MemoryBlock*)malloc(sizeof(MemoryBlock));//创建新的内存空闲块
        	new_block->start=start_addr;
        	new_block->is_free=1;
        	new_block->size=size;
        	new_block->end=start_addr+size-1;//对新的内存块内容进行设置，下一步是分割内存块，同时对新内存块连接进行配置 
        	
        	MemoryBlock* ac_b=current->next;//current前驱，ac_b后继
			 
			MemoryBlock* c = (MemoryBlock*)malloc(sizeof(MemoryBlock));//分割内存块，作为连接后继 
			c->end=current->end;
			c->start=new_block->end+1;
			c->is_free=0;
			new_block->next=c;//新内存块作为后继 
			c->next=ac_b;
			c->size=c->end-c->start+1;
			
			current->next=new_block;//更新原来内存块的前驱信息 
			current->end=new_block->start-1;
			current->size-=c->size+size;
			flag=1;
            break;
        }
        current = current->next;
    }
    if(!flag) printf("Can't find the block!!!\n"); 
    // 合并相邻的空闲块
    merge_adjacent_blocks();
}

void print_memory_status(int s) { 
    printf("Index\t*\tadr\t*\tend\t*\tsize\n");
    MemoryBlock* current = free_list;

    if (s == 0) { 
        // 最佳适应：按空闲块大小升序输出 统计空闲块数量
        int count = 0;
        current = free_list;
        while (current != NULL) {
            if (current->is_free) count++;
            current = current->next;
        }

        // 动态分配数组存储空闲块指针
        MemoryBlock** blocks = (MemoryBlock**)malloc(count * sizeof(MemoryBlock*));
        current = free_list;
        int i = 0;
        while (current != NULL) {
            if (current->is_free) {
                blocks[i++] = current;
            }
            current = current->next;
        }

        //按大小升序排序（冒泡排序）
        for (int i = 0; i < count - 1; i++) {
            for (int j = 0; j < count - i - 1; j++) {
                if (blocks[j]->size > blocks[j + 1]->size) {
                    MemoryBlock* temp = blocks[j];
                    blocks[j] = blocks[j + 1];
                    blocks[j + 1] = temp;
                }
            }
        }

        //输出排序后的结果
        for (int i = 0; i < count; i++) {
            printf("%d\t\t%d\t\t%d\t\t%d\n", i + 1, blocks[i]->start, blocks[i]->end, blocks[i]->size);
        }

        free(blocks); // 释放临时数组
    } else { 
        // 首次适应：按地址顺序输出
        int idx = 1;
        while (current != NULL) {
            if (current->is_free) {
                printf("%d\t\t%d\t\t%d\t\t%d\n", idx, current->start, current->end, current->size);
                idx++;
            }
            current = current->next;
        }
    }
}

int main() {
    initialize_memory();
    int s=0;//策略标记，0代表最佳，1代表首次 
    printf("Initial memory status:\n");
    print_memory_status(s);

    char strategy[10];
    printf("Input the way (best or first): ");
    scanf("%s", strategy);
    
	if (strcmp(strategy, "first") == 0) s=1; 
	
    char operation[10];
    while (1) {
        printf("Assign or Accept: ");
        scanf("%s", operation);
        if (strcmp(operation, "as") == 0) { 
            int app_size;
            printf("Input APPLICATION: ");
            scanf("%d", &app_size);
            MemoryBlock* block = NULL;
            if (!s) block = best_fit(app_size);
            else block = first_fit(app_size);//不同策略方法寻找合适的内存空间 
            if (block != NULL) {
                allocate_memory(block, app_size);
                printf("SUCCESS!!! ADDRESS=%d\n", block->end+1);
                print_memory_status(s);
            } else {
                printf("Too large application!\n");//找不到内存空间的情况 
                break;//太大，跳出循环 
            }
        } else if (strcmp(operation, "ac") == 0) {
            int addr, size;
            printf("Input adr and size: ");
            scanf("%d %d", &addr, &size);
            free_memory(addr, size);
            print_memory_status(s);
        }
    }
    return 0;
}
