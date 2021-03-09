# XWCRM

#### 需求
```
# 20181203需求
新建代理商和代理商提升名下客户，都加入了role[1]的修改
t_access有字段的变化

# 20181114需求
新建交易账户流程图更新
分组的取得方法 mtgroup = select mtgroup from v_mtuser where uid = 客户uid
新建MT账号那里，增加一个用户状态检查，当statusa=‘集群’，账号上限为100(x)
提交身份证信息的时候检查count <=3 提示错误“该证件绑定次数过多” 身份证号上限的值放入t_config(x)

# 20180127需求
config配置添加
信用卡支付对接
PostgreSQL连接池优化
```

#### config配置
```
name                value                             comment

mail_contentFile    templates/welcomemail.html
mail_domain         smtp.honghaigy.com
mail_from           info@fxenon.com
mail_password       goodluck00info
mail_port           25

mt_login            3000                              333
mt_password         Ilove125ED+
mtserver_ip         36.102.229.227                    111
mtserver_port       1997                              222
mt_timeout          5
MT默认组            bonus\std\100L\0r0c                用户注册时所创建的MT账户所在的默认组

OCR_apikey          8c1457fdefcc13735bad5cf2999e8e11
OCR_appid           5b67daca
OCR_base            http://webapi.xfyun.cn/v1/service/v1/ocr/

sms_AccessKeyId     LTAI9hAkoKsfr2hW
sms_AccessKeySecret dsq52jlCRqM1Uv44wPb8Vhqk9m01Cx
sms_DOMAIN          dysmsapi.aliyuncs.com
sms_PRODUCT_NAME    Dysmsapi
sms_REGION          cn-hangzhou
sms_sign_name       博纳斯
sms_template_modify SMS_138685008
sms_template_notice SMS_142152736
sms_template_register SMS_138685010

代理链接地址         https://xwcrm.bonusfx.cn/register?link= 代理链接前置地址部分
汇率系数             1.012
认证用户状态         正常
网银入金上限         10000
网银入金下限         1000
证件OCR             yes                               是否启用身份证和银行卡OCR识别
证件上限             3                                身份证件号码允许提交的最多次数
注册用户状态         出金冻结
```

#### ocr
```
http://ip.taobao.com/service/getIpInfo.php?ip=myip
讯飞账户=5zVm43XytFgL8Vn
APPID=5b67daca
APIKey=8c1457fdefcc13735bad5cf2999e8e11

https://doc.xfyun.cn/rest_api/%E9%93%B6%E8%A1%8C%E5%8D%A1%E8%AF%86%E5%88%AB.html
https://doc.xfyun.cn/rest_api/%E8%BA%AB%E4%BB%BD%E8%AF%81%E8%AF%86%E5%88%AB.html
https://www.xfyun.cn/services/idCardRecg
https://www.xfyun.cn/services/bankCardRecg
```

#### 工作流定义
```
TaskSuccess
/fin/deposit                 FinDeposit - 电汇入金
/fin/withdraw/mt             MTWithdraw - MT出金
/fin/withdraw                FinWithdraw - 会计出金
/md/agents/create            AgentsCreate - 新建代理商  
/md/agents/update            AgentsUpdate - 修改代理商   
/md/agents/customer/update   AgentsCustomerUpdate - 修改客户代理
/md/mtgroup/update           MTGroupUpdate - 修改交易账户分组
/medium/upgrade              UpgradeCustomer - 代理商升级名下客户

TaskFail 
    MTWithdraw - MT出金
    FinWithdraw - 会计出金
    AgentsCreate - 新建代理商
    AgentsCustomerUpdate - 修改客户代理
    UpgradeCustomer - 代理商升级名下客户
    AgentsUpdate - 修改代理商
    MTGroupUpdate - 修改交易账户分组
    FinDeposit - 电汇入金
```

