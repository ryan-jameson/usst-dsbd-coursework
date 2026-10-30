#ifndef DOUBLELINKEDLIST
#define DOUBLELINKEDLIST

#include"inc.h"
#include"ColorPrint.hpp"
using namespace std;

template<typename T>
class Node{
    public:
        T data;
        Node<T>* _next;
        Node<T>* _last;
        T* pointer(){
            return &data;
        }
};

template<typename T>
class DoubleLinkedList{
    private:
        Node<T> *_start;
        Node<T> *_end;
        int _listLen;
    public:
    class iterator{
            public:
                Node<T> *_ptr;
                iterator(Node<T> *p==nullptr):_ptr(p){};
                iterator operator--(){
                    _ptr=_ptr->_last;
                    return *this;
                }
                bool operator!=(iterator i){
                    return !(*this==i);
                }
                Node<T>& operator*() const{
                    return *(_ptr);
                }
                Node<T>* operator->() const{
                    return _ptr;
                }
                iterator &operator++(){
                    _ptr=_ptr->_next;
                    return *this;
                }
                iterator operator++(int){
                    Node<T> *temp=_ptr;
                    ++(*this);
                    return iterator(temp);
                }
                bool operator==(Node<T> *i){
                    return this->_ptr==i;
                }
                bool operator==(iterator i){
                    return this->_ptr==i._ptr;
                }
                Node<T>* getptr(){
                    return _ptr;
                }
        };
        DoubleLinkedList();
        bool empty();
        bool insert(const T& elem,iterator iter=nullptr);
        bool erase(iterator iter);
        bool erase(int idx);
        int getLen();
        void show();
        bool push_back(const T &elem);
        T& operator[](int idx);
        iterator begin();
        iterator end();
        void addnewnode(int num);
        bool orderinsert(const T& elem,bool (*cmp)(T,T));
        template<typename U,typename V>
        iterator search(U target,bool (*cmp)(U,V)){
            if(_listLen==-1)
                return nullptr;
            iterator iter(_start);
            bool ctrl=false;
            while(true){
                if(cmp(target,(*iter).data)){
                    ctrl=true;
                    break;
                }
                if(iter==_end)
                    break;
                iter++;
            }   
            return (ctrl?iter:nullptr);
        }
};



template<typename T>
inline void DoubleLinkedList<T>::addnewnode(int num){
    T temp;
    for(int i=0;i<num;i++)
        this->push_back(temp);
}

template<typename T>
bool DoubleLinkedList<T>::orderinsert(const T & elem, bool(* cmp)(T,T)){
    iterator iter(_start);
    if(_listLen==-1){
        return insert(elem);
    }
    while(!iter){
        if(cmp(elem,iter.getptr()->data))
            break;
        iter++;
    }
    if(!iter){
        push_back(elem);
        return true;
    }
    else{
        insert(elem,iter);
        return true;
    }
}

template<typename T>
typename::DoubleLinkedList<T>::iterator DoubleLinkedList<T>::end(){
    return iterator(_end);
}

template<typename T>
typename::DoubleLinkedList<T>::iterator DoubleLinkedList<T>::begin(){
    return iterator(_start);
}

template<typename T>
bool DoubleLinkedList<T>::push_back(const T &elem){
    if(_listLen==-1){
        return this->insert(elem);
    }
    _listLen++;
    Node<T>* newNode=new Node<T>;
    newNode->_last=_end;
    newNode->_next=NULL;
    newNode->data=elem;
    _end->_next=newNode;
    _end=newNode;
    return true;
}


template<typename T>
int DoubleLinkedList<T>::getLen(){
    return _listLen;
}

template<typename T>
DoubleLinkedList<T>::DoubleLinkedList(){
    _start=NULL;
    _end=NULL;
    _listLen=-1;
}

template<typename T>
bool DoubleLinkedList<T>::empty(){
    return _start==_end;
}

template<typename T>
T& DoubleLinkedList<T>::operator[](int idx){
    int accumulator=0;
    Node<T>* iter=_start;
    try{
        while(accumulator!=idx){
            if(iter==nullptr){
                throw "Error!Index out of bounds";
                break;
            }
            iter=iter->_next;
            accumulator++;
        }
        return iter->data;
    }
    catch(const char* msg){
        cerr<<msg<<endl;
    }
    return _end->data;
}

template<typename T>
bool DoubleLinkedList<T>::insert(const T& elem,iterator iter){
    Node<T> *new_node=new Node<T>,*temp=iter.getptr();
    if(new_node==nullptr){
        cerr<<"Error!Memory Limit Exceeded\n";
        return false;
    }
    _listLen++;
    new_node->data=elem;
    new_node->_last=nullptr;
    new_node->_next=nullptr;
    if(_listLen==0){
        _start=new_node;
        _end=new_node;
        return true;
    }
    if(iter==_start){
        new_node->_next=_start;
        _start->_last=new_node;
        _start=new_node;
        return true;
    }
    temp->_last->_next=new_node;
    new_node->_last=temp->_last;
    new_node->_next=temp;
    temp->_last=new_node;
    return true;
}

template<typename T>
bool DoubleLinkedList<T>::erase(iterator iter){
    Node<T> *i=iter.getptr();
    _listLen--;
    if(_listLen==-1){
        delete _start;
        _start=nullptr;
        _end=nullptr;
        return true;
    }
    if(iter==_start){
        Node<T> *temp=_start->_next;
        delete _start;
        _start=temp;
        _start->_last=nullptr;
        return true;
    }
    if(iter==_end){
        Node<T> *temp=_end->_last;
        delete _end;
        _end=temp;
        _end->_next=nullptr;
        return true;
    }
    i->_last->_next=i->_next;
    i->_next->_last=i->_last;
    delete i;
    return true;
}

template<typename T>
void DoubleLinkedList<T>::show(){
    if(this->_listLen==-1){
        return printMagenta("No Data");
    }
    Node<T>* iter=_start;int i=1;
    while(iter!=NULL){
        cout<<"Number:"<<i++<<endl;
        cout<<(iter->data)<<"\n";
        iter=iter->_next;
    }
}

template<typename T>
bool DoubleLinkedList<T>::erase(int idx){
    iterator iter=this->begin();
    while(idx--)
        iter++;
    return erase(iter);
}

#endif

