from os import getsid
from werkzeug.security import generate_password_hash
from user import User
import pymysql
from app import app, mysql

''' def save_user(id,password):
    password_hash = generate_password_hash(password)
    sql = "UPDATE Users SET password = %s where user_id = %s"
    data = (password_hash,id)
    print(data)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data,)
    conn.commit()
save_user(7548,'test5') '''

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
