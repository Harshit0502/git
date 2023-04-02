#include<stdio.h>
int main(){
    int a = 5;
    int b = 10;
    int c = (a>b)?printf("%d",a):printf("%d",b);
    printf("_%d", c);
    return 0;
}