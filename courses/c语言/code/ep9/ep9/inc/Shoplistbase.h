#ifndef SHOPLIST
#define SHOPLIST

#include"inc.h"
#include"File.hpp"
struct Attribute{
    char name[20]="";
    int value=0;
    friend ostream& operator<<(ostream& out,Attribute& att){
        return out<<"书名:"<<att.name<<"\t价格:"<<att.value<<endl;
    }
};

class Shoplistbase{
    protected:
        Attribute _attributelist[40];
        int idxAttribute=0;
    public:
        char _name[20];
        Shoplistbase():_name(""){};
        void addAttribute(char *k1,int k2);
        void eraseAttribute(char *k1);;
        void ShowAttribute();
        void init(){
            idxAttribute=0;
        }
        void sumvalue(){
            int sum=0;
            for(int i=0;i<idxAttribute;i++)
                {
                cout<<"Book:"<<i+1<<endl;
                cout<<_attributelist[i];
                sum+=_attributelist[i].value;
                cout<<"小计:"<<sum<<endl;
            }
            cout<<"总计:"<<sum<<endl;
            char stop;
            cout<<"Press C To Continue...\n";
            cin>>stop;
        }
        friend ostream& operator<<(ostream& out,Shoplistbase& crb){
            out<<"Client"<<crb._name<<endl;
            crb.ShowAttribute();
            return out;
        }
}; 

class Bookdatebase{
    private:
        DoubleLinkedList<Attribute> _booklist;
        FileOperate<DoubleLinkedList<Attribute>,Attribute> _f;
        static bool cmp(char* key,Attribute atr){
            return strcmp(key,atr.name)==0;
        }
    public:
        Bookdatebase(){
            char dir[]="/mnt/e/Code/ep9/data/bookbase.dat";
            _f.set_dir(dir);
        }
        void read(){
            _f.readfromfile(_booklist);
        }
        void write(){
            _f.savetofile(_booklist);
        }
        void earse(){
            system("clear");
            char name[20];
            cout<<"输入书名";
            cin>>name;
            _booklist.erase(_booklist.search(name,cmp));
        }
        void showAll(){
            system("clear");
            _booklist.show();
            char stop;
            cout<<"Press C To Continue...\n";
            cin>>stop;
        }
        void addnewbook(){
            _booklist.addnewnode(1);
            system("clear");
            char name[20];int value;
            cout<<"书名:";
            cin>> _booklist.end()._ptr->data.name;
            cout<<"价格:";
            cin>> _booklist.end()._ptr->data.value;
        }
        Attribute* search(){
            system("clear");
            char name[20];
            cout<<"输入书名";
            cin>>name;
            auto iter=_booklist.search(name,cmp);
            return &(iter._ptr->data);
        }
};

void Shoplistbase::addAttribute(char* k1,int k2){
    strcpy(_attributelist[idxAttribute].name,k1);
    _attributelist[idxAttribute++].value=k2;
}

void Shoplistbase::eraseAttribute(char* k1){
    int i=0;bool find=false;
    for(;i<idxAttribute;i++){
        if(strcmp(_attributelist[i].name,k1)==0){
            find=true;
            break;
        }
    }
    if(!find)
        return printRed("Error!No object");
    for(++i;i<20;i++){
        _attributelist[i-1]=_attributelist[i];
    }
}


void Shoplistbase::ShowAttribute(){
    for(int i=0;i<idxAttribute;i++)
        cout<<_attributelist[i];
}


#endif