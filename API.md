# 接口文档

### 错误码说明
- Http status code
    - 200 - 正常返回
    - 500 - 服务器错误
    - 400 - 请求错误

- 自定义body code
    - 200 - 正常返回(http code=200)
    - 900 - 通用错误返回(http code=200)
    - 901 - 用户未登录(http code=200)
    - 902 - 无权限访问(http code=200)
    - 903 - 该项操作不可用(http code=200)
    - 904 - 该账户已被封禁(http code=200)
    - 905 - 该账户状态异常(http code=200)
    - 906 - 订单支付失败(http code=200)
    - 907 - 警告(http code=200)
    - 9xx - 待定义错误码(http code=200)

## 接口设计(地址前缀 http://ip:port/)

### 前端HTTP请求
###### http header

名称	 |	说明 | 是否必填
--- | ---
Auth-Token |	用户的token(除明确标出不需要Auth-Token外,其他均需要) | 否

###### http body
```
{
    "参数1":"值1",
    "参数2":"值2",
    "参数3":"值3"
}
```

### 服务端HTTP响应
###### http header

名称	 |	说明 | 是否必填
--- | ---
Auth-Username |	用户的username | 否

###### http body

名称	 |	说明 | 是否必填
--- | ---
code |	返回码 | 是
msg |	提示信息 | 是
data |	响应数据 | 是

* 正常 Http Status Code=200
```
{
    "code": 200, //正常码
    "msg": "提示信息",
    "data": {
        //正常携带数据json
    }
}
```
* 错误 Http Status Code=200
```
{
    "code": 900, //错误码
    "msg": "提示信息",
    "data": {
        //错误携带数据json, 通常为空
    } 
}
```


### 认证接口
#### 1.注册验证码(不需要Auth-Token;mobile和email有一个即可)
```bash
curl -XPOST "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/register/code' -d ' 
{
    "mobile": "18912386146", 
    "email": "zhangxc@163.com"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "_nc_":"xxxxx"
    }
}
# 错误返回
{
    "msg": "参数错误",
    "code": 900,
    "data": null
}
{
    "msg": "手机号码错误", //手机号码已经注册也提示这个错误
    "code": 900,
    "data": null
}
{
    "msg": "邮箱错误", //邮箱已经注册也提示这个错误
    "code": 900,
    "data": null
}
```

#### 2.提交注册信息验证接口(不需要Auth-Token)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://192.168.103.119:8080/register/verify' -d ' 
{
    "cname": "zxc337", 
    "mobile": "18912386146", 
    "email": "zhangxc@163.com",
    "password": "123456",
    "password_confirm": "123456",
    "agent_id": "23" //可为空
    “firstname”:"xxx"//姓
    "lastname":"xxx"//名
    //说明：cname存在，是中国版；firstname、lastname存在，是国际版。只需一项存在！
}'
```
```
# 正常返回
{
    "msg": "register verify success",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "密码需要至少8位|邮箱格式不正确|用户名请使用小写字母，数字，下划线|邮箱或手机号错误|手机号格式不正确",
    "code": 900,
    "data": null
}
```

#### 3.提交注册(不需要Auth-Token)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://192.168.103.119:8080/register' -d ' 
{
    "_nc_":"xxxx",
    "cname": "zxc337", 
    "mobile": "18912386146", 
    "email": "zhangxc@163.com",
    "password": "123456",
    "password_confirm": "123456",
    "agent_id": "23",
    "code":"678909",
    “firstname”:"xxx"//姓
    "lastname":"xxx"//名
    //cname存在，是中国版；firstname、lastname存在，是国际版。只需一项存在！
}'
```
```
# 正常返回
{
    "msg": "register success",
    "code": 200,
    "data": {
        "certid": null,
        "firstname": null,
        "lastname": null,
        "swiftcode": null,
        "agent_id": "23",
        "bank": null,
        "bankbranch": null,
        "mobile": "18912386146",
        "menu": [
            {
                "children": [
                    {
                        "link": "/usermain",
                        "target": "_self",
                        "title": "我的首页"
                    },
                    {
                        "link": "/customerinfo",
                        "target": "_self",
                        "title": "我的信息"
                    },
                    {
                        "link": "/customerupdate",
                        "target": "_self",
                        "title": "身份验证"
                    },
                    {
                        "link": "/updatepassword",
                        "target": "_self",
                        "title": "修改密码"
                    },
                    {
                        "link": "quit",
                        "target": "_self",
                        "title": "退出系统"
                    }
                ],
                "title": "我的概况"
            },
            {
                "children": [
                    {
                        "link": "/deposit",
                        "target": "_self",
                        "title": "入金存款"
                    },
                    {
                        "link": "/withdrawmoney",
                        "target": "_self",
                        "title": "出金取款"
                    },
                    {
                        "link": "/accounttransfer",
                        "target": "_self",
                        "title": "账号之间转账"
                    },
                    {
                        "link": "/historymoney",
                        "target": "_self",
                        "title": "出入金记录"
                    }
                ],
                "title": "财务"
            },
            {
                "children": [
                    {
                        "link": "/accountlist",
                        "target": "_self",
                        "title": "交易账户"
                    },
                    {
                        "link": "/searchagent",
                        "target": "_self",
                        "title": "我的客户"
                    },
                    {
                        "link": "/network",
                        "target": "_self",
                        "title": "我的网络"
                    }
                ],
                "title": "账户管理"
            },
            {
                "children": [
                    {
                        "link": "#",
                        "target": "_blank",
                        "title": "MT5下载"
                    }
                ],
                "title": "信息"
            }
        ],
        "mt": [
            {
                "balance": 0,
                "mtlogin": "9003",
                "mtpasswd": "6a8vdxjn"
            }
        ],
        "token": "fdfe0f704f75027d4f69be531463ca4b17565b3d",
        "cname": "zxc337",
        "statusa": "出金冻结",
        "email": "zhangxc@163.com"
    }
}
# 错误返回
{
    "msg": "验证码错误|验证码过期|密码需要至少8位|邮箱格式不正确|用户名请使用小写字母，数字，下划线|邮箱或手机号错误|手机号格式不正确",
    "code": 900,
    "data": null
}
```

