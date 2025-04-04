#sign in
from flask import Blueprint, request, redirect, url_for, render_template
from pymongo import MongoClient
sign_in = Blueprint('sign_in', __name__, url_prefix='/sign_in')

client = MongoClient('mongodb+srv://asdfk:asdfghjkl@collegeproject.zftto.mongodb.net/')
db = client['CollegeProject']
users_collection = db['Credentials'] 


@sign_in.route('/', methods=['GET', 'POST'])
def signup_user():
     if request.method == 'POST':
        name = request.form.get('nm')
        password = request.form.get('password')

#user exists

        existing_user = users_collection.find_one({'username': name})
        if existing_user:
            return '''
            <h3>User already exists!</h3>
            <a href="/sign_in/">Try Again</a>
            '''

        users_collection.insert_one({'username': name, 'password': password})
        return redirect(url_for('login.login_user'))  # Redirect to login page
     return  render_template('Signup_page.html')
    