#include <stdio.h>
#include <stdlib.h>

#define MAXV 100

typedef struct {
    int edges[MAXV][MAXV]; // 邻接矩阵
    int n, e; // 顶点数，边数
    int vexs[MAXV]; // 顶点信息存放
} MatGraph; // 图的建立，用来建立邻接矩阵

typedef struct ANode {
    int adjvex; // 边结点信息
    struct ANode* next;
} ANode; // 邻接表子表的建立

typedef struct VNode {
    int vexs; // 顶点信息存放
    ANode* first; // 第一条边
} VNode; // 邻接表整表

typedef struct {
    VNode* AdjList[MAXV]; // 邻接表
    int n, e; // 顶点数和边的数量
} AdjGraph; // 图的建立，用来建立邻接表

int LocateMat(MatGraph G, int v) {
    for (int i = 0; i < G.n; i++) {
        if (G.vexs[i] == v) return i;
    }
    return -1;
}

void CreateGraph(MatGraph *G) {
    printf("输入图的顶点个数和边的数量\n");
    scanf("%d %d", &G->n, &G->e); // 输入图的顶点个数，边的个数
    for (int i = 0; i < G->n; i++) {
        printf("输入顶点信息\n");
        scanf("%d", &G->vexs[i]);
    }
    for (int i = 0; i < G->n; i++) {
        for (int j = 0; j < G->n; j++) {
            G->edges[i][j] = 0;
        }
    } // 初始化邻接矩阵

    for (int k = 0; k < G->e; k++) {
        int n1, n2;
        printf("输入顶点关系\n");
        scanf("%d %d", &n1, &n2); // 输入两个顶点，如果输入，就在邻接矩阵相应位置填入1
        int v1 = LocateMat(*G, n1);
        int v2 = LocateMat(*G, n2);
        if (v1 != -1 && v2 != -1) {
            G->edges[v1][v2] = 1;
            G->edges[v2][v1] = G->edges[v1][v2]; // 填入对称位置
        }
    }
} // 邻接矩阵创建完毕

void CreateAdjList(AdjGraph **A, MatGraph G) {
    ANode* p; // 结点声明
    *A = (AdjGraph*)malloc(sizeof(AdjGraph));

    (*A)->n = G.n;
    (*A)->e = G.e;
    for (int i = 0; i < (*A)->n; i++) {
        (*A)->AdjList[i] = (VNode*)malloc(sizeof(VNode));
        (*A)->AdjList[i]->vexs = G.vexs[i];
        (*A)->AdjList[i]->first = NULL;
    }

    for (int i = 0; i < (*A)->n; i++) { // 邻接表填入
        for (int j = 0; j < (*A)->n; j++) { // 邻接表子表填入
            if (G.edges[i][j] != 0) {
                p = (ANode*)malloc(sizeof(ANode));
                p->adjvex = G.vexs[j];
                p->next = (*A)->AdjList[i]->first;
                (*A)->AdjList[i]->first = p;
            }
        }
    } // 按照邻接矩阵自动填入邻接表
}

int visited[MAXV] = {0}; // 被访问标记

void DFS(MatGraph G, int v) {
    printf("%d\t", v); // 头输出
    int vi = LocateMat(G, v);
    visited[vi] = 1; // 已被访问过
    for (int i = 0; i < G.n; i++) {
        if (G.edges[vi][i] == 1 && visited[i] == 0) DFS(G, G.vexs[i]); // 递归输出
    }
} // 深度遍历

int LocateAdj(AdjGraph *A, int v) {
    for (int i = 0; i < A->n; i++) {
        if (A->AdjList[i]->vexs == v) return i;
    }
    return -1;
}

void BFS(AdjGraph *A, int v) {
    printf("%d\t", v);
    ANode *p;
    int vi = LocateAdj(A, v);
    for (int i = 0; i < A->n; i++) {
        visited[i]=0;
    }
    visited[vi] = 1;
    int QU[MAXV], front = 0, rear = 0; // 定义一个队列，用来存放输出的顶点
    
    rear = (rear + 1) % MAXV;
    QU[rear] = vi;

    while (front != rear) { // 队空结束输出
        front = (front + 1) % MAXV; // 输出头结点
        vi =QU[front];
        p = A->AdjList[vi]->first; // 定位一下头结点的邻接表
        while (p != NULL) {
            int wi = LocateAdj(A, p->adjvex);
            if (wi != -1 && visited[wi] == 0) {
                printf("%d\t", p->adjvex);
                visited[wi] = 1;
                rear = (rear + 1) % MAXV;
                QU[rear] = wi;
            }
            p = p->next;
        }
    }
} // 广度遍历

int main() {
    MatGraph G;
    AdjGraph* A;
    CreateGraph(&G);
    
    CreateAdjList(&A, G);
    DFS(G, 1);
    printf("\n");
    BFS(A, 1);
    return 0;
}