#### 4.登录(不需要Auth-Token;mobile和email有一个即可)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/login' -d ' 
{
    "mobile": "18912386146", 
    "email": "zhangxc@163.com", 
    "password": "123456"
}'
```
```
# 正常返回
{
    "msg": "login success",
    "code": 200,
    "data": {
        "menu": "",
        "token": "f620fa41ef1866087b957f6f795a3cf3867997d2",
        "cname": "姓名", 
        "firstname": "姓", 
        "lastname": "名", 
        "mobile": "手机号",
        "email": "邮箱",
        "certid": "身份证号码",
        "bank": "银行卡开户行",
        "bankbranch": "支行名称",
        "swiftcode": "SWIFT CODE",
        "agent_id": "代理编码",
        "mt":[
            {
                "mtlogin": "交易账户",
                "mtpasswd":"交易密码",
                "balance":"交易密码"
            }
        ]
    }
}
# 错误返回
{
    "msg": "不存在用户名或密码错误|请输入密码|请输入登录信息",
    "code": 900,
    "data": null
}
```

#### 4.1 管理员登录(不需要Auth-Token;mobile和email有一个即可)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/bg/login' -d ' 
{
    "mobile": "18912386146", 
    "email": "zhangxc@163.com", 
    "password": "123456"
}'
```
```
# 正常返回
{
    "msg": "login success",
    "code": 200,
    "data": {
        "menu": "",
        "token": "f620fa41ef1866087b957f6f795a3cf3867997d2",
        "cname": "姓名", 
        "firstname": "姓", 
        "lastname": "名", 
        "mobile": "手机号",
        "email": "邮箱",
        "certid": "身份证号码",
        "bank": "银行卡开户行",
        "bankbranch": "支行名称",
        "swiftcode": "SWIFT CODE",
        "agent_id": "代理编码",
        "mt":[
            {
                "mtlogin": "交易账户",
                "mtpasswd":"交易密码",
                "balance":"交易密码"
            }
        ]
    }
}
# 错误返回
{
    "msg": "不存在用户名或密码错误|请输入密码|请输入登录信息",
    "code": 900,
    "data": null
}
```

#### 5.登出(不需要Auth-Token)
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/logout' 
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": null
}
```

#### 6.找回密码验证码(不需要Auth-Token;mobile和email有一个即可)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/resetpwd/code' -d ' 
{
    "mobile": "18912386146", 
    "email": "zhangxc@163.com"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "_ncr_":"xxxx"
    }
}
# 错误返回
{
    "msg": "参数错误",
    "code": 900,
    "data": null
}
{
    "msg": "手机号码错误", //手机号码未注册也提示这个错误
    "code": 900,
    "data": null
}
{
    "msg": "邮箱错误", //邮箱未注册也提示这个错误
    "code": 900,
    "data": null
}
```

#### 7.提交找回密码(不需要Auth-Token)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/resetpwd' -d ' 
{
    "_ncr_":"xxxx",
    "mobile": "18025636985",
    "email": "zhangxc@163.com",
    "code": "1234", 
    "password": "123456"
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "验证码错误|验证码过期|密码需要至少8位|请输入正确的手机号码|请输入手机号码",
    "code": 900,
    "data": null
}
```
#### 8.个人客户修改密码
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/profile/passwd' -d ' 
{
    "old_password": "12345678",
    "new_password": "12345679",
    "new_password_confirm": "12345679"
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "前后2次密码一样|密码需要至少8位|不存在用户名或密码错误",
    "code": 900,
    "data": null
}
```

#### 9.个人客户信息查看
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/profile/info' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "cname": "姓名", 
        "firstname": "姓", 
        "lastname": "名", 
        "mobile": "手机号",
        "email": "邮箱",
        "certid": "身份证号码",
        "bank": "银行卡开户行",
        "bankbranch": "支行名称",
        "bankaccount":"银行账户",
        "swiftcode": "SWIFT CODE",
        "agent_id": "代理编码",
        "mt":[
            {
                "mtlogin": "交易账户",
                "mtpasswd":"交易密码",
                "balance":"交易密码"
            }
        ],
        "certpic0_url":"http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx", //证件图片0
        "certpic1_url":"http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx", //证件图片1
        "bankpic0_url":"http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx",  //银行卡图片0
        "certpic0":"xxxxxxxxxx", //证件图片0 ID
        "certpic1":"xxxxxxxxxx", //证件图片1 ID
        "bankpic0":"xxxxxxxxxx",  //银行卡图片0 ID
        "addrpic0_url":"http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx",  //地址图⽚
        "addrpic0":"xxxxxxxxxx"  //地址图⽚ ID
    }
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 10.个人客户信息更新
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/profile/info' -d ' 
{
    "cname": "姓名", 
    "firstname": "姓", 
    "lastname": "名", 
    "certid": "身份证号码",
    "bank": "银行卡开户行",
    "bankbranch": "支行名称",
    "bankaccount":"银行账户",
    "swiftcode": "SWIFT CODE",
    "certpic0":"xxxxxxxxxx",
    "certpic1":"xxxxxxxxxx",
    "bankpic0":"xxxxxxxxxx",
    "country": "国家", 
    "state": "州省", 
    "address": "地址", 
    "addrpic0":"地址图⽚ID",
    "email":"邮箱",
    "mobile":"手机号",
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 11. 个人客户手机号邮箱修改验证码
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/profile/loginid/code' -d ' 
{
    "mobile": "手机号", //选填
    "email": "邮箱" //选填
}' 
```
```
# 正常返回
{
    "msg": "send code success",
    "code": 200,
    "data": {
        "_plc_": "xxxxxxxxxxxxxxxxxxxx"
    }
}
# 错误返回
{
    "msg": "请输入手机号码|请输入邮箱|手机号已被绑定|邮箱已被绑定",
    "code": 900,
    "data": null
}
```

#### 12.个人客户手机号邮箱修改
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/profile/loginid' -d ' 
{
    "mobile": "手机号", //选填
    "email": "邮箱", //选填
    "code": "验证码",
    "_plc_": "xxxxxxxxxxxxxx"
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "请输入手机号码|请输入邮箱|请输入正确的手机号码",
    "code": 900,
    "data": null
}
```

#### 13.图片上传
```bash
# name为文件名
# file-type为文件类型,可为空,身份证=idcard,银行卡=bankcard;放在header里面
curl -XPOST --header 'Content-Type: multipart/form-data' --header 'Accept: application/json' --header 'file-type: idcard' -F "name=@/root/xxx.jpg" -i 'http://192.168.103.119:8080/profile/upload' 
或者
curl --request POST \
  --url http://127.0.0.1:8080/profile/upload \
  --header 'Accept: application/json' \
  --header 'file-type: idcard' \
  --header 'Cache-Control: no-cache' \
  --header 'Content-Type: multipart/form-data' \
  --header 'content-type: multipart/form-data;' \
  --form 'name=@C:\Users\zhangxc\Pictures\1465486648950.png'
```
```
# 正常返回
{
    "msg": "upload success",
    "code": 200,
    "data": {
        "pic_id": "xxxxxxxxxx",
        "pic_url": "http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx",
    }
}
# 错误返回
{
    "msg": "上传图片不能大于2M|upload file fail",
    "code": 900,
    "data": null
}
```

#### 14.图片预览
```bash
curl -XGET 'http://192.168.103.119:8080/profile/view?id=xxxxxxxxxx' 
```
```
# 正常返回
图片流
# 错误返回
{
    "msg": "图片不存在|view file fail",
    "code": 900,
    "data": null
}
```



### 外部用户直客接口
#### 1.交易账户类型
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/group' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "grouptypes": ["类型名", "类型英文名"]
    }
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 2.提交新建交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/create' -d ' 
{
    "type":"类型",
    "leverage ": "交易比例杠杆"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
        "mt":[
            {"mtlogin": "mtlogin", "mtpasswd": "mtpasswd", "balance": 0}
        ]
    }
}
# 错误返回
{
    "msg": "超过三个账户无法创建|内部错误|请输入交易比例杠杆",
    "code": 900,
    "data": null
}
```

#### 3.提交修改交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/up' -d ' 
{
    "mtlogin":"mt交易账户",
    "type":"类型",
    "leverage ": "交易比例杠杆"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "请输入交易比例杠杆|内部错误",
    "code": 900,
    "data": null
}
```

