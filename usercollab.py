import pandas as pd
import time
import numpy as np
import sqlite3 as sql
import pickle
import tensorflow as tf
if __name__ == '__main__':
    while True:
        final=pd.read_csv('freq.csv')
        final=final.drop(['Unnamed: 0'],axis=1)
        final=final.sort_values(by=['product_id'])
        df1=final.product_id.unique()
        uno=len(final.user_id.unique())
        df=pd.DataFrame(df1)
        df=df.rename(columns={0: 'product_id'})
        df['List Index']=df.index
        products=pd.read_csv('products.csv')
        prod=products[products['product_id']<10000]
        prod=prod.sort_values(by=['product_id'])
        df2=df.merge(prod,on='product_id')
        df2=df2.drop('aisle_id',axis=1).drop('department_id',axis=1).drop('List Index',axis=1)
        merged = df.merge(final, on='product_id')
        merged= merged.drop('abs_freq', axis=1).drop('cum_freq', axis=1)
        merged=merged.sort_values(['user_id'])
        userGroup = merged.groupby('user_id')
        amountOfUsedUsers = uno
        trX = []
        for userID, curUser in userGroup:
            #Create a temp that stores every movie's rating
            temp = [0]*len(df)
            for num, pro in curUser.iterrows():
                temp[int(pro['List Index'])] = pro['rel_freq']
            #Now add the realtive frequencies into the training list
            trX.append(temp)
            #Check to see if we finished adding in the amount of users for training
            if amountOfUsedUsers == 0:
                break
            amountOfUsedUsers -= 1
        hiddenUnits = 20
        visibleUnits = len(df)
        vb = tf.placeholder("float", [visibleUnits]) #Number of unique products
        hb = tf.placeholder("float", [hiddenUnits]) #Number of features we're going to learn
        W = tf.placeholder("float", [visibleUnits, hiddenUnits])
        #Phase 1: Input Processing
        v0 = tf.placeholder("float", [None, visibleUnits])
        _h0= tf.nn.sigmoid(tf.matmul(v0, W) + hb)
        h0 = tf.nn.relu(tf.sign(_h0 - tf.random_uniform(tf.shape(_h0))))
        #Phase 2: Reconstruction
        _v1 = tf.nn.sigmoid(tf.matmul(h0, tf.transpose(W)) + vb)
        v1 = tf.nn.relu(tf.sign(_v1 - tf.random_uniform(tf.shape(_v1))))
        h1 = tf.nn.sigmoid(tf.matmul(v1, W) + hb)
        #Learning rate
        alpha = 1.8
        #Create the gradients
        w_pos_grad = tf.matmul(tf.transpose(v0), h0)
        w_neg_grad = tf.matmul(tf.transpose(v1), h1)
        #Calculate the Contrastive Divergence to maximize
        CD = (w_pos_grad - w_neg_grad) / tf.to_float(tf.shape(v0)[0])
        #Create methods to update the weights and biases
        update_w = W + alpha * CD
        update_vb = vb + alpha * tf.reduce_mean(v0 - v1, 0)
        update_hb = hb + alpha * tf.reduce_mean(h0 - h1, 0)
        err = v0 - v1
        err_sum = tf.reduce_mean(err * err)
        #Current weight
        cur_w = np.zeros([visibleUnits, hiddenUnits], np.float32)
        #Current visible unit biases
        cur_vb = np.zeros([visibleUnits], np.float32)
        #Current hidden unit biases
        cur_hb = np.zeros([hiddenUnits], np.float32)
        #Previous weight
        prv_w = np.zeros([visibleUnits, hiddenUnits], np.float32)
        #Previous visible unit biases
        prv_vb = np.zeros([visibleUnits], np.float32)
        #Previous hidden unit biases
        prv_hb = np.zeros([hiddenUnits], np.float32)
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        reclist=[]
        #Feeding in the user and reconstructing the input
        from array import *
        for i in range(0,len(trX)):
            epochs = 15
            batchsize = 100
            errors = []
            for i in range(epochs):
                for start, end in zip( range(0, len(trX), batchsize), range(batchsize, len(trX), batchsize)):
                    batch = trX[start:end]
                    cur_w = sess.run(update_w, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
                    cur_vb = sess.run(update_vb, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
                    cur_nb = sess.run(update_hb, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
                    prv_w = cur_w
                    prv_vb = cur_vb
                    prv_hb = cur_nb
                errors.append(sess.run(err_sum, feed_dict={v0: trX, W: cur_w, vb: cur_vb, hb: cur_nb}))
            hh0 = tf.nn.sigmoid(tf.matmul(v0, W) + hb)
            vv1 = tf.nn.sigmoid(tf.matmul(hh0, tf.transpose(W)) + vb)
            feed = sess.run(hh0, feed_dict={ v0: [trX[i]], W: prv_w, hb: prv_hb})
            rec = sess.run(vv1, feed_dict={ hh0: feed, W: prv_w, vb: prv_vb})
            if(len(rec)!=0):
                reclist.append(rec[0].tolist())
        recprod=[]
        for i in range(0,len(trX)):
            searched_products_75=df2
            searched_products_75["Recommendation Score"] = reclist[i]
            searched_products_75=searched_products_75.sort_values(["Recommendation Score"], ascending=False)
            recprod.append(searched_products_75)
        uid=merged['user_id'].unique()
        searchprod=[]
        for i in range(0,len(uid)):
            products_75 = merged[merged['user_id']==uid[i]]
            searchprod.append(products_75)
        finrec=[]
        for i in range(0,len(uid)):
            merged_75 = recprod[i].merge(searchprod[i], on='product_id', how='outer')
            merged_75 = merged_75.drop('user_id', axis=1).drop('rel_freq',axis=1).drop('List Index',axis=1)
            finrec.append(merged_75)
        import pickle
        pickle.dump(finrec, open("rec.pkl","wb"))

    time.sleep(14400)
