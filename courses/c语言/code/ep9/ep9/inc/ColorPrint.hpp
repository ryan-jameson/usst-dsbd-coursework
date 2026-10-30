#ifndef COLORPRINT__
#define COLORPRINT__

#include<iostream>
#include<unistd.h>
using namespace std;

#define CLEAR "\033[0m"
#define GREEN "\033[32m"
#define RED "\033[31m"
#define MAGENTA "\033[35m"
#define SHINE "\033[5m"


template <typename T>
void printRed(T data){
    cout<<RED<<data<<CLEAR<<endl;
}

template<typename T>
void printShine(T data){
    cout<<SHINE<<data<<endl;
}

template<typename T>
void printGreen(T data){
    cout<<GREEN<<data<<CLEAR<<endl;
}


template<typename T>
void printMagenta(T data){
    cout<<MAGENTA<<data<<CLEAR<<endl;
}

#endif