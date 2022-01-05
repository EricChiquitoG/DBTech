# Imports

import pymysql
from app import app, mysql
from flask import Flask
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import flash, session, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
import uuid
import hashlib
from pymongo.errors import DuplicateKeyError
from user import User


from db import get_reviews, get_single_order,cus_released, new_review2,released,release,items_admin,ongoing,remove_item_cart,get_shipping,order_items,cart_to_order, remove_cart,cart_items, fetch_user, get_article, get_cart, get_stock ,is_admin, edit_product, is_customer, new_art, save_user_tokyo_drift,add_to_cart
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

@app.route("/signup", methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method=='POST':
        username=request.form.get('username')
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        email=request.form.get('email')
        password=request.form.get('password')
        stname=request.form.get('stname')
        st_number=request.form.get('st_number')
        postal_code=request.form.get('postal_code')
        state=request.form.get('state')
        country=request.form.get('country')
        try:
            save_user_tokyo_drift(username,first_name,last_name,email, password, stname,st_number,postal_code, state, country)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)

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
            cart=cart_items(current_user.username)
            return render_template('products.html',articles=prod, carts=cart)
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

@app.route('/add_to_cart', methods=["POST"])
@login_required
def add_prod_to_cart():
    prod_id= request.form["product-id"]
    prod_quant=request.form["quantity"]
    print(prod_quant,current_user.username,prod_id)
    add_to_cart(prod_quant,current_user.username,prod_id)
    prod=get_stock()
    cart=cart_items(current_user.username)
    return render_template('products.html',articles=prod, carts= cart)
    
@app.route('/purchase/<int:id>')
@login_required
def pur(id):
        print(id)
        
        cart_to_order(id)
        prod=get_stock()
        cart=cart_items(current_user.username)
        return render_template('products.html',articles=prod, carts= cart)

@app.route('/empty/<int:id>')
@login_required
def empty(id):
        prod=get_stock()
        cart=cart_items(current_user.username)
        remove_cart(id)
        return render_template('products.html',articles=prod, carts= cart)

@app.route('/myorders')
@login_required
def myorders():
    user=current_user.username
    items_cust=order_items(user)
    released_articles=cus_released(user)
    return render_template('orders_customer.html',items=items_cust, released=released_articles)

@app.route('/products/remove_item/<int:cart_id>/<int:item_id>')
@login_required
def removeitemcart(cart_id, item_id):
    remove_item_cart(cart_id,item_id)
    prod=get_stock()
    cart=cart_items(current_user.username)
    return render_template('products.html',articles=prod, carts= cart)

@app.route('/add/orders')
@login_required
def admin_orders():
    orders=ongoing()
    return render_template('orders_admin.html',orders=orders)

@app.route('/add/orders/<int:id>')
@login_required
def admin_itemsio(id):
    items=items_admin(id)
    return render_template('items_order.html',items=items)

@app.route('/add/orders/<int:id>/release')
@login_required
def release_recollection(id):
    release(id)
    orders=ongoing()
    releases=released()
    return render_template('orders_admin.html',orders=orders,releases=releases)

@app.route('/myorders/<int:id>')
@login_required
def new_review(id):
    return render_template('new_review.html',id=id)

@app.route('/myorders/<int:id>/review',methods=["POST"])
@login_required
def new_review_submit(id):
    user= current_user.username
    comment = request.form["comment"]
    grade = request.form["grade"]
    new_review2(user, id, grade, comment)
    items_cust=order_items(user)
    released_articles=cus_released(user)
    return render_template('orders_customer.html',items=items_cust, released=released_articles)

@app.route('/products/<int:id>/reviews')
@login_required
def all_reviews(id):
    reviews=get_reviews(id)
    return render_template('all_reviews.html',reviews=reviews,id=id)


@login_manager.user_loader
def load_user(username):
    return fetch_user(username)

if __name__ == '__main__':
    app.run(host='localhost')