#### aliyun_sms
```
https://m.aliyun.com/doc/document_detail/55491.html
AccessKeyId=LTAI9hAkoKsfr2hW
AccessKeySecret=dsq52jlCRqM1Uv44wPb8Vhqk9m01Cx
sms_sign_name=博纳斯
sms_template_name=用户注册验证码
sms_template_code=SMS_138685010
sms_template_content=验证码${code},您正在注册成为新用户,感谢您的支持!

模版类型:短信通知
模版名称:新用户欢迎短信
模版CODE:SMS_142152736
模版内容:欢迎${cname}注册为博纳斯用户！您的MT账号已经开通，账号为：${mtlogin}，密码为${mtpasswdd}
申请说明:博纳斯新用户的账号密码提示短信

模版类型:修改手机号的验证码
模版名称:信息变更验证码
模版CODE:SMS_138685008
模版内容:验证码${code}，您正在尝试变更重要信息，请妥善保管账户信息
```
#### 优先级

* 出金入金用户注册
* 代理商的那些功能完善
* 发短信阿里接口对接
* MT交互对接

### build
```
pip install -r requirements.txt
pip freeze >requirements.txt
```

#### install
http://python.jobbole.com/87305/
* 安装redis-py
```
pip install redis
检查是否安装成功
>>>import redis
```

#### 验证码使用cookies存储


#### 测试环境
```
https://xwcrm.bonusfx.cn/?bm

18604093690
qwer1234
```
```
source ~/xwtest/bin/activate
```
```
# 直客UI界面
http://www.honghaigy.com:8087

# 管理员UI界面
http://www.honghaigy.com:8087/?bm
```
```
db_params = {
    "database": "metatrader5",
    "user": "xwtest",
    "password": "xwtest00",
    "host": "127.0.0.1",
    "port": 5432
}
```
```
source ~/xwtest/bin/activate
cd xwtest/src/XWCRM/xwcrm/
git checkout dev
~/xwtest/bin/python run.py &

psql -U xwtest -d metatrader5 -h 127.0.0.1 -p 5432
xwtest00

UPDATE t_user set role_id = '{d793459dccde424e8d98c1a61a8eeb91}' WHERE uid = '84f1addde43748d6a1215acedadac1b7';

UPDATE t_user set mobile = '18912182563' WHERE uid = 'beb4bc7a9048497cafc0be5ade95f2bd';
```

#### 视图
```
CREATE OR REPLACE VIEW v_mtgroup AS
 SELECT mt5_groups."Group" AS mtname,
    mt5_groups."DemoLeverage" AS leverage
   FROM mt5_groups
  WHERE "position"(mt5_groups."Group"::text, 'bonus'::text) = 1;


CREATE OR REPLACE VIEW v_dealclosed AS
 SELECT dcd."Deal" AS deal,
    dcd."Timestamp" AS "timestamp",
    dcd."Login" AS login,
    dcd."Order" AS "order",
    dcd."Action" AS action,
    dcd."Entry" AS entry,
    dcd."Reason" AS reason,
    dcd."Time" AS "time",
    dcd."Symbol" AS symbol,
    dcd."Price" AS price,
    dcd."Volume" AS volume,
    dcd."Profit" AS profit,
    dcd."Storage" AS storage,
    dcd."Commission" AS commission,
    dcd."RateProfit" AS rateprofit,
    dcd."PositionID" AS positionid,
    dcd."PricePosition" AS priceposition,
    dcd."VolumeClosed" AS volumeclosed
   FROM mt5_deals dcd
  WHERE (dcd."Action" = 0::numeric OR dcd."Action" = 1::numeric) AND NOT (dcd."Timestamp" IN ( SELECT t2.ts
           FROM ( SELECT t1."PositionID" AS pos,
                    min(t1."Timestamp") AS ts
                   FROM mt5_deals t1
                  GROUP BY t1."PositionID") t2));

CREATE OR REPLACE VIEW v_mtuser AS
 SELECT t_user.uid,
    mt5_accounts."Login" AS mtlogin,
    mt5_users."Group" AS mtgroup,
    mt5_users."Leverage" AS leverage,
    mt5_accounts."Balance" AS balance,
    mt5_accounts."MarginLevel" AS marginlevel,
    mt5_accounts."Equity" AS equity
   FROM mt5_accounts,
    mt5_users,
    t_user
  WHERE (mt5_accounts."Login"::text = ANY (t_user.mtlogin::text[])) AND mt5_users."Login" = mt5_accounts."Login";
```

