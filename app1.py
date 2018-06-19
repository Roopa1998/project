#the file that does the main routing
from flask import Flask, session, render_template, request, flash,redirect,url_for
import sqlite3 as sql
import os
import uuid
from math import pi, cos, sin
from operator import itemgetter
import pickle
rec = pickle.load(open("rec.pkl", "rb"))
trend = pickle.load(open("trend.pkl", "rb"))
trend1=trend[:10]
app = Flask(__name__)
app.secret_key = os.urandom(24)
#routed to login page first
@app.route('/')
def home():
    return render_template('login.html')

#validation of entered userid and password against details in customer table
@app.route('/loginpage', methods=['POST', 'GET'])
def loginpage():

    if request.method == 'POST':
        try:
            check1=int(request.form['username'])
            check2=request.form['password']

            with sql.connect("proj.db") as con:
                cur=con.cursor()
                rows=cur.execute("select * from customer")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    dbPass = row[1]
                    print(dbUser)
                    print(dbPass)

                    if dbUser == check1:
                        print("yes")

                    if dbUser == check1 and dbPass == check2 and check1 != "" and check2 != "":
                        print('update flag')
                        cur.execute("UPDATE customer SET flag = ? WHERE uid =?",(1,dbUser))
                        print('update flag done')
                        session['oid'] = uuid.uuid4()
                        session['uid'] = dbUser
                        flash("correct")

                        return render_template('search.html')
                    else:
                        error='Invalid login details. Please Signup if new user.'
                return render_template('login.html',error=error)

        except:
            con.rollback()
            msg = "error"
            print(msg)
            #return render_template("login.html",msg = msg)

        finally:
            con.close()
#rendering of signup page
@app.route('/signup.html',methods=['GET','POST'])
def signup():
    return render_template('signup.html')

#adding the details of the new user to the customer table
@app.route('/addrec',methods=['POST', 'GET'])
def addrec():
    #inserted=False
    if request.method == 'POST':
        try:
            print('sign')
            p1 = request.form['fname']
            p2 = request.form['lname']
            p4 = request.form['phone']
            p3 = request.form['uname']
            p5 = request.form['pincode']
            p6 = request.form['dob']
            p7 = request.form['gender']
            p8 = request.form['email']
            p9= request.form['pass']
            with sql.connect("proj.db") as con:
                print('sign1')
                cur = con.cursor()
                cur.execute("INSERT INTO customer (uid,password,fname,lname,phone,pincode,dob,gender,email,flag) VALUES (?,?,?,?,?,?,?,?,?,?)",(p3,p9,p1,p2,p4,p5,p6,p7,p8,0) )
                print('sign2')
                con.commit()
                msg = "Record successfully added"
                session['oid'] = uuid.uuid4()
                session['uid'] = p3
                print('sign3')
                return render_template('search.html')

        except:
            con.rollback()
            error = "error in insert operation."
            return render_template("signup.html",error = error)

        finally:
            con.close()


#display of results based on product search
@app.route('/data', methods=['POST'])
def data():
    #print('hello')
    if request.method == 'POST':
        #print('hi')
        try:
            name = request.form.get('name')
            print(name)
            # #print('ssup')
            # lat = float((request.form['p1']))
            # lng = float((request.form['p2']))
            # print(lat)
            # print(lng)

            with sql.connect("proj.db") as con:
                cur = con.cursor()
                print("going to delete")
                cur.execute("delete from dummy ")
                #
                print("delete done")
                cur.execute("delete from dummy2")

                #cur1=con.cursor()
                print('hello')
                rows1 = cur.execute("select s.shop_id,s.shop_name,s.address,p.product_id,p.product_name,p.cost,p.count from store s, product p where s.shop_id=p.shop_id")
                print('hello done')
                rows1 = cur.fetchall()
                print("fetch done")
                value1=session.get('oid')
                value2=session.get('uid')
                print(rows1)
                arr1 = []
                print('array')
                proid=0
                for row in rows1:

                    #print(row)
                    print(row[4])
                    if str(row[4]) == str(name):
                        print('table1')
                        li = []
                        shopname=row[1]
                        shopaddress=row[2]
                        proid = row[3]
                        shopid = row[0]
                        cost = row[5]
                        count = row[6]
                        proname = row[4]
                        li.append(shopid)
                        li.append(shopname)
                        li.append(shopaddress)
                        li.append(proid)
                        li.append(proname)
                        li.append(cost)
                        li.append(count)

                        arr1.append(li)
                        print('table')
                print(arr1)

                # print(arr2)
                print('session')
                #insertion of search data into recommend table
                cur.execute("insert into recommend(uid,product_id,session_id) values (?,?,?)",(value2,proid,str(value1)))
                print('session1')


                print("after commit")
                #temporarily populating the results table displayed by storing the results of currently searched product in dummy2 table
                #the contents of the dummy2 table are deleted on logout and repopulated only after the next search.
                for row in arr1:
                    cur.execute("INSERT INTO dummy2 (shopid,prodid,cost,count,prodname) VALUES (?,?,?,?,?)",(row[0],row[3],row[5],row[6],row[4]))
                print("inserted")
                con.commit()


                return render_template("geoloc2.html",array2=arr1)

        except:
            con.rollback()
            msg = "error in retrieve operation"
            print(msg)
            return render_template("search.html",msg = msg)
        finally:
            con.close()
