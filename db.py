from datetime import datetime
from os import getsid
from werkzeug.security import generate_password_hash
from user import User
import pymysql
from app import app, mysql
import random



def save_user(id,password):
    password_hash = generate_password_hash(password)
    sql = "UPDATE Users SET password = %s where user_id = %s"
    data = (password_hash,id)
    print(data)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data,)
    conn.commit()

def save_user_tokyo_drift(username, fn, ln, email, password, stname, stn, pc, state, country):
    password_hash = generate_password_hash(password)
    randid=random.randint(100,9999)
    sql="INSERT into Users(user_id,username, first_name, last_name,email,password,stname, st_number, postal_code,state,country) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data=(randid,username,fn,ln,email,password_hash,stname,stn,pc,state,country)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data,)
    conn.commit()
    add_cost(randid,fn,ln)

def add_cost(id, fn, ln):
    sql = "INSERT into Customers(cust_id, first_name, last_name) VALUES (%s,%s,%s)"
    data=(id,fn,ln)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data,)
    conn.commit()

def get_uid(username):
    sql="Select user_id from Users WHERE username= %s"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, username,)
    record=cursor.fetchone()
    return record[0] if record else None


#Retreives user info necessary for the login
def fetch_user(username):
    sql="Select username, password from Users WHERE username= %s"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, username,)
    record=cursor.fetchone()
    return User(record[0],record[1]) if record else None

def get_stock():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(rows)

