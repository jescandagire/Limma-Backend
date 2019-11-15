from flask import Flask,request,render_template,jsonify,url_for, redirect,session,flash
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_identity)
import pymysql
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['JWT_SECRET_KEY'] = 'thisisasecretkey'  
# #for the image path upload
# UPLOAD_FOLDER = '/FlaskWeb/static/images/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  
jwt = JWTManager(app)

def db_con():
        db = 'mydb'
        con = pymysql.connect(database=db,user="root",password="",host="localhost")
        con.autocommit(True)
        cursor = con.cursor()
        dict_cursor = con.cursor(pymysql.cursors.DictCursor)
        return (cursor,dict_cursor)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def admin_dash():
    return render_template('dashboard.html')

@app.route('/crops')
def admin_panel():
    return render_template('admin-crop-form.html')

@app.route('/communities')
def admin_communities():
    return render_template('admin-communities.html')

@app.route('/events')
def admin_events():
    return render_template('admin-events.html')

@app.route('/contact')
def contact():
    return render_template('admin-contact-form.html')

@app.route('/users')
def users():
    return render_template('users.html')


#####################################activity with the db tables###########################


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    msg=''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
         # Check if account exists using MySQL
        cursor =db_con()[1]
        account = cursor.execute('SELECT email FROM myAdmin WHERE email = %s', (email))
        account = cursor.fetchone()
     
        if account == None:
            if not re.match(r'^[a-zA-Z0-9-+,.]+@[a-zA-Z0-9.]+\.[a-zA-Z0-9-.]+$', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO myAdmin VALUES (NULL, %s, %s, %s)', (username, email,password ))
            msg = 'You have successfully registered!'
            return render_template('admin-crop-form.html')

        # If account exists show error and validation checks
        if account['email']:
            return jsonify({"msg": "Account already exists"}), 401
  

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    cursor =db_con()[1]
    cursor.execute('SELECT * FROM myAdmin WHERE email = %s ', (email))
    # Fetch one record and return result
    admin = cursor.fetchone()
    if not admin:
        flash('You are not a registered user')
        return render_template('login.html'),401

    if email != admin['email'] or password != admin['password']:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    else:
        access_token = create_access_token(identity=email)
        print(access_token)
    # return jsonify(access_token=access_token), 200
        return render_template('admin-crop-form.html')


@app.route('/admin_crop', methods=['POST','GET'])
def admin_crop():
    if request.method=='POST':
        print(request)
        cursor =db_con()[0]
        crop_name = request.form['crop_name']
        preparations= request.form['preparations']
        image_uploaded = request.files['file']
        filename= secure_filename(image_uploaded.filename)
        image_path = os.path.join('static/images/uploads/', filename)
        image = image_uploaded.save(image_path)
        add_crop = "INSERT INTO crops(crop_name, preparations,image) VALUES (%s, %s, %s)"
        cursor.execute(add_crop, (crop_name,preparations,image_path))
        get_id = "SELECT max(id) FROM crops"
        cursor.execute(get_id)
        get_id = cursor.fetchone()
        crop_id = get_id
        diseases = request.form.getlist('diseases')
        signs = request.form.getlist('signs')
        cure = request.form.getlist('cure')
        add_diseases = "INSERT INTO cropdiseases(crop_id, diseases, signs,cure) VALUES (%s, %s, %s, %s)"
        for count in range(len(diseases)):
            cursor.execute(add_diseases, (crop_id, diseases[count], signs[count], cure[count]))
        cursor.close()
        
    return render_template('admin-crop-form.html')

@app.route('/admin_community', methods=['POST','GET'])
def admin_community():
    if request.method=='POST':
        cursor =db_con()[0]
        communityName = request.form['communityName']
        location= request.form['location']
        add_community = "INSERT INTO communities(communityName, location) VALUES (%s, %s)"
        cursor.execute(add_community, (communityName,location))
        cursor.close()
    return render_template('admin-communities.html')

@app.route('/admin_event', methods=['POST','GET'])
def admin_event():
    if request.method=='POST':
        cursor =db_con()[0]
        eventName = request.form['eventName']
        date = request.form['date']
        address= request.form['address']
        add_event = "INSERT INTO events(eventName, date,address) VALUES (%s, %s, %s)"
        cursor.execute(add_event, (eventName,date,address))
        cursor.close()
    return render_template('admin-events.html')


@app.route('/admin_contact', methods=['POST','GET'])
def admin_contact():
    if request.method=='POST':
        cursor =db_con()[0]
        telephone = request.form['telephone']
        
        location= request.form['location']
        email= request.form['email']
        add_contact = "INSERT INTO contact(telephone, location,email) VALUES (%s, %s, %s)"
        cursor.execute(add_contact, (telephone,location,email))
        cursor.close()
    return render_template('admin-contact-form.html')

@app.route('/fetch_crops', methods = ['POST', 'GET'])
def fetch_crops():
    cursor = db_con()[1]
    cursor.execute("SELECT * FROM CROPS")
    crops = cursor.fetchall()
    return render_template('cropsTable.html', crops = crops)

@app.route('/fetch_pests_diseases/<int:crop_id>', methods = ['POST', 'GET'])
def fetch_pests_diseases(crop_id):
    cursor = db_con()[1]
    cursor.execute("SELECT * FROM CROPDISEASES WHERE crop_id = %s", (crop_id))
    pests_diseases = cursor.fetchall()
    return render_template('cropDetailsTable.html', pests_diseases = pests_diseases)

@app.route('/edit_crop/<int:id>', methods = ['GET'])
def edit_crop(id):
    cursor = db_con()[1]
    #get crops that qualify with the supplied id
    cursor.execute("SELECT * FROM CROPS WHERE id = %s", (id))
    data = cursor.fetchall()
    data = data[0]
    #get diseases that qualify with the supplied id
    cursor.execute("SELECT * FROM CROPDISEASES WHERE crop_id = %s", (id))
    data1 = cursor.fetchall()
    data1 = data1
    #append diseases to crops object
    data.update({'diseases':data1})
    #return jsonify(data)
    #cursor.execute("SELECT * FROM CROPS LEFT JOIN CROPDISEASES ON crops.id=cropdiseases.crop_id WHERE crops.id = %s", (id))
    return render_template('edit-form.html', crops = data)

@app.route('/update_crop/<int:id>', methods=['POST'])
def update_crop(id):
    cursor =db_con()[0]
    crop_name = request.form['crop_name']
    preparations= request.form['preparations']
    image_uploaded = request.files['file']
    filename= secure_filename(image_uploaded.filename)
    image_path = os.path.join('static/images/uploads/', filename)
    image = image_uploaded.save(image_path)
    add_crop = "UPDATE crops SET crop_name = '{}' , preparations = '{}'WHERE id='{}'".format(crop_name,preparations,id)
    cursor.execute(add_crop)
    diseases = request.form.getlist('diseases')
    signs = request.form.getlist('signs')
    cure = request.form.getlist('cure')
    
    for count in range(len(diseases)):
        add_diseases = "UPDATE cropdiseases SET diseases = '{}' , signs = '{}', cure = '{}' WHERE id='{}'".format(diseases[count],signs[count], cure[count],id)
        cursor.execute(add_diseases)
    cursor.close()
        
    # return render_template('cropsTable.html')
    return redirect(url_for('edit_crop',id=id))

@app.route('/display_details', methods = ['POST', 'GET'])
def display_details(id):
    cursor = db_con()[0]
    cursor.execute("SELECT crops.id, crops.crop_name, crops.preparations, crops.image, cropdiseases.diseases, cropdiseases.signs, cropdiseases.cure FROM crops, cropdiseases WHERE crops.id = cropdiseases.crop_id")
    contents = cursor.fetchall()
    return render_template('crops-in-detail-table.html', contents = contents)
    
if __name__ == "__main__": 
    app.run(debug=True)