#### 4.提交修改交易密码
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/pass/up' -d ' 
{
    "mtlogin":"mt交易账户",
    "mtpasswd": "12345678",
    "mtpasswd_confirm": "12345678"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "两次密码不一致|内部错误",
    "code": 900,
    "data": null
}
```

#### 5.查询交易账户总体信息
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/info'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "mt":[
            {
                "mtlogin": "mtlogin", // MT账户
                "mtgroup": "mtgroup", // MT分组
                "type": "账户类型", // 账户类型
                "leverage": "leverage", // 杠杆率
                "typename": "账户类型名", // 账户类型名
                "balance": "balance", // 账户结余
                "marginlevel": "marginlevel", // 预付款维持率
                "equity": "equity" // 账户净值
            }
        ]
    }
}
```

#### 6.查询交易账户明细记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/record' -d ' 
{
    "start":"20180722",
    "end": "20180729"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "records": [
            {
                "deal": "交易号",
                "login": "账户",
                "order": "订单号",
                "action": "交易类型",
                "symbol": "品种",
                "price": "价格",
                "volume": "交易量(手数)",
                "profit": "利润",
                "storage": "过夜利息",
                "commission": "外佣",
                "rateprofit": "利润率"
            }
        ]
    }
}
# 错误返回
{
    "msg": "请输入交易账户账户|请输入交易品种",
    "code": 900,
    "data": null
}
```

#### 7.MT杠杆率查询(MT杠杆率查询,查看加佣,查看加点)
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/leverage' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": {
        "leverage": ["50","100"],  //杠杆率
        "spread": ["50","100"],  //内佣加点
        "commission": ["50","100"],  //外佣加点
    },
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 8.汇率查询
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/exchange' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": {
        "depositfx": xxx, //入金汇率
        "withdrawfx": xxx //出金汇率
    },
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 9.入金(paytype:10=在线支付,11=电汇入金)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/deposit' -d ' 
{
    "mtlogin":"mtaccount", //MT账户
    "amount_dollar": 1, //美元金额(需要与人民币和汇率对应)
    "amount_rmb": 8, //人民币金额
    "exchange": xxx, //汇率
    "paytype": 10, //支付方式
    "singleNumber": "xxxx" //汇款单号(可为空,仅电汇入金需要)
}'
```
```
# 正常返回
{
    "code": 200
    "msg": ""
    "data": {
        "payurl": "payurl", //支付链接,直接浏览器跳转打开该链接,由用户自行完成付款
        "orderid": "订单id"
    }
}
# 错误返回
{
    "msg": "交易金额换算错误|请输入交易金额|请输入交易方式|操作有误",
    "code": 900,
    "data": null
}
{
    "msg": "该用户状态异常",
    "code": 905,
    "data": null
}
```

#### 10.支付状态查询
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/pay/status' -d ' 
{
    "orderid":"订单id"
}'
```
```
# 正常返回
{
    "code": 200
    "msg": "支付成功"
    "data": null
}
# 错误返回
{
    "msg": "请输入订单号|订单不存在",
    "code": 900,
    "data": null
}
{
    "msg": "支付失败",
    "code": 906,
    "data": null
}
```

#### 11.MT出金
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/withdraw/mt' -d ' 
{
    "target_mt": "9002",  //出金交易账户
    "mount": 1.2132, //出金金额
    "exchange": 1.2132 //当前汇率
}'
```
```
# 正常返回
{
    "msg": "出金成功",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "请输入出金MT账户|请输入出金金额|请输入出金汇率|该用户状态异常|交易账户错误|余额不足|出金失败",
    "code": 900,
    "data": null
}
```

#### 12.会计出金
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/withdraw' -d ' 
{
    "mount": 1.2132, //出金金额
    "exchange": 1.2132 //当前汇率
}'
```
```
# 正常返回
{
    "msg": "出金成功",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "请输入出金金额|请输入出金汇率|该用户状态异常|交易账户错误|余额不足|出金失败",
    "code": 900,
    "data": null
}
```

#### 13.交易账号内部转账
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/transfer' -d ' 
{
    "out_mt":"mt1", //转出交易账户(电子钱包请传ewallet)
    "in_mt": "mt2", //转入交易账户
    "amount": 232.3554 //转出金额
}'
```
```
# 正常返回
{
    "msg": "转账成功",
    "code": 200,
    "data": null
}
```

#### 14.查看财务操作历史
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/history' -d ' 
{
    "mtlogin": "9006", 
    "opttype": 10, 
    "start": "2018-8-11", //格式%Y-%m-%d
    "end": "2018-8-18",
    "page": 1 //分页页码
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
            "comment": "", // 备注
            "credit": "0.00000", // 借
            "transaction": "", // 交易号
            "extpay_id": "lizhipay", // 支付源
            "createtime": "2018-08-17 17:35:37", // 创建时间
            "type": 10, // 类型(10=线上入金,11=电汇入金,20=标准出金,30=内转,50=内佣结算,51=外佣结算)
            "typename": "电汇入金",  //类型描述
            “typeename”:"dianhuirujin"
            "id": 2, // 客户资金变动表ID
            "extorder": "第三方单号",
            "mtlogin": "9006" // MT账户
        }
    ]
}
```

#### 15.电子钱包余额
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/balance/ewallet' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "amount": 123.3443 //账户余额
    }
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 16.交易账户余额
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/balance/mt' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        {
            "mt": [
                {
                    "mtlogin": "mt账户", 
                    "balance": "账户结余",
                    "equity": "账户净值"
                }
            ]
        }
    }
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 17.客户资金变动类型
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/fundtype' -d ' 
{
    
}' 
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "fundtypes": [
            {
                "type": "类型ID", 
                "name": "类型名称"
                “ename”:"类型英文名"
            }
        ]
    }
}
# 错误返回
{
    "msg": "",
    "code": 900,
    "data": null
}
```

#### 18.交易账户交易记录导出csv
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/summary/export' -d ' 
{
    "mtlogin":"MT账户"
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 19.出金状态跟踪
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/withdraw/trace' -d ' 
{
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15",  //结束时间
    "page" 1 //分页页码
}'
```
```
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "id": "Task表: 任务id", 
            "subject": "任务标题", 
            "taskname": "任务名称", 
            "body": "任务内容⽂本", 
            "o_uid": "发起⼈", 
            "o_cname": "发起⼈姓名", 
            "source_uid": "源⽤户", 
            "source_cname": "源⽤户姓名", 
            "target_uid": "⽬的⽤户", 
            "target_cname": "目的用户姓名", 
            "sourcemt": "源MT账户", 
            "targetmt": "⽬的MT账户", 
            "mtgroup": "MT分组", 
            "amount": "⾦额", 
            "exchange": "汇率", 
            "points": "点数", 
            "state": "状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)", 
            "tasknode_id": "当前节点id", 
            "createtime": "任务创建时间", 
            "updatetime": "上次修改时间", 
            "nodename": "当前节点名称", 
            "step": "当前节点阶段", 
            "approve": "approve命名", 
            "returned": "被return命名", 
            "canapprove": "approve可⽤", 
            "canreturn": "return可⽤", 
            "canreject": "reject可⽤", 
            "role_id": "处理者role"
        }
    ]
}
```

#### 20.出金状态跟踪导出csv
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/fin/withdraw/trace/export' -d ' 
{
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 21.MT账户成交历史记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/dealhistory/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id或为空值）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "sum":[

            {
                "profitraw_sum": "0.0",//净利润总和
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "10000.0",//利润总和
                "commission_sum": "0.0"//外佣总和
            }
        ],
        "list": [
            
            {
                "positionid": "票单号",
                "deal": "成交号",
                "price": "成交价",
                "volume": "交易量",
                "profitraw": "净利润",
                "profit": "利润",
                "priceposition": "开仓价格",
                "storage": "过夜利息",
                "commission": "外佣",
                "time": "时间",
                "action": "类型",
                "entry": "方向",
                "login": "MT账号",
                "symbol": "品种"
            },
            
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,
    "data": null
}
```

