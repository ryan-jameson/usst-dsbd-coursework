#ifndef FILEOPERATE
#define FILEOPERATE

#include<fstream>
#include"inc.h"
#include"ColorPrint.hpp"
using namespace std;

template<typename T,typename U>
class FileOperate{
    private:
        char _dir[60];
        bool isinit;
    public:
        FileOperate();
        FileOperate(char *dir);
        bool savetofile(T& elem);
        bool readfromfile(T& elem);
        void set_dir(char *dir);
};

template<typename T,typename U>
FileOperate<T,U>::FileOperate():_dir(""),isinit(false){}

template<typename T,typename U>
FileOperate<T,U>::FileOperate(char* dir):isinit(true){
    this->set_dir(dir);
}

template<typename T,typename U>
bool FileOperate<T,U>::savetofile(T& elem){
    if(!isinit){
        printRed("Error!Empty dir path\n");
        return false;
    }
    ofstream obin;
    obin.open(_dir);
    for(auto iter=elem.begin();;iter++){
        if(iter==nullptr){
            return true;
            obin.close();
        }
        U* temp=iter._ptr->pointer();
        obin.write(reinterpret_cast<char*>(temp),sizeof(U));
        if(iter==elem.end())
            break;
    }
    obin.close();
    return true;
}

template<typename T,typename U>
bool FileOperate<T,U>::readfromfile(T & elem){
    ifstream ibin;
    ibin.open(_dir);
    if(!isinit||!ibin.is_open()){
        printRed("Error!Empty dir path\n");
        return false;
    }
    U temp;
    while(!ibin.eof()){ 
        ibin.read(reinterpret_cast<char*>(&temp),sizeof(U));
        elem.push_back(temp);
        if(ibin.eof()){
            elem.erase(elem.end());
            break;
        }
    }
    ibin.close();
    return true;
}

template<typename T,typename U>
void FileOperate<T,U>::set_dir(char* dir){
    strcpy(_dir,dir);
    this->isinit=true;
}

#endif