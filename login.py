# login.py
from flask import Blueprint, request, redirect, url_for,flash, render_template
from pymongo import MongoClient
login = Blueprint('login', __name__, url_prefix='/login')

client = MongoClient('mongodb+srv://asdfk:asdfghjkl@collegeproject.zftto.mongodb.net/')
db = client['CollegeProject']
users_collection = db['Credentials'] 

@login.route('/', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        name = request.form.get('nm')
        password = request.form.get('password')
        user = users_collection.find_one({'username': name, 'password': password})
        if user:
            return redirect(url_for('dashboard.dashboard_homepage'))

        else:
            return '''
            <h3>Invalid credentials. Try again.</h3>
            <a href="/login/">Back to Login</a>
            '''

        
    return render_template('Login_page.html')
    