#### 22.MT账户交易历史记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/tradehistory/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id或为空值）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "sum":[

            {
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "-112.21",//利润总和
                "c_commission_sum": "0.0",//平仓外佣总和
                "profitraw_sum": "-112.21"//净利润总
            }
        ],
        "list": [
            {
                "positionid": "7566",//飘单号
                "o_deal": "9580",//开仓成交号
                "o_time": "2018-09-17 08:22:36",//开仓时间
                "volumeclosed": "1.00",//平仓量(手数)
                "c_deal": "9588",平仓成交号
                "c_time": "2018-09-17 08:22:53",//平仓成交时间
                "profit": "-20.0",//利润
                "storage": "0.0",//过夜利息
                "symbol": "GBPUSD",//品种
                "c_price": "1.30931",//平仓价格
                "volume": "1.00",//开仓交易量
                "o_commission": "0.0",//开仓外佣
                "c_commission": "0.0",//平仓外佣
                "login": "9005",//MT账号
                "o_action": "1",//开仓交易类型
                "o_price": "1.30911",//开仓价格
                "profitraw": "-20.0"//净利润
            },
            
            
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,
    "data": null
}
```
#### 23.MT账户飘单记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/mt/openposition/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id或为空值）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "sum":[
            {
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "-112.21",//利润总和
                
            }
        ],
        "list": [
            {
                "timecreate":“” , //时间
                "timeupdate": “”,//更新
                "position":“” ,//飘单号
                "login": “”, //MT账号
                "symbol": “”,//品种
                "action": “”,//类型
                "volume": “”,//交易量
                "priceopen": “”,//开仓价
                "pricesl": “”,//止损
                "pricetp": “”,//止盈
                "pricecurrent": “”,//当前价
                "storage": “”,//库存费
                "profit": “”//利利润

            }
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,
    "data": null
}
```

### 外部用户代理商接口
#### 1.搜索客户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/customer/search' -d ' 
{
    "cname":"姓名", //可为空
    "mobile": "手机号", //可为空
    "email":"邮箱", //可为空
    "mtlogin":"MT账户", //可为空
    "page": 1 //页面, 可为空
}'
```
```
# 正常返回
{
    "msg": "提示信息"
    "data": [
        {
            "uid":"用户id",
            "cname":"姓名",
            "mobile": "手机号",
            "email":"邮箱",
            "agent_id":"代理商ID",
            "mtlogin":"MT账户",
            "spread": "内佣加点",
            "commission": "外佣"
        }
    ]
}
```

#### 2.导出客户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/customer/export' -d ' 
{
    "cname":"姓名",
    "mobile": "手机号",
    "email":"邮箱",
    "mtlogin":"MT账户"
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 3.升级客户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/upgrade' -d ' 
{
    "source_uid": "客户ID",
    "cname": "用户名称",
    "points": "新佣金"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 4.修改交易佣金
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/update/brokerage' -d ' 
{
    "source_uid": "客户ID",
    "cname": "用户名称",
    "mtlogin": "MT账号",
    "spread": "内佣加点",
    "commission": "外佣加点"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 5.修改代理返佣
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/update/medium' -d ' 
{
    "source_uid": "客户ID",
    "cname": "用户名称",
    "points": "新佣金"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 6.代理商查看财务操作历史
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/fin/history' -d ' 
{
    "source_uid": "客户ID",
    "mtlogin": "MT账户",
    "opttype": "类型(10=⽹银⼊⾦,11=电汇入金,19=⽹银⼊⾦失败,20=MT出⾦,21=会计出⾦,30=MT内转,31=电⼦钱包内转,50=佣⾦结算N,51=佣⾦结算W,99=MT操作失败)",
    "start": "搜索开始时间",
    "end": "搜索结束时间",
    "page": "分页页码,可为空"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
            "id": "ID", 
            "type": "类型数字", 
            "typename": "类型(10=⽹银⼊⾦,11=电汇入金,19=⽹银⼊⾦失败,20=MT出⾦,21=会计出⾦,30=MT内转,31=电⼦钱包内转,50=佣⾦结算N,51=佣⾦结算W,99=MT操作失败)", 
            "typeename": "english express", 
            "mtlogin": "mt账户",
            "transaction": "交易号", 
            "credit": "借", 
            "comment": "备注",
            "extpay_id": "支付源", 
            "extorder": "第三方单号", 
            "createtime": "创建时间"
        }
    ]
}
```