#determining the nearest results to the entered or current location by calculation of radius using latitude and longitude values
@app.route('/geo',methods=['POST','GET'])
def geo():
    if request.method == 'POST':


        try:


            with sql.connect("proj.db") as con:
                print("going to delete")
                cur = con.cursor()
                cur.execute("delete from dummy ")
                #dummy table is using to hold the current results of location based search and deleted after every logout
                print('ssup')
                lat = float((request.form['p1']))
                lng = float((request.form['p2']))
                print(lat)
                print(lng)
                cur = con.cursor()
                lat = lat*(pi/180)
                lng = lng*(pi/180)
                print("done mul")
                CUR_cos_lat = cos(lat)
                print(CUR_cos_lat)
                print("1 done")
                CUR_sin_lat = sin(lat)
                print(CUR_sin_lat)
                print("2 done")
                CUR_cos_lng = cos(lng)
                print(CUR_cos_lng)
                print("3 done")
                CUR_sin_lng = sin(lng)
                print(CUR_sin_lng)
                print("4 done")
                cos_allowed_distance = cos(2.0 / 6371)
                print("5 done")
                #insert values calculated using longitude and latitude into dummy table
                cur.execute("insert into dummy(cur_cos_lat,cur_cos_long,cur_sin_lat,cur_sin_long) values(?,?,?,?)",(CUR_cos_lat,CUR_cos_lng,CUR_sin_lat,CUR_sin_lng))
                print("inserted")
                con.commit()
                print("commited")
                cur.execute("select * from dummy")
                rows = cur.fetchall()
                print(rows)
                print("going to execute")
                #retrieving the store details in order of proximity
                rows=cur.execute("select distinct s.shop_id,  shop_name,  s.address, (d.cur_sin_lat*s.sin_lat + d.cur_cos_lat*s.cos_lat*(s.cos_lng*d.cur_cos_long+s.sin_lng*d.cur_sin_long)) as distance from store s,dummy d order by distance desc")
                print("executed")
                rows = cur.fetchall()
                con.commit()
                print(rows)

                arr = []
                for row in rows:
                    li = []
                    dbshopid = row[0]
                    dbshopname = row[1]
                    dbaddress = row[2]


                    li.append(dbshopid)
                    li.append(dbshopname)
                    li.append(dbaddress)

                    arr.append(li)
                print(arr)
                #retrieving the product search results from the dummy2 table and sorting them based on proximity of store location
                rows1=cur.execute("select distinct * from dummy2")
                rows1=cur.fetchall()
                print(rows1)
                arr1=[]
                for row in rows1:
                    li = []
                    proid = row[1]
                    shopid = row[0]
                    cost = row[2]
                    count = row[3]
                    proname = row[4]
                    li.append(proid)
                    li.append(shopid)
                    li.append(cost)
                    li.append(count)
                    li.append(proname)
                    arr1.append(li)
                print(arr1)
                i=0
                j=0
                arr2=[]
                for i in arr:
                    li=[]
                    for j in arr1:
                        if(i[0]==j[1]):
                            li.append(i[0])
                            li.append(i[1])
                            li.append(i[2])
                            li.append(j[0])
                            li.append(j[2])
                            li.append(j[3])
                            li.append(j[4])
                            arr2.append(li)
                print(arr2)
                #arr2=[list(i) for i in set(tuple(i) for i in arr2)]





            return render_template("result.html",array=arr2)


        except:
            con.rollback()
            msg = "error in retrieve operation"
            print(msg)
            return render_template("search.html")
        finally:
            con.close()

