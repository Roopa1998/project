import pandas as pd
import time
import numpy as np
import sqlite3 as sql
import pickle
if __name__ == '__main__':
    #while True:
        conn = sql.connect("proj.db")
        df = pd.read_sql_query("select * from product_freq", conn)
        fin=df.sort_values(by=['user_id'])
        fin['rel_freq']=fin['abs_freq']/fin['cum_freq']
        fin.to_csv('freq.csv')
        #time.sleep(5)