#### 菜单
直客
```
[
  {
    "title": "我的概况",
    "children": [
      {
        "title": "我的首页",
        "link": "/usermain",
        "target": "_self"
      },
      {
        "title": "我的信息",
        "link": "/customerinfo",
        "target": "_self"
      },
      {
        "title": "身份验证",
        "link": "/customerupdate",
        "target": "_self"
      },
      {
        "title": "修改密码",
        "link": "/updatepassword",
        "target": "_self"
      },
      {
        "title": "退出系统",
        "link": "quit",
        "target": "_self"
      }
    ]
  },
  {
    "title": "财务",
    "children": [
      {
        "title": "入金存款",
        "link": "/deposit",
        "target": "_self"
      },
      {
        "title": "出金取款",
        "link": "/withdrawmoney",
        "target": "_self"
      },
      {
        "title": "账号之间转账",
        "link": "/accounttransfer",
        "target": "_self"
      },
      {
        "title": "出入金记录",
        "link": "/historymoney",
        "target": "_self"
      },
      {
        "title":"出金状态跟踪",
        "link":"/depositfollowing",
        "target":"_self"
      }
    ]
  },
  {
    "title": "账户管理",
    "children": [
      {
        "title": "交易账户",
        "link": "/accountlist",
        "target": "_self"
      },
      {
        "title": "我的客户",
        "link": "/searchagent",
        "target": "_self"
      },
      {
        "title": "我的网络",
        "link": "/network",
        "target": "_self"
      }
    ]
  },
  {
    "title": "信息",
    "children": [
      {
        "title": "MT5下载",
        "link": "#",
        "target": "_blank"
      }
    ]
  }
]
```

管理
```
[
  {
    "title": "客服部门",
    "children": [
      {
        "title": "任务",
        "link": "/dashboard",
        "target": "_self"
      },
      {
        "title": "消息",
        "link": "/message",
        "target": "_self"
      },
      {
        "title": "查找客户",
        "link": "/searchcustomer?service",
        "target": "_self"
      },
      {
        "title": "修改密码",
        "link": "/updatepasswordbm",
        "target": "_self"
      },
      {
        "title": "退出系统",
        "link": "quit",
        "target": "_self"
      }
    ]
  },
  {
    "title": "代理部门",
    "children": [
      {
        "title": "任务",
        "link": "/dashboard",
        "target": "_self"
      },
      {
        "title": "消息",
        "link": "/message",
        "target": "_self"
      },
      {
        "title": "查找客户",
        "link": "/searchcustomer?agent",
        "target": "_self"
      },
      {
        "title": "修改密码",
        "link": "/updatepasswordbm",
        "target": "_self"
      },
      {
        "title": "退出系统",
        "link": "quit",
        "target": "_self"
      }
    ]
  },
  {
    "title": "系统管理员",
    "children": [
      {
        "title": "用户管理",
        "link": "/internaluserlist",
        "target": "_self"
      },
      {
        "title": "角色管理",
        "link": "/roleinfolist",
        "target": "_self"
      },
      {
        "title": "工作流管理",
        "link": "/workflowlist",
        "target": "_self"
      },
      {
        "title": "分组管理",
        "link": "/mtgroup",
        "target": "_self"
      },
      {
        "title": "系统参数管理",
        "link": "/sysparameter",
        "target": "_self"
      },
      {
        "title": "修改密码",
        "link": "/updatepasswordbm",
        "target": "_self"
      },
      {
        "title": "退出系统",
        "link": "quit",
        "target": "_self"
      }
    ]
  }
]
```