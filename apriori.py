#this file needs to be running in the background to update the frequent item-sets
# from the new searches in the recommend table(previous search data)
import pandas as pd
import time
import numpy as np
import sqlite3 as sql
import pickle
from apyori import apriori

if __name__ == '__main__':
    #while True:
        users=pd.read_csv("apriori.csv",header=None)
        users.drop(0,axis=1)
        conn = sql.connect("proj.db")
        df = pd.read_sql_query("select * from recommend", conn)
        df.product_id = df.product_id.astype(str)
        df=df[df['product_id']!='0']
        df=df.drop('uid',axis=1)
        df1=df.values.tolist()
        dfconcat=df.groupby(['session_id'])['product_id'].apply(list)
        dfconcat=pd.DataFrame(dfconcat)
        dfconcat=dfconcat.reset_index()
        dfconcat=dfconcat.drop('session_id',axis=1)
        dfconcat=dfconcat.product_id.tolist()
        #pickle.dump(dfconcat,open("C:/Users/katasanisairupa/PycharmProjects/project1/apriori.pkl", "wb"))
        records=[]
        re=[]
        for i in range(1,5893):
            re=users[2][i].split(",")
            records.append(re)
        print(records)
        records.extend(dfconcat)
        print(len(records))
        rules = (apriori(records, min_support = 0.0005, min_confidence = 0.80, min_lift = 3, min_length =2))
        rule=(list(rules))
        pickle.dump(rule,open("exam.pkl",'wb'))
        #time.sleep(3600)


