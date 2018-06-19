import pandas as pd
import time
import numpy as np
import sqlite3 as sql
import pickle
from apyori import apriori

if __name__ == '__main__':
    #while True:
        final=pd.read_csv('freq.csv')
        final1=final
        final1=final1.groupby(['product_id'])['abs_freq'].sum()
        final1=pd.DataFrame(final1)
        final1=final1.reset_index()
        final1=final1.sort_values('abs_freq',ascending=False)
        prodname=pd.read_csv('freq.csv')
        prodname=prodname.drop('Unnamed: 0',axis=1).drop('user_id',axis=1).drop('abs_freq',axis=1).drop('cum_freq',axis=1).drop('rel_freq',axis=1)
        final2=final1.merge(prodname,on='product_id')
        final3=final2.drop_duplicates()
        final4=final3.values.tolist()
        pickle.dump(final4, open("trend.pkl", "wb"))
        #time.sleep(3600)