@app.route('/geo1',methods=['POST','GET'])
def geo1():
    try:
        with sql.connect("proj.db") as con:
            cur = con.cursor()

            print("connected")
            rows1=cur.execute("select distinct * from dummy2")
            rows1=cur.fetchall()
            print("fetched")
            arr1=[]
            for row in rows1:
                li = []
                proid = row[0]
                shopid = row[1]
                cost = row[2]
                count = row[3]
                proname = row[4]
                li.append(proid)
                li.append(shopid)
                li.append(cost)
                li.append(count)
                li.append(proname)
                arr1.append(li)
            print(arr1)
            #print(arr1)
            arr2=sorted(arr1,key=itemgetter(2))
            print(arr2)
            arr3=[list(i) for i in set(tuple(i) for i in arr2)]
            print(arr3)
            print("done arr3")
            arr3=sorted(arr3,key=itemgetter(2))
            #print(arr2)
            print(arr3)
        return render_template("result1.html",array4=arr3)

    except:


        con.rollback()
        msg = "error in retrieve operation"
        print(msg)
        return render_template("search.html")
    finally:
        con.close()
#when the recommendations button is clicked
@app.route('/recommend',methods=['POST','GET'])
def recommend():
    global name2
    if request.method == 'POST':
        try:
            with sql.connect("proj.db") as con:
                cur = con.cursor()
                user_id=int(session.get('uid'))
                print("user_id is")
                print(user_id)
                rows=cur.execute("select uid,flag from customer ")
                rows=cur.fetchall()
                print("caluculated user_id")
                print(rows)
                for row in rows:
                    print(row)
                    if row[0]== user_id:
                        if row[1]==0:
                            user_id=int(session.get('uid'))
                            ses_id=str(session.get('oid'))
                            print(user_id)
                            print(ses_id)

                            rules=pickle.load(open("exam.pkl","rb"))
                            print("pickle done")


                            some_thing=cur.execute("select uid,session_id,product_id from recommend ")
                            print(some_thing)

                            some_thing=cur.fetchall()
                            print("printd")
                            final=[]

                            for row2 in some_thing:
                                print("entered")
                                #print(row2[0])
                                #print(user_id)
                                if row2[0] == user_id:
                                    print("entered2")
                                    #print(row2[1])
                                    #print(ses_id)

                                    if row2[1] == ses_id:
                                        print("entered 3")
                                        value=row2[2]







                            value=str(row2[2])
                            print(value)

                            rule=(list(rules))
                            li=[]
                            for i in range(len(rule)):
                                si=rule[i][0]
                                li.append(list(si))
                            print(li)
                            print("after rules are generated")

                            value1=str(value)
                            print(value1)



                            output=[]
                            for i in range(len(li)):
                                print(li[i])
                                if value1 in li[i]:

                                    print(li[i])
                                    for j in range(len(li[i])):
                                        output.append(li[i][j])
                                        print(output)


                                final.extend(output)
                            final=set(final)
                            final=list(final)
                            print(final)
                            name1=[]
                            name2 =[]
                            rows5=cur.execute("select product_id,product_name from product")
                            print("done")
                            rows5=cur.fetchall()
                            print("jfj")
                            for i in final:
                                i=int(i)
                                print("in list")
                                print(i)
                                for j in rows5:
                                    #print(j[0])
                                    #print("in execute")
                                    if j[0] == i:

                                        print("entered")
                                        name1=[]
                                        name1.append(j[0])
                                        name1.append(j[1])
                                        print(name1)
                                name2.append(name1)
                            print(name2)
                            if name2 == []:
                                print('ssup1')
                                return render_template('trend1.html',rec2=trend1)




                            return render_template("rec.html",apr=name2)
                        else:
                            print("results from user collabaraiive filtering")

                            cur=con.cursor()
                            uid=session.get('uid')
                            count=-1
                            rows=cur.execute('select uid from customer')
                            rows=cur.fetchall()
                            for row in rows:
                                count=count+1
                                if uid == row[0]:
                                    break
                            print(count)
                            #product_name=[]
                            rec1=rec[count]
                            product_name=[]

                            print('hello1')
                            rows=cur.execute("select product_id,product_name from product")
                            rows = cur.fetchall()
                            print('hello2')
                            for row in rows:
                                rec3=[]
                                rec3.append(row[0])
                                rec3.append(row[1])
                                #print(rec3)
                                product_name.append(rec3)
                            print('hello')
                            #print(product_name)
                            prodname=[]
                            for i in range(0,10):
                                c=0
                                for li in product_name:
                                    #print(rec1[i])
                                    #print(li[0])
                                    if rec1[i] == li[0]:
                                        if c == 0:
                                            prodname.append(li)
                                            c=1
                            print('done')
                            print(prodname)
                            return render_template('recom1.html',rec2=prodname)








        except:
            con.rollback()
            msg = "error in retrieve operation"
            print(msg)
            return render_template("search.html")
        finally:
            con.close()