#### 7.佣金记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/record/brokerage' -d ' 
{
    "agentid": "当前代理商ID",
    "mtlogin": "MT账户",
    "start": "搜索开始时间",
    "end": "搜索结束时间",
    "page": "分页页码,可为空"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
            "deal": "MT已平仓单视图: 成交号", 
            "timestamp": "时间戳", 
            "login": "账户", 
            "order": "订单号",
            "action": "交易类型", 
            "entry": "", 
            "reason": "执行类型", 
            "time": "平仓时间",
            "symbol": "品种", 
            "price": "价格", 
            "volume": "交易量(手数)", 
            "profit": "利润",
            "storage": "过夜利息", 
            "commission": 外佣", 
            "rateprofit": "利润率",
            "positionid": "飘单号", 
            "priceposition": "", 
            "volumeclosed": "平仓量(手数)"
        }
    ]
}
```

#### 8.查看代理网络
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/tree' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {

        }
    ]
}
```
#### 9.代理商——MT账户成交历史记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/dealhistory/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,//正确码
    "data": {
        "sum":[

            {
                "profitraw_sum": "0.0",//净利润总和
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "10000.0",//利润总和
                "commission_sum": "0.0"//外佣总和
            }
        ],
        "list": [
            
            {
                "positionid": "票单号",
                "deal": "成交号",
                "price": "成交价",
                "volume": "交易量",
                "profitraw": "净利润",
                "profit": "利润",
                "priceposition": "开仓价格",
                "storage": "过夜利息",
                "commission": "外佣",
                "time": "时间",
                "action": "类型",
                "entry": "方向",
                "login": "MT账号",
                "symbol": "品种"
            },
            
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,//错误码
    "data": null//空数据
}
```
#### 10.代理商——MT账户交易历史记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/tradehistory/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,//正确码
    "data": {
        "sum":[

            {
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "-112.21",//利润总和
                "c_commission_sum": "0.0",//平仓外佣总和
                "profitraw_sum": "-112.21"//净利润总
            }
        ],
        "list": [
            {
                "positionid": "7566",//飘单号
                "o_deal": "9580",//开仓成交号
                "o_time": "2018-09-17 08:22:36",//开仓时间
                "volumeclosed": "1.00",//平仓量(手数)
                "c_deal": "9588",平仓成交号
                "c_time": "2018-09-17 08:22:53",//平仓成交时间
                "profit": "-20.0",//利润
                "storage": "0.0",//过夜利息
                "symbol": "GBPUSD",//品种
                "c_price": "1.30931",//平仓价格
                "volume": "1.00",//开仓交易量
                "o_commission": "0.0",//开仓外佣
                "c_commission": "0.0",//平仓外佣
                "login": "9005",//MT账号
                "o_action": "1",//开仓交易类型
                "o_price": "1.30911",//开仓价格
                "profitraw": "-20.0"//净利润
            },
            
            
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,//错误码
    "data": null//空数据
}
```
#### 11.代理商——MT账户飘单记录
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/medium/openposition/record' -d ' 
{
    "uid":"42f76b41fe9243908dabf0daa8d169ed",（指定用户id）
    "start":"2018-10-01",  //开始时间 
    "end":"2018-10-15"  //结束时间
    "page":"请求页"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,//正确码
    "data": {
        "sum":[
            {
                "storage_sum": "0.0",//库存量总和
                "profit_sum": "-112.21",//利润总和
                
            }
        ],
        "list": [
            {
                "timecreate":“” , //时间
                "timeupdate": “”,//更新
                "position":“” ,//飘单号
                "login": “”, //MT账号
                "symbol": “”,//品种
                "action": “”,//类型
                "volume": “”,//交易量
                "priceopen": “”,//开仓价
                "pricesl": “”,//止损
                "pricetp": “”,//止盈
                "pricecurrent": “”,//当前价
                "storage": “”,//库存费
                "profit": “”//利利润

            }
        ],
        "page": "当前页",，
        "pages": “总页数“，
        "total":“总条数”
    }
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,//错误码
    "data": null//空数据
}
```



### 内部用户管理员接口
#### 1.新建内部用户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/inner/user/add' -d ' 
{
    "cname":"叉叉",
    "email":"xxx5@xxx.com",
    "role_ids": [
        "d793459dccde424e8d98c1a61a8eeb91"
    ],
    "password":"12345678",
    "password_confirm":"12345678"
}'
```
```
# 正常返回
{
    "msg": "create success",
    "code": 200,
    "data": {
        "cname": "姓名", 
        "firstname": "姓", 
        "lastname": "名", 
        "mobile": "手机号",
        "email": "邮箱",
        "certid": "身份证号码",
        "bank": "银行卡开户行",
        "bankbranch": "支行名称",
        "swiftcode": "SWIFT CODE",
        "agent_id": "代理编码",
        "statusa":"正常",
        "rolenames": "角色名称,角色名称",
        "roleids": "角色id,角色id",
        "mt":[
            {
                "mtlogin": "交易账户",
                "mtpasswd":"交易密码",
                "balance":"交易密码"
            }
        ]
    }
}
```

#### 2.搜索内部用户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/inner/user/search' -d ' 
{
    "cname":"姓名", // 可为空
    "role_ids": [
        "d793459dccde424e8d98c1a61a8eeb91"
    ], // 可为空
    "page": 1 // 可为空, 页码
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "page": 1, //页码
        "total": 60, //总记录数
        "pages": 3, //总页码数
        "list": [
             "uid": "用户id", 
             "email": "用户邮箱", 
             "mobile": "用户手机号", 
             "cname": "用户姓名",
             "roles": [
                {
                    "role_id": "角色id", 
                    "role_name": "角色名称"
                }
             ], 
             "rolenames": "角色名称,角色名称",
             "roleids": "角色id,角色id",
             "gid": "用户分组", 
             "createtime": "创建时间"
        ]
    }
}
```

#### 3.修改内部用户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/inner/user/update' -d ' 
{
    "uid": "xxxxx",
    "cname":"姓名",
    "email":"邮箱",
    "role_ids": [
        "d793459dccde424e8d98c1a61a8eeb91"
    ],
    "password":"密码", // 可为空
    "password_confirm":"确认密码" // 可为空
}'
```
```
# 正常返回
{
    "msg": "create success",
    "code": 200,
    "data": {
        "cname": "姓名", 
        "firstname": "姓", 
        "lastname": "名", 
        "mobile": "手机号",
        "email": "邮箱",
        "certid": "身份证号码",
        "bank": "银行卡开户行",
        "bankbranch": "支行名称",
        "swiftcode": "SWIFT CODE",
        "agent_id": "代理编码",
        "statusa":"",
        "mt":[
            {
                "mtlogin": "交易账户",
                "mtpasswd":"交易密码",
                "balance":"交易密码"
            }
        ]
    }
}
```

#### 4.删除内部用户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/inner/user/del' -d ' 
{
    "uid": "xxxxx"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": null
}
```

#### 5.导出内部用户
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/inner/user/export' -d ' 
{
    "cname":"姓名", // 可为空
    "role_ids": [
        "d793459dccde424e8d98c1a61a8eeb91"
    ] // 可为空
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg":"export csv file fail"
    "code": 900,
    "data": null
}
```

#### 6.权限列表
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/access/list' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
            "id": "权限ID", 
            "name": "权限名称", 
            "url": "链接", 
            "element": "元素",       
            // 三位字符串串,每位取值为1/0,1表示yes,0表示no 
            // 三位表示,对于url:         [get] [post] [⽆无效]  
            // 三位表示,对于element:     [可显示] [可输⼊入/选择] [submit]
            // 例:101 - 表示⼀一个按钮可见并且可以点击;110表示⼀一个checkbox可见并且可以选择
            "type": "110", 
            "description": "备注", 
            "createtime": "创建时间"
        }    
    ]
}
```

#### 7.角色列表
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/role/search' -d ' 
{
    "role_name": "角色名称", // 可为空
    "page": 1 //页码 // 可为空
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "page": 1, //页码
        "total": 60, //总记录数
        "pages": 3, //总页码数
        "list": [
              {
                    "access": [
                        "153eb542a3a1472f8510b56c917d5f87",
                        "3a6e15ed5b8e4cedb8e944badb42d9ca"
                    ],
                    "accessnames": "我的网络,修改客户账号分组按钮",
                    "builtin": true, // 系统角色(缺省值为false,该值为true的记录,在管理员页面不可编辑)
                    "name": "测试", //角色名称
                    "accesss": [
                        {
                            "access_name": "我的网络",
                            "access_id": "153eb542a3a1472f8510b56c917d5f87"
                        },
                        {
                            "access_name": "修改客户账号分组按钮",
                            "access_id": "3a6e15ed5b8e4cedb8e944badb42d9ca"
                        }
                    ],
                    "description": "这是一个测试角色", //说明
                    "createtime": "2018-08-29 09:47:09", //创建时间
                    "id": "b8482057588e49e2a9619c46e928e3c3",//ID
                    "accessids": "153eb542a3a1472f8510b56c917d5f87,3a6e15ed5b8e4cedb8e944badb42d9ca"
              }
        ]
    }
}
```

