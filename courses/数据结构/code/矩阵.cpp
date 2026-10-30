#include <bits/stdc++.h>
//m 行数 n 列数 
int a[100][100];
int aT[100][100];
int m,n;


main(){
	printf("输入行数列数\n");
	scanf("%d%d",&m,&n);
	for(int i=0;i<m;i++){
		for(int j=0;j<n;j++){
			scanf("%d",&a[i][j]);
		}
	}

	for(int i=0;i<n;i++){
		for(int j=0;j<m;j++){
			aT[i][j]=a[j][i];
		}
	}
	
	for(int i=0;i<m;i++){
		for(int j=0;j<n;j++){
			printf("%d\t",a[i][j]);
		}
		printf("\n");
	}
	for(int i=0;i<n;i++){
		for(int j=0;j<m;j++){
			printf("%d\t",aT[i][j]);
		}
		printf("\n");
	}
}
