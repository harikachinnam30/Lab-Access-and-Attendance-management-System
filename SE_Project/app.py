from flask import Flask, flash, render_template, request, redirect, url_for, session, Response
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import re
import os
import sys


UPLOAD_FOLDER = r'D:\\SE_Lab\\SE_Project'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
   
app.secret_key = 'ab2123445'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2004'
app.config['MYSQL_DB'] = 'lab_access_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 
app.config['MYSQL_AUTH_PLUGIN'] = 'mysql_native_password'
mysql = MySQL(app)

  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND card_number = % s', (email, password ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['card_number']
            session['name'] = user['first_name']
            session['name1'] = user['last_name']
            session['email'] = user['email']
            session['role'] = user['role']
            session['card'] = user['card_number']
            session['rls'] = 'user'
            message = 'Logged in successfully !'            
            return redirect(url_for('dashboard'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)
       
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    user6 = session.get('rls')
    if 'loggedin' in session and user6=='user':
        # Assuming you have the user information in your session
        user = session.get('email')
        user1 = session.get('role')
        user2 = session.get('name')
        user3 = session.get('name1')
        user4=user2+" "+user3
        user5 = session.get('card')
        user6 = session.get('rls')
        return render_template("dashboard.html", user=user, user1=user1,user2=user4, user3=user5,user4=user6)
    elif 'loggedin' in session and user6=='admin':
        user8 = session.get('username') 
        print(user8)
        return render_template("dashboard.html", user2=user8)
    return redirect(url_for('login'))
   
    
@app.route("/users", methods =['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()    
        return render_template("users.html", users = users)
    return redirect(url_for('login'))

@app.route("/save_user", methods =['GET', 'POST'])
def save_user():
    msg = ''    
    if 'loggedin' in session:        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'role' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form :
            
            first_name = request.form['first_name']  
            last_name = request.form['last_name'] 
            email = request.form['email']            
            role = request.form['role']             
            action = request.form['action']
            cursor.execute("SELECT card_number FROM user ORDER BY card_number DESC LIMIT 1")
            result = cursor.fetchone()
            print(result)
            last_usermuber = result['card_number']+1
            card_number = last_usermuber
            filename = ''
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if action == 'updateUser':
                userId = request.form['email']
                print(userId)                
                cursor.execute('UPDATE user SET first_name= %s, last_name= %s, email= %s, picture= %s, role= %s WHERE email = %s', (first_name, last_name, email, filename, role, userId))
                mysql.connection.commit()   
            else:
                cursor.execute('INSERT INTO user (`first_name`, `last_name`, `email`, `picture`, `role`,`card_number`) VALUES (%s, %s, %s, %s, %s, %s)', (first_name, last_name, email, filename, role,last_usermuber))
                mysql.connection.commit()   

            return redirect(url_for('users',last_uber=last_usermuber))        
        elif request.method == 'POST':
            msg = 'Please fill out the form !'        
        return redirect(url_for('users',last_uber=last_usermuber))      
    return redirect(url_for('login'))

@app.route("/edit_user", methods =['GET', 'POST'])
def edit_user():
    msg = ''    
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = % s', (editUserId, ))
        users = cursor.fetchall()         

        return render_template("edit_user.html", users = users)
    return redirect(url_for('login'))

    
@app.route("/view_user", methods =['GET', 'POST'])
def view_user():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = % s', (viewUserId, ))
        user = cursor.fetchone()   
        return render_template("view_user.html", user = user)
    return redirect(url_for('login'))
    
    
@app.route("/delete_user", methods =['GET'])
def delete_user():
    if 'loggedin' in session:
        deleteUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE id = % s', (deleteUserId, ))
        mysql.connection.commit()   
        return redirect(url_for('users'))
    return redirect(url_for('login'))
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    print("registerpage")
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form['password']
        session['rls'] = 'admin'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = % s', (username, ))
        user = cursor.fetchone()
        
        if user and user['password'] == password:
            session['loggedin'] = True
            session['username'] = user['username']
            session['role'] = "admin"
            return redirect(url_for('dashboard',user2=username))

    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message = message)
    
@app.route("/attendance", methods =['GET', 'POST'])
def attendance():
    if 'loggedin' in session:
        userId = session.get('card')
        return render_template("attendance.html", userid = userId)
    return redirect(url_for('login'))

import time  # Import the time module

def generate(userImage):
    IMAGE_FILES = []
    filename = []
    imageDir = r'D:\\SE_Lab\\SE_Project'
    
    if userImage:                 
        img_path = os.path.join(imageDir, userImage)    
        print(img_path)
        img_path = face_recognition.load_image_file(img_path) 
        IMAGE_FILES.append(img_path)
        filename.append(userImage.split(".", 1)[0])    
            
    def encoding_img(IMAGE_FILES):
        encodeList = []
        for img in IMAGE_FILES:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)           
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_path = os.path.join(script_dir, 'attendence.csv')
    def addAttendence(name):        
        with open(csv_path, 'a+') as f:
            mypeople_list = f.readlines()
            dateList = []
            now = datetime.now()
            datestring = now.strftime('%m/%d/%Y')      
            for line in mypeople_list:
                entry = line.split(',')
                dateList.append(entry[1])
            if datestring not in dateList:    
                timestring = now.strftime('%H:%M:%S')              
                f.writelines(f'\n{name},{datestring}')

    encodeListknown = encoding_img(IMAGE_FILES)    

    cap = cv2.VideoCapture(0)

    start_time = time.time()  # Get the current time
    while time.time() - start_time <= 20:  # Run the loop for 10 seconds
        success, img = cap.read()
        imgc = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        # converting image to RGB from BGR
        imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        fasescurrent = face_recognition.face_locations(imgc)
        encode_fasescurrent = face_recognition.face_encodings(imgc, fasescurrent)

        # faceloc- one by one it grab one face location from fasescurrent
        # than encodeFace grab encoding from encode_fasescurrent
        # we want them all in same loop so we are using zip
        for encodeFace, faceloc in zip(encode_fasescurrent, fasescurrent):
            matches_face = face_recognition.compare_faces(encodeListknown, encodeFace)
            face_distence = face_recognition.face_distance(encodeListknown, encodeFace)
            # print(face_distence)
            # finding minimum distence index that will return best match
            matchindex = np.argmin(face_distence)

            if matches_face[matchindex]:
                name = filename[matchindex].upper()
                putText = 'Captured'                
                y1, x2, y2, x1 = faceloc
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), 2, cv2.FILLED)
                cv2.putText(img, putText, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                addAttendence(name)
                break
                
                
                
        
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')        
        key = cv2.waitKey(20)               
        if key == 27:
            cap.release()   
            cv2.destroyAllWindows()             
            break


@app.route('/take_attendance')
def take_attendance():    
    userId = session.get('card')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute('SELECT * FROM user WHERE card_number = % s', (userId, ))
    user = cursor.fetchone()   
    if(user['picture']):
        return Response(generate(user['picture']),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
if __name__ == "__main__":
    app.run(debug=True)
    #app.run()