def is_admin(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT A.first_name FROM Store.Admins A join Users U on A.admin_id=U.user_id where U.username=%s",user)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(True if rows else None)

def is_customer(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT A.first_name FROM Store.Customers A join Users U on A.cust_id=U.user_id where U.username=%s",user)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(True if rows else None)

def edit_product(stock, image_url,price,id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE articles SET stock = %s, image_url = %s, price = %s WHERE article_id = %s",
                       (stock, image_url, price, id))
    conn.commit()
    conn.close()


def get_article(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
            "SELECT article_id, article_name, category, stock, image_url, price FROM articles WHERE article_id = %s", (id,))
    art = cursor.fetchone()
    conn.close()
    return art

def new_art(id, name, category, stock, url, price):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (article_id, article_name, category, stock, image_url, price) VALUES (%s, %s, %s,%s, %s,%s)",(id, name, category, stock, url, price))
    conn.commit()
    conn.close()

def get_cart(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
            "SELECT cart_id FROM Cart WHERE user_id = %s", (user_id))
    cart = cursor.fetchone()
    conn.close()
    return cart

def get_order(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
            "SELECT order_id FROM Orders WHERE user_id = %s", (user_id))
    cart = cursor.fetchall()
    conn.close()
    return cart

def cart_items(user_id):
    user=get_uid(user_id)
    cart=get_cart(user)
    if cart == None:
        cart='1'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select n.article_name, n.image_url, n.quantity, n.total, n.cart_id, n.article_id from (SELECT c.cart_id, a.article_name, a.image_url, c.quantity, a.price*c.quantity as total, a.article_id    FROM cart_items c join articles a on a.article_id = c.article_id) n where n.cart_id = %s",(cart))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(rows)

def order_items(user_id):
    user=get_uid(user_id)
    carts=get_order(user)
    cart = tuple([item[0] for item in carts])
    print(cart)
    if cart == None:
        cart='1'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select n.order_id, n.article_name, n.image_url, n.quantity, n.total  from (SELECT c.order_id, a.article_name, a.image_url, c.quantity, a.price*c.quantity as total     FROM order_items c join articles a on a.article_id = c.article_id) n where n.order_id in {} and n.order_id in (select order_id from Orders where status = 'submitted') ".format(cart))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(rows)

def cus_released(user_id):
    user=get_uid(user_id)
    carts=get_order(user)
    cart = tuple([item[0] for item in carts])
    print(cart)
    if cart == None:
        cart='1'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select n.order_id, n.article_name, n.image_url, n.quantity, n.total, n.article_id  from (SELECT c.order_id, a.article_name, c.article_id, a.image_url, c.quantity, a.price*c.quantity as total    FROM order_items c join articles a on a.article_id = c.article_id) n where n.order_id in {} and n.order_id in (select order_id from Orders where status = 'released') ".format(cart))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return(rows)

def get_shipping(order_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("SELECT date, stname, st_number, postal_code, state, country, status FROM Orders WHERE order_id = %s", (order_id))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    return rows

def item_in_cart(cart_id, art_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("SELECT * FROM cart_items WHERE cart_id = %s and article_id = %s", (cart_id,art_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_quant(cart_id, art_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("SELECT quantity FROM cart_items WHERE cart_id = %s and article_id = %s", (cart_id,art_id))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    return rows


def add_item_cart(cart_id,art_id,uid,quantity):
    randid=random.randint(100,9999)
    conn = mysql.connect()
    cursor = conn.cursor()
    
    if item_in_cart(cart_id,art_id):
        quant=get_quant(cart_id,art_id)[0]
        cursor.execute("UPDATE cart_items SET quantity = %s WHERE cart_id= %s and article_id = %s",
                       (int(quant)+int(quantity), cart_id, art_id))
    else:
        cursor.execute("insert into cart_items (id, cart_id, article_id, user_id,quantity, price, created_at) select %s, %s, %s,  %s,%s, price, %s  from articles where article_id = %s",(randid,cart_id,art_id,uid,quantity,datetime.now(),art_id))
    conn.commit()
    conn.close()

def get_single_order(order_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("SELECT * FROM Orders WHERE order_id = %s", (order_id))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    return rows

def add_to_cart(quantity, username,art_id):
    
    user=get_uid(username)
    print(user)
    cart=get_cart(user)
    if cart == None: # This means there is no cart created by this issuer so a new cart has to be created
        conn = mysql.connect()
        cursor = conn.cursor()
        randid=random.randint(100,9999)
        cursor.execute("insert into Cart (cart_id, user_id, created_at,  email, stname, st_number, postal_code, state, country,status) select %s, user_id, %s, email, stname, st_number, postal_code, state, country, %s  from Users where user_id = %s",(randid,datetime.now(),'submitted',user))
        conn.commit()
        conn.close()
        cart=get_cart(user)
    cart=cart[0]
    add_item_cart(cart,art_id,user,quantity)
    # At this point we know the ID of the cart to which the product will be added.

def stock_deduct(order_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("SELECT article_id, quantity FROM order_items WHERE order_id = %s", (order_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for i in rows:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET stock = stock-%s WHERE article_id = %s",
                        (int(i[1]),i[0]))
        conn.commit()
        conn.close()

def cart_to_order(cart_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("insert into Orders (order_id, user_id, date, email,stname, st_number, postal_code, state, country, status) select cart_id, user_id, %s,  email, stname, st_number, postal_code, state, country, %s  from Cart where cart_id = %s",(datetime.now(), 'submitted', cart_id))
    cursor.execute("Insert into order_items select * from cart_items where cart_id=%s", (cart_id))

 
    conn.commit()   
    cursor.close()
    conn.close()
       ## Script to reduce stock by the ammount of the purchase
    stock_deduct(cart_id)
    
    remove_cart(cart_id)

def remove_cart(cart_id):
    print(cart_id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("delete from cart_items where cart_id=%s", (cart_id))
    cursor.execute ("delete from Cart where cart_id=%s", (cart_id))
    conn.commit()
    cursor.close()
    conn.close()

def remove_item_cart(cart_id, art_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("delete from cart_items where cart_id=%s and article_id=%s", (cart_id, art_id))
    conn.commit()
    cursor.close()
    conn.close()

def ongoing():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("select * from Orders where status = 'submitted'")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def released():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("select * from Orders where status = 'released'")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def items_admin(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select n.order_id, n.article_name, n.image_url, n.quantity, n.total  from (SELECT c.order_id, a.article_name, a.image_url, c.quantity, a.price*c.quantity as total     FROM order_items c join articles a on a.article_id = c.article_id) n where n.order_id = {}".format(id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def release(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE Orders SET status = 'released' WHERE order_id = %s",
                       (id))
    conn.commit()
    conn.close()

def new_review2(uid, article_id, rate, comment):
    conn = mysql.connect()
    cursor = conn.cursor()
    user_id=get_uid(uid)
    cursor.execute("INSERT into reviews2 (id, article_id, user_id, grade, review) VALUES (%s,%s,%s,%s,%s)",(random.randint(100,9999),article_id,user_id,rate,comment))
    conn.commit()   
    cursor.close()
    conn.close()
    calulate_grade(article_id,rate)

def score_exist(article_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("select avg_rate from articles where article_id = %s",(article_id))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    return rows

def calulate_grade(article_id, score):
    conn = mysql.connect()
    cursor = conn.cursor()
    if score_exist(article_id)==None:
        cursor.execute("UPDATE articles SET avg_rate = %s WHERE article_id = %s",
                       (score, article_id))
    else:
        cursor.execute("update articles a join (select article_id, avg(grade) as avg_rate from reviews2 r group by article_id) r on a.article_id = r.article_id set a.avg_rate = r.avg_rate")
    conn.commit()
    conn.close()

def get_reviews(article_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute ("select * from reviews2 where article_id = %s",(article_id))
    rows = cursor.fetchall()
    print(rows)
    cursor.close()
    conn.close()
    return rows

#add_to_cart(2,1465,47001)
#print(get_uid('ericc'))
