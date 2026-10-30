#ifndef _UI_
#define _UI_
#include"inc.h"
#include"File.hpp"

class UI{
    private:
        User _user;
        bool _islogin,_isread;
        Shoplistbase _shoplist;
        Bookdatebase _bookdata;
        DoubleLinkedList<User> _userlist;
        FileOperate<DoubleLinkedList<User>,User> _f;
        static bool cmp(char* name,User u){
            return strcmp(name,u._username)==0;
        }
    public:
        UI(){
            _islogin=false;_isread=false;
            char dir[]="/mnt/e/Code/ep9/build/user.dat";
            _f.set_dir(dir);
            _f.readfromfile(_userlist);
        }
        void UIloginn(){
            sleep(1); 
            while(!_islogin){
                system("clear");
                cout<<"------------------Login Menu------------------\n";
                cout<<"                   1 注册                     \n";
                cout<<"                   2 登录                     \n";
                cout<<"                   0 退出                     \n";
                int opt;
                cin>>opt;
                switch(opt){
                    case 0:return;
                    case 1:_register();break;
                    case 2:login();break;
                    default: printRed("Error!Please enter right idx");
                }
                sleep(1);
            }
        }
        void login(){
            while(1){
                system("clear");
                cout<<"--------------------Login---------------------\n";
                cout<<"   UserName:";
                char name[20]="",password[20]="",isadmin[]="admin";
                cin>>name;
                cout<<"   Password:";
                cin>>password;
                if(strcmp(name,isadmin)==0&&strcmp(password,isadmin)==0){
                    User admin(isadmin,isadmin,0);
                    _user=admin;
                    _islogin=true;
                    return printGreen("   Successfully login");
                }
                auto iter=_userlist.search(name,cmp);
                bool ctrl=true;
                if(iter.getptr()==nullptr){
                ctrl=false;
                }
                if(ctrl&&(*iter).data.login(password)){
                    _islogin=true;
                    _user=(*iter).data;
                    return printGreen("   Successfully login");
                }
                else{
                    printRed("   Incorrect username or password");
                }
                sleep(1);
            }
        }
        void _register(){
            system("clear");
            cout<<"-------------------Register--------------------\n";
            cout<<"   UserName:";
            char name[20]="",password[20]="";
            cin>>name;
            cout<<"   Password:";
            cin>>password;
            if(_userlist.search(name,cmp).getptr()!=nullptr){
                printRed("Error!Account already exists");
                sleep(1);
                return;
            }
            User temp(name,password,1);
            _userlist.push_back(temp);
        }
        void READDATA(){
            if(_isread){
                printMagenta("请勿重复读取!");
                sleep(1);
            }
            _isread=true;
            _bookdata.read();
        }
        void UISwitch(){
            if(!_islogin)
                return;
            int level=_user.get__level();
            if(level==1)
                UIClint();
            if(level==0)
                UIAdmin();
        }
        void UIstart(){
            UIloginn();
            UISwitch();
        }
        void UIAdmin(){
            while(1){
                system("clear");
                int opt;
                cout<<"------------Admin------------\n";
                cout<<"          1 添加书籍\n";
                cout<<"          2 删除书籍\n";
                cout<<"          3 显示所有书籍\n";
                cout<<"          4 保存\n";
                cout<<"          5 读取\n";
                cout<<"          6 权限管理\n";
                cout<<"          7 用户界面\n";
                cout<<"          0 退出";
                cout<<"\n\n输入序号:";
                cin>>opt;
                switch(opt){
                    case 0:return;
                    case 1:{
                        _bookdata.addnewbook();
                    }break;
                    case 2:{
                        _bookdata.earse();
                    }break;
                    case 3:
                        _bookdata.showAll();break;
                    case 4:
                        _bookdata.write();break;
                    case 5:
                        READDATA();break;
                    case 6:
                        adminempowerment();break;
                    case 7:
                        UIClint();break;
                    default:printRed("Error!Please enter right idx");
                }
            }
        }
        void adminempowerment(){
            system("clear");
            cout<<"------------------Empowerment------------------\n";
            if(_user.get__level()!=0)
                return printMagenta("Permission denied");
            _userlist.show();
            cout<<"\n\n---------选择提权序号---------\n";
            char temp[999]="";
            cin>>temp;
            cout<<"\n\n----------输入权值----------\n";
            cout<<"管理员:0  用户:1\n";
            int n;
            cin>>n;
            for(int i=0;i<strlen(temp);i++){
                int idx=(temp[i]-'0')-1;
                if(idx==-1)
                    return;
                _userlist[idx].empowerment(n);
            }
        }
        void UIClint(){
            strcpy(_shoplist._name,_user._username);
            READDATA();
            while(1){
                system("clear");
                int opt;
                cout<<"------------Clint------------\n";
                cout<<"          1 搜索购买\n";
                cout<<"          2 显示所有书籍\n";
                cout<<"          3 结账\n";
                cout<<"          4 清空购物车\n";
                cout<<"          5 删除书本\n";
                cout<<"          0 退出(警告!不保存购买记录)\n";
                cout<<"\n\n输入序号:";
                cin>>opt;
                switch(opt){
                    case 0:return;
                    case 1:{
                        auto iter=_bookdata.search();
                        if(iter==nullptr)
                            printRed("Error!No book");
                        else{
                            char ctrl;
                            cout<<"是否购买(y/any):";
                            cin>>ctrl;
                            if(ctrl=='y')
                                _shoplist.addAttribute(iter->name,iter->value);
                        }break;
                    }break;
                    case 2:
                        _bookdata.showAll();break;
                    case 3:
                        _shoplist.sumvalue();break;
                    case 4:
                        _shoplist.init();break;
                    case 5:{
                        char key[20];
                        system("clear");
                        cout<<"输入书名:";
                        cin>>key;
                        _shoplist.eraseAttribute(key);
                    }break;
                    default:printRed("Error!Please enter right idx");
                }
            }
        }
        ~UI(){
            READDATA();
            _bookdata.write();
            _f.savetofile(_userlist);
        }
};
#endif