#include<stdio.h>
int main(){
    int a,b,c,x,y,z,s;
    printf("enter the value:");
    scanf("%d",&a);
    printf("enter the value:");
    scanf("%d",&b);
    printf("enter the value:");
    scanf("%d",&c);
    printf("enter the value:");
    scanf("%d",&x);
    printf("enter the value:");
    scanf("%d",&y);
    printf("enter the value:");
    scanf("%d",&z);
    s==a+b+c;
    if(s==180 && (x+y)>z){
        printf("triangle is valid");
    }
    else{
        printf("null");
    }

    if(x==y==z){
        printf("equilateral");
    }
    else if(x==y||y==z){
        printf("isoceles");
    }
    else{
        printf("scalane");
    }
}