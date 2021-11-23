# Imports

import pymysql
from app import app, mysql
from flask import Flask
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import flash, session, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
import uuid
import hashlib
from user import User


from db import fetch_user, get_article, get_stock ,is_admin, edit_product, is_customer, new_art
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
# Add hashed passwords



#Login
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user=fetch_user(username)
        if user and user.check_password(password_input):
            login_user(user)

            return redirect(url_for('home'))
        else:
            message = 'Failed to login!'
    return render_template('login.html', message=message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Test route
@app.route('/products', methods=['GET'])
@login_required
def products():
    if is_customer(current_user.username):
        try: 
            prod=get_stock()
            return render_template('products.html',products=prod)
        except Exception as e:
            print (e)
    else: return("this view is only available for customers",404)

@app.route('/', methods=['GET'])
@login_required
def home():
    try: 
        return render_template('home.html')
    except Exception as e:
        print (e)

@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if is_admin(current_user.username):
        if request.method=='GET':
            return render_template('admin_productos.html', articles=get_stock())
    else:
        return "User is not admin", 404


@app.route('/edit/<int:id>')
@login_required
def edit(id):
    if is_admin(current_user.username):
        art=get_article(id)
        return render_template('edit_product.html',article=art)
    else:
        return "User is not admin", 404

@app.route('/edit/update/<int:id>',methods=["POST"])
@login_required
def update(id):

    if is_admin(current_user.username):
        stock = request.form["stock"]
        image_url = request.form["image_url"]
        price = request.form["price"]
        
        edit_product(stock, image_url, price,id)
        return render_template('admin_productos.html', articles=get_stock())

    else:
        return "User is not admin", 404
    
@app.route('/add_art')
@login_required
def add_art():
    return render_template("add.html")


@app.route("/add_art/save", methods=["POST"])
def save():
    id=request.form["id"]
    name=request.form["name"]
    category=request.form["category"]
    stock=request.form["stock"]
    url=request.form["url"]
    price=request.form["price"]
    new_art(id,name, category, stock, url, price)

    return redirect("/add")



#Placeholder
@app.route('/erase', methods=['GET','POST'])
@login_required
def erase():
    if is_admin(current_user.username):

        return render_template('admin_productos.html', articles=get_stock())
    else:
        return "User is not admin", 404

@login_manager.user_loader
def load_user(username):
    return fetch_user(username)

if __name__ == '__main__':
    app.run(host='localhost')