#!/usr/bin/env python
# -*- coding:utf-8 -*-


import psycopg2
from datetime import *


def doInsert(dbconn, agentid, fundtype, mtlogin, credit, extorder):
    if credit == 0.0:
        print("[ERROR] Zero credit in deal: " + extorder)
        return(1)
    # 通过agentid获取代理商uid和状态
    query1 = "SELECT uid, status FROM t_agent WHERE agentid='" + agentid + "'"
    cur1 = dbconn.cursor()
    cur1.execute(query1)
    uid, status = cur1.fetchone()
    if status != '正常':
        print("[STATUS] uid: " + uid + " is not in normal status. Credit is skipped.")
        return 0
    # 排除交易号重复的相同佣金类型记录
    query2 = "SELECT type FROM t_fundflow WHERE extorder ='" + extorder + "'"
    cur2 = dbconn.cursor()
    cur2.execute(query2)
    sametype = cur2.fetchone()
    if fundtype == sametype:
        print("[ERROR] Duplicate MT deal: " + agentid, uid, fundtype, mtlogin, credit, extorder)
        return 0
    # 插入资金变动表
    cur3 = dbconn.cursor()
    cur3.execute("INSERT INTO t_fundflow(uid, type, mtlogin, credit, debit, extorder) VALUES (%s, %s, %s, %s, %s, %s)",
                 (uid, fundtype, mtlogin, credit, 0, extorder))
    print('[Credit] ' + agentid, uid, fundtype, mtlogin, credit, extorder)
    return 0


# 数据库连接信息
db_params = {
    "database": "metatrader5",
    "user": "xw",
    "password": "g00dluckDB",
    "host": "185.84.236.29",
    "port": 5432
}
DSN = "dbname=%(database)s host=%(host)s port=%(port)s user=%(user)s password=%(password)s" % db_params

# 定义结算时间
cutoff = time(21, 0)
now = datetime.utcnow()
today = now.date()
yesterday = today - timedelta(1)
thiscutoff = datetime.combine(today, cutoff)
lastcutoff = datetime.combine(yesterday, cutoff)

# 成交查询
query1 = "SELECT deal, login, time, symbol, commission, volumeclosed, agent_id1, reward1, " + \
    "agent_id2, reward2, agent_id3, reward3 FROM v_dealclosed WHERE time > %s AND time <= %s;"
# query10 = "SELECT deal, login, time, symbol, commission, volumeclosed, agent_id1, reward1, " + \
#     "agent_id2, reward2, agent_id3, reward3 FROM xw.v_dealclosed WHERE time > '2018-10-09 8:0:0';"
# query1 = "SELECT deal, login, time, symbol, commission, volumeclosed," + \
#    "agent_id1, reward1, agent_id2, reward2, agent_id3, reward3 FROM xwtest.v_dealclosed WHERE deal=;"
# query1 = "SELECT deal, login, time, symbol, commission, volumeclosed," + \
#    "agent_id1, reward1, agent_id2, reward2, agent_id3, reward3 FROM xwtest.v_dealclosed WHERE login=;"

with psycopg2.connect(DSN) as dbconn:
    cur1 = dbconn.cursor()
    print("[DBConn] Connect to DB server.")
    cur1.execute(query1, (lastcutoff, thiscutoff))
    # 遍历已成交单视图
    for record in cur1:
        # 取得每笔交易的账号，品种，手数，单号
        mtlogin = str(record[1])
        symbol = record[3]
        lot = record[5] / 10000
        deal = str(record[0])
        commission = record[4]
        agent = {}
        # print(mtlogin)
        """
        # 查询佣金视图，取得各级代理商基础返佣点数
        query2 = "SELECT uid, commission, agent_id1, reward1+spread, agent_id2, reward2-reward1, agent_id3, " + \
            "reward3-reward2-reward1 FROM v_commission where mtlogin='" + mtlogin + "';"
        cur.execute(query2)
        if cur.rowcount != 1:
            print("DB Logic error, single record for a mtlogin is required!")
            exit(1)
        v_commission = cur.fetchone()
        """
        agent[record[6]] = record[7]
        agent[record[8]] = record[9]
        agent[record[10]] = record[11]

        # 外佣入账
        agentid = record[6]
        if agentid is not None and commission != 0:
            fundtype = 51
            extorder = deal
            credit = 0 - commission
            doInsert(dbconn, agentid, fundtype, mtlogin, credit, extorder)

        # 内佣入账
        fundtype = 50
        extorder = deal
        credit = 0.0

        for agentid, reward in agent.iteritems():
            # print('AAA', agentid, reward)
            if agentid is None or reward == 0:
                continue
            # agentid = agent_id
            # 查询产品佣金比例关系视图，计算佣金
            query2 = "SELECT factor, maxreward, formula, reward0, reward1, reward2 FROM v_symbolfactor WHERE symbol='" \
                + symbol + "'"
            cur2 = dbconn.cursor()
            cur2.execute(query2)
            if cur2.rowcount != 1:
                print("[ERROR] Invalid record is returned on symbol " + symbol + " of deal " + deal)
                exit(1)
            v_symbolfactor = cur2.fetchone()
            factor = v_symbolfactor[0]
            maxreward = v_symbolfactor[1]
            formula = v_symbolfactor[2]
            reward0 = v_symbolfactor[3]
            reward1 = v_symbolfactor[4]
            reward2 = v_symbolfactor[5]
            # if reward > (maxreward * lot):
            #     reward = maxreward * lot
            # else:
            #     reward_in_point = reward
            if formula == 0:
                credit = reward0 * reward
            elif formula == 1:
                credit = reward1 * reward
            elif formula == 2:
                credit = reward2 * reward
            doInsert(dbconn, agentid, fundtype, mtlogin, credit, extorder)

dbconn.close()
