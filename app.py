from flask import *
from flask_pymongo import PyMongo
from datetime import datetime
from passlib.hash import pbkdf2_sha512

app=Flask(__name__)
app.config['SECRET_KEY']="hi"
app.config['MONGO_URI']="mongodb+srv://saachi:Pepperika22@cluster0.i9bhj.mongodb.net/trial?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
mongo=PyMongo(app)

@app.route('/')
def homescreen():
    return render_template("Homescreen.html")

@app.route('/home',methods=["GET","POST"])
def home():
    if "user" in session:
        if request.method=="GET":
            notes=list(mongo.db.user_notes.find({"user":session['user']}).sort([("created at",-1)]))
            user=session['user']
            return render_template('Home.html',notes=notes,user=user)
        elif request.method=="POST":
            note=mongo.db.user_notes.insert_one({
                "note_text":request.form["MyNote"],
                "created at":datetime.utcnow(),
                "user":session["user"]
            })
            flash("Note successfully saved")
            return redirect('/home')
    else:
        flash("Login to continue")
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out")
    return redirect('/login')

@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("Signup.html")
    else:
        #global user_data
        #user_data[request.form['Username']]=request.form['Password']
        user=mongo.db.user.find_one({
            'username':request.form['Username']
            })
        print(user)
        if user == None:
            mongo.db.user.insert_one({
                "username":request.form['Username'],
                "password":pbkdf2_sha512.hash(request.form['Password']),
                "email":request.form['Email'],
                "dob":request.form['DOB'],
                "created at":datetime.utcnow()
                })
            flash("Sign Up Successful")
            return redirect('/login')
        else:
            flash("Choose a Different Username")
            return redirect('/signup')
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("Login.html")
    else:
        username=request.form["Username"]
        password=request.form["Password"]
        user=mongo.db.user.find_one({
            'username':request.form["Username"]
        })
        print(user)
        if user == None:
            flash("Username not Found")
            return redirect('/login')
        if not pbkdf2_sha512.verify(password,user['password']):
            flash ("Password Incorrect")
            return redirect('/login')
        flash("Login Successful")
        session['user']=username
        return redirect('/home')

@app.errorhandler(404)
def error(e):
    return render_template("Not_found.html")

if __name__=="__main__":
    app.run()