#### 8.添加角色
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/role/add' -d ' 
{
    "role_name": "角色名称",
    "access_list": [
        "", "", ""
    ], // 权限ID列表
    "description": "说明"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
         "id": "角色id", 
         "name": "角色名称", 
         "access": ["", "", ""], // 权限ID列表
         "builtin": True, // 系统角色(缺省值为false,该值为true的记录,在管理员页面不可编辑)
         "description": "角色说明", 
         "createtime": "创建时间"
    }
}
```

#### 9.修改角色
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/role/update' -d ' 
{
    "role_id": "角色ID",
    "role_name": "角色名称",
    "access_list": [
        "", "", ""
    ], // 权限ID列表
    "description": "说明"
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
```

#### 10.删除角色
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/role/del' -d ' 
{
    "role_id": "角色ID"
}'
```
```
# 正常返回
{
    "msg": "delete success",
    "code": 200,
    "data": null
}
```

#### 11.导出角色
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/role/export' -d ' 
{
    "role_name": "角色名称" // 可为空
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 12. 查询MT分组类型
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/type' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
         "type": "ID",
         "name": "分组名"
         "ename": "分组英文名"
    }
}
```

#### 13.添加MT分组
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/add' -d ' 
{
    "name": "组名",
    "mtname": "MT名",
    "type":"类型(1:标准组,2:专业组,3:VIP组,0:特殊组)", // 请输入数字
    "leverage": "杠杆率",
    "spread": "内佣加点",
    "commission": "外佣加点",
    "maxbalance": "资金上限",
    "type": "type 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)"
}'
```
```
# 正常返回
{
    "msg": "create success",
    "code": 200,
    "data": {
         "name": "组名",
         "mtname": "MT名",
         "leverage": "杠杆率",
         "spread": "内佣加点",
         "commission": "外佣加点",
         "maxbalance": "资金上限",
         "type": "type 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)",
         "createtime": "创建时间"
    }
}
```

#### 14.查询MT分组
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/search' -d ' 
{
    "name": "组名", // 可为空
    "page" 1 // 可为空 分页页码
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "page": 1, //页码
        "total": 60, //总记录数
        "pages": 3, //总页码数
        "list": [
            {
                 "name": "组名",
                 "ename": "英文组名",
                 "mtname": "MT分组名称",
                 "leverage": "杠杆率",
                 "spread": "内佣加点",
                 "commission": "外佣加点",
                 "maxbalance": "资金上限",
                 "type": "type 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)",
                 "typename": "type 类型名称(1:标准组,2:专业组,3:VIP组,0:特殊组)",
                 "createtime": "创建时间"
            }
        ]
    }
}
```

#### 15.更新MT分组
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/update' -d ' 
{
    "name": "组名",
    "mtname": "MT名",
    "leverage": "杠杆率",
    "spread": "内佣加点",
    "commission": "外佣加点"
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
```

#### 16.删除MT分组
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/del' -d ' 
{
    "name": "组名"
}'
```
```
# 正常返回
{
    "msg": "delete success",
    "code": 200,
    "data": {
         
    }
}
```

#### 17.导出MT分组
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/mtgroup/export' -d ' 
{
    "name": "组名" // 可为空
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 18.查询工作流类型
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/type' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
             "type": "Task类表: id", 
             "name": "类型名称"
        }
    ]
}
```

#### 19.查询工作流
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/search' -d ' 
{
    "type": "Task类表: id", // 可为空
    "subject": "标题", // 可为空
    "page": 1 // 可为空 页码
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "page": 1, //页码
        "total": 60, //总记录数
        "pages": 3, //总页码数
        "list": [
            {
                 "type": "Task类表: id", 
                 "name": "类型名称", 
                 "trigger": "发起者URL", 
                 "success": "成功触发",
                 "fail": "失败触发", 
                 "subject": "标题", 
                 "body": "内容文本",
                 "createtime": "创建时间"
            }
        ]
    }
}
```

#### 20.更新工作流
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/update' -d ' 
{
    "type": "Task类表: id",
    "name": "类型名称",
    "subject": "标题",
    "body": "内容文本"
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
```

#### 21.删除工作流
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/del' -d ' 
{
    "type": "Task类表: id"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
         
    }
}
```

#### 22.导出工作流
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/export' -d ' 
{
    "type": "Task类表: id", // 可为空
    "subject": "标题" // 可为空
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 23.添加工作流节点
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/node/add' -d ' 
{
    "previous":"上一个节点ID",
    "name":"节点名称",
    "t_type":"所属Task类id",
    "approve":"approve命名",
    "step":"节点阶段",
    "canapprove":"approve可用",
    "canreturn":"return可用",
    "canreject":"reject可用",
    "returned":"被return命名",
    "role_id":"处理者role"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": {
        "id":"Task节点表: id",
        "previous":"上一个节点ID",
        "name":"节点名称",
        "t_type":"所属Task类id",
        "approve":"approve命名",
        "step":"节点阶段",
        "canapprove":"approve可用",
        "canreturn":"return可用",
        "canreject":"reject可用",
        "returned":"被return命名",
        "role_id":"处理者role",
        "createtime":"创建时间"
    }
}
```

#### 24.查询工作流节点
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/node/search' -d ' 
{
    "type": "Task类表: id"
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
         {
            "id":"Task节点表: id",
            "previous":"上一个节点ID",
            "name":"节点名称",
            "t_type":"所属Task类id",
            "approve":"approve命名",
            "step":"节点阶段",
            "canapprove":"approve可用",
            "canreturn":"return可用",
            "canreject":"reject可用",
            "returned":"被return命名",
            "role_id":"处理者role",
            "createtime":"创建时间"
         }
    ]
}
```

#### 25.更新工作流节点
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/node/update' -d ' 
{
    "id":"Task节点表: id",
    "name":"节点名称",
    "t_type":"所属Task类id",
    "approve":"approve命名",
    "canapprove":"approve可用",
    "canreturn":"return可用",
    "canreject":"reject可用",
    "returned":"被return命名",
    "role_id":"处理者role"
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
```

#### 26.删除工作流节点
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/node/del' -d ' 
{
    "id":"Task节点表: id"
}'
```
```
# 正常返回
{
    "msg": "delete success",
    "code": 200,
    "data": null
}
```

#### 27.导出工作流节点
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/node/export' -d ' 
{
    
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 28.管理员用的搜索所有已完成未完成任务的接口
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/workflow/task' -d ' 
{
    "page": 2 //可为空
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
         {
            
         }
    ]
}
```

#### 28.系统参数配置项查询
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/sysconf/view' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "",
    "code": 200,
    "data": [
        {
            "name": "配置项名称", 
            "value": "配置项值", 
            "comment": "配置项说明"
        }    
    ]
}
```

#### 29.系统参数配置项添加
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/sysconf/add' -d ' 
{
    "name": "配置项名称", 
    "value": "配置项值", 
    "comment": "配置项说明"
}'
```
```
# 正常返回
{
    "msg": "create success",
    "code": 200,
    "data": {
         "name": "配置项名称", 
         "value": "配置项值", 
         "comment": "配置项说明"
    }
}
# 错误返回
{
    "msg": "参数项已经存在|请输入参数项名称|请输入参数值",
    "code": 900,
    "data": null
}
```

#### 30.系统参数配置项更新
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/sysconf/update' -d ' 
{
    "name": "配置项名称", 
    "value": "配置项值", 
    "comment": "配置项说明"
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "参数项不存在|请输入参数项名称|请输入参数值",
    "code": 900,
    "data": null
}
```
#### 31.待处理的任务
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/task/search/unfinish' -d ' 
{
    "task_type": "任务类型", 
    "o_cname": "发起人姓名", 
    "page": "请求页"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,
    "data": null
}
```
#### 32.已完成的任务
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/ma/task/search/finish' -d ' 
{
    "task_type": "任务类型", 
    "o_cname": "发起人姓名", 
    "page": "请求页"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "提示信息",
    "code": 900,
    "data": null
}
```
### 内部客服部门接口
#### 1.任务类型查询
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/name' -d ' 
{

}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "task_type": "任务类型"
        }
    ]
}
```

#### 2.任务查询: 待处理的任务
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/search' -d ' 
{
    "task_type":"任务类型", //可为空
    "o_cname":"发起人姓名", //可为空
    "page":"分页页码" //可为空
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "id": "Task表: 任务id", 
            "subject": "任务标题", 
            "taskname": "任务名称", 
            "body": "任务内容⽂本", 
            "o_uid": "发起⼈", 
            "o_cname": "发起⼈姓名", 
            "source_uid": "源⽤户", 
            "source_cname": "源⽤户姓名", 
            "target_uid": "⽬的⽤户", 
            "target_cname": "目的用户姓名", 
            "sourcemt": "源MT账户", 
            "targetmt": "⽬的MT账户", 
            "mtgroup": "MT分组", 
            "amount": "⾦额", 
            "exchange": "汇率", 
            "points": "点数", 
            "state": "状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)", 
            "tasknode_id": "当前节点id", 
            "createtime": "任务创建时间", 
            "updatetime": "上次修改时间", 
            "nodename": "当前节点名称", 
            "step": "当前节点阶段", 
            "approve": "approve命名", 
            "returned": "被return命名", 
            "canapprove": "approve可⽤", 
            "canreturn": "return可⽤", 
            "canreject": "reject可⽤", 
            "role_id": "处理者role"
        }
    ]
}
```

