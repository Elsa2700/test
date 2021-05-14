#載入flask套件
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
#載入python-mysql連線套件
import mysql.connector
from mysql.connector import Error
import json




#資料庫連線
mydb=mysql.connector.connect(
    host="localhost",    #主機名稱
    user="root",         #帳號
    password="ELSA2700", #密碼
    database="mydb",     #使用資料庫
)


#建立application 物件
app=Flask(__name__)

#session產生金鑰
#comand: python -c 'import os; print(os.urandom(16))'
app.secret_key='secret'


#路由: 建立api==================================================
@app.route("/api/users", methods=["GET"])
def data():
    #使用者輸入要求字串username，預設為ply
    username=request.args.get("username","ply")

    #資料庫處理**************************************
    try:
        #當連線成功，執行下列程式碼
        if mydb.is_connected():
            #操作方法
            mycursor=mydb.cursor()

            #查詢要查詢的會員帳號
            #操作SQL:查詢資料表(單一參數)----------------
            sql="SELECT * FROM users WHERE username = %s"
            mycursor.execute(sql, (username,))

            #從資料庫搜尋到的查詢結果
            record=mycursor.fetchall()
            #特定json格式
            success={
                "data":{
                    "id":record[0][0],
                    "name":record[0][1],
                    "username":record[0][2]
                }
            }

            #導向成功取得資料的json格式
            return json.dumps(success, ensure_ascii= False)
            
    #無對應結果:導向沒有取得資料的json格式
    except IndexError as error:
        null = None
        fail = {"data":null}
        return json.dumps(fail, ensure_ascii= False)


    #資料庫處理**************************************

#路由: 修改姓名 建立api==================================================
@app.route("/api/user", methods=["POST"])
def newName():
    # force=False, silent=False, cache=True
    data = request.get_json()
    updatename = data['updatename']
    name=session['username']
    print("使用者帳號: ",name)
   
    #資料庫處理**************************************
    try:
        #當連線成功，執行下列程式碼
        if mydb.is_connected():
            #操作方法
            mycursor=mydb.cursor()
            #操作SQL:更新資料庫的姓名----------------
            sql = "UPDATE users SET name = %s WHERE username = %s"
            val = (updatename, name)
            mycursor.execute(sql, val)
            mydb.commit()
            #操作SQL:查詢資料表----------------
            sql="SELECT * FROM users WHERE username = %s"
            mycursor.execute(sql, (name,))
            #查詢結果
            record=mycursor.fetchall()
            print("更新後的新姓名: ",record[0][1])

    
            # 導向成功取得資料的json格式==========
            ok = {"ok":True}
            return json.dumps(ok, ensure_ascii= False)
            
    #無對應結果:導向沒有取得資料的json格式
    except IndexError as error:
        error = {"error":True}
        print("更新失敗")
        return json.dumps(error, ensure_ascii= False)
    # 資料庫處理**************************************


#路由: 登入首頁==================================================
@app.route("/")
def homepage():
    return render_template("homepage.html")

#路由:註冊程序==================================================
@app.route("/signup",methods=["POST","GET"])
def signup():
    #POST方法:取得會員的註冊資料
    name=request.form["name"]
    account=request.form["account"]
    password=request.form["password"]
    #input的資料不得為空值
    if not name or not account or not password:
        return redirect(url_for('error',msg="皆需要輸入結果喔"))

    #資料庫處理**************************************
    try:
        #當連線成功，執行下列程式碼
        if mydb.is_connected():
            #操作方法
            mycursor=mydb.cursor()
            #資料庫帳號username 設為UNIQUE:決定帳號名稱是否重複
            # 操作SQL:建立新資料表----------------
            sql="CREATE TABLE users (Id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, UNIQUE (username), PRIMARY KEY(Id))"

            #當資料未重覆:成功新增註冊資料列
            #操作SQL:資料表users中新增資料----------------
            sql="INSERT INTO users (name, username, password) VALUES (%s,%s,%s) "
            val=(name, account,password)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect("/")

    # 當資料未重覆: 連線失敗，導向失敗頁面，顯示"帳號已經被註冊"訊息
    except Error as error:
        #後端回覆: 帳號重複，網頁導向失敗------------------------------
        return redirect(url_for('error',msg="帳號已經被註冊")) 
        print("帳號重複了，導向失敗頁面")
        #資料庫連線錯誤
        print("資料庫無法連線", error)

    #資料庫處理**************************************



#路由:登入程序==================================================
@app.route("/signin",methods=["POST","GET"])
def signin():
    #POST方法:取得會員的帳號、密碼
    account=request.form["account"]
    password=request.form["password"]

    #資料庫處理**************************************
    try:
        #當連線成功，執行下列程式碼
        if mydb.is_connected():
            #操作方法
            mycursor=mydb.cursor()

            #查詢使用者輸入的帳號、密碼:有對應結果 
            #操作SQL:查詢資料表----------------
            sql="SELECT * FROM users WHERE username = %s and password = %s"
            val=(account,password)
            mycursor.execute(sql,val)

            #從資料庫搜尋到的查詢結果
            record=mycursor.fetchall()
            print("使用者登入資料: ",record[0])
    
            #透過session紀錄使用狀態、使用者的名稱
            session['status']='login'  #使用狀態
            session['username']=record[0][2] #使用者的帳號
            session['name']=record[0][1] #使用者的名稱
            print("使用者名稱: ",session['name'])
            print("使用者帳號: ",session['username'])

            #導向成功頁面
            return redirect(url_for('member'))

    #查詢使用者輸入的帳號、密碼:無對應結果 
    except IndexError as error:
        # 後端回覆: 無對應的帳密，網頁導向失敗------------------------------
        return redirect(url_for('error',msg="帳號或密碼輸入錯誤")) 
        print("帳號重複了，導向失敗頁面")
        #資料庫連線錯誤
        print("資料庫無法連線", error)


    #資料庫處理**************************************


#路由:成功會員頁面==================================================
@app.route("/member",methods=["POST","GET"])
def member():
    #取得使用者登入的session狀態
    status=session.get('status')  
    print("目前狀態為: ",status)
    #使用session傳遞資料庫中的使用者名稱
    print(session['name'])
    if status=="login":
        return render_template("member.html",name=session['name'])
    else:
        return redirect("/")

#路由:帳號密碼登出==================================================
@app.route("/signout")
def signout():
    #重設使用者登入狀態
    session['status']='unlogin'
    status=session.get('status')
    print("目前狀態為: ",status)
    return redirect("/")

#路由:失敗頁面==================================================
@app.route("/error/<msg>")
def error(msg):
    return render_template("error.html",msg=msg)
    



#啟動applicaiotn，定義埠號port
app.run(port=3000, debug=True)
