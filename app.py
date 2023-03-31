import sqlite3, random
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify, make_response, session

app = Flask(__name__)

DB_FILE_NAME = "data.db"

@app.route("/")
def home():  
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    error = None
    username = request.form["username"]
    password = request.form["password"]
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            users = mycursor.execute("SELECT DISTINCT * FROM users")
            for u,p,e in users:
                if username == u and password == p:
                    global user_log
                    user_log = u   
                    return redirect(url_for('mylist')) 
            else: 
                error = "Invalid username or password. Please try again!"    
                return render_template("index.html", error = error)  
    except:
         return redirect(url_for('home'))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register/successfully", methods=["POST"])
def successfully_reg():
    error = None
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    try:
        if username and password and email:
            with sqlite3.connect(DB_FILE_NAME) as conn:
                mycursor = conn.cursor()
                mycursor.execute("CREATE TABLE IF NOT EXISTS users(username UNIQUE, password, email UNIQUE)")
                mycursor.execute(f"INSERT INTO users VALUES ('{username}', '{password}', '{email}')") 
            return render_template("successfully.html", name = username)
        else:
            error = "Please make sure all fields are filled in correctly."
            return render_template("register.html", error = error)
    except:
        error = "Username or Email already exists. Please try again!"
        return render_template("register.html", error = error)

@app.route("/mylist")
def mylist():
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            mycursor.execute(f"SELECT * FROM todolist WHERE user = '{user_log}'")    
            return render_template("mylist.html", tasks = mycursor.fetchall()) 
    except:
         return render_template("mylist.html") 

@app.route("/add", methods = ["POST"])
def add():   
    task = request.form["task"]
    date = request.form["date"]
    id_number = unique_id_number()
    try:     
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            mycursor.execute("CREATE TABLE IF NOT EXISTS todolist (task, task_date, user, id INTEGER UNIQUE)")
            if (date != "" and task != ""):           
                mycursor.execute(f"INSERT INTO todolist VALUES ('{task}', '{date}', '{user_log}', '{id_number}')")   
                conn.commit()
                return redirect(url_for('mylist'))
            else:
                return redirect(url_for('mylist'))  
    except:
        return redirect(url_for('mylist'))

@app.route("/logout")
def logout():
    return redirect(url_for('home'))

@app.route("/delete")
def delete():
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            mycursor.execute(f"DELETE FROM todolist WHERE user = '{user_log}'")
            conn.commit()
            return redirect(url_for('mylist')) 
    except:
        return redirect(url_for('mylist')) 

@app.route("/delete_task", methods = ["POST"])
def delete_task():
    id_number = request.form["id"]
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            mycursor.execute(f"DELETE FROM todolist WHERE user = '{user_log}' AND id = {id_number}")
            conn.commit()
            return redirect(url_for('mylist')) 
    except:
        return redirect(url_for('mylist')) 

@app.route("/sorting", methods = ["POST"])
def sorting():
    sort_by = request.form["sortedby"]
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            if sort_by == "Date":
                mycursor.execute(f"SELECT * FROM todolist WHERE user = '{user_log}' ORDER BY task_date")
                return render_template("mylist.html", tasks = mycursor.fetchall())
            elif sort_by == "Name":
                mycursor.execute(f"SELECT * FROM todolist WHERE user = '{user_log}' ORDER BY task")
                return render_template("mylist.html", tasks = mycursor.fetchall())
            else:
                return redirect(url_for('mylist'))   
    except:
        return redirect(url_for('mylist')) 

@app.route("/edit", methods = ["POST"])
def edit():
    global task_id
    id_number = request.form["id"]
    old_task = request.form["old_task"]
    old_date = request.form["old_date"] 
    task_id = id_number
    return render_template("edit.html", old_task = old_task, old_date = old_date) 

@app.route("/edit_task", methods = ["POST"])
def edit_task():
    error = None
    new_task = request.form["new_task"]
    new_date = request.form["new_date"]
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            if (new_date != "" and new_task != ""):        
                mycursor.execute(f"UPDATE todolist SET task = '{new_task}', task_date = '{new_date}' WHERE id = {task_id}")
                conn.commit()
                return redirect(url_for('mylist'))  
            else:
                error = "Please make sure all fields are filled in correctly."
                return render_template("edit.html", error = error)             
    except:
        return redirect(url_for('mylist')) 

def unique_id_number(): 
    while(True): 
        num = random.randint(1,1000) 
        with sqlite3.connect(DB_FILE_NAME) as conn:
            mycursor = conn.cursor()
            id_numbers = [id[0] for id in mycursor.execute("SELECT id FROM todolist")]
            if num not in id_numbers:        
                return num
            else:        
                None 

def delete_data():
    with sqlite3.connect(DB_FILE_NAME) as conn:
        mycursor = conn.cursor()  
        mycursor.execute("DROP TABLE users")  
        mycursor.execute("DROP TABLE todolist")

if __name__ == "__main__":
    app.run(debug = True, port = 5000)