#### 3.任务查询: 我发起的任务
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/search/my' -d ' 
{
    "task_type":"任务类型", //可为空
    "state":"任务状态", //可为空
    "page":"分页页码" //可为空
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "id": "Task表: 任务id", 
            "subject": "任务标题", 
            "taskname": "任务名称", 
            "body": "任务内容⽂本", 
            "o_uid": "发起⼈", 
            "o_cname": "发起⼈姓名", 
            "source_uid": "源⽤户", 
            "source_cname": "源⽤户姓名", 
            "target_uid": "⽬的⽤户", 
            "target_cname": "目的用户姓名", 
            "sourcemt": "源MT账户", 
            "targetmt": "⽬的MT账户", 
            "mtgroup": "MT分组", 
            "amount": "⾦额", 
            "exchange": "汇率", 
            "points": "点数", 
            "state": "状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)", 
            "tasknode_id": "当前节点id", 
            "createtime": "任务创建时间", 
            "updatetime": "上次修改时间", 
            "nodename": "当前节点名称", 
            "step": "当前节点阶段", 
            "approve": "approve命名", 
            "returned": "被return命名", 
            "canapprove": "approve可⽤", 
            "canreturn": "return可⽤", 
            "canreject": "reject可⽤", 
            "role_id": "处理者role"
        }
    ]
}
```

#### 4.任务历史
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/history' -d ' 
{
    "taskitem_id": "当前任务id"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "id": "历史id", 
            "taskitem_id": "任务id", 
            "oprator": "操作者", 
            "change": "状态改变 state:{"new", "approve", "returned", "reject"}",
            "tasknode_id": "节点", 
            "comment": "注释",
            "createtime": "创建时间"
        }
    ]
}
```

#### 5.任务修改
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/update' -d ' 
{
    "taskitem_id":122, //任务ID
    "state":"approve", // approve, returned, reject
    "comments":122 //任务注释
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
# 错误返回
{
    "msg": "任务不存在|请输入任务ID|请输入任务状态|请输入任务注释|出金失败|操作失败",
    "code": 900,
    "data": null
}
```

#### 6.任务查看
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/view' -d ' 
{
    "taskitem_id":122 //任务ID
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
         "id": "Task表: 任务id", 
         "subject": "任务标题", 
         "taskname": "任务名称", 
         "body": "任务内容⽂本", 
         "o_uid": "发起⼈", 
         "o_cname": "发起⼈姓名", 
         "source_uid": "源⽤户", 
         "source_cname": "源⽤户姓名", 
         "target_uid": "⽬的⽤户", 
         "target_cname": "目的用户姓名", 
         "sourcemt": "源MT账户", 
         "targetmt": "⽬的MT账户", 
         "mtgroup": "MT分组", 
         "amount": "⾦额", 
         "exchange": "汇率", 
         "points": "点数", 
         "state": "状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)", 
         "tasknode_id": "当前节点id", 
         "createtime": "任务创建时间", 
         "updatetime": "上次修改时间", 
         "nodename": "当前节点名称", 
         "step": "当前节点阶段", 
         "approve": "approve命名", 
         "returned": "被return命名", 
         "canapprove": "approve可⽤", 
         "canreturn": "return可⽤", 
         "canreject": "reject可⽤", 
         "role_id": "处理者role"
    }
}
```

#### 7.导出任务
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/task/export' -d ' 
{
    "task_type":12, //类型
    "o_uid":12, //发起人
    "state":12 //状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 8.消息类型查询
```bash
curl -XGET -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/msg/type' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "msgtype": "类型", 
            "name": "类型名称", 
            "trigger": "发起者URL", 
            "role_id": "接收者role",
            "subject": "标题", 
            "body": "内容文本", 
            "createtime": "创建时间",
            "updatetime": "更新时间"
        }
    ]
}
```

#### 9.个人消息查询
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/msg/search' -d ' 
{
    "msgtype": "xxxx", //类型
    "o_uid": "xxxx", //发起人ID
    "page": 2 // 分页页码,可为空
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "id": "id", 
            "name": "类型名称", 
            "subject": "标题", 
            "body": "内容文本",
            "m_type": "类型", 
            "o_uid": "发起人", 
            "source_uid": "源用户",
            "target_id": "目的用户", 
            "sourcemt": "源MT账户", 
            "targetmt": "目的MT账户",
            "amount": "金额", 
            "points": "点数", 
            "createtime": "创建时间"
        }
    ]
}
```

#### 10.个人消息查看
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/msg/view' -d ' 
{
    "msgitem_id": "消息id"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
        "id": "id", 
        "name": "类型名称", 
        "subject": "标题", 
        "body": "内容文本",
        "m_type": "类型", 
        "o_uid": "发起人", 
        "source_uid": "源用户",
        "target_id": "目的用户", 
        "sourcemt": "源MT账户", 
        "targetmt": "目的MT账户",
        "amount": "金额", 
        "points": "点数", 
        "createtime": "创建时间"
    }
}
```