@app.route('/location',methods=['POST', 'GET'])
def location():
    if request.method == 'POST':


        try:
            name = request.form['name']
            print(name)

            with sql.connect("proj.db") as con:
                print("going to delete")
                cur = con.cursor()
                cur.execute("delete from dummy ")
                print("delete done")

                print("commited")
                cur.execute("select * from store")

                print("selected")
                rows10 = cur.fetchall()
                print("done")
                for doomed in rows10:
                    print(doomed)
                    if doomed[2] == name:


                        print('ssup')
                        lat = float(doomed[3])
                        lng = float(doomed[4])
                        print(lat)
                        print(lng)
                        cur = con.cursor()
                        lat = lat*(pi/180)
                        lng = lng*(pi/180)
                        print("done mul")
                        CUR_cos_lat = cos(lat)
                        print(CUR_cos_lat)
                        print("1 done")
                        CUR_sin_lat = sin(lat)
                        print(CUR_sin_lat)
                        print("2 done")
                        CUR_cos_lng = cos(lng)
                        print(CUR_cos_lng)
                        print("3 done")
                        CUR_sin_lng = sin(lng)
                        print(CUR_sin_lng)
                        print("4 done")
                        cos_allowed_distance = cos(2.0 / 6371)
                        print("5 done")

                        cur.execute("insert into dummy(cur_cos_lat,cur_cos_long,cur_sin_lat,cur_sin_long) values(?,?,?,?)",(CUR_cos_lat,CUR_cos_lng,CUR_sin_lat,CUR_sin_lng))
                        print("inserted")
                        con.commit()
                        print("commited")
                        cur.execute("select * from dummy")
                        rows = cur.fetchall()
                        print(rows)
                        print("going to execute")
                        rows=cur.execute("select distinct s.shop_id,  shop_name,  s.address, (d.cur_sin_lat*s.sin_lat + d.cur_cos_lat*s.cos_lat*(s.cos_lng*d.cur_cos_long+s.sin_lng*d.cur_sin_long)) as distance from store s,dummy d order by distance desc")
                        print("executed")
                        rows = cur.fetchall()
                        con.commit()
                        print(rows)

                        arr = []
                        for row in rows:
                            li = []
                            dbshopid = row[0]
                            dbshopname = row[1]
                            dbaddress = row[2]


                            li.append(dbshopid)
                            li.append(dbshopname)
                            li.append(dbaddress)

                            arr.append(li)
                        print(arr)

                        rows1=cur.execute("select distinct * from dummy2")
                        rows1=cur.fetchall()
                        print(rows1)
                        arr1=[]
                        for row in rows1:
                            li = []
                            proid = row[1]
                            shopid = row[0]
                            cost = row[2]
                            count = row[3]
                            proname = row[4]
                            li.append(proid)
                            li.append(shopid)
                            li.append(cost)
                            li.append(count)
                            li.append(proname)
                            arr1.append(li)
                        print(arr1)
                        i=0
                        j=0
                        arr2=[]
                        for i in arr:
                            li=[]
                            for j in arr1:
                                if(i[0]==j[1]):
                                    li.append(i[0])
                                    li.append(i[1])
                                    li.append(i[2])
                                    li.append(j[0])
                                    li.append(j[2])
                                    li.append(j[3])
                                    li.append(j[4])
                                    arr2.append(li)
                        print(arr2)
                        #arr2=[list(i) for i in set(tuple(i) for i in arr2)]





                        return render_template("result.html",array=arr2)






        except:
            con.rollback()
            msg = "error in retrieve operation"
            print(msg)
            return render_template("search.html")
        finally:
            con.close()
















# when the logout button is clicked
@app.route('/logout',methods=['POST', 'GET'])
def logout():
    #inserted=False
    if request.method == 'POST':
        print("going to logout")
        uid=session.get('uid')
        print(uid)
        session.pop(uid,None)
        print("popped")
        return render_template("logout.html")








if __name__ == '__main__':
   app.run(debug=True)
