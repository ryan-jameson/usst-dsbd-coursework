#ifndef USER
#define USER

#include"inc.h"
using namespace std;

class User{
    private:
        int _hash,_level;
        int StringtoHash(const char* n){
            int res=0,M=1e9+7,B=133;
            for(int i=0;i<strlen(n);i++){
                res=((long long)res*B+n[i])&M;
            }
            return res;
        }
    public:
        char  _username[20];
        User():_username(""){};
        User(const User& u1):_username(""){
            _hash=u1._hash;
            _level=u1._level;
            strcpy(_username,u1._username);
        }
        void operator=(const User& u1){
            _hash=u1._hash;
            _level=u1._level;
            if(!u1._username)
                return;
            strcpy(_username,u1._username);
        }
        User(const char* username,char* key,int level=-1):_hash(this->StringtoHash(key)),_level(level){
            strcpy(_username,username);
        };
        bool login(char* key){
            return _hash==this->StringtoHash(key);
        };
        friend ostream& operator<<(ostream& out,User& user){
            return out<<"Name:"<<user._username<<"\nLevel:"<<user.get__level()<<endl;
        }
        void empowerment(int n){
            _level=n;
        }
        inline int get__level() const {return _level;}
};

#endif