#### 11.导出消息
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/msg/export' -d ' 
{
    "msgtype": "xxxx", //类型,可为空
    "o_uid": "xxxx" //发起人ID,可为空
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 12.搜索客户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/customer/search' -d ' 
{
    "cname": "", // 中文姓名(界面上姓名)
    "mobile": "", // 手机号
    "email": "", // 电子邮箱
    "certid": "", // 证件号
    "bankaccount": "", // 银行账户
    "mtlogin": "", // MT账户
    "agent_id": "", // 上级代理ID
    "page": "" // 分页页码
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "uid": "用户ID", 
            "cname": "用户名", 
            "mobile": "用户手机号", 
            "email": "用户邮箱", 
            "certid": "用户身份证",
            "bankaccount": "用户银行卡",
            "mtlogin": "MT账户", 
            "statusa": "用户状态A", 
            "agentid": "用户代理商编码",
            "parentid": "上级代理",
            "a_level": "用户代理层级",
            "a_status": "用户代理商状态",
            "a_createtime": "用户代理创建时间",
            "createtime": "用户创建时间"
        }    
    ]
}
```

#### 13.导出客户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/customer/export' -d ' 
{
    "cname": "", // 中文姓名(界面上姓名)
    "mobile": "", // 手机号
    "email": "", // 电子邮箱
    "certid": "", // 证件号
    "bankaccount": "", // 银行账户
    "mtlogin": "", // MT账户
    "agent_id": "", // 上级代理ID
    "page": "" // 分页页码
}'
```
```
# 正常返回
csv下载流
# 错误返回
{
    "msg": "export csv file fail",
    "code": 900,
    "data": null
}
```

#### 14.查看客户基本信息
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/customer/view' -d ' 
{
    "uid":"用户id"
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
         "cname": "中文姓名(界面上姓名)", 
         "firstname": "英文名", 
         "lastname": "英文姓",
         "mobile": "手机号", 
         "email": "电子邮箱", 
         "certid": "证件号", 
         "bank": "开户行",
         "bankbranch": "支行名称", 
         "swiftcode": "SWIFT CODE", 
         "agent_id": "上级代理ID",
         "statusa": "用户状态A(界面显示的用户状态: 正常,交易冻结,出金冻结,入金冻结,警告,封禁,删除,审核中)ID", 
         "certpic0": "证件图片0", 
         "certpic1": "证件图片1", 
         "bankpic0": "银行卡图片0",
         "certpic0_url": "证件图片0_url", 
         "certpic1_url": "证件图片1_url", 
         "bankpic0_url": "银行卡图片0_url",
         "mt": [
            "mt1", "mt2"
         ]
    }
}
```

#### 15.修改客户基本信息
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/customer/update' -d ' 
{
    "uid":"用户id",
    “cname”：“中文名”
    "firstname": "英文名", 
    "lastname": "英文姓",
    "certid": "证件号", 
    "bank": "开户行",
    "bankbranch": "支行名称", 
    "swiftcode": "SWIFT CODE", 
    "statusa": "用户状态A(界面显示的用户状态: 正常,交易冻结,出金冻结,入金冻结,警告,封禁,删除,审核中)ID", 
    "email":"邮箱",
    "mobile":"手机号",
    "certpic0": "证件图片0", 
    "certpic1": "证件图片1", 
    "bankpic0": "银行卡图片0"
    “country：“国家”，
    “state”：“州”，
    “adress”：“地址”，
    “addrpic0：“地址图片”，
   
}'
```
```
# 正常返回
{
    "msg": "update success",
    "code": 200,
    "data": null
}
```

#### 16.新建交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mt/create' -d ' 
{
    "uid": "",// 用户id
    "type": "",// 类型
    "leverage": ""// 交易比例杠杆
}'
```
```
# 正常返回
{
    "msg": "mt add success",
    "code": 200,
    "data": {
         "mt":[
            {
                "mtlogin": "mt账户", 
                "mtpasswd": "mt密码", 
                "balance": 0 //余额
            }
         ]
    }
}
```

#### 17.修改交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mt/update' -d ' 
{
    "uid": "",// 用户id
    "mtlogin": "mt账户",
    "leverage": ""// 交易比例杠杆
}'
```
```
# 正常返回
{
    "msg": "success",
    "code": 200,
    "data": null
}
```


#### 18.审批新建交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mt/create/approval' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
         
    }
}
```

#### 19.审批修改交易账户
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mt/update/approval' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {
        
    }
}
```

#### 20.MT分组查询接口
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mtgroup/search' -d ' 
{
    "mtlogin": "MT账户", // 
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "mtgroup": "MT分组", 
            "groupname": "MT分组名称"
        }
    ]
}
```

#### 21.MT全部分组名称接口
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/mtgroup/all' -d ' 
{
    
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": [
        {
            "name": "MT分组表:组名", 
            "mtname": "MT名"
        }
    ]
}
```

#### 22.客户资金变动历史接口
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/fin/history' -d ' 
{
    “mtlogin”：“MT账号”，
    “opttype”：“操作类型”，
    “start”：“开始时间”，
    “end”：“结束时间”，
    “page”：“请求页”，
    “uid”：“用户id”
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {}
    
}
```

#### 23.电子钱包余额接口
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/cs/fin/balance/ewallet' -d ' 
{
    “uid”：“用户id”
}'
```
```
# 正常返回
{
    "msg": "提示信息",
    "code": 200,
    "data": {}
}

# 错误返回
{
    "msg": "用户错误",
    "code": 900,
    "data": null
}
```

### 内部代理部门接口
#### 1.创建代理商(任务流)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/md/agents/create' -d ' 
{
    "uid": "用户ID", // 
    "reward": "代理返佣"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 2.修改代理商(任务流)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/md/agents/update' -d ' 
{
    "uid": "用户ID", // 
    "reward": "代理返佣",
    "agent_status": "代理商状态",
    "parent_uid": "上级代理用户ID"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 3.修改交易账户分组(任务流)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/md/mtgroup/update' -d ' 
{
    "uid": "用户ID", // 
    "mtlogin": "MT账号", //
    "mtgroup": "MT分组"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 4.修改客户代理(任务流)
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/md/agents/customer/update' -d ' 
{
    "uid": "用户ID", // 
    "mtlogin": "MT账号", //
    "agent_uid": "代理商用户ID"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": null
}
```

#### 5.代理商搜索
```bash
curl -XPOST -H "Accept: application/json" -H "Content-type: application/json" 'http://127.0.0.1:8080/md/agents/search' -d ' 
{
    "keyword": "搜索关键词"
}'
```
```
# 正常返回
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {
            "agent_uid": "用户ID", 
            "agent_cname": "用户名称", 
            "agentid": "代理商ID"
        }
    ]
}
```