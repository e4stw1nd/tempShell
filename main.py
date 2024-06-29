from flask import Flask,render_template, request, redirect, url_for, session, make_response
import mysql.connector, kubernetesg,runcmd
import os,hashlib,jwt,re,random
pwd=os.getcwd().strip()
print(pwd)
mydb = mysql.connector.connect(
  host="localhost",
  user="e4stw1nd",
  password="e4stw1nd",auth_plugin='mysql_native_password',database='user'
)
cursor = mydb.cursor()

app = Flask(__name__)
app.secret='wsqje38h92'
app.session='6v@g291+'
def validate(username,password,email):
        query='select * from users where username = "{}" or email= "{}" '.format(username, email)
        print(query)
        cursor.execute(query)
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
           
            hash = password+app.secret
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            
            cursor.execute('INSERT INTO users VALUES ( %s, %s, %s , NULL)', (username, password, email))
            mydb.commit()
            msg = 'You have successfully registered!'
        return(msg)
    
@app.route('/',methods=['GET'])
def home():
    path='index.html'
    return render_template(path,msg='')
@app.route('/shell',methods=['GET','POST'])
def shell():
    if(request.method=='GET'):
        try:
                cookie=request.cookies.get('Token')
                user=jwt.decode(jwt=cookie,key=app.secret,algorithms=["HS256"])
                # print(user)
                query="select * from users where username = '"+user['User']+"' ;"
                # print(query)
                cursor.execute(query)
                x=cursor.fetchone()
                if(not x):
                    return redirect('/login.html') 
                # print(x)
                if(not x[3]):
                     x=str(random.randint(1,1000000000))
                     x=hashlib.sha1(x.encode()).hexdigest()
                     kubernetesg.create_pod(x, "ubuntu")
                     query="update users set shell= '"+x+"' where username = '"+user['User']+"' ;"
                     cursor.execute(query)
                     mydb.commit()
                    #  print(x)   
                return render_template('/shell.html',msg='Login Done!') 
        except:
            return redirect('/login.html') 
    if(request.method=='POST'):
        CMD=request.form['cmd']
        print(CMD)
        try:
            cookie=request.cookies.get('Token')
            user=jwt.decode(jwt=cookie,key=app.secret,algorithms=["HS256"])
            query="select * from users where username = '"+user['User']+"' ;"
            # print(query)
            cursor.execute(query)
            x=cursor.fetchone()
            if(not x):
                return redirect('/login.html')
            if(not x[3]):
                 x=str(random.randint(1,1000000000))
                 x=hashlib.sha1(x.encode()).hexdigest()
                 kubernetesg.create_pod(x, "ubuntu")
                 query="update users set shell= '"+x+"' where username = '"+user['User']+"' ;"
                 cursor.execute(query)
                 mydb.commit()
            else:
                 x=x[3]
            return render_template('/shell.html',msg=runcmd.runner(x,"ubuntu",CMD))
        except:
            return redirect('/login.html') 
@app.route('/signup',methods=['GET','POST'])
def signup():
    if(request.method=='GET'):
         return render_template('signup.html')
    elif (request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form):
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        msg=validate(username,password,email)
        return render_template('signup.html',msg=msg)
    elif (request.method=='POST'):
         msg='All the fields are mandatory'

@app.route('/logout',methods=['GET'])
def logout():
    resp=make_response(redirect('login.html'))
    resp.set_cookie('Token','7',max_age=0)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
            resp = make_response(render_template('login.html',msg=''))
            
            return resp
       
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']+app.secret
        hash = hashlib.sha1(password.encode())
        password = hash.hexdigest()
        query='SELECT * FROM USERS WHERE username = "'+username +  '" AND password = "' +password +'"'

        
        cursor.execute(query)
        user=cursor.fetchone()
        if user:
            cookie=jwt.encode({"User":username},app.secret,algorithm="HS256")
            resp = make_response(render_template('login.html',msg='Login Successful.'))
            resp.set_cookie('Token', cookie)
            return resp
        else:
             return render_template('login.html',msg="Wrong Password")
app.run()