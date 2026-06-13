# _______auther: moogiegik
import akshare as ak
import pandas as pd
from dataclasses import make_dataclass
from sqlalchemy import create_engine
import sqlite3

from datetime import datetime
import logging

import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# _______auther: moogiegik
tables = ["info_resource","info_handle","info_search"]
db_path='MData.db'
# table info_resource
Types = [["TEXT","TEXT","TEXT"],["integer","TEXT","TEXT"],["integer","TEXT","TEXT"]]
Fields = [["time","resource","reserve"],["id","text","regular"],["id","website","regular","name"]]
# _______auther: moogiegik

def generate_insert_sql(table, fields, values):
    placeholders = ', '.join(['?'] * len(values))
    fields_str = ', '.join(fields)
    sql = f"INSERT INTO {table} ({fields_str}) VALUES ({placeholders})"
    return sql

def save_update_delete(table, fields, values, db_path):
    if not values:  # Check if values is empty
        return {"status": "error", "message": "Values cannot be empty"}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM {table} WHERE {fields[0]} = ?", (values[0],))
    exists = cursor.fetchone()
    # DELETE or UPDATE operation
    if exists:  # Record exists
        if len(values) == 1:  # Check if values has only one item
            print("Delete operation")
            sql = f"DELETE FROM {table} WHERE {fields[0]} = ?"
            cursor.execute(sql, (values[0],))
            result = {"status": "success", "message": "Data deleted successfully"}
        else:  # Update operation
            print("Update operation")
            if len(fields) != len(values):
                return {"status": "error", "message": "Fields and values length mismatch"}
            set_clause = ', '.join([f"{field} = ?" for field in fields])
            sql = f"UPDATE {table} SET {set_clause} WHERE {fields[0]} = ?"
            update_values = values + [values[0]]
            cursor.execute(sql, update_values)
            result = {"status": "success", "message": "Data updated successfully"}
    # INSERT operation
    elif(len(values)>1):  # Record does not exist, proceed with insertion
        print("Insert operation")
        sql = generate_insert_sql(table, fields, values)
        cursor.execute(sql, values)
        result = {"status": "success", "message": "Data inserted successfully"}
    else:
        result = {"status": "fail", "message": "wrong order"}
    conn.commit()
    conn.close()
    return result
# _______auther: moogiegik
def find_row_with_max_id(table, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row
# _______auther: moogiegik
def query_with_offset_and_limit(table, key, offset, limit, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Modify the query to order by id in descending order
    sql = f"SELECT * FROM {table} ORDER BY "+ key +" DESC LIMIT ? OFFSET ?"
    # sql = f"SELECT * FROM {table} LIMIT ? OFFSET ?"
    cursor.execute(sql, (limit, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()# _______auther: moogiegik
    return rows

def find(table, key, value, offset, limit, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = f"SELECT * FROM {table} WHERE time LIKE '%{value}%' OR resource LIKE '%{value}%' ORDER BY {key}"
    # sql = f"SELECT * FROM {table} WHERE resource LIKE '"+value+"'"
    # sql = f"SELECT * FROM {table} WHERE resource LIKE '%伊朗%'"
    # print("sql",sql)
    # 执行查询
    cursor.execute(sql)
    # 获取所有结果
    results = cursor.fetchall()
    # # print("results",results)
    # print("---------------")
    # print(f"找到{len(results)}条数据：")
    # for  row in results:
    #     print(row)
    # # 找出第5个以后的数据
    retVal = []
    if len(results) > offset:
        # limit = min(limit, len(results) - offset)  # 确保limit不超过剩余数据的数量
        for i in range(len(results)-offset-1,len(results)-limit-1,-1):
            if i < 0:break
            else:retVal.append(results[i])
        # print("retVal",retVal)
    else:# _______auther: moogiegik
        print("没有足够的数据，无法找到第5个以后的数据。")
    # print("---------------")
    # print(f"找到{len(retVal)}条数据：")
    # for  row in retVal:
    #     print(row)    
    # 关闭数据库连接
    cursor.close()
    conn.close()
    return retVal

def Start(json):
    type = json.get("type")
    data = json.get("data")
    table = json.get("table")

    if type == 'change':
        # when it not delete option
        if(len(data)!=1):
            # generate id for table put it for the first place
            if(table == 0):
                # 获取当前日期和时间
                now = datetime.now()
                # 格式化日期和时间
                formatted_date = now.strftime("%y-%m-%d-%H:%M-%S.%f")[:-3]
                data.insert(0, formatted_date)
            elif(table == 1 or table == 2):
                # formatted_date = now.strftime("%y-%m-%d")
                id = find_row_with_max_id(tables[table], db_path)[0]+1
                data.insert(0, id)
        # elif(len(data)==1):
        #     data.extend(["", ""])
        # data for table 0 is ['time','resource','reserve']
        # data for table 1 is ['id','text','regular']
        # data for table 2 is ['id','website','regular']
        # when delete :
        # for table 0, data is ['time']
        # for table 0, data is ['id']
        print("Start prove data",data)
        # logging.info("Start processing data: %s", data) #not work
        # logging.error("This is an error message")
        save_update_delete(tables[table], Fields[table], data, db_path)
        return {"result":type + ' successfully',"data":type,"json":json}
    elif type == 'query':
        info = query_with_offset_and_limit(tables[table], Fields[table][0], data[0], data[1], db_path)
        return {"result":type + ' successfully',"data":info,"json":json}
    elif type == 'find':
        # value_find = json.get("find")
        info = find(tables[table], Fields[table][0], data[2], data[0], data[1], db_path)
        return {"result":type + ' successfully',"data":info,"json":json}
    return {"result":'failed wrong older'}

def Get_Local_IP():
    try:
        # 创建一个 UDP 套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公共的 IP 地址（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        # 获取本机 IP 地址
        ip = s.getsockname()[0]
        s.close()
        return ["successfully!",ip]
# _______auther: moogiegik
    except Exception as e:
        # print(f"获取本地 IP 地址失败: {e}")
        return ["error!"]
# query option
# table,key, offset, limit, db_path
# print(Start({"type":'query',"table":0,"data":[0,10]}))

# delete option
# print(Start({"type":'change',"table":0,"data":["25-04-17-14:11-05.121"]}))
# print(Start({"type":'change',"table":0,"data":["25-04-17-14:11-05.121"]}))

# print(find(tables[0], "time", "伊朗", 0, 3, db_path))
# retttVal = (query_with_offset_and_limit(tables[0], "time", 0, 5, db_path))
# print("query")
# for  row in retttVal:
#         print(row)






